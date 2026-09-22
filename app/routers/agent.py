from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.supabase_client import get_db
from app.db.models import Machine, SensorReading
from app.schemas.agent import AgentDiagnoseRequest, AgentDiagnoseResponse
from app.agent.graph import get_graph_agent

router = APIRouter(prefix="/agent", tags=["LangGraph Diagnostic Agent"])

@router.post("/diagnose", response_model=AgentDiagnoseResponse)
def diagnose_machine(req: AgentDiagnoseRequest, db: Session = Depends(get_db)):
    machine = db.query(Machine).filter(Machine.id == req.machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    latest_reading = db.query(SensorReading).filter(SensorReading.machine_id == req.machine_id).order_by(SensorReading.timestamp.desc()).first()

    if not latest_reading:
        # Default baseline reading if no prior readings in DB
        reading_dict = {
            'air_temp': 300.0,
            'process_temp': 310.5,
            'rpm': 1500.0,
            'torque': 42.0,
            'tool_wear': 110.0,
            'product_type': machine.product_type
        }
    else:
        reading_dict = {
            'air_temp': latest_reading.air_temp,
            'process_temp': latest_reading.process_temp,
            'rpm': latest_reading.rpm,
            'torque': latest_reading.torque,
            'tool_wear': latest_reading.tool_wear,
            'product_type': machine.product_type
        }

    machine_dict = {
        'id': machine.id,
        'name': machine.name,
        'product_type': machine.product_type,
        'asset_criticality': machine.asset_criticality,
        'failure_cost': machine.failure_cost,
        'pm_cost': machine.pm_cost
    }

    graph_agent = get_graph_agent()
    diagnosis, _ = graph_agent.run_diagnostic_workflow(machine_dict, reading_dict)

    return AgentDiagnoseResponse(
        machine_id=diagnosis['machine_id'],
        machine_name=diagnosis['machine_name'],
        alert_priority=diagnosis['alert_priority'],
        risk_score=diagnosis['risk_score'],
        health_score=diagnosis['health_score'],
        primary_failure_mode=diagnosis['primary_failure_mode'],
        primary_failure_prob=diagnosis['primary_failure_prob'],
        recommendation=diagnosis['recommendation'],
        action_steps=diagnosis['action_steps'],
        supporting_sops=diagnosis['supporting_sops'],
        expected_cost_analysis=diagnosis['expected_cost_analysis'],
        shap_top_drivers=diagnosis['shap_top_drivers']
    )
