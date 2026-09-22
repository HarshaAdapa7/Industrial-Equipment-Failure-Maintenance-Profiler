from fastapi import APIRouter
from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.ml.model_loader import get_model_service
from app.ml.shap_explainer import get_shap_service

router = APIRouter(prefix="/predict", tags=["ML Predictions & Explainability"])

@router.post("/anomaly")
def predict_anomaly(req: PredictionRequest):
    model_service = get_model_service()
    reading_dict = req.model_dump()
    res = model_service.predict_reading(reading_dict)
    return {
        "anomaly_score": res['anomaly_score'],
        "is_anomaly": res['is_anomaly']
    }

@router.post("/failure", response_model=PredictionResponse)
def predict_failure(req: PredictionRequest):
    model_service = get_model_service()
    shap_service = get_shap_service()
    reading_dict = req.model_dump()

    res = model_service.predict_reading(reading_dict)
    shap_res = shap_service.explain_prediction(reading_dict)

    return PredictionResponse(
        any_failure=res['any_failure'],
        risk_score=res['risk_score'],
        health_score=res['health_score'],
        anomaly_score=res['anomaly_score'],
        label_probs=res['label_probs'],
        shap_values=shap_res.get('feature_attributions', [])
    )

@router.post("/explain")
def explain_prediction(req: PredictionRequest):
    shap_service = get_shap_service()
    reading_dict = req.model_dump()
    return shap_service.explain_prediction(reading_dict)
