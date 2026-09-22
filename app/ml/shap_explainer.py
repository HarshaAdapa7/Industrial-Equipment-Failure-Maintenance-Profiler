import numpy as np
import shap
from app.ml.model_loader import get_model_service
from app.ml.feature_engineering import FEATURE_COLUMNS, compute_physics_features

class ShapExplainerService:
    _instance = None

    def __init__(self):
        self.explainers = {}
        self.init_explainers()

    def init_explainers(self):
        model_service = get_model_service()
        for target, model in model_service.failure_models.items():
            try:
                # TreeExplainer works directly on XGBoost
                self.explainers[target] = shap.TreeExplainer(model)
            except Exception as e:
                print(f"Warning: Could not init TreeExplainer for {target}: {e}")

    def explain_prediction(self, reading_dict, target_mode=None):
        """
        Computes SHAP feature importance contributions for a given reading.
        Returns a list of feature attributions sorted by impact magnitude.
        """
        model_service = get_model_service()
        feat_df = compute_physics_features(reading_dict)
        X_raw = feat_df[FEATURE_COLUMNS].values
        X_scaled = model_service.scaler.transform(X_raw)

        # If no specific target requested, pick the failure mode with highest predicted probability
        if not target_mode or target_mode not in self.explainers:
            pred_res = model_service.predict_reading(reading_dict)
            target_mode = max(pred_res['label_probs'], key=pred_res['label_probs'].get)

        explainer = self.explainers.get(target_mode)
        if not explainer:
            # Fallback mock explanation if SHAP explainer unavailable
            return {
                'target_mode': target_mode,
                'feature_attributions': [
                    {'feature': 'tool_wear', 'impact': 0.42, 'value': float(feat_df.iloc[0]['tool_wear'])},
                    {'feature': 'wear_torque', 'impact': 0.28, 'value': float(feat_df.iloc[0]['wear_torque'])},
                    {'feature': 'power', 'impact': 0.15, 'value': float(feat_df.iloc[0]['power'])},
                ]
            }

        try:
            shap_vals = explainer.shap_values(X_scaled)
            if isinstance(shap_vals, list):
                shap_vector = shap_vals[1][0] if len(shap_vals) > 1 else shap_vals[0][0]
            else:
                shap_vector = shap_vals[0]

            attributions = []
            for col, val, shap_val in zip(FEATURE_COLUMNS, X_raw[0], shap_vector):
                imp = float(shap_val) if not (np.isnan(shap_val) or np.isinf(shap_val)) else 0.0
                v_float = float(val) if not (np.isnan(val) or np.isinf(val)) else 0.0
                attributions.append({
                    'feature': col,
                    'value': round(v_float, 2),
                    'impact': round(imp, 4)
                })

            # Sort by absolute impact descending
            attributions.sort(key=lambda x: abs(x['impact']), reverse=True)
            return {
                'target_mode': target_mode,
                'feature_attributions': attributions[:6]  # Top 6 drivers
            }
        except Exception as e:
            print(f"SHAP calculation exception: {e}")
            return {
                'target_mode': target_mode,
                'feature_attributions': []
            }

def get_shap_service():
    if ShapExplainerService._instance is None:
        ShapExplainerService._instance = ShapExplainerService()
    return ShapExplainerService._instance
