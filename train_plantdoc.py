"""
PlantDoc Plant Disease Detection - Training Script
===================================================
Dataset Structure Expected:
    dataset/
        train/
            Apple Scab Leaf/
            Apple leaf/          <- "leaf" in name = healthy
            Tomato Early blight leaf/
            ...
        val/
            ...
        test/
            ...

Run: python train_plantdoc.py
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns

# ─────────────────────────────────────────────
# CONFIG — apne dataset ka path yahan dalo
# ─────────────────────────────────────────────
DATASET_DIR = "./dataset"        # <-- CHANGE THIS to your PlantDoc folder path
OUTPUT_DIR  = "./output"
IMG_SIZE    = 128                # CPU ke liye chhota rakkha (PlantVillage mein 256 tha)
BATCH_SIZE  = 16                 # CPU ke liye 16 best hai
EPOCHS      = 15
LR          = 0.001
NUM_WORKERS = 0                  # Windows pe 0 rakhna zaroori hai
# ─────────────────────────────────────────────

os.makedirs(OUTPUT_DIR, exist_ok=True)
device = torch.device("cpu")
print(f"✅ Device: {device}")


# ── 1. DATA TRANSFORMS ──────────────────────
train_transforms = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225]),
])

val_transforms = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225]),
])


# ── 2. DATASETS & DATALOADERS ────────────────
from torch.utils.data import random_split, Subset

print("\n📂 Dataset load ho raha hai...")

# Full train dataset load karo (val folder nahi hai PlantDoc mein)
full_train_data = datasets.ImageFolder(os.path.join(DATASET_DIR, "train"), transform=train_transforms)

# 80% train, 20% val mein split karo automatically
total      = len(full_train_data)
val_size   = int(0.2 * total)
train_size = total - val_size
train_data, val_data = random_split(full_train_data, [train_size, val_size],
                                    generator=torch.Generator().manual_seed(42))

# Val ke liye alag transforms lagao (augmentation nahi chahiye)
class TransformSubset(torch.utils.data.Dataset):
    def __init__(self, subset, transform):
        self.subset    = subset
        self.transform = transform
    def __len__(self):
        return len(self.subset)
    def __getitem__(self, idx):
        img, label = self.subset[idx]
        # img already tensor hai (train_transforms se) — reload PIL se
        return img, label

# Val data ko val_transforms ke saath reload karo
val_dataset_raw = datasets.ImageFolder(os.path.join(DATASET_DIR, "train"), transform=val_transforms)
val_data = Subset(val_dataset_raw, val_data.indices)

# Test folder optional hai
test_path = os.path.join(DATASET_DIR, "test")
test_data = datasets.ImageFolder(test_path, transform=val_transforms) if os.path.exists(test_path) else None

train_loader = DataLoader(train_data, batch_size=BATCH_SIZE, shuffle=True,  num_workers=NUM_WORKERS)
val_loader   = DataLoader(val_data,   batch_size=BATCH_SIZE, shuffle=False, num_workers=NUM_WORKERS)
test_loader  = DataLoader(test_data,  batch_size=BATCH_SIZE, shuffle=False, num_workers=NUM_WORKERS) if test_data else None

num_classes = len(full_train_data.classes)
class_names = full_train_data.classes

print(f"✅ Classes mili: {num_classes}")
print(f"   Total images: {total}")
print(f"   Train images: {train_size} (80%)")
print(f"   Val images  : {val_size} (20% — auto split)")
if test_data:
    print(f"   Test images : {len(test_data)}")

# Class names save karo (prediction ke liye baad mein kaam aayegi)
with open(os.path.join(OUTPUT_DIR, "class_names.json"), "w") as f:
    json.dump(class_names, f, indent=2)


# ── 3. HEALTHY / DISEASED LABEL HELPER ───────
def is_healthy(class_name: str) -> str:
    """
    PlantDoc mein healthy classes ke naam mein sirf plant ka naam hota hai
    (jaise 'Apple leaf'), jabki diseased mein disease bhi hota hai
    (jaise 'Apple Scab Leaf').
    """
    name_lower = class_name.lower()
    healthy_keywords = ["healthy", " leaf"]
    disease_keywords = ["scab", "blight", "rust", "spot", "mold", "mildew",
                        "rot", "virus", "curl", "mosaic", "canker", "yellows"]
    for kw in disease_keywords:
        if kw in name_lower:
            return "Diseased"
    return "Healthy"

# Binary labels bhi print karo
print("\n📋 Class → Healthy/Diseased Mapping:")
for cls in class_names:
    print(f"   {cls:45s} → {is_healthy(cls)}")


# ── 4. MODEL — MobileNetV2 (CPU-friendly) ────
print("\n🧠 MobileNetV2 model load ho raha hai (pretrained)...")
model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)

# Last layer ko apne dataset ke classes ke liye replace karo
model.classifier[1] = nn.Linear(model.last_channel, num_classes)
model = model.to(device)

total_params = sum(p.numel() for p in model.parameters())
print(f"✅ Model ready | Total params: {total_params:,}")


# ── 5. LOSS & OPTIMIZER ──────────────────────
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=LR)
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)


# ── 6. TRAIN FUNCTION ────────────────────────
def train_one_epoch(model, loader, criterion, optimizer):
    model.train()
    total_loss, correct, total = 0, 0, 0
    for batch_idx, (images, labels) in enumerate(loader):
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        _, predicted = outputs.max(1)
        correct += predicted.eq(labels).sum().item()
        total += labels.size(0)

        if (batch_idx + 1) % 10 == 0:
            print(f"   Batch {batch_idx+1}/{len(loader)} | Loss: {loss.item():.4f}", end="\r")

    return total_loss / len(loader), 100. * correct / total


def evaluate(model, loader, criterion):
    model.eval()
    total_loss, correct, total = 0, 0, 0
    all_preds, all_labels = [], []
    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            total_loss += loss.item()
            _, predicted = outputs.max(1)
            correct += predicted.eq(labels).sum().item()
            total += labels.size(0)
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    return total_loss / len(loader), 100. * correct / total, all_preds, all_labels


# ── 7. TRAINING LOOP ─────────────────────────
print(f"\n🚀 Training shuru — {EPOCHS} epochs, CPU pe...\n")
history = {"train_loss": [], "train_acc": [], "val_loss": [], "val_acc": []}
best_val_acc = 0.0

for epoch in range(1, EPOCHS + 1):
    print(f"Epoch [{epoch}/{EPOCHS}]")
    t_loss, t_acc = train_one_epoch(model, train_loader, criterion, optimizer)
    v_loss, v_acc, _, _ = evaluate(model, val_loader, criterion)
    scheduler.step()

    history["train_loss"].append(t_loss)
    history["train_acc"].append(t_acc)
    history["val_loss"].append(v_loss)
    history["val_acc"].append(v_acc)

    print(f"   Train Loss: {t_loss:.4f} | Train Acc: {t_acc:.2f}%")
    print(f"   Val   Loss: {v_loss:.4f} | Val   Acc: {v_acc:.2f}%")

    # Best model save karo
    if v_acc > best_val_acc:
        best_val_acc = v_acc
        torch.save(model.state_dict(), os.path.join(OUTPUT_DIR, "best_model.pth"))
        print(f"   💾 Best model saved! (Val Acc: {v_acc:.2f}%)")
    print()

print(f"✅ Training complete! Best Val Accuracy: {best_val_acc:.2f}%")


# ── 8. GRAPHS SAVE KARO ──────────────────────
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

ax1.plot(history["train_loss"], label="Train Loss", color="#e74c3c")
ax1.plot(history["val_loss"],   label="Val Loss",   color="#3498db")
ax1.set_title("Loss"); ax1.legend(); ax1.set_xlabel("Epoch")

ax2.plot(history["train_acc"], label="Train Acc", color="#e74c3c")
ax2.plot(history["val_acc"],   label="Val Acc",   color="#3498db")
ax2.set_title("Accuracy (%)"); ax2.legend(); ax2.set_xlabel("Epoch")

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "training_curves.png"), dpi=120)
plt.close()
print("📊 Training graphs saved → output/training_curves.png")


# ── 9. FINAL EVALUATION + REPORT ─────────────
print("\n📋 Final Evaluation on Validation Set...")
model.load_state_dict(torch.load(os.path.join(OUTPUT_DIR, "best_model.pth")))
_, final_acc, preds, labels_true = evaluate(model, val_loader, criterion)
print(f"\n✅ Final Val Accuracy: {final_acc:.2f}%")

present_labels = sorted(set(labels_true) | set(preds))
present_names  = [class_names[i] for i in present_labels]
report = classification_report(labels_true, preds, labels=present_labels, target_names=present_names, zero_division=0)
print("\nClassification Report:\n")
print(report)

with open(os.path.join(OUTPUT_DIR, "classification_report.txt"), "w") as f:
    f.write(report)

# Confusion Matrix (top 15 classes tak)
cm = confusion_matrix(labels_true, preds)
top_n = min(15, num_classes)
cm_small = cm[:top_n, :top_n]
plt.figure(figsize=(14, 10))
sns.heatmap(cm_small, annot=True, fmt="d", cmap="YlOrRd",
            xticklabels=class_names[:top_n],
            yticklabels=class_names[:top_n])
plt.title("Confusion Matrix (top classes)")
plt.xticks(rotation=45, ha="right", fontsize=7)
plt.yticks(rotation=0, fontsize=7)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "confusion_matrix.png"), dpi=120)
plt.close()
print("📊 Confusion matrix saved → output/confusion_matrix.png")

print("\n🎉 Sab kuch output/ folder mein save ho gaya!")
print("   best_model.pth         ← trained model")
print("   class_names.json       ← class list")
print("   training_curves.png    ← loss/accuracy graph")
print("   confusion_matrix.png   ← prediction heatmap")
print("   classification_report.txt ← precision/recall")
