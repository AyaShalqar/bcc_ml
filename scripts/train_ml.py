import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import joblib

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
OUT_DIR = os.path.join(BASE_DIR, "out")
os.makedirs(OUT_DIR, exist_ok=True)

def main():
    df = pd.read_csv(os.path.join(OUT_DIR, "ml_features.csv"))

    # X — признаки, y — целевой продукт
    X = df.drop(columns=["best_product", "client_code"])
    y = df["best_product"]

    # кодируем продукты в числа
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    # обучаем простую модель
    model = RandomForestClassifier(
        n_estimators=200, random_state=42, class_weight="balanced"
    )
    model.fit(X, y_encoded)

    # сохраняем модель и encoder
    joblib.dump(model, os.path.join(OUT_DIR, "ml_model.pkl"))
    joblib.dump(le, os.path.join(OUT_DIR, "label_encoder.pkl"))

    print("✅ Model trained and saved")

if __name__ == "__main__":
    main()
