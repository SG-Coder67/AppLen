from sqlalchemy import Column, Integer, BigInteger, String, Float, Boolean, Date
from app.database import Base


class App(Base):
    __tablename__ = "apps"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Basic app information
    app_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    developer = Column(String, nullable=False)

    # App performance
    rating = Column(Float)
    downloads = Column(BigInteger)

    # Original pricing
    monthly_price = Column(Float)
    yearly_price = Column(Float)
    currency = Column(String)
    free_trial_days = Column(Integer)

    # Pricing information
    pricing_type = Column(String, nullable=False)
    pricing_source = Column(String, nullable=False)
    pricing_date = Column(Date, nullable=False)
    pricing_status = Column(String, nullable=False)

    # -------------------------
    # Engineered features
    # -------------------------

    # Normalized prices
    normalized_monthly_price = Column(Float)
    normalized_yearly_price = Column(Float)

    # Yearly pricing analysis
    annualized_monthly_cost = Column(Float)
    annual_savings = Column(Float)
    annual_discount_pct = Column(Float)

    # Download/popularity features
    downloads_numeric = Column(Float)
    log_downloads = Column(Float)
    popularity_score = Column(Float)

    # Engagement
    rating_score = Column(Float)
    engagement_score = Column(Float)

    # Pricing classification
    price_tier = Column(String)
    has_free_trial = Column(Boolean)
    is_freemium = Column(Boolean)
    is_verified_price = Column(Boolean)

    # Value analysis
    price_adjusted_value_score = Column(Float)