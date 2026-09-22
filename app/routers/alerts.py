from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from app.db.supabase_client import get_db
from app.db.models import Alert, Machine
from app.schemas.alert import AlertAcknowledgeRequest, AlertResponse

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("")
def list_alerts(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Alert, Machine).join(Machine, Alert.machine_id == Machine.id)
    if status:
        query = query.filter(Alert.status == status)

    query = query.order_by(Alert.priority_score.desc(), Alert.created_at.desc())
    results = query.all()

    alert_list = []
    for alert, machine in results:
        alert_list.append({
            "id": alert.id,
            "machine_id": machine.id,
            "machine_name": machine.name,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "priority_score": alert.priority_score,
            "message": alert.message,
            "status": alert.status,
            "created_at": alert.created_at.isoformat(),
            "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None
        })
    return alert_list

@router.post("/{id}/ack")
def acknowledge_alert(id: str, req: AlertAcknowledgeRequest, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = "ACKNOWLEDGED"
    alert.acknowledged_at = datetime.utcnow()
    db.commit()

    return {"ok": True, "alert_id": id, "status": "ACKNOWLEDGED"}
