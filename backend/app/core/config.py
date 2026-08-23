from typing import Union, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


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
    ACTIVE_MODEL_VERSION: str = "return-risk-hgb-v1"

    # CORS Origins (comma-separated string or list)
    CORS_ORIGINS: Union[List[str], str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
        description="Allowed CORS origins for the frontend application"
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            origins = [origin.strip() for origin in v.split(",") if origin.strip()]
            return origins if origins else ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
        elif isinstance(v, list):
            return [str(origin).strip() for origin in v if str(origin).strip()]
        return ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"]

    def get_cors_origins(self) -> List[str]:
        origins = self.CORS_ORIGINS if isinstance(self.CORS_ORIGINS, list) else [self.CORS_ORIGINS]
        if self.APP_ENV.lower() == "production" and ("*" in origins or any(o == "*" for o in origins)):
            raise ValueError("Unsafe CORS configuration: Wildcard '*' is strictly prohibited in production environment.")
        return origins

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
