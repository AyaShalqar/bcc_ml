from fastapi import FastAPI, HTTPException
import os, pandas as pd

from .models import ClientData
from .recommender import compute_scores, choose_product, gen_push
from .recommend_for_client import recommend_for_client
from .utils import safe_int, safe_float

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")

CLIENTS_CSV = os.path.join(DATA_DIR, "clients.csv")
TX_CSV      = os.path.join(DATA_DIR, "all_transactions_final_v6.csv")
TRF_CSV     = os.path.join(DATA_DIR, "all_transfers_final_v6.csv")

app = FastAPI(title="Bank Push Personalization API")

CLIENTS = {}
TR_TYPES = {}

def load_data():
    clients = pd.read_csv(CLIENTS_CSV)
    tx = pd.read_csv(TX_CSV)
    tr = pd.read_csv(TRF_CSV)

    objs = {}
    tr_types_by_client = {}

    for _, row in clients.iterrows():
        cid = safe_int(row["client_code"])
        name = str(row["name"])
        status = str(row.get("status", ""))
        age = safe_int(row.get("age", 0))
        city = str(row.get("city", ""))
        balance = safe_float(row.get("avg_monthly_balance_KZT", 0))

        tx_c = tx[tx["client_code"] == cid].copy()
        tr_c = tr[tr["client_code"] == cid].copy()

        spend_by_cat = tx_c.groupby("category")["amount"].sum().to_dict()
        spend_total = float(tx_c["amount"].sum())
        spend_travel = float(tx_c[tx_c["category"].isin(["Такси","Путешествия","Отели","Авиабилеты"])]["amount"].sum())
        spend_online = float(tx_c[tx_c["category"].isin(["Едим дома","Смотрим дома","Играем дома"])]["amount"].sum())
        trips_count = int(len(tx_c[tx_c["category"] == "Такси"]))

        inflows = float(tr_c[tr_c["direction"]=="in"]["amount"].sum())
        outflows = float(tr_c[tr_c["direction"]=="out"]["amount"].sum())

        objs[cid] = ClientData(
            client_code=cid,
            name=name,
            status=status,
            age=age,
            city=city,
            avg_monthly_balance_KZT=balance,
            spend_by_cat=spend_by_cat,
            spend_total=spend_total,
            spend_travel=spend_travel,
            spend_online=spend_online,
            trips_count=trips_count,
            travel_peak_month=None,
            inflows=inflows,
            outflows=outflows,
        )

        tr_types_by_client[cid] = tr_c.groupby("type")["amount"].sum().to_dict()

    return objs, tr_types_by_client

@app.on_event("startup")
def startup_event():
    global CLIENTS, TR_TYPES
    CLIENTS, TR_TYPES = load_data()

@app.get("/health")
def health():
    return {"status": "ok", "clients_loaded": len(CLIENTS)}

@app.get("/recommend/{client_id}")
def recommend(client_id: int):
    c = CLIENTS.get(client_id)
    if not c:
        raise HTTPException(status_code=404, detail="Client not found")
    return recommend_for_client(c, TR_TYPES.get(client_id, {}))

@app.get("/recommend_all")
def recommend_all():
    return [recommend_for_client(c, TR_TYPES.get(c.client_code, {})) for c in CLIENTS.values()]
