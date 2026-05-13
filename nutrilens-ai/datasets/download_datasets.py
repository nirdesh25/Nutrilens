#!/usr/bin/env python3
"""
Download all required datasets from Kaggle.

Prerequisites:
1. Install kaggle CLI: pip install kaggle
2. Configure API token: ~/.kaggle/kaggle.json
"""

import os
import subprocess
import sys

DATASETS = [
    {
        'name': 'Fruits Fresh & Rotten (Primary)',
        'kaggle_id': 'sriramr/fruits-fresh-and-rotten-for-classification',
        'output_dir': 'freshness_dataset'
    },
    {
        'name': 'Fresh & Rotten Fruits (Alternative)',
        'kaggle_id': 'swoyam2609/fresh-and-rotten-fruits',
        'output_dir': 'freshness_dataset_alt'
    },
    {
        'name': 'Food-101',
        'kaggle_id': 'dansbecker/food-101',
        'output_dir': 'food_recognition_dataset'
    },
    {
        'name': 'Fruits-360',
        'kaggle_id': 'moltean/fruits',
        'output_dir': 'fruits_360_dataset'
    },
    {
        'name': 'Food Waste',
        'kaggle_id': 'adityajn105/food-waste-dataset',
        'output_dir': 'waste_dataset'
    },
    {
        'name': 'Milk Quality',
        'kaggle_id': 'cpluzshrijayan/milkquality',
        'output_dir': 'milk_quality_dataset'
    },
    {
        'name': 'Glycemic Index',
        'kaggle_id': 'mssmartypants/glycemic-index-dataset',
        'output_dir': 'gi_dataset'
    },
    {
        'name': 'Indian Food',
        'kaggle_id': 'nehaprabhavalkar/indian-food',
        'output_dir': 'indian_food_dataset'
    }
]

def check_kaggle_installed():
    """Check if Kaggle CLI is installed."""
    try:
        subprocess.run(['kaggle', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def download_dataset(kaggle_id, output_dir):
    """Download a dataset from Kaggle."""
    print(f"\nDownloading {kaggle_id}...")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Download dataset
    cmd = ['kaggle', 'datasets', 'download', '-d', kaggle_id, '-p', output_dir, '--unzip']
    
    try:
        subprocess.run(cmd, check=True)
        print(f"✓ Successfully downloaded to {output_dir}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to download: {e}")
        return False

def main():
    print("=" * 60)
    print("NutriLens AI - Dataset Downloader")
    print("=" * 60)
    
    # Check if Kaggle CLI is installed
    if not check_kaggle_installed():
        print("\n✗ Kaggle CLI not found!")
        print("\nInstall it with: pip install kaggle")
        print("Then configure your API token: https://www.kaggle.com/docs/api")
        sys.exit(1)
    
    print("\n✓ Kaggle CLI found")
    
    # Download each dataset
    success_count = 0
    for dataset in DATASETS:
        print(f"\n[{success_count + 1}/{len(DATASETS)}] {dataset['name']}")
        if download_dataset(dataset['kaggle_id'], dataset['output_dir']):
            success_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Download Summary: {success_count}/{len(DATASETS)} successful")
    print("=" * 60)
    
    if success_count == len(DATASETS):
        print("\n✓ All datasets downloaded successfully!")
        print("\nNext steps:")
        print("1. Run: python preprocess_datasets.py")
        print("2. Train models: cd ../ml_models && python train_freshness_model.py")
    else:
        print("\n⚠ Some datasets failed to download. Check errors above.")
        print("\nNote: USDA FoodData must be downloaded manually from:")
        print("https://fdc.nal.usda.gov/download-datasets.html")

if __name__ == "__main__":
    main()
