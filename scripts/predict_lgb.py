import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import joblib

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
OUT_DIR = os.path.join(BASE_DIR, "out")

# Загружаем фичи
features_path = os.path.join(OUT_DIR, "ml_features.csv")
df = pd.read_csv(features_path)

# Загружаем модель и энкодер
model = joblib.load(os.path.join(OUT_DIR, "lgb_model.pkl"))
encoder = joblib.load(os.path.join(OUT_DIR, "lgb_label_encoder.pkl"))

# Разделяем X / y
X = df.drop(columns=["client_code", "best_product"])
client_ids = df["client_code"]

# Предсказания
pred_encoded = model.predict(X)
pred_labels = encoder.inverse_transform(pred_encoded)

# Сохраняем результат
out_df = pd.DataFrame({
    "client_code": client_ids,
    "predicted_product": pred_labels
})
out_path = os.path.join(OUT_DIR, "lgb_predictions.csv")
out_df.to_csv(out_path, index=False, encoding="utf-8-sig")

print(f"✅ Predictions saved to {out_path}")
print(out_df.head())
