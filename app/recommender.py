from typing import Dict
from .models import ClientData

# --- Ставки и лимиты ---
TRAVEL_CB_RATE = 0.04
TRAVEL_CB_CAP = 100_000

PREMIUM_CB_BASE_BY_BALANCE = [
    (6_000_000, 0.04),
    (1_000_000, 0.03),
    (0, 0.02),
]
PREMIUM_CB_CAP = 100_000
PREMIUM_PRIV_CATS = {"Ювелирные изделия", "Косметика и Парфюмерия", "Кафе и рестораны"}

CREDIT_TOP_RATE = 0.10
CREDIT_CB_CAP = 100_000
ONLINE_CATS = {"Играем дома", "Едим дома", "Смотрим дома"}

SAVINGS_MULTI_RATE = 0.145
SAVINGS_FIXED_RATE = 0.165
SAVINGS_ACC_RATE   = 0.155

INV_START_BONUS = 5000
GOLD_HINT_VALUE = 3000

TRAVEL_CATS = {"Путешествия", "Отели", "Такси", "Авиабилеты"}


# --- Скоринг ---
def score_travel(c: ClientData) -> float:
    travel_sum = sum(v for k, v in c.spend_by_cat.items() if k in TRAVEL_CATS)
    return min(TRAVEL_CB_RATE * travel_sum, TRAVEL_CB_CAP)

def score_premium(c: ClientData, tr_types: Dict[str, float]) -> float:
    # ставка от баланса
    for th, rate in PREMIUM_CB_BASE_BY_BALANCE:
        if c.avg_monthly_balance_KZT >= th:
            base = rate * c.spend_total
            break
    else:
        base = 0

    # бонусные категории
    bonus = 0.04 * sum(v for k, v in c.spend_by_cat.items() if k in PREMIUM_PRIV_CATS)

    # экономия на снятиях и переводах
    atm_out = tr_types.get("atm_withdrawal", 0)
    p2p_out = tr_types.get("p2p_out", 0)
    saved = atm_out * 0.01 + p2p_out * 0.005

    return min(base + bonus + saved, PREMIUM_CB_CAP)

def score_credit(c: ClientData) -> float:
    top3 = sorted(c.spend_by_cat.items(), key=lambda kv: kv[1], reverse=True)[:3]
    sum_top3 = sum(v for _, v in top3)
    return min(CREDIT_TOP_RATE * (sum_top3 + c.spend_online), CREDIT_CB_CAP)

def score_fx(c: ClientData, tr_types: Dict[str, float]) -> float:
    fx_turnover = tr_types.get("fx_buy", 0) + tr_types.get("fx_sell", 0)
    abroad_spend = sum(v for k,v in c.spend_by_cat.items() if k in ["Отели","Путешествия"])
    return 0.01 * (fx_turnover + abroad_spend)

def score_cash_loan(c: ClientData, tr_types: Dict[str, float]) -> float:
    if c.inflows > 0 and c.outflows > c.inflows * 1.3:
        return 10_000
    if tr_types.get("loan_payment", 0) > 0:
        return 8_000
    return 0

def score_savings_fixed(c: ClientData) -> float:
    return (c.avg_monthly_balance_KZT * SAVINGS_FIXED_RATE) / 12

def score_savings_acc(c: ClientData) -> float:
    return (c.avg_monthly_balance_KZT * SAVINGS_ACC_RATE) / 12

def score_savings_multi(c: ClientData) -> float:
    return (c.avg_monthly_balance_KZT * SAVINGS_MULTI_RATE) / 12

def score_invest(c: ClientData) -> float:
    return INV_START_BONUS if c.avg_monthly_balance_KZT > 100_000 else 0

def score_gold(c: ClientData) -> float:
    return GOLD_HINT_VALUE if c.avg_monthly_balance_KZT > 3_000_000 else 0

def compute_scores(c: ClientData, tr_types: Dict[str, float]) -> Dict[str, float]:
    return {
        "Карта для путешествий": score_travel(c),
        "Премиальная карта": score_premium(c, tr_types),
        "Кредитная карта": score_credit(c),
        "Обмен валют": score_fx(c, tr_types),
        "Кредит наличными": score_cash_loan(c, tr_types),
        "Депозит Сберегательный": score_savings_fixed(c),
        "Депозит Накопительный": score_savings_acc(c),
        "Депозит Мультивалютный": score_savings_multi(c),
        "Инвестиции": score_invest(c),
        "Золотые слитки": score_gold(c),
    }

def choose_product(scores: Dict[str, float]):
    return sorted(scores.items(), key=lambda kv: kv[1], reverse=True)

def gen_push(c: ClientData, product: str, scores: Dict[str, float]) -> str:
    if product == "Карта для путешествий":
        return f"{c.name}, вернули бы ≈{round(scores[product])} ₸ кешбэком за поездки и такси. Оформить карту?"
    if product == "Премиальная карта":
        return f"{c.name}, держите солидный остаток — премиум даст кешбэк и бесплатные переводы."
    if product == "Кредитная карта":
        return f"{c.name}, до 10% кешбэка в ваших любимых категориях и онлайн-сервисах."
    if product == "Обмен валют":
        return f"{c.name}, ловите лучший курс прямо в приложении — без комиссии 24/7."
    if product == "Кредит наличными":
        return f"{c.name}, быстрое оформление кредита наличными без залога и справок."
    return f"{c.name}, персональное предложение готово."
