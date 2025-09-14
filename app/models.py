from dataclasses import dataclass
from datetime import datetime
from typing import Dict

@dataclass
class ClientData:
    client_code: int
    name: str
    status: str
    age: int
    city: str
    avg_monthly_balance_KZT: float

    spend_by_cat: Dict[str, float]
    spend_total: float
    spend_travel: float
    spend_online: float
    trips_count: int
    travel_peak_month: datetime | None

    inflows: float
    outflows: float
