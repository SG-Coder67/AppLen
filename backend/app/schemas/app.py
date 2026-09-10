from pydantic import BaseModel,ConfigDict,Field
from datetime import date
class AppCreate(BaseModel):
    name:str=Field(
        min_length=2,
        max_length=100
    )
    price:int=Field(
        ge=0
    )

class AppResponse(BaseModel):
    id: int
    app_name: str
    category: str
    developer: str

    rating: float | None = None
    downloads: int | None = None

    monthly_price: float | None = None
    yearly_price: float | None = None
    currency: str | None = None
    free_trial_days: int | None = None

    pricing_type: str
    pricing_source: str
    pricing_date: date
    pricing_status: str

    normalized_monthly_price: float | None = None
    normalized_yearly_price: float | None = None
    annualized_monthly_cost: float | None = None
    annual_savings: float | None = None
    annual_discount_pct: float | None = None

    downloads_numeric: float | None = None
    log_downloads: float | None = None
    popularity_score: float | None = None
    rating_score: float | None = None
    engagement_score: float | None = None

    price_tier: str | None = None

    has_free_trial: bool | None = None
    is_freemium: bool | None = None
    is_verified_price: bool | None = None

    price_adjusted_value_score: float | None = None

    model_config = ConfigDict(from_attributes=True)