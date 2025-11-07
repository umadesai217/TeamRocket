import discord
import torch
import clip
import faiss
import numpy as np
from PIL import Image
from ultralytics import YOLO
import io
import os
import easyocr
import re
from dotenv import load_dotenv
from discord.ui import View, Button

# === OCR ===
reader = easyocr.Reader(['en'])  # Better OCR than Tesseract

class FeedbackView(View):
    def __init__(self, card_name):
        super().__init__(timeout=None)
        self.card_name = card_name

    @discord.ui.button(label="✅ Correct", style=discord.ButtonStyle.success)
    async def correct(self, interaction: discord.Interaction, button: Button):
        print(f"[FEEDBACK] ✅ Correct match for: {self.card_name}")
        await interaction.response.send_message("✅ Thanks for confirming!", ephemeral=True)
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)

    @discord.ui.button(label="❌ Wrong", style=discord.ButtonStyle.danger)
    async def wrong(self, interaction: discord.Interaction, button: Button):
        print(f"[FEEDBACK] ❌ Incorrect match for: {self.card_name}")
        await interaction.response.send_message("❌ Noted — thanks!", ephemeral=True)
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)

# === Load environment variables ===
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# === Discord setup ===
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# === Config ===
# Prefer trained weights if available, otherwise fall back to a small public model.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FAISS_INDEX_PATH = os.path.join(BASE_DIR, "card_index.faiss")
FILENAMES_PATH = os.path.join(BASE_DIR, "card_filenames.txt")
CARD_IMAGE_DIR = os.path.join(BASE_DIR, "pokemon_cards")
K = 3  # Top K matches

# Resolve YOLO weights with sensible fallbacks.
_yolo_candidates = [
    os.path.join(BASE_DIR, "runs", "detect", "train", "weights", "best.pt"),
    os.path.join(BASE_DIR, "yolov8n.pt"),  # local lightweight model if present
]

def _resolve_yolo_weights():
    for p in _yolo_candidates:
        if os.path.isfile(p):
            print(f"Using YOLO weights: {p}")
            return p
    # As a final fallback, let Ultralytics auto-download by name if needed.
    print("YOLO trained weights not found; falling back to 'yolov8n.pt' (will auto-download if missing).")
    return "yolov8n.pt"

# === Load models ===
device = "cuda" if torch.cuda.is_available() else "cpu"
clip_model, preprocess = clip.load("ViT-B/32", device=device)
yolo_model = YOLO(_resolve_yolo_weights())

# === Load FAISS index and filenames ===
def _require_path(path: str, desc: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing {desc}: {path}")

_require_path(FAISS_INDEX_PATH, "FAISS index file")
_require_path(FILENAMES_PATH, "card filenames list")
_require_path(CARD_IMAGE_DIR, "card images directory")

index = faiss.read_index(FAISS_INDEX_PATH)
with open(FILENAMES_PATH, "r", encoding="utf-8") as f:
    filenames = [line.strip() for line in f.readlines()]

# === Functions ===
def detect_and_crop(pil_image, image_path):
    results = yolo_model(image_path)
    boxes = results[0].boxes.xyxy.cpu().numpy()
    if len(boxes) == 0:
        print("⚠️ No card detected. Using full image.")
        return pil_image
    x1, y1, x2, y2 = map(int, boxes[0])
    cropped = pil_image.crop((x1, y1, x2, y2))
    print("✅ Cropped detected card.")
    return cropped

def extract_hp(image: Image.Image) -> str:
    width, height = image.size
    hp_region = image.crop((width - 230, 15, width - 20, 100))
    hp_region = hp_region.resize((hp_region.width * 2, hp_region.height * 2))
    results = reader.readtext(np.array(hp_region))
    for _, text, _ in results:
        digits = re.search(r'\d{2,4}', text)
        if digits:
            return digits.group()
    return ""

def validate_hp_local(query_img: Image.Image, matched_img_path: str):
    matched_img = Image.open(matched_img_path).convert("RGB")
    query_hp = extract_hp(query_img)
    matched_hp = extract_hp(matched_img)
    is_match = query_hp == matched_hp
    return is_match, query_hp, matched_hp

def auto_orient_with_clip(image: Image.Image):
    best_score = -1
    best_angle = 0
    best_result = []
    best_rotated = image

    for angle in [0, 90, 180, 270]:
        rotated = image.rotate(angle, expand=True)
        image_tensor = preprocess(rotated).unsqueeze(0).to(device)
        with torch.no_grad():
            embedding = clip_model.encode_image(image_tensor)
        embedding = embedding / embedding.norm(dim=-1, keepdim=True)
        query_vector = embedding.cpu().numpy().astype("float32")
        D, I = index.search(query_vector, K)
        score = D[0][0]
        if score > best_score:
            best_score = score
            best_angle = angle
            best_result = [(filenames[idx], float(sim)) for idx, sim in zip(I[0], D[0])]
            best_rotated = rotated

    print(f"🔄 Auto-oriented to {best_angle}°")
    return best_result, best_rotated

# === Discord events ===
@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user.name}")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.lower() == "!ping":
        await message.channel.send("Pong!")
        return

    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.lower().endswith((".jpg", ".jpeg", ".png")):
                await message.channel.send("🧠 Processing image...")

                try:
                    img_bytes = await attachment.read()
                    pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                    temp_path = os.path.join(BASE_DIR, "query.jpg")
                    pil_img.save(temp_path)

                    cropped_img = detect_and_crop(pil_img, temp_path)
                    results, oriented_img = auto_orient_with_clip(cropped_img)

                    top_match_filename = results[0][0]
                    top_match_path = os.path.join(CARD_IMAGE_DIR, top_match_filename)

                    hp_match, query_hp, matched_hp = validate_hp_local(oriented_img, top_match_path)

                    response = "🔍 **Top Matches:**\n"
                    for i, (name, score) in enumerate(results, 1):
                        response += f"{i}. `{name}` (Similarity: {score:.4f})\n"

                    # if hp_match:
                    #     response += f"\n✅ HP match: `{query_hp}`"
                    # else:
                    #     response += f"\n⚠️ HP mismatch: input `{query_hp}` vs matched `{matched_hp}`"

                    cropped_path = os.path.join(BASE_DIR, "cropped.jpg")
                    oriented_img.save(cropped_path)

                    files = []
                    if os.path.exists(cropped_path):
                        files.append(discord.File(cropped_path, filename="cropped.jpg"))
                    if os.path.exists(top_match_path):
                        files.append(discord.File(top_match_path, filename="match.jpg"))

                    view = FeedbackView(top_match_filename)
                    await message.channel.send(response, files=files, view=view)

                except Exception as e:
                    await message.channel.send(f"❌ Error: {str(e)}")
                    raise

# === Run Bot ===
if not DISCORD_TOKEN:
    raise Exception("Please set DISCORD_TOKEN in a .env file or environment variable.")
client.run(DISCORD_TOKEN)
