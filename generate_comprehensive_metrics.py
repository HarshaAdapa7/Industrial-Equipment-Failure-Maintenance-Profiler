import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, precision_recall_curve, auc
from xgboost import XGBClassifier
from app.ml.feature_engineering import compute_physics_features, TARGET_FAILURE_MODES, FEATURE_COLUMNS

def evaluate_models():
    df = pd.read_csv('app/data/ai4i2020.csv')
    X = compute_physics_features(df)[FEATURE_COLUMNS]
    y = df[TARGET_FAILURE_MODES]

    print("=== DATASET EDA MATRIX ===")
    print("Total Records:", len(df))
    print("Features Count:", X.shape[1])
    print("Missing Values:", df.isnull().sum().sum())

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42, stratify=df['Machine failure'])
    print(f"Train Set: {X_train.shape[0]} | Test Set: {X_test.shape[0]}")

    results = []

    for target in TARGET_FAILURE_MODES:
        y_tr = y_train[target]
        y_te = y_test[target]

        pos_count = y_tr.sum()
        neg_count = len(y_tr) - pos_count
        spw = (neg_count / max(1, pos_count)) * 1.5

        xgb = XGBClassifier(n_estimators=100, max_depth=5, scale_pos_weight=spw, random_state=42, eval_metric='logloss')
        xgb.fit(X_train, y_tr)
        xgb_preds = xgb.predict(X_test)
        xgb_probs = xgb.predict_proba(X_test)[:, 1]

        cm = confusion_matrix(y_te, xgb_preds)
        tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (len(y_te)-y_te.sum(), 0, y_te.sum(), 0)

        rec = tp / max(1, (tp + fn))
        prec = tp / max(1, (tp + fp))
        f1 = 2 * (prec * rec) / max(1e-6, (prec + rec))
        roc = roc_auc_score(y_te, xgb_probs) if len(np.unique(y_te)) > 1 else 0.5
        p, r, _ = precision_recall_curve(y_te, xgb_probs)
        pr_auc = auc(r, p)

        results.append({
            'Target': target,
            'Model': 'XGBoost (Weighted)',
            'TN': tn, 'FP': fp, 'FN': fn, 'TP': tp,
            'Recall': round(rec, 4),
            'Precision': round(prec, 4),
            'F1': round(f1, 4),
            'ROC-AUC': round(roc, 4),
            'PR-AUC': round(pr_auc, 4)
        })

    res_df = pd.DataFrame(results)
    print("\n=== MODEL PERFORMANCE METRICS TABLE ===")
    print(res_df.to_string(index=False))

if __name__ == '__main__':
    evaluate_models()
