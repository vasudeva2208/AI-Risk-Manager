"""
Model Registry Service.

Maintains metadata, file locations, status (ACTIVE vs INACTIVE), and thresholds
for all trained model artifacts. Ensures exactly one active champion candidate
while keeping baseline models accessible for comparison.
"""

import os
import json
from typing import Dict, List, Optional, Any
from backend.app.schemas.domain import ModelRegistryEntry


CHAMPION_MODEL_VERSION = "return-risk-hgb-v1"
BASELINE_MODEL_VERSION = "return-risk-logreg-v1"


class ModelRegistryService:
    def __init__(self, base_artifacts_dir: str = "ml/models"):
        self.base_artifacts_dir = base_artifacts_dir
        self.active_version = CHAMPION_MODEL_VERSION

    def list_models(self) -> List[ModelRegistryEntry]:
        """Lists all registered models with their metadata and active status."""
        entries = []

        # Champion Tree Model
        hgb_meta_path = os.path.join(self.base_artifacts_dir, "candidate", f"{CHAMPION_MODEL_VERSION}_meta.json")
        hgb_meta = self._load_meta(hgb_meta_path)
        entries.append(ModelRegistryEntry(
            model_version=CHAMPION_MODEL_VERSION,
            algorithm=hgb_meta.get("algorithm", "HistGradientBoostingClassifier"),
            feature_version="v2_point_in_time_23f",
            calibration_method=hgb_meta.get("calibration_method", "sigmoid (Platt scaling)"),
            selected_threshold=hgb_meta.get("selected_threshold", 0.30),
            status="ACTIVE" if self.active_version == CHAMPION_MODEL_VERSION else "INACTIVE",
            trained_at=hgb_meta.get("trained_at"),
            sample_count=hgb_meta.get("sample_count", 3500),
            description="Calibrated HistGradientBoosting model capturing multi-window return velocities and non-linear interactions.",
        ))

        # Baseline Logistic Regression Model
        logreg_meta_path = os.path.join(self.base_artifacts_dir, "baseline", f"{BASELINE_MODEL_VERSION}_meta.json")
        logreg_meta = self._load_meta(logreg_meta_path)
        entries.append(ModelRegistryEntry(
            model_version=BASELINE_MODEL_VERSION,
            algorithm=logreg_meta.get("algorithm", "LogisticRegression"),
            feature_version="v2_point_in_time_23f",
            calibration_method=logreg_meta.get("calibration_method", "sigmoid (Platt scaling)"),
            selected_threshold=logreg_meta.get("selected_threshold", 0.30),
            status="ACTIVE" if self.active_version == BASELINE_MODEL_VERSION else "INACTIVE",
            trained_at=logreg_meta.get("trained_at"),
            sample_count=logreg_meta.get("sample_count", 3500),
            description="Interpretable linear baseline model with standardized scaling and L2 regularization.",
        ))

        return entries

    def get_model_entry(self, model_version: str) -> Optional[ModelRegistryEntry]:
        """Retrieves metadata for a specific model version."""
        models = self.list_models()
        for m in models:
            if m.model_version == model_version:
                return m
        return None

    def get_active_model_entry(self) -> ModelRegistryEntry:
        """Retrieves the active production model entry."""
        entry = self.get_model_entry(self.active_version)
        if not entry:
            raise RuntimeError(f"Active model '{self.active_version}' not found in registry.")
        return entry

    def _load_meta(self, path: str) -> Dict[str, Any]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}


model_registry = ModelRegistryService()
