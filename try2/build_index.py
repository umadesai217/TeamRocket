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






# import os
# import torch
# import clip
# import faiss
# import numpy as np
# from PIL import Image, ImageEnhance, ImageFilter
# from tqdm import tqdm

# # === Setup ===
# device = "cuda" if torch.cuda.is_available() else "cpu"
# model, preprocess = clip.load("ViT-B/32", device=device)



# card_image_dir = "pokemon_cards"
# filenames = sorted([f for f in os.listdir(card_image_dir) if f.lower().endswith((".jpg", ".png"))])
# embeddings = []
# filename_mapping = []



# # === Augmentations ===
# def augment_image(img: Image.Image):
#     # Base orientation
#     base = [
#         img,
#         img.filter(ImageFilter.GaussianBlur(radius=2)),
#         ImageEnhance.Brightness(img).enhance(1.5),
#         ImageEnhance.Brightness(img).enhance(0.5),
#         img.rotate(45, expand=True),
#         img.rotate(-45, expand=True)
#     ]

#     # # Upside-down orientation (180 degrees)
#     # flipped = img.rotate(180)
#     # flipped_aug = [
#     #     flipped,
#     #     flipped.filter(ImageFilter.GaussianBlur(radius=2)),
#     #     ImageEnhance.Brightness(flipped).enhance(1.5),
#     #     ImageEnhance.Brightness(flipped).enhance(0.5),
#     #     flipped.rotate(8, expand=True),
#     #     flipped.rotate(-8, expand=True)
#     # ]

#     return base # + flipped_aug  # total: 12 variants per image

# print(f"Encoding {len(filenames)} card images with upright + upside-down augmentations...")

# for filename in tqdm(filenames):
#     image_path = os.path.join(card_image_dir, filename)
#     image = Image.open(image_path).convert("RGB")
#     variants = augment_image(image)

#     image_tensors = torch.stack([preprocess(v) for v in variants]).to(device)

#     with torch.no_grad():
#         batch_embeddings = model.encode_image(image_tensors)
#     batch_embeddings = batch_embeddings / batch_embeddings.norm(dim=-1, keepdim=True)

#     for emb in batch_embeddings:
#         embeddings.append(emb.cpu().numpy().astype("float32"))
#         filename_mapping.append(filename)

# # === Build and save FAISS index ===
# embedding_matrix = np.vstack(embeddings)
# index = faiss.IndexFlatIP(embedding_matrix.shape[1])
# index.add(embedding_matrix)

# faiss.write_index(index, "card_index.faiss")

# with open("card_filenames.txt", "w") as f:
#     for name in filename_mapping:
#         f.write(name + "\n")

# np.save("card_embeddings.npy", embedding_matrix)

# print(f"✅ Saved index with {len(embeddings)} embeddings from {len(filenames)} images.")
