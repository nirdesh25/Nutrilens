import nbformat as nbf
import os

def create_freshness_notebook():
    nb = nbf.v4.new_notebook()
    nb['cells'] = [
        nbf.v4.new_markdown_cell("# Freshness Detection Model Training\n\nRun this notebook in Google Colab with GPU enabled (Runtime -> Change runtime type -> T4 GPU)."),
        nbf.v4.new_code_cell("!pip install kaggle tensorflow scikit-learn"),
        nbf.v4.new_markdown_cell("## Setup Kaggle API\nPaste your `KAGGLE_API_TOKEN` (starts with `KGAT_...`) to download the datasets directly to Colab."),
        nbf.v4.new_code_cell("import os, getpass\nos.environ['KAGGLE_API_TOKEN'] = getpass.getpass('Enter your KAGGLE_API_TOKEN: ')"),
        nbf.v4.new_markdown_cell("## Download Dataset"),
        nbf.v4.new_code_cell("!kaggle datasets download -d sriramr/fruits-fresh-and-rotten-for-classification\n!unzip -q fruits-fresh-and-rotten-for-classification.zip -d dataset\n!ls dataset"),
        nbf.v4.new_markdown_cell("## Train Model"),
        nbf.v4.new_code_cell('''import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model

# Setup paths and data generators
train_dir = "dataset/dataset/train"
test_dir = "dataset/dataset/test"

train_datagen = ImageDataGenerator(rescale=1./255, rotation_range=20, horizontal_flip=True, validation_split=0.2)

train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',
    subset='training'
)

val_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',
    subset='validation'
)

# Build Model
base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
for layer in base_model.layers:
    layer.trainable = False

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(128, activation='relu')(x)
predictions = Dense(train_generator.num_classes, activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=predictions)
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Train Model
history = model.fit(train_generator, validation_data=val_generator, epochs=5)

# Save Model
model.save("freshness_model.h5")
'''),
        nbf.v4.new_markdown_cell("## Download the Trained Model\nAfter training, you can download `freshness_model.h5` and place it in the `nutrilens-ai/ml_models` folder in your project."),
        nbf.v4.new_code_cell("files.download('freshness_model.h5')")
    ]
    with open("c:/Users/nirde/OneDrive/Documents/nutri lens/nutrilens-ai/ml_models/colab_notebooks/Train_Freshness_Model.ipynb", 'w') as f:
        nbf.write(nb, f)


def create_food_recognition_notebook():
    nb = nbf.v4.new_notebook()
    nb['cells'] = [
        nbf.v4.new_markdown_cell(
            "# Food Recognition — EfficientNetB0 on Food-101\n\n"
            "Run this notebook in **Google Colab with T4 GPU** enabled.\n\n"
            "This trains a 101-class food classifier using EfficientNetB0 transfer learning.\n"
            "The saved model integrates directly into the NutriLens `/api/scan/predict` endpoint."
        ),
        nbf.v4.new_code_cell("!pip install -q kaggle tensorflow keras"),
        nbf.v4.new_code_cell(
            "import os, getpass\n"
            "os.environ['KAGGLE_API_TOKEN'] = getpass.getpass('Enter your KAGGLE_API_TOKEN: ')"
        ),
        nbf.v4.new_code_cell(
            "!kaggle datasets download -d dansbecker/food-101\n"
            "!unzip -q food-101.zip -d food-101-dataset\n"
            "!ls food-101-dataset/food-101/images | head -10\n"
            "print('Dataset extracted.')"
        ),
        nbf.v4.new_markdown_cell("## Data Preparation"),
        nbf.v4.new_code_cell('''import tensorflow as tf
import os, pathlib, shutil, random
from sklearn.model_selection import train_test_split

DATA_DIR = pathlib.Path("food-101-dataset/food-101/images")
CLASSES = sorted([d.name for d in DATA_DIR.iterdir() if d.is_dir()])
print(f"Total classes: {len(CLASSES)}")

IMG_SIZE = (224, 224)
BATCH_SIZE = 32
AUTOTUNE = tf.data.AUTOTUNE

# Build file lists
all_files, all_labels = [], []
for idx, cls in enumerate(CLASSES):
    for img in (DATA_DIR / cls).glob("*.jpg"):
        all_files.append(str(img))
        all_labels.append(idx)

train_files, val_files, train_labels, val_labels = train_test_split(
    all_files, all_labels, test_size=0.2, stratify=all_labels, random_state=42
)
print(f"Train: {len(train_files)}  Val: {len(val_files)}")

def load_image(path, label):
    img = tf.io.read_file(path)
    img = tf.image.decode_jpeg(img, channels=3)
    img = tf.image.resize(img, IMG_SIZE)
    img = tf.cast(img, tf.float32) / 255.0
    return img, label

def augment(img, label):
    img = tf.image.random_flip_left_right(img)
    img = tf.image.random_brightness(img, 0.2)
    img = tf.image.random_contrast(img, 0.8, 1.2)
    img = tf.image.random_saturation(img, 0.8, 1.2)
    return img, label

train_ds = (
    tf.data.Dataset.from_tensor_slices((train_files, train_labels))
    .map(load_image, num_parallel_calls=AUTOTUNE)
    .map(augment, num_parallel_calls=AUTOTUNE)
    .shuffle(1000).batch(BATCH_SIZE).prefetch(AUTOTUNE)
)
val_ds = (
    tf.data.Dataset.from_tensor_slices((val_files, val_labels))
    .map(load_image, num_parallel_calls=AUTOTUNE)
    .batch(BATCH_SIZE).prefetch(AUTOTUNE)
)'''),
        nbf.v4.new_markdown_cell("## Build EfficientNetB0 Model"),
        nbf.v4.new_code_cell('''from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras import layers, Model
import tensorflow.keras.backend as K

base = EfficientNetB0(include_top=False, weights="imagenet", input_shape=(224, 224, 3))
base.trainable = False  # Phase 1: freeze base

inputs = layers.Input((224, 224, 3))
x = base(inputs, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.BatchNormalization()(x)
x = layers.Dropout(0.4)(x)
x = layers.Dense(512, activation="relu")(x)
x = layers.Dropout(0.3)(x)
outputs = layers.Dense(len(CLASSES), activation="softmax")(x)

model = Model(inputs, outputs)
model.compile(
    optimizer=tf.keras.optimizers.Adam(1e-3),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)
model.summary()'''),
        nbf.v4.new_markdown_cell("## Phase 1 — Train classification head (5 epochs)"),
        nbf.v4.new_code_cell('''callbacks = [
    tf.keras.callbacks.EarlyStopping(monitor="val_accuracy", patience=3, restore_best_weights=True),
    tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=2, min_lr=1e-7)
]

history1 = model.fit(train_ds, validation_data=val_ds, epochs=5, callbacks=callbacks)
print(f"Phase 1 val accuracy: {max(history1.history['val_accuracy']):.3f}")'''),
        nbf.v4.new_markdown_cell("## Phase 2 — Fine-tune top 30 layers"),
        nbf.v4.new_code_cell('''base.trainable = True
# Freeze all except last 30 layers
for layer in base.layers[:-30]:
    layer.trainable = False

model.compile(
    optimizer=tf.keras.optimizers.Adam(1e-5),  # Very low LR for fine-tuning
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

history2 = model.fit(train_ds, validation_data=val_ds, epochs=15, callbacks=callbacks)
print(f"Phase 2 best val accuracy: {max(history2.history['val_accuracy']):.3f}")'''),
        nbf.v4.new_markdown_cell("## Evaluate & Save"),
        nbf.v4.new_code_cell('''import json

loss, acc = model.evaluate(val_ds)
print(f"Final Validation Accuracy: {acc*100:.2f}%")
print(f"Final Validation Loss:     {loss:.4f}")

# Save model
model.save("food_recognition_model.h5")
print("Model saved as food_recognition_model.h5")

# Save class label mapping (needed for inference)
class_map = {str(i): name for i, name in enumerate(CLASSES)}
with open("food_recognition_classes.json", "w") as f:
    json.dump(class_map, f, indent=2)
print("Class map saved as food_recognition_classes.json")'''),
        nbf.v4.new_markdown_cell(
            "## Download\n\n"
            "Download both files and place them in `nutrilens-ai/ml_models/`.\n"
            "Set `FOOD_RECOGNITION_MODEL_PATH=./ml_models/food_recognition_model.h5` in your `.env`."
        ),
        nbf.v4.new_code_cell(
            "files.download('food_recognition_model.h5')\n"
            "files.download('food_recognition_classes.json')"
        ),
    ]
    with open("c:/Users/nirde/OneDrive/Documents/nutri lens/nutrilens-ai/ml_models/colab_notebooks/Train_Food_Recognition.ipynb", 'w') as f:
        nbf.write(nb, f)

def create_waste_classification_notebook():
    nb = nbf.v4.new_notebook()
    nb['cells'] = [
        nbf.v4.new_markdown_cell("# Waste Classification Model Training\n\nRun this notebook in Google Colab with GPU enabled (Runtime -> Change runtime type -> T4 GPU)."),
        nbf.v4.new_code_cell("!pip install -q kaggle tensorflow scikit-learn"),
        nbf.v4.new_code_cell("import os, getpass\nos.environ['KAGGLE_API_TOKEN'] = getpass.getpass('Enter your KAGGLE_API_TOKEN: ')"),
        nbf.v4.new_code_cell("!kaggle datasets download -d techsash/waste-classification-data\n!unzip -q waste-classification-data.zip -d waste_dataset\n!ls waste_dataset/DATASET/TRAIN"),
        nbf.v4.new_code_cell('''import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model
import json
import os

# Setup paths and data generators
train_dir = "waste_dataset/DATASET/TRAIN"
test_dir = "waste_dataset/DATASET/TEST"

# Sometimes Kaggle dataset extraction creates a nested dataset structure based on how you unzip it
if not os.path.exists(train_dir) and os.path.exists("waste_dataset/dataset/DATASET/TRAIN"):
    train_dir = "waste_dataset/dataset/DATASET/TRAIN"
    test_dir = "waste_dataset/dataset/DATASET/TEST"

train_datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)
train_generator = train_datagen.flow_from_directory(
    train_dir, target_size=(224, 224), batch_size=32, class_mode='categorical', subset='training'
)
val_generator = train_datagen.flow_from_directory(
    train_dir, target_size=(224, 224), batch_size=32, class_mode='categorical', subset='validation'
)

# Build Model
base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
base_model.trainable = False

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(128, activation='relu')(x)
predictions = Dense(train_generator.num_classes, activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=predictions)
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Train Model
model.fit(train_generator, validation_data=val_generator, epochs=5)

# Save Model
model.save("waste_model.h5")

# Save class label mapping
class_map = {str(i): name for name, i in train_generator.class_indices.items()}
with open("waste_classes.json", "w") as f:
    json.dump(class_map, f, indent=2)
'''),
        nbf.v4.new_code_cell("from google.colab import files\nfiles.download('waste_model.h5')\nfiles.download('waste_classes.json')")
    ]
    with open("c:/Users/nirde/OneDrive/Documents/nutri lens/nutrilens-ai/ml_models/colab_notebooks/Train_Waste_Classification.ipynb", 'w') as f:
        nbf.write(nb, f)

def create_milk_quality_notebook():
    nb = nbf.v4.new_notebook()
    nb['cells'] = [
        nbf.v4.new_markdown_cell("# Milk Quality Model Training\n\nRun this notebook in Google Colab (GPU not required)."),
        nbf.v4.new_code_cell("!pip install kaggle pandas scikit-learn joblib"),
        nbf.v4.new_code_cell("import os, getpass\nos.environ['KAGGLE_API_TOKEN'] = getpass.getpass('Enter your KAGGLE_API_TOKEN: ')"),
        nbf.v4.new_code_cell("!kaggle datasets download -d cpluzshrijayan/milkquality\n!unzip -q milkquality.zip -d milkquality"),
        nbf.v4.new_code_cell("""import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

# Load dataset
df = pd.read_csv("milkquality/milknew.csv")

# Train model
X = df.drop('Grade', axis=1)
y = df['Grade']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

print(classification_report(y_test, model.predict(X_test)))

# Save model
joblib.dump(model, 'milk_quality_model.pkl')
"""),
        nbf.v4.new_code_cell("files.download('milk_quality_model.pkl')")
    ]
    with open("c:/Users/nirde/OneDrive/Documents/nutri lens/nutrilens-ai/ml_models/colab_notebooks/Train_Milk_Quality.ipynb", 'w') as f:
        nbf.write(nb, f)

if __name__ == '__main__':
    create_freshness_notebook()
    create_food_recognition_notebook()
    create_waste_classification_notebook()
    create_milk_quality_notebook()
    print("Notebooks generated.")
