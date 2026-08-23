from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    APP_NAME: str = "AI Return Risk Manager"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "default_development_secret_key_change_in_production"

    # Database
    DATABASE_URL: str = "sqlite:///./risk_manager.db"

    # ML Config
    MODEL_DIR: str = "ml/models/artifacts"
    ACTIVE_MODEL_VERSION: str = "v1_baseline_logistic_regression"

    # Bounded Policy Thresholds
    POLICY_THRESHOLD_LOW: float = Field(default=0.30, description="Upper bound for low risk APPROVE policy recommendation")
    POLICY_THRESHOLD_HIGH: float = Field(default=0.70, description="Lower bound for high risk MANUAL_REVIEW policy recommendation")

    # Financial Cost Assumptions (USD)
    COST_REVIEW_FRICTION: float = Field(default=15.00, description="Cost of human review labor per case")
    COST_FALSE_POSITIVE_CHURN: float = Field(default=35.00, description="Customer friction and churn cost")
    COST_RETURN_SHIPPING: float = Field(default=8.50, description="Average shipping and processing cost")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
