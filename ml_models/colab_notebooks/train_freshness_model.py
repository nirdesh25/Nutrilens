#!/usr/bin/env python3
"""
Train food freshness detection model.

Dataset: Fruits Fresh & Rotten Dataset
Model: CNN (ResNet50 or EfficientNet)
Output: freshness_model.h5
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau

# Configuration
IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 50
DATASET_PATH = '../datasets/freshness_dataset'
MODEL_OUTPUT_PATH = 'freshness_model.h5'

def create_model(num_classes=2):
    """
    Create CNN model for freshness classification.
    
    Architecture: EfficientNetB0 + Custom head
    """
    # Load pre-trained EfficientNetB0
    base_model = EfficientNetB0(
        include_top=False,
        weights='imagenet',
        input_shape=(IMG_SIZE, IMG_SIZE, 3)
    )
    
    # Freeze base model layers
    base_model.trainable = False
    
    # Add custom classification head
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(256, activation='relu')(x)
    x = Dropout(0.5)(x)
    x = Dense(128, activation='relu')(x)
    x = Dropout(0.3)(x)
    outputs = Dense(num_classes, activation='softmax')(x)
    
    model = Model(inputs=base_model.input, outputs=outputs)
    
    return model

def prepare_data_generators():
    """Prepare training and validation data generators."""
    
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        zoom_range=0.2,
        validation_split=0.2
    )
    
    train_generator = train_datagen.flow_from_directory(
        DATASET_PATH,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='training'
    )
    
    validation_generator = train_datagen.flow_from_directory(
        DATASET_PATH,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='validation'
    )
    
    return train_generator, validation_generator

def train_model():
    """Train the freshness detection model."""
    
    print("=" * 60)
    print("Training Freshness Detection Model")
    print("=" * 60)
    
    # Check if dataset exists
    if not os.path.exists(DATASET_PATH):
        print(f"\n✗ Dataset not found at {DATASET_PATH}")
        print("Please download the dataset first using datasets/download_datasets.py")
        return
    
    # Prepare data
    print("\nPreparing data generators...")
    train_gen, val_gen = prepare_data_generators()
    
    print(f"Training samples: {train_gen.samples}")
    print(f"Validation samples: {val_gen.samples}")
    print(f"Classes: {train_gen.class_indices}")
    
    # Create model
    print("\nCreating model...")
    model = create_model(num_classes=len(train_gen.class_indices))
    
    # Compile model
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print(model.summary())
    
    # Callbacks
    callbacks = [
        ModelCheckpoint(
            MODEL_OUTPUT_PATH,
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        ),
        EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-7
        )
    ]
    
    # Train model
    print("\nTraining model...")
    history = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=EPOCHS,
        callbacks=callbacks
    )
    
    # Save final model
    model.save(MODEL_OUTPUT_PATH)
    print(f"\n✓ Model saved to {MODEL_OUTPUT_PATH}")
    
    # Evaluate
    print("\nEvaluating model...")
    val_loss, val_accuracy = model.evaluate(val_gen)
    print(f"Validation Loss: {val_loss:.4f}")
    print(f"Validation Accuracy: {val_accuracy:.4f}")
    
    return model, history

if __name__ == "__main__":
    train_model()
