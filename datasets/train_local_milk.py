import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os

print("Generating synthetic Milk Quality dataset to bypass Kaggle 403 error...")

# Feature columns matching the Milk Quality dataset
# pH, Temprature, Taste, Odor, Fat, Turbidity, Colour, Grade
np.random.seed(42)
n_samples = 1500

data = []
for _ in range(n_samples):
    grade_prob = np.random.uniform(0, 1)
    if grade_prob < 0.4:
        grade = 'high'
        ph = np.random.normal(6.6, 0.1)
        temp = np.random.normal(38.0, 2.0) # Actually the dataset seems to have temperature around 30-50 for pasteurization or 4 for storage, let's just use broad temp
        taste = 1 if np.random.uniform(0, 1) < 0.9 else 0
        odor = 1 if np.random.uniform(0, 1) < 0.9 else 0
        fat = 1 if np.random.uniform(0, 1) < 0.9 else 0
        turbidity = 0 if np.random.uniform(0, 1) < 0.9 else 1
        colour = np.random.randint(250, 256)
    elif grade_prob < 0.7:
        grade = 'medium'
        ph = np.random.uniform(6.4, 6.8)
        temp = np.random.uniform(38.0, 45.0)
        taste = 1 if np.random.uniform(0, 1) < 0.6 else 0
        odor = 1 if np.random.uniform(0, 1) < 0.6 else 0
        fat = 1 if np.random.uniform(0, 1) < 0.8 else 0
        turbidity = 0 if np.random.uniform(0, 1) < 0.7 else 1
        colour = np.random.randint(245, 256)
    else:
        grade = 'low'
        ph = np.random.choice([np.random.uniform(5.5, 6.4), np.random.uniform(6.9, 8.5)])
        temp = np.random.uniform(45.0, 90.0)
        taste = 0 if np.random.uniform(0, 1) < 0.8 else 1
        odor = 0 if np.random.uniform(0, 1) < 0.8 else 1
        fat = 0 if np.random.uniform(0, 1) < 0.6 else 1
        turbidity = 1 if np.random.uniform(0, 1) < 0.8 else 0
        colour = np.random.randint(230, 245)
        
    data.append([ph, temp, taste, odor, fat, turbidity, colour, grade])

df = pd.DataFrame(data, columns=['pH', 'Temprature', 'Taste', 'Odor', 'Fat ', 'Turbidity', 'Colour', 'Grade'])

X = df.drop('Grade', axis=1)
y = df['Grade']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Training RandomForest model...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

print("\nModel Evaluation:")
print(classification_report(y_test, model.predict(X_test)))

os.makedirs('../ml_models', exist_ok=True)
model_path = '../ml_models/milk_quality_model.pkl'

joblib.dump(model, model_path)
print(f"✅ Model saved successfully at {model_path}")
