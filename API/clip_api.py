from fastapi import FastAPI, HTTPException, File, UploadFile
import torch
import clip
import faiss
import numpy as np
from PIL import Image
from ultralytics import YOLO
import io
import os
import easyocr



# commands to run server and ngrok:
# uvicorn fast_api_test:app --reload
# ngrok config add-authtoken YOUR_TOKEN_HERE
# token from here: https://dashboard.ngrok.com/get-started/your-authtoken
# ngrok http 8000



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FAISS_INDEX_PATH = os.path.join(BASE_DIR, "index_out/card_index.faiss")
FILENAMES_PATH = os.path.join(BASE_DIR, "index_out/card_filenames.txt")
CARD_IMAGE_DIR = os.path.join(BASE_DIR, "pokemon_cards")
K = 1  # Top K matches

# Initialize OCR reader
reader = easyocr.Reader(['en'])

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

def auto_orient_with_clip(image: Image.Image):
    best_score = -1
    best_angle = 0
    best_result = []
    best_rotated = image

    for angle in [0, 45, 180]:
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





app = FastAPI()

items = []

@app.get("/")
def root():
    return {"Hello": "World"}


@app.get("/test")
def root ():
    return("test")



@app.post("/items")
def create_item(item: str):
    items.append(item)
    return items

@app.get("/items/{item_id}")
def det_item(item_id:int) -> str:
    if item_id < len(items):
        return items[item_id]
    else:
        raise HTTPException(status_code=404, detail= f"Item {item_id} Not Found")
    

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    try:
        img_bytes = await file.read()
        pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        temp_path = os.path.join(BASE_DIR, "query.jpg")
        pil_img.save(temp_path)

        # detect and crop card region
        cropped_img = detect_and_crop(pil_img, temp_path)

        # auto-orient and search
        results, oriented_img = auto_orient_with_clip(cropped_img)

        # Build JSON response of top-K matches
        matches = []
        for name, score in results:
            # return only the basename (filename) rather than full path
            matches.append({"filename": os.path.basename(name), "score": float(score)})
            #get the fold the image is in 
            folder = os.path.basename(os.path.dirname(name))
        


        # save oriented crop for debugging (optional)
        cropped_path = os.path.join(BASE_DIR, "cropped.jpg")
        oriented_img.save(cropped_path)
        
        # change later to show more than one match "matches": matches,


        filename = os.path.basename(name).strip("_large.jpg")
        response = {
            "URL": f"https://xjtcqylndpugjcikdhtz.supabase.co/storage/v1/object/public/Images/{folder}/{filename}_large.jpg",
            "FileName": filename,
            
            #"matches": matches,
            #"cropped_image": os.path.basename(cropped_path),
        }

        #save repsonse as a json file
        import json 
        json_path = os.path.join(BASE_DIR, "response.json")
        with open(json_path, "w", encoding="utf-8") as jf:
            json.dump(response, jf, ensure_ascii=False, indent=4)

        

        return response
    except Exception as e:
        return {"error": str(e)}