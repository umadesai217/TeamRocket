import torch
import clip
import faiss
import numpy as np
from PIL import Image
from ultralytics import YOLO

# === CONFIG ===
query_image_path = "151zard4.jpg"
yolo_model_path = "runs/detect/train/weights/best.pt"  # Update if your path differs
faiss_index_path = "card_index.faiss"
filename_list_path = "card_filenames.txt"

# === Setup CLIP ===
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

# === Load FAISS index and filenames ===
index = faiss.read_index(faiss_index_path)
with open(filename_list_path, "r") as f:
    filenames = [line.strip() for line in f.readlines()]

# === Step 1: Use YOLOv8 to detect and crop the card ===
query_image = Image.open(query_image_path)
yolo_model = YOLO(yolo_model_path)
results = yolo_model(query_image_path)

boxes = results[0].boxes.xyxy.cpu().numpy()
if len(boxes) == 0:
    print("⚠️ No card detected. Using full image.")
    cropped_image = query_image
else:
    x1, y1, x2, y2 = map(int, boxes[0])  # Use the first detected box
    cropped_image = query_image.crop((x1, y1, x2, y2))
    print("✅ Cropped detected card.")

# === Optional: show cropped image ===
cropped_image.show()

# === Step 2: Generate embedding from cropped image ===
image = preprocess(cropped_image).unsqueeze(0).to(device)
with torch.no_grad():
    embedding = model.encode_image(image)
embedding = embedding / embedding.norm(dim=-1, keepdim=True)
query_vector = embedding.cpu().numpy().astype("float32")

# === Step 3: Search for top match ===
k = 3  # top 1 match
D, I = index.search(query_vector, k)
print("\n🔍 Top Match(es):")
for rank, (idx, score) in enumerate(zip(I[0], D[0]), 1):
    print(f"{rank}. {filenames[idx]} (Similarity: {score:.4f})")
