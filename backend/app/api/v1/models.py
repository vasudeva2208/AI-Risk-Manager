from fastapi import APIRouter, HTTPException, status
from typing import List
from backend.app.schemas.domain import ModelRegistryEntry
from backend.app.services.model_registry import model_registry

router = APIRouter(prefix="/models", tags=["Model Registry"])


@router.get("", response_model=List[ModelRegistryEntry])
def list_registered_models():
    """Lists all registered models, their operational status (ACTIVE vs INACTIVE), and thresholds."""
    return model_registry.list_models()


@router.get("/{model_version}", response_model=ModelRegistryEntry)
def get_model_details(model_version: str):
    """Retrieves metadata for a specific model version."""
    entry = model_registry.get_model_entry(model_version)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Model version '{model_version}' not found.")
    return entry
