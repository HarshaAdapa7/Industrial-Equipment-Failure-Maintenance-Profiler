from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class AgentDiagnoseRequest(BaseModel):
    machine_id: str

class AgentDiagnoseResponse(BaseModel):
    machine_id: str
    machine_name: str
    alert_priority: str
    risk_score: float
    health_score: float
    primary_failure_mode: str
    primary_failure_prob: float
    recommendation: str
    action_steps: List[str]
    supporting_sops: List[Dict[str, Any]]
    expected_cost_analysis: Dict[str, Any]
    shap_top_drivers: List[Dict[str, Any]]
