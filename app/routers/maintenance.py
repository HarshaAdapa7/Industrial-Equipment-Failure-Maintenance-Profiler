from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from app.db.supabase_client import get_db
from app.db.models import MaintenanceAction, Machine, Alert, Prediction
from app.schemas.maintenance import MaintenanceActionCreate

router = APIRouter(prefix="/maintenance", tags=["Maintenance & Financial ROI"])

@router.post("/actions")
def log_maintenance_action(req: MaintenanceActionCreate, db: Session = Depends(get_db)):
    machine = db.query(Machine).filter(Machine.id == req.machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    action = MaintenanceAction(
        machine_id=req.machine_id,
        alert_id=req.alert_id,
        action_taken=req.action_taken,
        performed_by=req.performed_by or "Technician",
        cost=req.cost,
        result="SUCCESS"
    )
    db.add(action)

    # If alert specified, mark alert as RESOLVED
    if req.alert_id:
        alert = db.query(Alert).filter(Alert.id == req.alert_id).first()
        if alert:
            alert.status = "RESOLVED"

    # Reset machine predictions to healthy status
    latest_pred = db.query(Prediction).filter(Prediction.machine_id == req.machine_id).order_by(Prediction.timestamp.desc()).first()
    if latest_pred:
        latest_pred.risk_score = 5.0
        latest_pred.health_score = 95.0
        latest_pred.any_failure = False
        latest_pred.anomaly_score = 0.1

    db.commit()
    db.refresh(action)

    return {"ok": True, "action_id": action.id, "message": "Maintenance action logged and asset health restored."}

@router.get("/summary")
def get_maintenance_summary(db: Session = Depends(get_db)):
    actions = db.query(MaintenanceAction, Machine).join(Machine, MaintenanceAction.machine_id == Machine.id).all()

    total_actions = len(actions)
    total_pm_cost = sum(a.cost for a, m in actions)

    # Calculate prevented failure savings
    total_prevented_cost = sum(m.failure_cost for a, m in actions)
    net_roi_savings = max(0.0, total_prevented_cost - total_pm_cost)

    action_list = []
    for a, m in actions:
        action_list.append({
            "id": a.id,
            "machine_id": m.id,
            "machine_name": m.name,
            "action_taken": a.action_taken,
            "performed_by": a.performed_by,
            "cost": a.cost,
            "timestamp": a.timestamp.isoformat(),
            "result": a.result
        })

    return {
        "total_actions": total_actions,
        "total_pm_cost": round(total_pm_cost, 2),
        "total_prevented_downtime_cost": round(total_prevented_cost, 2),
        "net_roi_savings": round(net_roi_savings, 2),
        "actions_history": action_list
    }
