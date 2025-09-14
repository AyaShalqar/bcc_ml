import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import joblib

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
OUT_DIR = os.path.join(BASE_DIR, "out")

def main():
    df = pd.read_csv(os.path.join(OUT_DIR, "ml_features.csv"))
    X = df.drop(columns=["best_product", "client_code"])

    # загрузка модели и encoder
    model = joblib.load(os.path.join(OUT_DIR, "xgb_model.pkl"))
    le = joblib.load(os.path.join(OUT_DIR, "xgb_label_encoder.pkl"))

    # предсказания
    probs = model.predict_proba(X)
    preds = model.predict(X)
    pred_labels = le.inverse_transform(preds)

    # собираем результаты
    out = df[["client_code"]].copy()
    out["ml_predicted_product"] = pred_labels

    # топ-3 продуктов
    classes = le.classes_
    for i, cls in enumerate(classes):
        out[f"prob_{cls}"] = probs[:, i]

    out_file = os.path.join(OUT_DIR, "xgb_predictions.csv")
    out.to_csv(out_file, index=False, encoding="utf-8-sig")
    print(f"✅ Predictions saved: {out_file}")

if __name__ == "__main__":
    main()
