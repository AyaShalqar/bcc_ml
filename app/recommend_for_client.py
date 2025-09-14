from typing import Any, Dict
from .models import ClientData
from .recommender import compute_scores, choose_product, gen_push
from .utils import fmt_money

def recommend_for_client(c: ClientData, tr_types: Dict[str, float]) -> Dict[str, Any]:
    scores = compute_scores(c, tr_types)
    ranking = choose_product(scores)
    best_product, _ = ranking[0]
    push = gen_push(c, best_product, scores)

    # топ-5 категорий
    top5_spend = sorted(c.spend_by_cat.items(), key=lambda kv: kv[1], reverse=True)[:5]
    top5_spend = [f"{cat}: {fmt_money(val)}" for cat, val in top5_spend]

    return {
        "client_code": c.client_code,
        "name": c.name,
        "city": c.city,
        "status": c.status,
        "balance": fmt_money(c.avg_monthly_balance_KZT),
        "inflows": fmt_money(c.inflows),
        "outflows": fmt_money(c.outflows),
        "top5_spend": top5_spend,
        "best_product": best_product,
        "push": push,
        "top4_products": [
            {"product": prod, "score": round(score, 2)}
            for prod, score in ranking[:4]
        ],
    }
