import os
import io
from io import BytesIO

import torch
import clip
import faiss
import numpy as np

from PIL import Image, ImageOps, ImageEnhance, ImageFilter
from torchvision.transforms import functional as F

# --- Helpers ---
def jpeg_compress(img: Image.Image, quality: int = 40) -> Image.Image:
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    buf.seek(0)
    return Image.open(buf).convert("RGB")

def add_gaussian_noise(img: Image.Image, sigma: float = 8.0) -> Image.Image:
    arr = np.asarray(img).astype(np.float32)
    noise = np.random.normal(0, sigma, arr.shape).astype(np.float32)
    out = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(out)

def crop_pct(img: Image.Image, pct: float, anchor: str = "center") -> Image.Image:
    """Crop by percentage (e.g., 0.9 keeps 90%) from a given anchor, then resize back."""
    w, h = img.size
    new_w, new_h = int(w * pct), int(h * pct)

    if anchor == "center":
        left = (w - new_w) // 2
        top = (h - new_h) // 2
    elif anchor == "tl":
        left, top = 0, 0
    elif anchor == "tr":
        left, top = w - new_w, 0
    elif anchor == "bl":
        left, top = 0, h - new_h
    elif anchor == "br":
        left, top = w - new_w, h - new_h
    else:
        left = (w - new_w) // 2
        top = (h - new_h) // 2

    cropped = img.crop((left, top, left + new_w, top + new_h))
    return cropped.resize((w, h), Image.BICUBIC)

def mild_affine(img: Image.Image, angle: float = 0.0, shear: float = 0.0, scale: float = 1.0) -> Image.Image:
    # F.affine expects degrees, scale, translation, shear
    return F.affine(img, angle=angle, translate=(0, 0), scale=scale, shear=shear, interpolation=Image.BICUBIC)

def adjust_all(img: Image.Image, b=1.0, c=1.0, s=1.0) -> Image.Image:
    img = ImageEnhance.Brightness(img).enhance(b)
    img = ImageEnhance.Contrast(img).enhance(c)
    img = ImageEnhance.Color(img).enhance(s)
    return img

# --- Augmentations ---
def augment_image(img: Image.Image, MAX_VARIANTS: int = 24):
    """
    A curated, deterministic-ish variety of robustness augmentations.
    Adjust MAX_VARIANTS or comment sections to control size/cost.
    """
    variants = []

    # 0) Always include original
    variants.append(img)

    # 1) Small rotations (common hand tilt)
    for a in (-15, -8, 8, 15):
        variants.append(img.rotate(a, resample=Image.BICUBIC, expand=True))

    # 2) Upside-down + slight tilt (people hold phones weird!)
    for a in (180, 188, 172):
        variants.append(img.rotate(a, resample=Image.BICUBIC, expand=True))

    # 3) Mild affine “perspective-ish” warps (shear + small scale jitter)
    affine_params = [
        (0, -8, 0.95), (0, 8, 0.95),
        (0, -5, 1.05), (0, 5, 1.05),
        (-5, 0, 1.0), (5, 0, 1.0),
    ]
    for angle, shear, scale in affine_params:
        variants.append(mild_affine(img, angle=angle, shear=shear, scale=scale))

    # 4) Crops (center & edges), then resize back
    crop_specs = [
        (0.92, "center"),
        (0.90, "tl"), (0.90, "tr"),
        (0.90, "bl"), (0.90, "br"),
    ]
    for pct, anchor in crop_specs:
        variants.append(crop_pct(img, pct, anchor))

    # 5) Photometric: brightness/contrast/color
    photometric = [
        (0.85, 1.05, 1.00),
        (1.20, 0.95, 1.00),
        (1.00, 1.15, 1.10),
        (0.95, 1.10, 0.85),
    ]
    for (b, c, s) in photometric:
        variants.append(adjust_all(img, b=b, c=c, s=s))

    # 6) Blur & sharpen (camera focus variability)
    variants.append(img.filter(ImageFilter.GaussianBlur(radius=1.2)))
    variants.append(img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3)))

    # 7) Compression and noise (messaging apps, screenshots)
    variants.append(jpeg_compress(img, quality=35))
    variants.append(add_gaussian_noise(img, sigma=7.0))

    # 8) (Optional) slight vignette/edge darkening could be added if needed

    # Keep to MAX_VARIANTS to control index size
    if len(variants) > MAX_VARIANTS:
        # deterministic downselect: take evenly spaced
        idxs = np.linspace(0, len(variants) - 1, MAX_VARIANTS).astype(int).tolist()
        variants = [variants[i] for i in idxs]

    # Ensure all are RGB and same base orientation size for preprocess
    variants = [v.convert("RGB") for v in variants]
    return variants






import threading
import queue
import argparse
from pathlib import Path
import json
import time
from tqdm import tqdm

# --- GUI Indexer App ---
def find_sets(root_dir: str):
    """Return immediate subfolders under root_dir as sets."""
    rd = Path(root_dir)
    if not rd.exists() or not rd.is_dir():
        return []
    return sorted([p.name for p in rd.iterdir() if p.is_dir()])


def gather_image_files(root_dir: str, selected_sets):
    exts = (".jpg", ".jpeg", ".png", ".webp", ".bmp")
    for s in selected_sets:
        d = Path(root_dir) / s
        if not d.exists():
            continue
        for p in d.rglob("*"):
            if p.is_file() and p.suffix.lower() in exts:
                yield str(p)


class Indexer(threading.Thread):
    def __init__(self, app, image_paths, out_dir, device, max_variants):
        super().__init__(daemon=True)
        self.app = app
        self.image_paths = image_paths
        self.out_dir = Path(out_dir)
        self.device = device
        self.max_variants = max_variants
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def run(self):
        try:
            self._run_impl()
        except Exception as e:
            self.app.log(f"[error] {e}")
        finally:
            self.app.on_index_finished()

    def _run_impl(self):
        import torch
        import clip
        import faiss
        import numpy as np

        self.app.log(f"Loading CLIP model on device {self.device}...")
        model, preprocess = clip.load("ViT-B/32", device=self.device)
        model.eval()

        embeddings = []
        filenames = []

        total = len(self.image_paths)
        done = 0

        for img_path in self.image_paths:
            if self._stop.is_set():
                self.app.log("Indexing stopped by user.")
                break
            try:
                img = Image.open(img_path).convert("RGB")
            except Exception as e:
                self.app.log(f"[warn] Failed open: {img_path} -> {e}")
                done += 1
                self.app.set_progress(done / max(1, total))
                continue

            variants = augment_image(img, MAX_VARIANTS=self.max_variants)
            # process in one batch per image (variants small)
            try:
                tensors = torch.stack([preprocess(v) for v in variants]).to(self.device)
                with torch.no_grad():
                    batch_emb = model.encode_image(tensors)
                batch_emb = batch_emb / batch_emb.norm(dim=-1, keepdim=True)
                for e in batch_emb:
                    embeddings.append(e.cpu().numpy().astype("float32"))
                    filenames.append(img_path)
            except Exception as e:
                self.app.log(f"[warn] Encoding failed for {img_path}: {e}")

            done += 1
            if done % 5 == 0 or done == total:
                self.app.set_progress(done / max(1, total))

        if len(embeddings) == 0:
            self.app.log("No embeddings created; nothing to save.")
            return

        self.app.log("Building FAISS index...")
        emb_matrix = np.vstack(embeddings)
        index = faiss.IndexFlatIP(emb_matrix.shape[1])
        index.add(emb_matrix)

        self.out_dir.mkdir(parents=True, exist_ok=True)
        faiss_path = str(self.out_dir / "card_index.faiss")
        faiss.write_index(index, faiss_path)

        names_path = str(self.out_dir / "card_filenames.txt")
        with open(names_path, "w", encoding="utf-8") as f:
            for n in filenames:
                f.write(n.replace("\\", "/") + "\n")

        np.save(str(self.out_dir / "card_embeddings.npy"), emb_matrix)

        # manifest (counts per set)
        manifest = {}
        for p in filenames:
            # filename contains set folder after root; guess by taking part between root and filename
            manifest.setdefault(Path(p).parts[-2] if len(Path(p).parts) >= 2 else "unknown", 0)
            manifest[Path(p).parts[-2] if len(Path(p).parts) >= 2 else "unknown"] += 1
        with open(self.out_dir / "index_manifest.json", "w", encoding="utf-8") as f:
            json.dump({"total_embeddings": len(embeddings), "by_set": manifest}, f, indent=2)

        self.app.log(f"✅ Saved index to {faiss_path} ({len(embeddings)} embeddings)")


try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
except Exception:
    tk = None


class AppUI:
    def __init__(self):
        if tk is None:
            raise RuntimeError("Tkinter not available in this environment")
        self.root = tk.Tk()
        self.root.title("Pokémon Card Index Builder")
        self.root.geometry("1000x680")

        self.log_q = queue.Queue()
        self.indexer = None
        self.selected_sets = []

        self._build_ui()
        self._load_selected_cache()
        self._apply_filter()
        self.root.after(120, self._drain_log)

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill="both", expand=True)

        opt = ttk.LabelFrame(main, text="Options", padding=8)
        opt.pack(fill="x")

        ttk.Label(opt, text="Cards root (folder with set subfolders):").grid(row=0, column=0, sticky="w")
        # default to the `pokemon_cards` folder next to this script (try2/pokemon_cards)
        self.root_var = tk.StringVar(value=str(Path(__file__).parent / "pokemon_cards"))
        row0 = ttk.Frame(opt)
        row0.grid(row=0, column=1, sticky="we")
        ttk.Entry(row0, textvariable=self.root_var).pack(side="left", fill="x", expand=True)
        ttk.Button(row0, text="Browse", command=self._browse_root).pack(side="left", padx=6)

        ttk.Label(opt, text="Output folder:").grid(row=1, column=0, sticky="w")
        # default output to the `index_out` folder next to this script (try2/index_out)
        self.out_var = tk.StringVar(value=str(Path(__file__).parent / "index_out"))
        row1 = ttk.Frame(opt)
        row1.grid(row=1, column=1, sticky="we")
        ttk.Entry(row1, textvariable=self.out_var).pack(side="left", fill="x", expand=True)
        ttk.Button(row1, text="Browse", command=self._browse_out).pack(side="left", padx=6)

        ttk.Label(opt, text="Device:").grid(row=2, column=0, sticky="w")
        self.device_var = tk.StringVar(value=("cuda" if torch.cuda.is_available() else "cpu"))
        ttk.Entry(opt, textvariable=self.device_var, width=12).grid(row=2, column=1, sticky="w")

        ttk.Label(opt, text="Max variants per image:").grid(row=3, column=0, sticky="w")
        self.variants_var = tk.IntVar(value=12)
        ttk.Spinbox(opt, from_=1, to=48, textvariable=self.variants_var, width=6).grid(row=3, column=1, sticky="w")

        btns = ttk.Frame(main)
        btns.pack(fill="x", pady=(8,6))
        ttk.Button(btns, text="Refresh Sets", command=self.refresh_sets).pack(side="left")
        ttk.Button(btns, text="Start Indexing", command=self.start_indexing).pack(side="left", padx=8)
        self.stop_btn = ttk.Button(btns, text="Stop", command=self.stop_indexing, state="disabled")
        self.stop_btn.pack(side="left", padx=8)

        self.progress = ttk.Progressbar(main, mode="determinate")
        self.progress.pack(fill="x", pady=(4,8))

        lists = ttk.Frame(main)
        lists.pack(fill="both", expand=True)

        left = ttk.Frame(lists)
        left.pack(side="left", fill="both", expand=True)
        top_left = ttk.Frame(left)
        top_left.pack(fill="x")
        ttk.Label(top_left, text="Available Sets").pack(side="left")
        ttk.Label(top_left, text="Filter:").pack(side="left", padx=(12,2))
        self.filter_var = tk.StringVar()
        ent = ttk.Entry(top_left, textvariable=self.filter_var, width=24)
        ent.pack(side="left")
        ent.bind("<KeyRelease>", lambda e: self._apply_filter())

        self.available_list = tk.Listbox(left, selectmode=tk.EXTENDED)
        self.available_list.pack(fill="both", expand=True, pady=(4,0))
        self.available_list.bind("<Double-Button-1>", lambda e: self.add_selected())

        mid = ttk.Frame(lists, padding=10)
        mid.pack(side="left", fill="y")
        ttk.Button(mid, text="Add »", command=self.add_selected, width=10).pack(pady=(30,6))
        ttk.Button(mid, text="« Remove", command=self.remove_selected, width=10).pack()

        right = ttk.Frame(lists)
        right.pack(side="left", fill="both", expand=True)
        ttk.Label(right, text="Selected Sets (to index)").pack()
        self.selected_list = tk.Listbox(right, selectmode=tk.EXTENDED)
        self.selected_list.pack(fill="both", expand=True, pady=(4,0))

        log_frame = ttk.LabelFrame(main, text="Log", padding=6)
        log_frame.pack(fill="both", expand=False, pady=(8,0))
        self.log_text = tk.Text(log_frame, height=10, wrap="word", state="disabled")
        self.log_text.pack(fill="both", expand=True)

    def _browse_root(self):
        d = filedialog.askdirectory(title="Select cards root folder")
        if d:
            self.root_var.set(d)

    def _browse_out(self):
        d = filedialog.askdirectory(title="Select output folder")
        if d:
            self.out_var.set(d)

    def log(self, msg: str):
        self.log_q.put(msg)

    def _drain_log(self):
        try:
            while True:
                msg = self.log_q.get_nowait()
                self.log_text.configure(state="normal")
                self.log_text.insert(tk.END, msg + "\n")
                self.log_text.see(tk.END)
                self.log_text.configure(state="disabled")
        except queue.Empty:
            pass
        self.root.after(120, self._drain_log)

    def set_progress(self, frac: float):
        frac = max(0.0, min(1.0, frac))
        self.progress["value"] = int(frac * 100)

    def _apply_filter(self):
        q = self.filter_var.get().strip().lower()
        self.available_list.delete(0, tk.END)
        sets = find_sets(self.root_var.get())
        self._available_sets = sets
        for s in sets:
            if not q or q in s.lower():
                self.available_list.insert(tk.END, s)

    def refresh_sets(self):
        self._apply_filter()
        self.log("Sets refreshed.")

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
            s = self.available_list.get(i)
            if s not in self.selected_sets:
                self.selected_sets.append(s)
                self.selected_list.insert(tk.END, s)
                changed = True
        if changed:
            self._save_selected_cache()

    def remove_selected(self):
        indices = sorted(list(self.selected_list.curselection()), reverse=True)
        removed = False
        for i in indices:
            s = self.selected_list.get(i)
            self.selected_list.delete(i)
            try:
                self.selected_sets.remove(s)
            except ValueError:
                pass
            removed = True
        if removed:
            self._save_selected_cache()

    def _selected_cache_file(self):
        return Path(__file__).parent / "selected_sets_cache.json"

    def _save_selected_cache(self):
        try:
            with open(self._selected_cache_file(), "w", encoding="utf-8") as f:
                json.dump(self.selected_sets, f, indent=2)
        except Exception as e:
            self.log(f"[warn] failed saving selected cache: {e}")

    def _load_selected_cache(self):
        p = self._selected_cache_file()
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    self.selected_sets = json.load(f)
                self.selected_list.delete(0, tk.END)
                for s in self.selected_sets:
                    self.selected_list.insert(tk.END, s)
            except Exception as e:
                self.log(f"[warn] failed load selected cache: {e}")

    def start_indexing(self):
        if self.indexer and self.indexer.is_alive():
            messagebox.showinfo("Busy", "Indexing already in progress.")
            return
        if not self.selected_sets:
            messagebox.showerror("No sets", "No sets selected to index.")
            return
        root = self.root_var.get()
        image_paths = list(gather_image_files(root, self.selected_sets))
        if not image_paths:
            messagebox.showerror("No images", "No images found in selected sets.")
            return
        out = self.out_var.get()
        device = self.device_var.get()
        variants = int(self.variants_var.get())

        self.set_progress(0.0)
        self.stop_btn.configure(state="normal")
        self.log(f"Indexing {len(image_paths)} images -> {out}")

        self.indexer = Indexer(self, image_paths, out, device, variants)
        self.indexer.start()

    def stop_indexing(self):
        if self.indexer:
            self.indexer.stop()
        self.stop_btn.configure(state="disabled")

    def on_index_finished(self):
        self.stop_btn.configure(state="disabled")
        self.log("Indexing finished.")

    def run(self):
        self.root.mainloop()


def main_gui():
    ui = AppUI()
    ui.run()


if __name__ == "__main__":
    # Provide simple CLI to launch GUI or run non-interactive in future
    parser = argparse.ArgumentParser(description="Build FAISS index from card set folders (visual)")
    parser.add_argument("--nogui", action="store_true", help="Do not launch GUI (reserved)")
    args = parser.parse_args()
    if args.nogui:
        print("Non-GUI mode not implemented. Use the GUI to select sets.")
    else:
        main_gui()
