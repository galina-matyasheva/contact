from pydantic import BaseModel


class MetricsResponse(BaseModel):
    total_contacts: int
    today_contacts: int
    sentiment_distribution: dict[str, int]
    category_distribution: dict[str, int]
