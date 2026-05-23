# 🌿 Plant Disease Detector — PlantDoc
### CPU-Friendly | MobileNetV2 | Classification + Disease Name

---

## 📁 Project Structure

```
your-project/
│
├── dataset/                    ← PlantDoc dataset yahan rakhna
│   ├── train/
│   │   ├── Apple Scab Leaf/
│   │   ├── Apple leaf/
│   │   └── ...
│   ├── val/
│   └── test/
│
├── output/                     ← Auto-banta hai training ke baad
│   ├── best_model.pth
│   ├── class_names.json
│   ├── training_curves.png
│   └── confusion_matrix.png
│
├── uploads/                    ← Web UI ke liye (auto-banta hai)
│
├── train_plantdoc.py           ← Training script ⭐
├── predict.py                  ← Single image prediction ⭐
├── app.py                      ← Web UI (Flask) ⭐
└── requirements.txt
```

---

## ⚙️ Step 1 — Install karo

```bash
pip install -r requirements.txt

# Web UI ke liye Flask bhi chahiye
pip install flask
```

---

## 🗂️ Step 2 — Dataset Path Set Karo

`train_plantdoc.py` open karo aur line 32 change karo:

```python
DATASET_DIR = "./dataset"   # ← apna actual path dalo
# Example Windows: DATASET_DIR = "C:/Users/YourName/PlantDoc"
# Example Linux  : DATASET_DIR = "/home/user/PlantDoc"
```

---

## 🚀 Step 3 — Training Chalao

```bash
python train_plantdoc.py
```

**CPU pe approx time:**
| IMG_SIZE | Epochs | Time (estimate) |
|----------|--------|-----------------|
| 128      | 15     | ~45-90 min      |
| 64       | 15     | ~20-40 min      |

> 💡 Tip: Pehli baar 5 epochs aur IMG_SIZE=64 rakh ke test karo

---

## 🔍 Step 4 — Single Image Predict

```bash
python predict.py --image path/to/leaf.jpg
```

Output example:
```
=======================================================
  🌿 PLANT DISEASE DETECTION RESULT
=======================================================
  📷 Image     : tomato_leaf.jpg
  🌱 Plant     : Tomato
  🔬 Status    : Diseased
  🦠 Disease   : Tomato Early blight leaf
  📊 Confidence: 87.43%

  Top Predictions:
    1. ⚠️  Tomato Early blight leaf         87.43%
    2. ⚠️  Tomato Septoria leaf spot        8.21%
    3. ✅  Tomato leaf                       4.36%
=======================================================
```

---

## 🌐 Step 5 — Web UI Chalao (Optional)

```bash
python app.py
```

Browser mein open karo: **http://localhost:5000**

Web UI features:
- Image drag & drop ya click karke upload
- Real-time prediction
- Healthy/Diseased badge
- Top 5 predictions table

---

## ⚡ Performance Tips (CPU ke liye)

```python
# train_plantdoc.py mein yeh changes karo agar bahut slow hai:
IMG_SIZE   = 64    # 128 se 64 karo → 4x faster
BATCH_SIZE = 8     # 16 se 8 karo → kam RAM use
EPOCHS     = 10    # 15 se 10 karo → jaldi khatam
```

---

## 🔧 Common Errors

| Error | Fix |
|-------|-----|
| `FileNotFoundError: dataset` | DATASET_DIR path galat hai, sahi path dalo |
| `ModuleNotFoundError: torch` | `pip install torch torchvision` chalao |
| `RuntimeError: CUDA` | Ignore karo, CPU pe chal raha hai |
| `class_names.json not found` | Pehle training run karo |
| Accuracy bahut kam hai | Epochs badhao ya learning rate kam karo |

---

## 📊 PlantDoc Classes (27 total)

| Plant       | Disease Classes                            |
|-------------|---------------------------------------------|
| Apple       | Scab, Rust, Healthy                        |
| Tomato      | Early Blight, Late Blight, Leaf Mold, etc. |
| Potato      | Early Blight, Late Blight, Healthy         |
| Corn        | Gray Leaf Spot, Common Rust, Healthy       |
| Grape       | Black Rot, Leaf Blight, Healthy            |
| + aur bhi  | ...                                        |

---

Made for PlantDoc Dataset • MobileNetV2 • CPU Optimized
