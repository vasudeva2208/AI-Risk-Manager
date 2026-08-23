from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.database import engine, Base
from backend.app.api.v1.risk import router as risk_router
from backend.app.api.v1.reviews import router as reviews_router
from backend.app.api.v1.audit import router as audit_router
from backend.app.api.v1.models import router as models_router

# Create tables in relational database (PostgreSQL / SQLite)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="Defense-only Return Abuse & Friendly Fraud Risk Management Engine — API v1",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

cors_origins = settings.get_cors_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register versioned API routers
app.include_router(risk_router, prefix=settings.API_V1_STR)
app.include_router(reviews_router, prefix=settings.API_V1_STR)
app.include_router(audit_router, prefix=settings.API_V1_STR)
app.include_router(models_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "active_model": settings.ACTIVE_MODEL_VERSION,
        "currency": "INR",
        "policy_thresholds": {
            "low": settings.POLICY_THRESHOLD_LOW,
            "high": settings.POLICY_THRESHOLD_HIGH,
        },
    }
