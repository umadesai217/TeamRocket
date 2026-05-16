import os
import time
import requests
from tqdm import tqdm
from pokemontcgsdk import RestClient, Card
from dotenv import load_dotenv

# === Load API key from .env ===
load_dotenv()
API_KEY = os.getenv("POKEMON_API_KEY")
if not API_KEY:
    raise Exception("❌ POKEMON_API_KEY is not set in your .env file!")

# === SDK Configuration ===
RestClient.configure(API_KEY)

# === Config ===
IMAGE_DIR = "pokemon_cards"
PAGE_SIZE = 250
RETRY_LIMIT = 6
WAIT_BETWEEN_PAGES = 1
WAIT_BETWEEN_RETRIES = 3
START_PAGE = 75  # You can resume from a specific page
MAX_PAGES = 1000  # Safety cap to prevent infinite loops

os.makedirs(IMAGE_DIR, exist_ok=True)

# === Image downloader with retry ===
def download_image(url, out_path):
    for attempt in range(RETRY_LIMIT):
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            with open(out_path, 'wb') as f:
                f.write(r.content)
            return True
        except Exception as e:
            print(f"⚠️ Image download failed ({attempt+1}/{RETRY_LIMIT}): {url} — {e}")
            time.sleep(WAIT_BETWEEN_RETRIES * (attempt + 1))
    return False

# === Safe page request with retry ===
def safe_card_page(page):
    for attempt in range(RETRY_LIMIT):
        try:
            return Card.where(q="", page=page, pageSize=PAGE_SIZE)
        except Exception as e:
            try:
                # Handle weird SDK binary error messages
                error_message = e.read().decode("utf-8") if hasattr(e, "read") else str(e)
            except Exception:
                error_message = "Unknown error"
            print(f"⚠️ Page {page} fetch error ({attempt+1}/{RETRY_LIMIT}): {error_message}")
            time.sleep(WAIT_BETWEEN_RETRIES * (attempt + 1))
    print(f"❌ Skipping page {page} after {RETRY_LIMIT} failed attempts.")
    return []

# === Main download logic ===
def download_all_cards():
    total_downloaded = 0
    page = START_PAGE

    print("🔁 Starting download using pokemontcgsdk...\n")

    while page <= MAX_PAGES:
        cards = safe_card_page(page)

        if not cards:
            print(f"📭 No cards returned on page {page} — assuming end.")
            break

        for card in tqdm(cards, desc=f"Page {page}", unit="card"):
            card_id = card.id
            image_url = card.images.large
            ext = image_url.split('.')[-1].split('?')[0]
            out_path = os.path.join(IMAGE_DIR, f"{card_id}.{ext}")

            if not os.path.exists(out_path):
                if download_image(image_url, out_path):
                    total_downloaded += 1

        page += 1
        time.sleep(WAIT_BETWEEN_PAGES)

    print(f"\n✅ Done! Total new images downloaded: {total_downloaded}")

# === Run it ===
if __name__ == "__main__":
    download_all_cards()
