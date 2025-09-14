import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import lightgbm as lgb
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import joblib

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
OUT_DIR = os.path.join(BASE_DIR, "out")
os.makedirs(OUT_DIR, exist_ok=True)

def main():
    # читаем фичи
    df = pd.read_csv(os.path.join(OUT_DIR, "ml_features.csv"))

    # X — признаки, y — целевой продукт
    X = df.drop(columns=["best_product", "client_code"])
    y = df["best_product"]

    # кодируем продукты в числа
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    # LightGBM классификатор
    model = lgb.LGBMClassifier(
        n_estimators=300,
        learning_rate=0.1,
        max_depth=-1,
        random_state=42
    )

    model.fit(X, y_encoded)

    # предсказания для отчёта
    preds = model.predict(X)
    acc = accuracy_score(y_encoded, preds)
    print("✅ Train Accuracy:", acc)
    print(classification_report(y_encoded, preds, target_names=le.classes_))

    # сохраняем модель и encoder
    joblib.dump(model, os.path.join(OUT_DIR, "lgb_model.pkl"))
    joblib.dump(le, os.path.join(OUT_DIR, "lgb_label_encoder.pkl"))

    print("✅ LightGBM model trained and saved")

if __name__ == "__main__":
    main()
