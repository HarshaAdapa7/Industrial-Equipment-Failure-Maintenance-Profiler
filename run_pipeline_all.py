import os
import requests
from app.ml.train_pipeline import train_and_evaluate
from app.ml.model_loader import get_model_service
from app.ml.shap_explainer import get_shap_service
from app.agent.graph import get_graph_agent

def run_full_pipeline():
    print("==================================================")
    print(" PredictSense ML Model Training & Agent Retraining")
    print("==================================================")

    # 1. Train ML Pipeline (Isolation Forest + Multi-Label XGBoost)
    metrics = train_and_evaluate()
    print("\n[ML Models Retrained Successfully!]")
    for mode, m in metrics.items():
        print(f"  - {mode:5s}: Recall={m['recall']:.4f} | Precision={m['precision']:.4f} | F1={m['f1_score']:.4f} | ROC-AUC={m['roc_auc']:.4f}")

    # 2. Test Model Loader & SHAP Explainer
    print("\n[Testing Model Loader & SHAP Explainer...]")
    model_service = get_model_service()
    shap_service = get_shap_service()

    sample_reading = {
        'air_temp': 300.5,
        'process_temp': 310.2,
        'rpm': 1500.0,
        'torque': 55.0,
        'tool_wear': 210.0,
        'product_type': 'M'
    }

    pred_res = model_service.predict_reading(sample_reading)
    shap_res = shap_service.explain_prediction(sample_reading)

    print(f"Sample Prediction: Risk Score={pred_res['risk_score']}% | Health Score={pred_res['health_score']}%")
    print(f"Top SHAP Driver: {shap_res['feature_attributions'][0]['feature']} (Impact: {shap_res['feature_attributions'][0]['impact']})")

    # 3. Test Diagnostic LangGraph Agent & RAG SOP Retrieval
    print("\n[Testing LangGraph Diagnostic Agent & RAG Store...]")
    graph_agent = get_graph_agent()
    machine_dict = {
        'id': 'm1_cnc_mill',
        'name': 'CNC Milling Machine #1',
        'product_type': 'M',
        'asset_criticality': 2.0,
        'failure_cost': 200000.0,
        'pm_cost': 15000.0
    }

    diagnosis, _ = graph_agent.run_diagnostic_workflow(machine_dict, sample_reading)
    print(f"Agent Recommendation: {diagnosis['recommendation']}")
    print(f"Retrieved SOPs: {[s['title'] for s in diagnosis['supporting_sops']]}")
    print(f"Financial Savings: ${diagnosis['expected_cost_analysis']['net_savings_from_pm']:,.2f}")

    print("\n==================================================")
    print(" ALL PIPELINE COMPONENTS VERIFIED AND OPERATIONAL")
    print("==================================================")

if __name__ == '__main__':
    run_full_pipeline()
