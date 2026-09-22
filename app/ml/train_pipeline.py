import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report, recall_score, precision_score, f1_score, roc_auc_score
from xgboost import XGBClassifier

from app.ml.feature_engineering import compute_physics_features, FEATURE_COLUMNS, TARGET_FAILURE_MODES

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), 'artifacts')
MODEL_PATH = os.path.join(ARTIFACTS_DIR, 'predictsense_models.joblib')

def train_and_evaluate():
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ai4i2020.csv')
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset not found at {data_path}. Please create it first.")

    df = pd.read_csv(data_path)
    print(f"Loaded dataset with {len(df)} records.")

    # 1. Feature Engineering
    X_df = compute_physics_features(df)
    y_any = df['Machine failure'].values
    y_multi = df[TARGET_FAILURE_MODES]

    # 2. Train/Test Split (70/15/15)
    X_train, X_temp, y_train_any, y_temp_any = train_test_split(
        X_df, y_any, test_size=0.30, random_state=42, stratify=y_any
    )
    X_val, X_test, y_val_any, y_test_any = train_test_split(
        X_temp, y_temp_any, test_size=0.50, random_state=42, stratify=y_temp_any
    )

    y_train_multi = y_multi.iloc[X_train.index]
    y_test_multi = y_multi.iloc[X_test.index]

    # 3. Fit StandardScaler
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 4. Train Unsupervised Isolation Forest (trained on normal records only)
    normal_indices = (y_train_any == 0)
    iso_forest = IsolationForest(
        n_estimators=150, contamination=0.05, random_state=42, n_jobs=-1
    )
    iso_forest.fit(X_train_scaled[normal_indices])

    # Isolation forest anomaly score evaluation on test set
    test_anomaly_scores = iso_forest.score_samples(X_test_scaled)
    # Convert raw score to [0, 1] normalized anomaly probability
    test_anomaly_probs = 1.0 / (1.0 + np.exp(test_anomaly_scores * 4.0))

    print("\n--- Unsupervised Isolation Forest Evaluated ---")
    print(f"Mean Normal Anomaly Prob: {np.mean(test_anomaly_probs[y_test_any == 0]):.4f}")
    print(f"Mean Failure Anomaly Prob: {np.mean(test_anomaly_probs[y_test_any == 1]):.4f}")

    # 5. Train Supervised Multi-Label Failure Mode Classifiers (XGBoost)
    failure_models = {}
    metrics_summary = {}

    print("\n--- Training Failure Mode Classifiers (XGBoost) ---")
    for target in TARGET_FAILURE_MODES:
        y_tr = y_train_multi[target].values
        y_te = y_test_multi[target].values

        # Calculate imbalance weight
        neg_count = (y_tr == 0).sum()
        pos_count = (y_tr == 1).sum()
        scale_pos_weight = (neg_count / max(1, pos_count)) * 1.5

        clf = XGBClassifier(
            n_estimators=150,
            max_depth=5,
            learning_rate=0.08,
            scale_pos_weight=scale_pos_weight,
            random_state=42,
            eval_metric='logloss'
        )
        clf.fit(X_train_scaled, y_tr)
        failure_models[target] = clf

        # Evaluate
        preds_prob = clf.predict_proba(X_test_scaled)[:, 1]
        preds_bin = (preds_prob >= 0.40).astype(int)

        rec = recall_score(y_te, preds_bin, zero_division=0)
        prec = precision_score(y_te, preds_bin, zero_division=0)
        f1 = f1_score(y_te, preds_bin, zero_division=0)
        try:
            auc = roc_auc_score(y_te, preds_prob)
        except Exception:
            auc = 0.5

        metrics_summary[target] = {
            'recall': round(float(rec), 4),
            'precision': round(float(prec), 4),
            'f1_score': round(float(f1), 4),
            'roc_auc': round(float(auc), 4),
            'positive_samples': int(pos_count)
        }
        print(f"Target: {target:5s} | Recall: {rec:.4f} | Precision: {prec:.4f} | F1: {f1:.4f} | ROC-AUC: {auc:.4f}")

    # 6. Save Artifacts
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    artifacts = {
        'scaler': scaler,
        'isolation_forest': iso_forest,
        'failure_models': failure_models,
        'feature_columns': FEATURE_COLUMNS,
        'target_failure_modes': TARGET_FAILURE_MODES,
        'metrics_summary': metrics_summary
    }

    joblib.dump(artifacts, MODEL_PATH)
    print(f"\nModel artifacts successfully saved to {MODEL_PATH}")
    return metrics_summary

if __name__ == '__main__':
    train_and_evaluate()
