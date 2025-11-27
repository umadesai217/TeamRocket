import os
import json
from tqdm import tqdm
from pokemontcgsdk import RestClient, Card
from dotenv import load_dotenv

# === Load API key ===
load_dotenv()
API_KEY = os.getenv("POKEMON_API_KEY")
if not API_KEY:
    raise Exception("❌ POKEMON_API_KEY is not set in your .env file!")

RestClient.configure(API_KEY)

# === Config ===
IMAGE_DIR = "pokemon_cards"
OUTPUT_FILE = "card_metadata.json"
PAGE_SIZE = 250  # max allowed
MAX_PAGES = 200  # should be enough for ~50k cards

# === Get all card IDs from your image filenames ===
local_ids = {
    os.path.splitext(f)[0]: f
    for f in os.listdir(IMAGE_DIR)
    if f.lower().endswith((".jpg", ".png"))
}

metadata = {}

print("🔄 Fetching metadata in bulk...")
for page in tqdm(range(1, MAX_PAGES + 1), desc="Pages"):
    cards = Card.where(q="", page=page, pageSize=PAGE_SIZE)
    if not cards:
        break

    for card in cards:
        card_id = card.id
        if card_id in local_ids:
            filename = local_ids[card_id]
            hp = card.hp.strip() if card.hp else ""
            metadata[filename] = hp

# Fill in any missing cards
for filename in local_ids.values():
    if filename not in metadata:
        metadata[filename] = ""

# === Save to JSON ===
with open(OUTPUT_FILE, "w") as f:
    json.dump(metadata, f, indent=2)

print(f"✅ Saved metadata for {len(metadata)} cards to {OUTPUT_FILE}")
