import os, json, torch, torch.nn as nn
import matplotlib.pyplot as plt
import seaborn as sns
from torchvision import transforms, models, datasets
from torch.utils.data import DataLoader, Subset
from sklearn.metrics import classification_report, confusion_matrix

OUTPUT_DIR = "./output"
DATASET_DIR = "./dataset"
IMG_SIZE = 128
BATCH_SIZE = 16

with open(os.path.join(OUTPUT_DIR, "class_names.json")) as f:
    class_names = json.load(f)

num_classes = len(class_names)
model = models.mobilenet_v2(weights=None)
model.classifier[1] = nn.Linear(model.last_channel, num_classes)
model.load_state_dict(torch.load(os.path.join(OUTPUT_DIR, "best_model.pth"), map_location="cpu"))
model.eval()

val_transforms = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225]),
])
full = datasets.ImageFolder(os.path.join(DATASET_DIR, "train"), transform=val_transforms)
import torch
val_idx = torch.load(os.path.join(OUTPUT_DIR, "val_indices.pth")) if os.path.exists(os.path.join(OUTPUT_DIR,"val_indices.pth")) else list(range(int(0.8*len(full)), len(full)))
val_data = Subset(full, val_idx)
val_loader = DataLoader(val_data, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

preds, labels_true = [], []
with torch.no_grad():
    for imgs, lbls in val_loader:
        out = model(imgs)
        _, predicted = out.max(1)
        preds.extend(predicted.numpy())
        labels_true.extend(lbls.numpy())

present_labels = sorted(set(labels_true) | set(preds))
present_names  = [class_names[i] for i in present_labels]
report = classification_report(labels_true, preds, labels=present_labels, target_names=present_names, zero_division=0)
print(report)
with open(os.path.join(OUTPUT_DIR, "classification_report.txt"), "w") as f:
    f.write(report)
print("✅ Report saved!")