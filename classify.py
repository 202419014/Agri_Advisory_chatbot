import os
import shutil
from pathlib import Path
from PIL import Image
import torch
from transformers import pipeline
 
IMAGE_FOLDER  = "Images"
OUTPUT_FOLDER = "classified"
 
PEST_CLASSES = [
    "fall armyworm",
    "stalk borer",
    "aphids",
    "corn earworm",
    "cutworm",
    "leafhopper",
    "thrips",
    "corn rootworm",
]
 
print("Loading model... (this may take 1-2 minutes the first time)\n")
 
classifier = pipeline(
    "zero-shot-image-classification",
    model="openai/clip-vit-base-patch32"
)
 
print("Model loaded! Starting classification...\n")
 
for cls in PEST_CLASSES + ["unknown"]:
    os.makedirs(os.path.join(OUTPUT_FOLDER, cls.replace(" ", "_")), exist_ok=True)
 
image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
images = [f for f in Path(IMAGE_FOLDER).iterdir() if f.suffix.lower() in image_extensions]
print(f"Found {len(images)} images.\n")
 
candidate_labels = [f"a photo of {pest}" for pest in PEST_CLASSES]
 
for i, img_path in enumerate(images):
    try:
        image = Image.open(img_path).convert("RGB")
        results = classifier(image, candidate_labels=candidate_labels)
 
        top = results[0]
        score = top["score"]
        label_text = top["label"].replace("a photo of ", "")
 
        if score < 0.15:
            label = "unknown"
        else:
            label = label_text
 
        dest = os.path.join(OUTPUT_FOLDER, label.replace(" ", "_"), img_path.name)
        shutil.copy(str(img_path), dest)
        print(f"[{i+1}/{len(images)}] {img_path.name}  →  {label}  (confidence: {score:.0%})")
 
    except Exception as e:
        print(f"  ERROR on {img_path.name}: {e}")
 
print("\nDone! Check the 'classified' folder.")