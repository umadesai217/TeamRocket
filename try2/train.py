from ultralytics import YOLO
import os

# === CONFIGURATION ===
DATA_YAML = "pokemon_cards_yolo8 v2/data.yaml"
MODEL_TYPE = "yolov8n.pt"  # or yolov8s.pt/yolov8m.pt depending on your needs
EPOCHS = 50
IMG_SIZE = 640
PROJECT_NAME = "pokemon_hp_detection"
RUN_NAME = "v2"  # change this for each experiment

# === TRAINING ===
print("🚀 Starting training...")
model = YOLO(MODEL_TYPE)
model.train(
    data=DATA_YAML,
    epochs=EPOCHS,
    imgsz=IMG_SIZE,
    project=PROJECT_NAME,
    name=RUN_NAME,
    workers=2,
    patience=10  # stop early if no improvement
)
print("✅ Training completed.")

# === LOAD TRAINED MODEL ===
trained_model_path = "pokemon_hp_detection/v22/weights/best.pt"
model = YOLO(trained_model_path)

# === TEST ON SINGLE IMAGE ===
test_image = "151zard2.jpg"  # replace with your test image
results = model(test_image, save=True, imgsz=IMG_SIZE, conf=0.25)
print("✅ Test image processed.")

# # === TEST ON A FOLDER OF IMAGES ===
# # Optional: run on a batch of images and save results
# test_folder = "test_images"  # make a folder with your test images
# if os.path.exists(test_folder):
#     model.predict(source=test_folder, save=True, imgsz=IMG_SIZE, conf=0.25)
#     print(f"✅ Predictions saved to 'runs/detect/predict'")

# === EVALUATION ===
# Run validation metrics on the validation set
metrics = model.val()
print("📊 Validation results:")
print(metrics)
