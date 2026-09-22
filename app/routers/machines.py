from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.db.supabase_client import get_db
from app.db.models import Machine, SensorReading, Prediction

router = APIRouter(prefix="/machines", tags=["Machines"])

class MachineCreate(BaseModel):
    name: str
    product_type: str = "M"
    description: Optional[str] = "CNC Milling Machine"
    asset_criticality: float = 1.5
    failure_cost: float = 180000.0
    pm_cost: float = 15000.0

@router.get("")
def list_machines(org_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Machine)
    if org_id:
        query = query.filter(Machine.org_id == org_id)
    machines = query.all()

    results = []
    for m in machines:
        latest_pred = db.query(Prediction).filter(Prediction.machine_id == m.id).order_by(Prediction.timestamp.desc()).first()
        results.append({
            "id": m.id,
            "name": m.name,
            "product_type": m.product_type,
            "description": m.description,
            "asset_criticality": m.asset_criticality,
            "failure_cost": m.failure_cost,
            "pm_cost": m.pm_cost,
            "current_health": latest_pred.health_score if latest_pred else 100.0,
            "current_risk": latest_pred.risk_score if latest_pred else 0.0,
            "status": "CRITICAL" if (latest_pred and latest_pred.risk_score >= 75) else ("WARNING" if (latest_pred and latest_pred.risk_score >= 40) else "HEALTHY")
        })
    return results

@router.get("/{id}")
def get_machine_detail(id: str, db: Session = Depends(get_db)):
    machine = db.query(Machine).filter(Machine.id == id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    latest_pred = db.query(Prediction).filter(Prediction.machine_id == id).order_by(Prediction.timestamp.desc()).first()
    recent_readings = db.query(SensorReading).filter(SensorReading.machine_id == id).order_by(SensorReading.timestamp.desc()).limit(20).all()

    return {
        "id": machine.id,
        "name": machine.name,
        "product_type": machine.product_type,
        "description": machine.description,
        "asset_criticality": machine.asset_criticality,
        "failure_cost": machine.failure_cost,
        "pm_cost": machine.pm_cost,
        "latest_prediction": {
            "risk_score": latest_pred.risk_score if latest_pred else 0.0,
            "health_score": latest_pred.health_score if latest_pred else 100.0,
            "anomaly_score": latest_pred.anomaly_score if latest_pred else 0.0,
            "label_probs": latest_pred.label_probs if latest_pred else {"TWF": 0, "HDF": 0, "PWF": 0, "OSF": 0, "RNF": 0},
            "shap_values": latest_pred.shap_values if latest_pred else []
        } if latest_pred else None,
        "recent_readings": [
            {
                "timestamp": r.timestamp.isoformat(),
                "air_temp": r.air_temp,
                "process_temp": r.process_temp,
                "rpm": r.rpm,
                "torque": r.torque,
                "tool_wear": r.tool_wear
            } for r in reversed(recent_readings)
        ]
    }

@router.post("")
def create_machine(req: MachineCreate, org_id: Optional[str] = "org_default", db: Session = Depends(get_db)):
    machine = Machine(
        org_id=org_id,
        name=req.name,
        product_type=req.product_type,
        description=req.description,
        asset_criticality=req.asset_criticality,
        failure_cost=req.failure_cost,
        pm_cost=req.pm_cost
    )
    db.add(machine)
    db.commit()
    db.refresh(machine)
    return machine
