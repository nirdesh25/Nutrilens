# ML Models - Training Scripts

This directory contains scripts for training AI models using the downloaded datasets.

## Available Training Scripts

### 1. Freshness Detection Model
**Script:** `train_freshness_model.py`
**Dataset:** Fruits Fresh & Rotten Dataset
**Architecture:** EfficientNetB0 + Custom head
**Output:** `freshness_model.h5`

```bash
python train_freshness_model.py
```

### 2. Food Recognition Model
**Script:** `train_food_recognition_model.py`
**Dataset:** Food-101 Dataset
**Architecture:** ResNet50 or EfficientNetB3
**Output:** `food_recognition_model.h5`

```bash
python train_food_recognition_model.py
```

### 3. Waste Classification Model
**Script:** `train_waste_model.py`
**Dataset:** Food Waste Dataset
**Architecture:** MobileNetV2
**Output:** `waste_model.h5`

```bash
python train_waste_model.py
```

### 4. pH Strip Analysis Model
**Script:** `train_ph_model.py`
**Dataset:** Custom pH strip images (to be collected)
**Architecture:** Color extraction + Regression
**Output:** `ph_model.h5`

```bash
python train_ph_model.py
```

## Training Requirements

### Hardware
- GPU recommended (NVIDIA with CUDA support)
- Minimum 8GB RAM
- 20GB free disk space

### Software
```bash
pip install tensorflow==2.15.0
pip install torch torchvision
pip install opencv-python
pip install scikit-learn
pip install matplotlib
```

## Training Workflow

1. **Download datasets**
   ```bash
   cd ../datasets
   python download_datasets.py
   ```

2. **Preprocess data**
   ```bash
   python preprocess_datasets.py
   ```

3. **Train models**
   ```bash
   cd ../ml_models
   python train_freshness_model.py
   python train_food_recognition_model.py
   python train_waste_model.py
   ```

4. **Copy trained models to backend**
   ```bash
   cp *.h5 ../backend/ml_models/
   ```

5. **Update backend configuration**
   Edit `backend/.env` with model paths

## Model Performance Targets

| Model | Target Accuracy | Training Time |
|-------|----------------|---------------|
| Freshness Detection | >90% | 2-4 hours |
| Food Recognition | >85% | 4-8 hours |
| Waste Classification | >88% | 1-2 hours |
| pH Analysis | >80% | 1-2 hours |

## Using Pre-trained Models

If you don't want to train from scratch, you can use transfer learning:
- Models are initialized with ImageNet weights
- Fine-tuned on specific datasets
- Faster training with good performance

## Troubleshooting

### Out of Memory
- Reduce `BATCH_SIZE` in training scripts
- Use smaller model architecture
- Enable mixed precision training

### Low Accuracy
- Increase `EPOCHS`
- Adjust learning rate
- Add more data augmentation
- Collect more training data

### Slow Training
- Use GPU instead of CPU
- Reduce image size
- Use smaller model architecture
- Enable multi-GPU training
