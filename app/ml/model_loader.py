import os
import joblib
import numpy as np
import pandas as pd
from app.ml.feature_engineering import compute_physics_features, FEATURE_COLUMNS, TARGET_FAILURE_MODES

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), 'artifacts')
MODEL_PATH = os.path.join(ARTIFACTS_DIR, 'predictsense_models.joblib')

class ModelLoaderService:
    _instance = None

    def __init__ (self):
        self.scaler = None
        self.isolation_forest = None
        self.failure_models = None
        self.metrics_summary = None
        self.loaded = False

        self.load_models()

    def load_models(self):
        if not os.path.exists(MODEL_PATH):
            print(f"Artifacts missing at {MODEL_PATH}. Running train_pipeline...")
            from app.ml.train_pipeline import train_and_evaluate
            train_and_evaluate()

        artifacts = joblib.load(MODEL_PATH)
        self.scaler = artifacts['scaler']
        self.isolation_forest = artifacts['isolation_forest']
        self.failure_models = artifacts['failure_models']
        self.metrics_summary = artifacts.get('metrics_summary', {})
        self.loaded = True
        print("ModelLoaderService initialized successfully.")

    def predict_reading(self, reading_dict):
        """
        Takes raw reading dict (air_temp, process_temp, rpm, torque, tool_wear, product_type),
        computes physics features, scales, and outputs full predictive assessment.
        """
        # 1. Feature calculation
        feat_df = compute_physics_features(reading_dict)
        X_raw = feat_df[FEATURE_COLUMNS].values

        # 2. Scale features
        X_scaled = self.scaler.transform(X_raw)

        # 3. Isolation Forest Anomaly Score
        raw_iso_score = float(self.isolation_forest.score_samples(X_scaled)[0])
        # Normalize anomaly score between 0.0 (perfect normal) and 1.0 (extreme anomaly)
        anomaly_prob = float(1.0 / (1.0 + np.exp(raw_iso_score * 4.0)))
        is_anomaly = bool(anomaly_prob > 0.58)

        # 4. Multi-Label Failure Mode Classifiers
        label_probs = {}
        max_failure_prob = 0.0

        for target in TARGET_FAILURE_MODES:
            clf = self.failure_models[target]
            prob = float(clf.predict_proba(X_scaled)[0, 1])
            label_probs[target] = round(prob, 4)
            if prob > max_failure_prob:
                max_failure_prob = prob

        # 5. Composite Risk & Health Score Calculation
        # Risk Score is calibrated between 0 and 100 based on highest failure mode probability and anomaly score
        risk_score = round(min(100.0, max(max_failure_prob * 100.0, anomaly_prob * 85.0)), 1)
        health_score = round(max(0.0, 100.0 - risk_score), 1)
        any_failure = bool(risk_score >= 50.0 or max_failure_prob >= 0.40 or is_anomaly)

        return {
            'features': feat_df.iloc[0].to_dict(),
            'anomaly_score': round(anomaly_prob, 4),
            'is_anomaly': is_anomaly,
            'label_probs': label_probs,
            'risk_score': risk_score,
            'health_score': health_score,
            'any_failure': any_failure
        }

def get_model_service():
    if ModelLoaderService._instance is None:
        ModelLoaderService._instance = ModelLoaderService()
    return ModelLoaderService._instance
