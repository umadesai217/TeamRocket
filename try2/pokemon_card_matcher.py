import os
import torch
import clip
import faiss
import numpy as np
from PIL import Image
from tqdm import tqdm

device = "cuda" if torch.cuda.is_available() else "cpu"

# Load CLIP model
model, preprocess = clip.load("ViT-B/32", device=device)

# Paths
card_image_dir = "pokemon_cards"  # Folder containing all your card images
query_image_path = "151zard2.jpg"    # Change this to the image you want to identify

# Step 1: Load and encode all card images
filenames = sorted([f for f in os.listdir(card_image_dir) if f.lower().endswith((".jpg", ".png"))])
embeddings = []

print(f"Encoding {len(filenames)} card images...")
for filename in tqdm(filenames):
    image_path = os.path.join(card_image_dir, filename)
    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
    with torch.no_grad():
        embedding = model.encode_image(image)
    embedding = embedding / embedding.norm(dim=-1, keepdim=True)
    embeddings.append(embedding.cpu().numpy().astype("float32"))

embedding_matrix = np.vstack(embeddings)
index = faiss.IndexFlatIP(embedding_matrix.shape[1])
index.add(embedding_matrix)

# Step 2: Encode the query image
query_image = preprocess(Image.open(query_image_path)).unsqueeze(0).to(device)
with torch.no_grad():
    query_embedding = model.encode_image(query_image)
query_embedding = query_embedding / query_embedding.norm(dim=-1, keepdim=True)
query_embedding_np = query_embedding.cpu().numpy().astype("float32")

# Step 3: Search the nearest neighbor
D, I = index.search(query_embedding_np, k=1)
match_idx = I[0][0]
match_filename = filenames[match_idx]

print(f"\n🟩 Closest match: {match_filename} (Similarity: {D[0][0]:.4f})")
