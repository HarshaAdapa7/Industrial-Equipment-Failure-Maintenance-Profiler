from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Dict
import json
from datetime import datetime

from app.db.supabase_client import get_db
from app.db.models import SensorReading, Prediction, Alert, Machine
from app.schemas.telemetry import SensorReadingCreate
from app.ml.model_loader import get_model_service
from app.ml.shap_explainer import get_shap_service

router = APIRouter(tags=["Telemetry Ingestion"])

# WebSocket Manager for real-time dashboard updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

ws_manager = ConnectionManager()

@router.post("/readings")
async def ingest_sensor_reading(req: SensorReadingCreate, db: Session = Depends(get_db)):
    machine = db.query(Machine).filter(Machine.id == req.machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine ID not found")

    reading_dict = {
        'air_temp': req.air_temp,
        'process_temp': req.process_temp,
        'rpm': req.rpm,
        'torque': req.torque,
        'tool_wear': req.tool_wear,
        'product_type': req.product_type or machine.product_type
    }

    # Run ML Inference & SHAP explanation
    model_service = get_model_service()
    shap_service = get_shap_service()

    pred_res = model_service.predict_reading(reading_dict)
    shap_res = shap_service.explain_prediction(reading_dict)

    # Save Sensor Reading
    reading = SensorReading(
        machine_id=req.machine_id,
        air_temp=req.air_temp,
        process_temp=req.process_temp,
        rpm=req.rpm,
        torque=req.torque,
        tool_wear=req.tool_wear,
        derived_features=pred_res['features']
    )
    db.add(reading)
    db.commit()
    db.refresh(reading)

    # Save Prediction Result
    prediction = Prediction(
        machine_id=req.machine_id,
        any_failure=pred_res['any_failure'],
        risk_score=pred_res['risk_score'],
        health_score=pred_res['health_score'],
        anomaly_score=pred_res['anomaly_score'],
        label_probs=pred_res['label_probs'],
        shap_values=shap_res.get('feature_attributions', [])
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    # Automatic Alert Triggering logic
    triggered_alert = None
    if pred_res['risk_score'] >= 50.0 or pred_res['is_anomaly']:
        # Pick primary failure mode
        sorted_modes = sorted(pred_res['label_probs'].items(), key=lambda x: x[1], reverse=True)
        primary_mode, prob = sorted_modes[0]

        severity = "CRITICAL" if pred_res['risk_score'] >= 75.0 else "HIGH"
        priority_score = min(100.0, pred_res['risk_score'] * machine.asset_criticality)

        message = f"High Risk Alert: {primary_mode} predicted with {prob*100:.0f}% probability on {machine.name}."

        existing_active = db.query(Alert).filter(
            Alert.machine_id == req.machine_id, Alert.status == "ACTIVE"
        ).first()

        if not existing_active:
            triggered_alert = Alert(
                machine_id=req.machine_id,
                prediction_id=prediction.id,
                alert_type=primary_mode if prob > 0.40 else "ANOMALY",
                severity=severity,
                priority_score=priority_score,
                message=message
            )
            db.add(triggered_alert)
            db.commit()

    # Broadcast via WebSockets
    payload = {
        "event": "telemetry_update",
        "machine_id": req.machine_id,
        "timestamp": reading.timestamp.isoformat(),
        "telemetry": reading_dict,
        "prediction": pred_res,
        "shap": shap_res.get('feature_attributions', []),
        "alert": {
            "id": triggered_alert.id,
            "message": triggered_alert.message,
            "severity": triggered_alert.severity,
            "priority_score": triggered_alert.priority_score
        } if triggered_alert else None
    }
    await ws_manager.broadcast(payload)

    return {
        "ok": True,
        "reading_id": reading.id,
        "prediction_id": prediction.id,
        "risk_score": pred_res['risk_score'],
        "health_score": pred_res['health_score'],
        "any_failure": pred_res['any_failure']
    }

@router.websocket("/ws/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
