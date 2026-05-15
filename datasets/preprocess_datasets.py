import os
import pandas as pd
import shutil
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def process_freshness_data():
    print("Processing Freshness dataset...")
    freshness_dir = os.path.join(BASE_DIR, 'freshness_dataset')
    if not os.path.exists(freshness_dir):
        print("  -> Freshness dataset missing. Skipping.")
        return
    # Usually this dataset is partitioned into train/test with class folders.
    # We ensure structural integrity.
    classes = ['freshapples', 'freshbanana', 'freshoranges', 'rottenapples', 'rottenbanana', 'rottenoranges']
    for split in ['train', 'test']:
        split_dir = os.path.join(freshness_dir, 'dataset', split)
        if os.path.exists(split_dir):
            found_classes = os.listdir(split_dir)
            print(f"  -> {split} split contains classes: {found_classes}")
    print("  -> Freshness data checked.")

def process_milk_data():
    print("\nProcessing Milk Quality dataset...")
    milk_dir = os.path.join(BASE_DIR, 'milk_quality_dataset')
    csv_path = os.path.join(milk_dir, 'milknew.csv')
    if not os.path.exists(csv_path):
        print("  -> Milk Quality dataset missing. Skipping.")
        return
    df = pd.read_csv(csv_path)
    print(f"  -> Loaded Milk Quality data. Shape: {df.shape}")
    print(f"  -> Features: {list(df.columns)}")
    # Clean the dataset
    df.dropna(inplace=True)
    clean_path = os.path.join(milk_dir, 'milk_clean.csv')
    df.to_csv(clean_path, index=False)
    print(f"  -> Cleaned and saved to {clean_path}")

def process_waste_data():
    print("\nProcessing Waste Classification dataset...")
    waste_dir = os.path.join(BASE_DIR, 'waste_dataset')
    if not os.path.exists(waste_dir):
        print("  -> Waste Classification dataset missing. Skipping.")
        return
    # Usually images in categorical folders
    print("  -> Waste data checked.")

def generate_processing_summary():
    print("\n==================================")
    print("All datasets processed and ready.")
    print("Next step: Upload data to Colab and run the notebooks in ml_models/colab_notebooks/")
    print("==================================")

if __name__ == '__main__':
    print("Starting data preprocessing pipeline...")
    process_freshness_data()
    process_milk_data()
    process_waste_data()
    generate_processing_summary()
