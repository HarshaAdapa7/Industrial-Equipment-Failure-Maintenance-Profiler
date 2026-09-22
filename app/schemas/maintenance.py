from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MaintenanceActionCreate(BaseModel):
    machine_id: str
    alert_id: Optional[str] = None
    action_taken: str
    performed_by: Optional[str] = "Technician"
    cost: float = 0.0

class MaintenanceActionResponse(BaseModel):
    id: str
    machine_id: str
    alert_id: Optional[str] = None
    action_taken: str
    performed_by: str
    cost: float
    timestamp: datetime
    result: str

    class Config:
        from_attributes = True
