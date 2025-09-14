import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from app.main import load_data
from app.recommend_for_client import recommend_for_client

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
OUT_DIR = os.path.join(BASE_DIR, "out")
os.makedirs(OUT_DIR, exist_ok=True)

def main():
    clients, tr_types = load_data()
    rows = []

    for c in clients.values():
        r = recommend_for_client(c, tr_types.get(c.client_code, {}))

        top3 = "; ".join([f"{p['product']}: {p['score']}" for p in r["top4_products"][:3]])
        top5 = "; ".join(r["top5_spend"])

        rows.append([
            r["client_code"],
            r["name"],
            r["balance"],
            r["inflows"],
            r["outflows"],
            top5,
            r["best_product"],
            r["push"],
            top3
        ])

    df = pd.DataFrame(rows, columns=[
        "client_code","name","balance","inflows","outflows",
        "top5_spend","best_product","push","top3_products"
    ])
    out_file = os.path.join(OUT_DIR, "push_recommendations.csv")
    df.to_csv(out_file, index=False, encoding="utf-8-sig")
    print(f"✅ Saved: {out_file}")

if __name__ == "__main__":
    main()
