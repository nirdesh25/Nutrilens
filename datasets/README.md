# Dataset Integration Guide

This directory contains scripts for downloading, preprocessing, and integrating Kaggle datasets into NutriLens AI.

## Required Datasets

### 1. Fruits Fresh & Rotten Dataset
**Purpose:** Freshness detection model training
**Link:** https://www.kaggle.com/datasets/sriramr/fruits-fresh-and-rotten-for-classification
**Size:** ~13,000 images
**Classes:** Fresh/Rotten (Apple, Banana, Orange, etc.)

```bash
kaggle datasets download -d sriramr/fruits-fresh-and-rotten-for-classification
unzip fruits-fresh-and-rotten-for-classification.zip -d freshness_dataset/
```

### 2. Food-101 Dataset
**Purpose:** Food recognition and classification
**Link:** https://www.kaggle.com/datasets/dansbecker/food-101
**Size:** 101,000 images
**Classes:** 101 food categories

```bash
kaggle datasets download -d dansbecker/food-101
unzip food-101.zip -d food_recognition_dataset/
```

### 3. Food Waste Dataset
**Purpose:** Waste classification
**Link:** https://www.kaggle.com/datasets/adityajn105/food-waste-dataset
**Size:** ~2,000 images

```bash
kaggle datasets download -d adityajn105/food-waste-dataset
unzip food-waste-dataset.zip -d waste_dataset/
```

### 4. Milk Quality Dataset
**Purpose:** Spoilage prediction (tabular data)
**Link:** https://www.kaggle.com/datasets/cpluzshrijayan/milkquality
**Size:** ~1,000 records

```bash
kaggle datasets download -d cpluzshrijayan/milkquality
unzip milkquality.zip -d milk_quality_dataset/
```

### 5. USDA FoodData Central
**Purpose:** Nutritional information database
**Link:** https://fdc.nal.usda.gov/download-datasets.html
**Size:** 300,000+ foods

Download manually from USDA website or use API.

### 6. Glycemic Index Dataset
**Purpose:** Diabetes-friendly food recommendations
**Link:** https://www.kaggle.com/datasets/mssmartypants/glycemic-index-dataset

```bash
kaggle datasets download -d mssmartypants/glycemic-index-dataset
unzip glycemic-index-dataset.zip -d gi_dataset/
```

## Setup Instructions

### 1. Install Kaggle CLI
```bash
pip install kaggle
```

### 2. Configure Kaggle API
1. Go to https://www.kaggle.com/account
2. Create new API token
3. Download `kaggle.json`
4. Place in `~/.kaggle/kaggle.json` (Linux/Mac) or `C:\Users\<username>\.kaggle\kaggle.json` (Windows)

### 3. Download All Datasets
```bash
cd datasets
python download_datasets.py
```

### 4. Preprocess Datasets
```bash
python preprocess_datasets.py
```

## Directory Structure

```
datasets/
├── freshness_dataset/          # Fruits fresh & rotten
├── food_recognition_dataset/   # Food-101
├── waste_dataset/              # Food waste
├── milk_quality_dataset/       # Milk quality (tabular)
├── usda_fooddata/              # USDA nutritional data
├── gi_dataset/                 # Glycemic index
├── ph_strips/                  # Custom pH strip images (to collect)
├── processed/                  # Preprocessed data ready for training
└── scripts/                    # Preprocessing scripts
```

## Custom Dataset: pH Strips

You need to collect 200-400 pH strip images:
- Different pH levels (1-14)
- Various lighting conditions
- Different food types (milk, juice, meat)
- Label with actual pH values

Store in `datasets/ph_strips/` with structure:
```
ph_strips/
├── milk/
│   ├── ph_6.5_001.jpg
│   ├── ph_6.8_002.jpg
│   └── ...
├── juice/
└── meat/
```

## Next Steps

After downloading datasets:
1. Run preprocessing scripts
2. Train models using `ml_models/train_*.py`
3. Save trained models to `backend/ml_models/`
4. Update model paths in `backend/.env`
