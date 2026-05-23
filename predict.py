"""
PlantDoc Plant Disease Detector - Prediction Script
====================================================
Ek image deke disease predict karo.

Usage:
    python predict.py --image path/to/leaf.jpg

Ya directly import karke use karo:
    from predict import predict_image
    result = predict_image("leaf.jpg")
"""

import os
import sys
import json
import argparse
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image

# ─────────────────────────────────────────────
OUTPUT_DIR = "./output"
IMG_SIZE   = 128
# ─────────────────────────────────────────────

DISEASE_KEYWORDS = [
    "scab", "blight", "rust", "spot", "mold", "mildew",
    "rot", "virus", "curl", "mosaic", "canker", "yellows",
    "powdery", "downy", "leaf miner", "septoria", "bacterial"
]

def is_healthy_class(class_name: str) -> bool:
    name_lower = class_name.lower()
    for kw in DISEASE_KEYWORDS:
        if kw in name_lower:
            return False
    return True


def load_model(output_dir: str = OUTPUT_DIR):
    """Saved model aur class names load karo."""
    class_file = os.path.join(output_dir, "class_names.json")
    model_file = os.path.join(output_dir, "best_model.pth")

    if not os.path.exists(class_file):
        raise FileNotFoundError(f"class_names.json nahi mila: {class_file}\nPehle train_plantdoc.py chalao!")
    if not os.path.exists(model_file):
        raise FileNotFoundError(f"best_model.pth nahi mila: {model_file}\nPehle train_plantdoc.py chalao!")

    with open(class_file) as f:
        class_names = json.load(f)

    num_classes = len(class_names)
    model = models.mobilenet_v2(weights=None)
    model.classifier[1] = nn.Linear(model.last_channel, num_classes)
    model.load_state_dict(torch.load(model_file, map_location="cpu"))
    model.eval()

    return model, class_names


def predict_image(image_path: str, top_k: int = 3):
    """
    Ek image ka disease predict karo.

    Returns:
        dict with keys:
            - image_path
            - top_predictions  : list of {class, confidence, status}
            - binary_status    : "Healthy" ya "Diseased"
            - disease_name     : predicted disease (ya "None - Healthy")
            - plant_name       : guessed plant name
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image nahi mili: {image_path}")

    model, class_names = load_model()

    transform = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225]),
    ])

    img = Image.open(image_path).convert("RGB")
    tensor = transform(img).unsqueeze(0)  # batch dimension add karo

    with torch.no_grad():
        outputs = model(tensor)
        probs   = torch.softmax(outputs, dim=1)[0]

    top_probs, top_idxs = torch.topk(probs, k=min(top_k, len(class_names)))

    top_predictions = []
    for prob, idx in zip(top_probs.tolist(), top_idxs.tolist()):
        cls = class_names[idx]
        top_predictions.append({
            "class":      cls,
            "confidence": round(prob * 100, 2),
            "status":     "Healthy" if is_healthy_class(cls) else "Diseased"
        })

    best = top_predictions[0]
    plant_name = best["class"].replace("leaf", "").replace("Leaf", "").strip()

    # Disease name extract karo
    if best["status"] == "Diseased":
        disease_name = best["class"]
    else:
        disease_name = "None - Plant Healthy Hai ✅"

    return {
        "image_path":     image_path,
        "top_predictions": top_predictions,
        "binary_status":  best["status"],
        "disease_name":   disease_name,
        "plant_name":     plant_name,
        "confidence":     best["confidence"],
    }


def print_result(result: dict):
    """Result ko achhe se print karo."""
    print("\n" + "="*55)
    print("  🌿 PLANT DISEASE DETECTION RESULT")
    print("="*55)
    print(f"  📷 Image     : {result['image_path']}")
    print(f"  🌱 Plant     : {result['plant_name']}")
    print(f"  🔬 Status    : {result['binary_status']}")
    print(f"  🦠 Disease   : {result['disease_name']}")
    print(f"  📊 Confidence: {result['confidence']}%")
    print("\n  Top Predictions:")
    for i, pred in enumerate(result["top_predictions"], 1):
        emoji = "✅" if pred["status"] == "Healthy" else "⚠️"
        print(f"    {i}. {emoji} {pred['class']:40s} {pred['confidence']:6.2f}%")
    print("="*55 + "\n")


# ── CLI ──────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plant Disease Predictor")
    parser.add_argument("--image", type=str, required=True,
                        help="Leaf image ka path (jpg/png)")
    parser.add_argument("--top_k", type=int, default=3,
                        help="Kitne top predictions dikhane hain")
    args = parser.parse_args()

    try:
        result = predict_image(args.image, top_k=args.top_k)
        print_result(result)
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
