"""
Interpretable Baseline Model Pipeline (Logistic Regression - return-risk-logreg-v1).

Implements end-to-end preprocessing, training, calibration, persistence, and inference.
"""

import os
import joblib
import json
import datetime
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from ml.features.extractor import NUMERICAL_FEATURE_NAMES, CATEGORICAL_FEATURE_NAMES, extract_features


MODEL_VERSION = "return-risk-logreg-v1"


class BaselineRiskModel:
    def __init__(self, model_version: str = MODEL_VERSION, random_state: int = 42):
        self.model_version = model_version
        self.random_state = random_state
        self.pipeline: Pipeline = None
        self.calibrated_model: CalibratedClassifierCV = None
        self.feature_names_out_: List[str] = []
        self.trained_at_: str = None
        self.selected_threshold_: float = 0.50

    def _build_preprocessor(self) -> ColumnTransformer:
        numeric_transformer = Pipeline(steps=[
            ("scaler", StandardScaler())
        ])
        categorical_transformer = Pipeline(steps=[
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
        ])

        preprocessor = ColumnTransformer(
            transformers=[
                ("num", numeric_transformer, NUMERICAL_FEATURE_NAMES),
                ("cat", categorical_transformer, CATEGORICAL_FEATURE_NAMES),
            ]
        )
        return preprocessor

    def train(
        self,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame = None,
        target_col: str = "return_abuse",
        calibrate: bool = True,
    ) -> Dict[str, Any]:
        """Trains the baseline Logistic Regression model on the training set."""
        X_train = extract_features(train_df)
        y_train = train_df[target_col].values

        preprocessor = self._build_preprocessor()
        base_clf = LogisticRegression(
            penalty="l2",
            C=1.0,
            solver="liblinear",
            class_weight="balanced",
            random_state=self.random_state,
            max_iter=1000,
        )

        self.pipeline = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("classifier", base_clf)
        ])

        self.pipeline.fit(X_train, y_train)
        self.trained_at_ = datetime.datetime.utcnow().isoformat()

        # Capture feature names
        cat_encoder = self.pipeline.named_steps["preprocessor"].named_transformers_["cat"].named_steps["onehot"]
        cat_features_out = cat_encoder.get_feature_names_out(CATEGORICAL_FEATURE_NAMES).tolist()
        self.feature_names_out_ = NUMERICAL_FEATURE_NAMES + cat_features_out

        calibration_method = "sigmoid (Platt scaling)"
        if calibrate:
            if val_df is not None and len(val_df) > 0:
                X_val = extract_features(val_df)
                y_val = val_df[target_col].values
                self.calibrated_model = CalibratedClassifierCV(
                    estimator=self.pipeline,
                    method="sigmoid",
                    cv="prefit",
                )
                self.calibrated_model.fit(X_val, y_val)
            else:
                self.calibrated_model = CalibratedClassifierCV(
                    estimator=self.pipeline,
                    method="sigmoid",
                    cv=3,
                )
                self.calibrated_model.fit(X_train, y_train)
        else:
            self.calibrated_model = None
            calibration_method = "None"

        metadata = {
            "model_version": self.model_version,
            "algorithm": "LogisticRegression",
            "hyperparameters": {
                "penalty": "l2",
                "C": 1.0,
                "solver": "liblinear",
                "class_weight": "balanced",
            },
            "calibration_method": calibration_method,
            "trained_at": self.trained_at_,
            "sample_count": len(train_df),
            "target_prevalence": float(np.mean(y_train)),
            "num_features_in": len(NUMERICAL_FEATURE_NAMES) + len(CATEGORICAL_FEATURE_NAMES),
            "num_features_out": len(self.feature_names_out_),
        }
        return metadata

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        """Computes calibrated probability of return abuse: P(return_abuse = 1)."""
        X = extract_features(df)
        if self.calibrated_model is not None:
            probs = self.calibrated_model.predict_proba(X)
        elif self.pipeline is not None:
            probs = self.pipeline.predict_proba(X)
        else:
            raise ValueError("Model pipeline has not been trained or loaded.")
        return probs[:, 1]

    def explain_instance(self, single_row_df: pd.DataFrame, top_k: int = 4) -> List[Dict[str, Any]]:
        """
        Extracts linear contribution breakdown for an individual return assessment.
        Linear contribution: w_i * x_i
        """
        if self.pipeline is None:
            raise ValueError("Model pipeline has not been trained or loaded.")

        X = extract_features(single_row_df)
        preprocessed_x = self.pipeline.named_steps["preprocessor"].transform(X)[0]
        coefs = self.pipeline.named_steps["classifier"].coef_[0]

        contributions = []
        for feat_name, x_val, w_val in zip(self.feature_names_out_, preprocessed_x, coefs):
            contrib = float(x_val * w_val)
            contributions.append({
                "feature_name": feat_name,
                "feature_value": round(float(x_val), 3),
                "contribution": round(contrib, 4),
                "description": f"Contribution {contrib:+.3f} to risk log-odds",
            })

        contributions.sort(key=lambda x: abs(x["contribution"]), reverse=True)
        return contributions[:top_k]

    def save(self, artifact_dir: str):
        """Saves model pipeline and metadata to disk."""
        os.makedirs(artifact_dir, exist_ok=True)
        model_path = os.path.join(artifact_dir, f"{self.model_version}.joblib")
        calib_path = os.path.join(artifact_dir, f"{self.model_version}_calibrated.joblib")
        meta_path = os.path.join(artifact_dir, f"{self.model_version}_meta.json")

        joblib.dump(self.pipeline, model_path)
        if self.calibrated_model is not None:
            joblib.dump(self.calibrated_model, calib_path)

        metadata = {
            "model_version": self.model_version,
            "algorithm": "LogisticRegression",
            "trained_at": self.trained_at_,
            "selected_threshold": self.selected_threshold_,
            "feature_names_out": self.feature_names_out_,
            "numerical_features": NUMERICAL_FEATURE_NAMES,
            "categorical_features": CATEGORICAL_FEATURE_NAMES,
        }
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

    @classmethod
    def load(cls, artifact_dir: str, model_version: str = MODEL_VERSION) -> "BaselineRiskModel":
        """Loads trained model pipeline and metadata from disk."""
        model_path = os.path.join(artifact_dir, f"{model_version}.joblib")
        calib_path = os.path.join(artifact_dir, f"{model_version}_calibrated.joblib")
        meta_path = os.path.join(artifact_dir, f"{model_version}_meta.json")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model checkpoint not found at {model_path}")

        instance = cls(model_version=model_version)
        instance.pipeline = joblib.load(model_path)
        if os.path.exists(calib_path):
            instance.calibrated_model = joblib.load(calib_path)

        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
                instance.trained_at_ = meta.get("trained_at")
                instance.feature_names_out_ = meta.get("feature_names_out", [])
                instance.selected_threshold_ = meta.get("selected_threshold", 0.50)

        return instance
