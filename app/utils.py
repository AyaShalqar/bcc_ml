from datetime import datetime

RU_MONTHS_GEN = {
    1: "январе", 2: "феврале", 3: "марте", 4: "апреле",
    5: "мае", 6: "июне", 7: "июле", 8: "августе",
    9: "сентябре", 10: "октябре", 11: "ноябре", 12: "декабре"
}

def fmt_money(val: float) -> str:
    s = f"{round(val):,}".replace(",", " ")
    return f"{s} ₸"

def month_genitive(dt: datetime) -> str:
    return RU_MONTHS_GEN.get(dt.month, "")

def plural_trips(n: int) -> str:
    if n % 10 == 1 and n % 100 != 11:
        return "поездка"
    if 2 <= (n % 10) <= 4 and not (12 <= (n % 100) <= 14):
        return "поездки"
    return "поездок"

def safe_int(x) -> int:
    try:
        return int(x)
    except Exception:
        return 0

def safe_float(x) -> float:
    try:
        return float(x)
    except Exception:
        return 0.0
