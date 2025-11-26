#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pokémon TCG Image Downloader — Scrydex MINI GUI (REST-only, Dual-List + Caching)

- Uses Scrydex Pokémon API (not pokemontcg.io).
- Auth: X-Api-Key + X-Team-ID.
- Endpoints:
    • GET /pokemon/v1/expansions
    • GET /pokemon/v1/expansions/{id}/cards

- Caches:
    • sets_cache.json         -> avoids re-fetching expansions each time
    • selected_cache.json     -> remembers which expansions you picked last time

- UI: Available (left) <-> Selected (right), filter, Add/Remove, double-click to move
- Per-expansion folders inside output folder (e.g., pokemon_cards/sv1/...).
- Parallel downloads, retries, progress bar + log.
"""

import json
import math
import queue
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Iterable

import requests
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import dotenv

# -----------------------------
# CONFIG: paste your Scrydex credentials here (optional)
# -----------------------------
API_KEY_DEFAULT = dotenv.get_key(".env", "API_KEY")
TEAM_ID_DEFAULT = dotenv.get_key(".env", "TEAM_ID")

API_BASE = "https://api.scrydex.com/pokemon/v1"
DEFAULT_PAGE_SIZE = 250
APP_USER_AGENT = "pokemon-tcg-image-downloader-mini-scrydex/1.0"

# Cache files (next to the script)
CACHE_DIR = Path.cwd()
SETS_CACHE_FILE = CACHE_DIR / "sets_cache.json"
SELECTED_CACHE_FILE = CACHE_DIR / "selected_cache.json"

# -----------------------------
# Networking helpers
# -----------------------------
def make_session(api_key: Optional[str], team_id: Optional[str]) -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": APP_USER_AGENT})
    s.headers.update({"Accept": "application/json"})
    if api_key:
        s.headers.update({"X-Api-Key": api_key})
    if team_id:
        s.headers.update({"X-Team-ID": team_id})
    return s


def backoff_sleep(attempt: int, base: float = 0.75, cap: float = 8.0):
    time.sleep(min(cap, base * (2 ** (attempt - 1))))


def http_get_json(
    session: requests.Session,
    url: str,
    params: Dict = None,
    max_retries: int = 6
) -> Dict:
    params = params or {}
    last_err = None
    for attempt in range(1, max_retries + 1):
        try:
            r = session.get(url, params=params, timeout=30)
            if r.status_code in (429, 500, 502, 503, 504):
                backoff_sleep(attempt)
                continue
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last_err = e
            backoff_sleep(attempt)
    raise RuntimeError(f"GET failed after {max_retries} attempts: {url}\n{last_err}")


# -----------------------------
# Expansion helpers
# -----------------------------
def normalize_expansion(raw: Dict) -> Dict:
    """
    Normalize Scrydex expansion object into:

      - id:     used in URL (/expansions/{id}/cards)
      - name:   expansion name
      - series: grouping/series label (best effort)
    """
    exp_id = (
        raw.get("id")
        or raw.get("slug")
        or raw.get("code")
    )
    name = raw.get("name") or exp_id
    series = raw.get("series") or raw.get("category") or ""
    return {
        "id": exp_id,
        "name": name,
        "series": series,
        "_raw": raw,
    }


def list_sets(session: requests.Session) -> List[Dict]:
    """
    List expansions from Scrydex with pagination.

    Expected shape:
      {
        "data": [ { ...expansion... }, ... ],
        "page": int,
        "page_size": int,
        "count": int,
        "total_count": int
      }
    """
    expansions: List[Dict] = []
    page = 1

    while True:
        params = {
            "page": page,
            "page_size": DEFAULT_PAGE_SIZE,
        }
        data = http_get_json(session, f"{API_BASE}/expansions", params=params)

        if not isinstance(data, dict):
            break

        raw_list = data.get("data", [])
        if not isinstance(raw_list, list) or not raw_list:
            break

        for e in raw_list:
            if not isinstance(e, dict):
                continue
            norm = normalize_expansion(e)
            if norm.get("id"):
                expansions.append(norm)

        count = data.get("count", len(raw_list))
        total_count = data.get("total_count")
        if count < params["page_size"]:
            break
        if total_count is not None and page >= math.ceil(total_count / params["page_size"]):
            break

        page += 1

    return expansions


# -----------------------------
# Card helpers
# -----------------------------
def paginate_cards(
    session: requests.Session,
    set_id: str,
    page_size: int = DEFAULT_PAGE_SIZE
) -> Iterable[Dict]:
    """
    Yield card dicts for an expansion in Scrydex.

    Scrydex response shape:
      {
        "data": [ { ...card... }, ... ],
        "page": int,
        "page_size": int,     # ACTUAL page size used by the API (often 100)
        "count": int,         # number of cards in THIS page
        "total_count": int    # total cards across all pages
      }

    We:
      - Request with page_size (e.g. 250)
      - But ALWAYS respect the response page_size (API may clamp to 100)
      - Stop when we've reached total_count, or when a page returns no cards.
    """
    page = 1
    while True:
        params = {
            "page": page,
            "page_size": page_size,
        }
        url = f"{API_BASE}/expansions/{set_id}/cards"
        data = http_get_json(session, url, params=params)

        if not isinstance(data, dict):
            break

        cards = data.get("data", [])
        if not isinstance(cards, list) or not cards:
            # no cards = no more pages
            break

        # Yield all cards from this page
        for card in cards:
            if isinstance(card, dict):
                yield card

        # Use the ACTUAL page_size reported by the API (it might clamp)
        resp_page_size = data.get("page_size") or page_size
        count = data.get("count", len(cards))
        total_count = data.get("total_count")

        # If total_count is provided, stop when we've reached or passed it
        if isinstance(total_count, int) and total_count > 0:
            if page * resp_page_size >= total_count:
                break
        else:
            # Fallback: if this page returned fewer cards than the API's page_size,
            # there are no more pages.
            if count < resp_page_size:
                break

        page += 1



def ext_from_url(url: str) -> str:
    tail = url.split("?", 1)[0].split("/")[-1]
    if "." in tail:
        return "." + tail.split(".")[-1].lower()
    return ".jpg"


def pick_image_url(card: Dict, size_key: str) -> Optional[str]:
    """
    Scrydex card example:

      "images": [
        {
          "type": "front",
          "small": "https://...",
          "medium": "https://...",
          "large": "https://..."
        }
      ]

    We:
      - Prefer image with type=="front"
      - Fall back to first image
      - Then pick size_key, or large/medium/small in that order.
    """
    images = card.get("images")
    if isinstance(images, list) and images:
        chosen = None
        for img in images:
            if isinstance(img, dict) and img.get("type") == "front":
                chosen = img
                break
        if chosen is None:
            chosen = images[0] if isinstance(images[0], dict) else None
        if isinstance(chosen, dict):
            return (
                chosen.get(size_key)
                or chosen.get("large")
                or chosen.get("medium")
                or chosen.get("small")
            )

    elif isinstance(images, dict):
        return (
            images.get(size_key)
            or images.get("large")
            or images.get("medium")
            or images.get("small")
        )

    return None


def download_image(
    session: requests.Session,
    url: str,
    out_path: Path,
    max_retries: int = 6
) -> bool:
    for attempt in range(1, max_retries + 1):
        try:
            with session.get(url, stream=True, timeout=60) as r:
                if r.status_code in (429, 500, 502, 503, 504):
                    backoff_sleep(attempt, base=0.9, cap=20)
                    continue
                r.raise_for_status()
                tmp = out_path.with_suffix(out_path.suffix + ".part")
                with open(tmp, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1 << 15):
                        if chunk:
                            f.write(chunk)
                tmp.replace(out_path)
                return True
        except Exception:
            backoff_sleep(attempt, base=0.9, cap=20)
    return False


# -----------------------------
# Worker thread
# -----------------------------
class Downloader(threading.Thread):
    def __init__(
        self,
        app_ref,
        session: requests.Session,
        sets: List[Dict],
        size_key: str,
        out_dir: Path,
        max_workers: int,
        overwrite: bool
    ):
        super().__init__(daemon=True)
        self.app = app_ref
        self.s = session
        self.sets = sets
        self.size_key = size_key
        self.out_dir = out_dir
        self.max_workers = max_workers
        self.overwrite = overwrite
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def run(self):
        try:
            self._run_impl()
        except Exception as e:
            self.app.log(f"[error] {e}")
        finally:
            self.app.on_download_finished()

    def _run_impl(self):
        import concurrent.futures

        tasks = []

        for s in self.sets:
            if not isinstance(s, dict):
                self.app.log(
                    f"[warn] Skipping expansion entry of unexpected type {type(s)}: {s}"
                )
                continue

            sid = s.get("id")
            sname = s.get("name")
            if not sid:
                self.app.log(f"[warn] Expansion missing id: {s}")
                continue

            self.app.log(f"Enumerating cards for expansion {sid}: {sname}")
            try:
                for card in paginate_cards(self.s, sid):
                    if self._stop.is_set():
                        break

                    if not isinstance(card, dict):
                        self.app.log(
                            f"[warn] Skipping card with unexpected type {type(card)} in {sid}: {card}"
                        )
                        continue

                    url = pick_image_url(card, self.size_key)
                    if not url:
                        continue

                    ext = ext_from_url(url)
                    dest_dir = self.out_dir / sid  # per-expansion folder
                    dest_dir.mkdir(parents=True, exist_ok=True)

                    cid = card.get("id") or card.get("number") or "unknown"
                    out_path = dest_dir / f"{cid}_{self.size_key}{ext}"

                    if out_path.exists() and not self.overwrite:
                        self.app.progress_total += 1
                        self.app.progress_done += 1
                        continue

                    tasks.append((url, out_path, cid))

            except Exception as e:
                self.app.log(f"[warn] Failed to enumerate expansion {sid}: {e}")

            if self._stop.is_set():
                self.app.log("Stopped during enumeration.")
                break

        if not tasks and self.app.progress_done == 0:
            self.app.log(
                "Nothing to download (either no images or everything already exists)."
            )
            self.app.set_progress(1.0)
            return

        self.app.progress_total += len(tasks)
        self.app.set_progress(0.0)
        self.app.log(f"Starting downloads: {len(tasks)} images ...")

        def worker(tup):
            url, out_path, cid = tup
            ok = download_image(self.s, url, out_path, max_retries=6)
            return (cid, ok)

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers
        ) as ex:
            for cid, ok in ex.map(worker, tasks):
                if self._stop.is_set():
                    self.app.log("Stopped by user.")
                    break
                self.app.progress_done += 1
                self.app.set_progress(
                    self.app.progress_done / max(1, self.app.progress_total)
                )
                if ok:
                    self.app.log(f"✓ {cid}")
                else:
                    self.app.log(f"✗ {cid} (failed)")


# -----------------------------
# Tkinter App (Dual-List + Cache)
# -----------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pokémon TCG Image Downloader (Scrydex — REST, Cached)")
        self.geometry("1000x680")
        self.minsize(900, 640)

        # state
        self.sets: List[Dict] = []
        self.sets_by_id: Dict[str, Dict] = {}
        self.selected_ids: List[str] = []  # persists via cache
        self.progress_total = 0
        self.progress_done = 0
        self.worker: Optional[Downloader] = None
        self.log_queue = queue.Queue()

        # UI
        self._build_ui()

        # Load caches immediately (no network needed)
        self._load_sets_cache()
        self._load_selected_cache()
        self._apply_filter_available()

        # log pump
        self.after(120, self._drain_log)

    # --- UI
    def _build_ui(self):
        root = ttk.Frame(self, padding=10)
        root.pack(fill="both", expand=True)

        opt = ttk.LabelFrame(root, text="Options", padding=10)
        opt.pack(fill="x")

        # API key
        ttk.Label(opt, text="API Key:").grid(row=0, column=0, sticky="w")
        self.api_var = tk.StringVar(value=API_KEY_DEFAULT)
        ttk.Entry(opt, textvariable=self.api_var, width=54).grid(
            row=0, column=1, sticky="we", padx=6, pady=2
        )

        # Team ID
        ttk.Label(opt, text="Team ID:").grid(row=1, column=0, sticky="w")
        self.team_var = tk.StringVar(value=TEAM_ID_DEFAULT)
        ttk.Entry(opt, textvariable=self.team_var, width=54).grid(
            row=1, column=1, sticky="we", padx=6, pady=2
        )

        # Image size
        ttk.Label(opt, text="Image size:").grid(row=2, column=0, sticky="w")
        self.size_var = tk.StringVar(value="large")
        ttk.Combobox(
            opt,
            textvariable=self.size_var,
            values=["small", "medium", "large"],
            state="readonly",
            width=10,
        ).grid(row=2, column=1, sticky="w", padx=6, pady=2)

        # Parallel downloads
        ttk.Label(opt, text="Parallel downloads:").grid(row=3, column=0, sticky="w")
        self.workers_var = tk.IntVar(value=8)
        ttk.Spinbox(
            opt,
            from_=1,
            to=64,
            textvariable=self.workers_var,
            width=6,
        ).grid(row=3, column=1, sticky="w", padx=6, pady=2)

        # Output folder
        ttk.Label(opt, text="Output folder:").grid(row=4, column=0, sticky="w")

        script_dir = Path(__file__).resolve().parent
        self.out_var = tk.StringVar(
            value=str(script_dir / "pokemon_cards")
        )

        out_row = ttk.Frame(opt)
        out_row.grid(row=4, column=1, sticky="we", padx=6, pady=2)
        ttk.Entry(out_row, textvariable=self.out_var).pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(out_row, text="Browse", command=self._browse_out).pack(
            side="left", padx=(6, 0)
        )

        # Overwrite
        self.overwrite_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            opt,
            text="Overwrite existing files",
            variable=self.overwrite_var,
        ).grid(row=5, column=1, sticky="w", padx=6, pady=2)

        opt.columnconfigure(1, weight=1)

        # Actions
        actions = ttk.Frame(root)
        actions.pack(fill="x", pady=(8, 6))
        ttk.Button(
            actions,
            text="Refresh Expansions (from Scrydex)",
            command=self.refresh_sets,
        ).pack(side="left")
        ttk.Button(
            actions, text="Start Download", command=self.start_download
        ).pack(side="left", padx=(8, 0))
        self.stop_btn = ttk.Button(
            actions, text="Stop", command=self.stop_download, state="disabled"
        )
        self.stop_btn.pack(side="left", padx=(8, 0))

        # Progress
        self.progress = ttk.Progressbar(root, mode="determinate")
        self.progress.pack(fill="x", pady=(4, 10))

        # Dual lists
        lists = ttk.Frame(root)
        lists.pack(fill="both", expand=True)

        left = ttk.Frame(lists)
        left.pack(side="left", fill="both", expand=True)

        top_left = ttk.Frame(left)
        top_left.pack(fill="x")
        ttk.Label(top_left, text="Available Expansions").pack(side="left")
        ttk.Label(top_left, text="Filter:").pack(side="left", padx=(12, 2))
        self.filter_var = tk.StringVar()
        f_entry = ttk.Entry(top_left, textvariable=self.filter_var, width=24)
        f_entry.pack(side="left")
        f_entry.bind("<KeyRelease>", lambda e: self._apply_filter_available())

        self.available_list = tk.Listbox(left, selectmode=tk.EXTENDED)
        self.available_list.pack(fill="both", expand=True, pady=(4, 0))
        self.available_list.bind(
            "<Double-Button-1>", lambda e: self.add_selected()
        )

        left_btns = ttk.Frame(left)
        left_btns.pack(fill="x", pady=(6, 0))
        ttk.Button(
            left_btns, text="Select All (left)", command=self._select_all_available
        ).pack(side="left")
        ttk.Button(
            left_btns, text="Clear (left)", command=self._clear_available_selection
        ).pack(side="left", padx=(6, 0))

        mid = ttk.Frame(lists, padding=10)
        mid.pack(side="left", fill="y")
        ttk.Button(
            mid, text="Add »", command=self.add_selected, width=10
        ).pack(pady=(30, 6))
        ttk.Button(
            mid, text="« Remove", command=self.remove_selected, width=10
        ).pack()

        right = ttk.Frame(lists)
        right.pack(side="left", fill="both", expand=True)

        top_right = ttk.Frame(right)
        top_right.pack(fill="x")
        ttk.Label(
            top_right, text="Selected for Download"
        ).pack(side="left")

        self.selected_list = tk.Listbox(right, selectmode=tk.EXTENDED)
        self.selected_list.pack(fill="both", expand=True, pady=(4, 0))
        self.selected_list.bind(
            "<Double-Button-1>", lambda e: self.remove_selected()
        )

        right_btns = ttk.Frame(right)
        right_btns.pack(fill="x", pady=(6, 0))
        ttk.Button(
            right_btns, text="Select All (right)", command=self._select_all_selected
        ).pack(side="left")
        ttk.Button(
            right_btns, text="Clear (right)", command=self._clear_selected_selection
        ).pack(side="left", padx=(6, 0))

        # Log
        log_frame = ttk.LabelFrame(root, text="Log", padding=6)
        log_frame.pack(fill="both", expand=False, pady=(8, 0))
        self.log_text = tk.Text(log_frame, height=10, wrap="word", state="disabled")
        self.log_text.pack(fill="both", expand=True)

    # ----- Cache helpers -----
    def _load_sets_cache(self):
        if SETS_CACHE_FILE.exists():
            try:
                with open(SETS_CACHE_FILE, "r", encoding="utf-8") as f:
                    self.sets = json.load(f)
                self.sets_by_id = {s.get("id", ""): s for s in self.sets if isinstance(s, dict)}
                self.log(f"Loaded expansions from cache ({len(self.sets)}).")
            except Exception as e:
                self.log(f"[warn] Failed reading sets cache: {e}")

    def _save_sets_cache(self):
        try:
            with open(SETS_CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.sets, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log(f"[warn] Failed writing sets cache: {e}")

    def _load_selected_cache(self):
        if SELECTED_CACHE_FILE.exists():
            try:
                with open(SELECTED_CACHE_FILE, "r", encoding="utf-8") as f:
                    self.selected_ids = json.load(f)
                self.selected_list.delete(0, tk.END)
                for sid in self.selected_ids:
                    s = self.sets_by_id.get(sid)
                    if s:
                        self.selected_list.insert(
                            tk.END,
                            f"{s.get('id')} | {s.get('name')} | {s.get('series')}",
                        )
                self.log(
                    f"Restored {len(self.selected_ids)} selected expansion(s) from cache."
                )
            except Exception as e:
                self.log(f"[warn] Failed reading selected cache: {e}")

    def _save_selected_cache(self):
        try:
            with open(SELECTED_CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.selected_ids, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log(f"[warn] Failed writing selected cache: {e}")

    # ----- Utility/UI helpers -----
    def _browse_out(self):
        d = filedialog.askdirectory(
            title="Select Output Folder", mustexist=True
        )
        if d:
            self.out_var.set(d)

    def log(self, msg: str):
        self.log_queue.put(msg)

    def _drain_log(self):
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.log_text.configure(state="normal")
                self.log_text.insert(tk.END, msg + "\n")
                self.log_text.see(tk.END)
                self.log_text.configure(state="disabled")
        except queue.Empty:
            pass
        self.after(120, self._drain_log)

    def set_progress(self, frac: float):
        frac = max(0.0, min(1.0, frac))
        self.progress["value"] = int(frac * 100)

    # Available list helpers
    def _apply_filter_available(self):
        q = self.filter_var.get().strip().lower()
        self.available_list.delete(0, tk.END)
        for s in self.sets:
            if not isinstance(s, dict):
                continue
            label = f"{s.get('id')} | {s.get('name')} | {s.get('series')}"
            if not q or q in label.lower():
                self.available_list.insert(tk.END, label)

    def _select_all_available(self):
        self.available_list.select_set(0, tk.END)

    def _clear_available_selection(self):
        self.available_list.selection_clear(0, tk.END)

    # Selected list helpers
    def _select_all_selected(self):
        self.selected_list.select_set(0, tk.END)

    def _clear_selected_selection(self):
        self.selected_list.selection_clear(0, tk.END)

    # Move between lists + persist
    def add_selected(self):
        indices = list(self.available_list.curselection())
        if not indices and self.available_list.size() > 0:
            try:
                idx = self.available_list.index(tk.ACTIVE)
                if idx is not None:
                    indices = [idx]
            except Exception:
                pass

        changed = False
        for i in indices:
            label = self.available_list.get(i)
            sid = label.split("|", 1)[0].strip()
            if sid.lower() not in [x.lower() for x in self.selected_ids]:
                self.selected_ids.append(sid)
                self.selected_list.insert(tk.END, label)
                changed = True
        if changed:
            self._save_selected_cache()

    def remove_selected(self):
        indices = sorted(
            list(self.selected_list.curselection()), reverse=True
        )
        removed_sids = set()
        for i in indices:
            label = self.selected_list.get(i)
            sid = label.split("|", 1)[0].strip()
            removed_sids.add(sid.lower())
            self.selected_list.delete(i)
        if removed_sids:
            self.selected_ids = [
                sid
                for sid in self.selected_ids
                if sid.lower() not in removed_sids
            ]
            self._save_selected_cache()

    # ----- Actions -----
    def refresh_sets(self):
        def task():
            try:
                key = self.api_var.get().strip() or None
                team = self.team_var.get().strip() or None
                if not key or not team:
                    raise RuntimeError(
                        "Please paste your API key AND Team ID first."
                    )
                s = make_session(key, team)
                self.log("Fetching expansion list from Scrydex...")
                all_sets = list_sets(s)
                self.sets = all_sets
                self.sets_by_id = {
                    s.get("id", ""): s for s in all_sets if isinstance(s, dict)
                }
                self._save_sets_cache()
                self.log(
                    f"Loaded {len(all_sets)} expansions (and cached)."
                )
                self.after(0, self._apply_filter_available)
            except Exception as e:
                messagebox.showerror(
                    "Error", f"Failed to fetch expansions:\n{e}"
                )

        threading.Thread(target=task, daemon=True).start()

    def start_download(self):
        if self.worker and self.worker.is_alive():
            messagebox.showinfo(
                "Busy", "A download is already in progress."
            )
            return

        key = self.api_var.get().strip() or None
        team = self.team_var.get().strip() or None
        if not key or not team:
            messagebox.showerror(
                "Credentials", "Please paste your API key AND Team ID first."
            )
            return
        session = make_session(key, team)

        chosen_ids = [sid.strip() for sid in self.selected_ids if sid.strip()]
        if not chosen_ids:
            if not messagebox.askyesno(
                "No expansions selected",
                "No expansions selected. Download ALL expansions?",
            ):
                return
            selected_sets = self.sets
        else:
            idset = {sid.lower() for sid in chosen_ids}
            selected_sets = [
                s
                for s in self.sets
                if isinstance(s, dict)
                and s.get("id", "").lower() in idset
            ]

        size_key = self.size_var.get()
        out_dir = Path(self.out_var.get()).expanduser().resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        try:
            max_workers = max(
                1, min(int(self.workers_var.get()), 64)
            )
        except Exception:
            max_workers = 8
        overwrite = bool(self.overwrite_var.get())

        # Reset progress
        self.progress_total = 0
        self.progress_done = 0
        self.set_progress(0.0)

        self.stop_btn.configure(state="normal")
        self.log(f"Output: {out_dir}")
        self.log(
            f"Size: {size_key} | Workers: {max_workers} | Overwrite: {overwrite}"
        )
        self.log(f"Downloading {len(selected_sets)} expansion(s).")

        self.worker = Downloader(
            self,
            session,
            selected_sets,
            size_key,
            out_dir,
            max_workers,
            overwrite,
        )
        self.worker.start()

    def stop_download(self):
        if self.worker:
            self.worker.stop()
        self.stop_btn.configure(state="disabled")

    def on_download_finished(self):
        self.stop_btn.configure(state="disabled")
        self.log("Done.")


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
