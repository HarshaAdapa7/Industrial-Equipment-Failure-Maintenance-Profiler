from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime

class PredictionRequest(BaseModel):
    air_temp: float
    process_temp: float
    rpm: float
    torque: float
    tool_wear: float
    product_type: Optional[str] = "M"

class PredictionResponse(BaseModel):
    id: Optional[str] = None
    machine_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    any_failure: bool
    risk_score: float
    health_score: float
    anomaly_score: float
    label_probs: Dict[str, float]
    shap_values: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True
