import os
import time
import requests
from pokemontcgsdk import RestClient, Card

API_KEY = "3d957c86-3533-4f75-b263-ba37a6fd8af1"
SET_ID = "sv10"
SAVE_FOLDER = "images"
PAGESIZE = 50

RestClient.configure(API_KEY)
os.makedirs(SAVE_FOLDER, exist_ok=True)

def download_set_images(set_id):
    page = 1
    while True:
        try:
            cards = Card.where(q=f'set.id:{set_id}', page=page, pageSize=PAGESIZE)
        except Exception as e:
            print(f"Error fetching page {page}: {e}. Retrying in 5 seconds...")
            time.sleep(5)
            continue  # retry current page

        if not cards:
            print("No more cards to fetch.")
            break

        for card in cards:
            img_url = card.images.large
            img_path = os.path.join(SAVE_FOLDER, f"{card.id}.jpg")

            if os.path.exists(img_path):
                print(f"Skipping {card.name} (already downloaded)")
                continue

            try:
                print(f"Downloading {card.name}...")
                img_data = requests.get(img_url, timeout=10).content
                with open(img_path, "wb") as f:
                    f.write(img_data)
            except Exception as e:
                print(f"Failed to download {card.name}: {e}. Skipping...")

            time.sleep(0.3)  # short delay to avoid rate limits

        page += 1

if __name__ == "__main__":
    print(f"Starting download of set '{SET_ID}'...")
    download_set_images(SET_ID)
    print("Done!")
