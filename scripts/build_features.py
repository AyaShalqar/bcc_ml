import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import numpy as np
from datetime import datetime
from app.main import load_data
from app.recommend_for_client import recommend_for_client

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
OUT_DIR = os.path.join(BASE_DIR, "out")
os.makedirs(OUT_DIR, exist_ok=True)

def is_weekend(date_str: str) -> bool:
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        return d.weekday() >= 5
    except:
        return False

def main():
    clients, tr_types = load_data()
    rows = []

    for c in clients.values():
        r = recommend_for_client(c, tr_types.get(c.client_code, {}))

        spend_total = c.spend_total if c.spend_total > 0 else 1

        # --- Shares ---
        share_food = c.spend_by_cat.get("Продукты питания", 0) / spend_total
        share_rest = c.spend_by_cat.get("Кафе и рестораны", 0) / spend_total
        share_travel = sum(c.spend_by_cat.get(cat, 0) for cat in ["Такси","Отели","Путешествия","Авиабилеты"]) / spend_total
        share_online = sum(c.spend_by_cat.get(cat, 0) for cat in ["Смотрим дома","Едим дома","Играем дома"]) / spend_total

        # --- Inflows / Outflows ---
        inflows_outflows_ratio = (c.inflows + 1) / (c.outflows + 1)

        # --- Transfers flags ---
        tmap = tr_types.get(c.client_code, {})
        loan_payments = tmap.get("loan_payment", 0)
        atm_withdraw = tmap.get("atm_withdrawal", 0)
        fx_ops = tmap.get("fx_buy", 0) + tmap.get("fx_sell", 0)

        has_loans = 1 if loan_payments > 0 else 0
        has_atm_out = 1 if atm_withdraw > 0 else 0
        has_fx = 1 if fx_ops > 0 else 0

        loan_ratio = loan_payments / (c.outflows + 1)
        atm_ratio = atm_withdraw / (c.outflows + 1)
        fx_ratio = fx_ops / (c.outflows + 1)

        # --- Seasonality (летние траты travel) ---
        travel_seasonality = 0
        if c.travel_peak_month and c.travel_peak_month.month in [6,7,8]:
            travel_seasonality = 1

        # --- Weekend spending share ---
        weekend_spending = 0
        if hasattr(c, "transactions") and len(c.transactions) > 0:
            weekend_amounts = [amt for cat, amt, date in c.transactions if is_weekend(date)]
            weekend_spending = sum(weekend_amounts) / spend_total if spend_total > 0 else 0

        # --- Target ---
        best_product = r["best_product"]

        rows.append([
            c.client_code,
            round(share_food, 3),
            round(share_rest, 3),
            round(share_travel, 3),
            round(share_online, 3),
            round(c.avg_monthly_balance_KZT, 2),
            round(inflows_outflows_ratio, 3),
            has_loans,
            has_atm_out,
            has_fx,
            round(loan_ratio, 3),
            round(atm_ratio, 3),
            round(fx_ratio, 3),
            travel_seasonality,
            round(weekend_spending, 3),
            best_product
        ])

    df = pd.DataFrame(rows, columns=[
        "client_code","share_food","share_rest","share_travel","share_online",
        "avg_balance","inflows_outflows_ratio","has_loans","has_atm_out","has_fx",
        "loan_ratio","atm_ratio","fx_ratio","travel_seasonality","weekend_spending",
        "best_product"
    ])

    out_file = os.path.join(OUT_DIR, "ml_features.csv")
    df.to_csv(out_file, index=False, encoding="utf-8-sig")
    print(f"✅ Saved ML features v2: {out_file} ({len(df)} rows, {df.shape[1]} features)")

if __name__ == "__main__":
    main()
