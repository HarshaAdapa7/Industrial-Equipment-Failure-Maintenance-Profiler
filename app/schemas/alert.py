from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AlertBase(BaseModel):
    machine_id: str
    alert_type: str
    severity: str
    priority_score: float
    message: str

class AlertCreate(AlertBase):
    prediction_id: Optional[str] = None

class AlertAcknowledgeRequest(BaseModel):
    acknowledged_by: Optional[str] = "Technician"
    user_comment: Optional[str] = "Acknowledged alert and inspecting machine."

class AlertResponse(AlertBase):
    id: str
    prediction_id: Optional[str] = None
    status: str
    created_at: datetime
    acknowledged_at: Optional[datetime] = None

    class Config:
        from_attributes = True
