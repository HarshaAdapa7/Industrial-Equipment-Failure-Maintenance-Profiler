from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class SensorReadingBase(BaseModel):
    air_temp: float = Field(..., example=300.5, description="Air temperature in Kelvin")
    process_temp: float = Field(..., example=310.2, description="Process temperature in Kelvin")
    rpm: float = Field(..., example=1500.0, description="Rotational speed in RPM")
    torque: float = Field(..., example=55.0, description="Torque in Nm")
    tool_wear: float = Field(..., example=180.0, description="Tool wear in minutes")
    product_type: Optional[str] = Field("M", example="M", description="Product Type (L, M, H)")

class SensorReadingCreate(SensorReadingBase):
    machine_id: str

class SensorReadingResponse(SensorReadingBase):
    id: str
    machine_id: str
    timestamp: datetime
    derived_features: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
