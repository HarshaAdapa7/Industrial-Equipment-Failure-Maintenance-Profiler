import asyncio
import os
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.db.supabase_client import SessionLocal, get_db
from app.db.models import Machine
from app.routers.telemetry import ingest_sensor_reading, SensorReadingCreate

router = APIRouter(prefix="/simulator", tags=["Live Simulator & Fault Injection"])

class SimulatorState:
    running = False
    delay_seconds = 1.0
    current_index = 0
    df = None
    task = None

sim_state = SimulatorState()

class FaultInjectionRequest(BaseModel):
    machine_id: str
    fault_type: str  # TWF, HDF, PWF, OSF

def load_simulation_data():
    if sim_state.df is None:
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ai4i2020.csv')
        if os.path.exists(data_path):
            sim_state.df = pd.read_csv(data_path)

async def simulation_loop():
    load_simulation_data()
    if sim_state.df is None or len(sim_state.df) == 0:
        return

    while sim_state.running:
        try:
            row = sim_state.df.iloc[sim_state.current_index % len(sim_state.df)]
            sim_state.current_index += 1

            db = SessionLocal()
            try:
                machine = db.query(Machine).first()
                if machine:
                    req = SensorReadingCreate(
                        machine_id=machine.id,
                        air_temp=float(row['Air temperature [K]']),
                        process_temp=float(row['Process temperature [K]']),
                        rpm=float(row['Rotational speed [rpm]']),
                        torque=float(row['Torque [Nm]']),
                        tool_wear=float(row['Tool wear [min]']),
                        product_type=str(row['Type'])
                    )
                    await ingest_sensor_reading(req, db)
            finally:
                db.close()

            await asyncio.sleep(sim_state.delay_seconds)
        except Exception as e:
            print(f"Simulation loop error: {e}")
            await asyncio.sleep(2.0)

@router.post("/start")
async def start_simulator(speed_delay: Optional[float] = 1.0):
    sim_state.running = True
    sim_state.delay_seconds = max(0.2, speed_delay or 1.0)
    asyncio.create_task(simulation_loop())
    return {"ok": True, "status": "SIMULATOR_RUNNING", "delay_seconds": sim_state.delay_seconds}

@router.post("/pause")
def pause_simulator():
    sim_state.running = False
    return {"ok": True, "status": "SIMULATOR_PAUSED"}

@router.get("/status")
def get_simulator_status():
    return {
        "running": sim_state.running,
        "delay_seconds": sim_state.delay_seconds,
        "current_index": sim_state.current_index
    }

@router.post("/inject-fault")
async def inject_fault(req: FaultInjectionRequest, db: Session = Depends(get_db)):
    machine = db.query(Machine).filter(Machine.id == req.machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    fault_map = {
        "TWF": {"air_temp": 300.0, "process_temp": 311.0, "rpm": 1450.0, "torque": 68.0, "tool_wear": 235.0},
        "HDF": {"air_temp": 302.0, "process_temp": 309.5, "rpm": 1250.0, "torque": 58.0, "tool_wear": 120.0}, # Process - Air < 8.6
        "PWF": {"air_temp": 298.5, "process_temp": 309.0, "rpm": 2850.0, "torque": 75.0, "tool_wear": 140.0}, # Power > 9000W
        "OSF": {"air_temp": 301.0, "process_temp": 312.0, "rpm": 1300.0, "torque": 65.0, "tool_wear": 210.0}  # ToolWear * Torque > 12000
    }

    params = fault_map.get(req.fault_type.upper(), fault_map["TWF"])

    reading_req = SensorReadingCreate(
        machine_id=req.machine_id,
        air_temp=params["air_temp"],
        process_temp=params["process_temp"],
        rpm=params["rpm"],
        torque=params["torque"],
        tool_wear=params["tool_wear"],
        product_type=machine.product_type
    )

    res = await ingest_sensor_reading(reading_req, db)
    return {
        "ok": True,
        "injected_fault": req.fault_type.upper(),
        "result": res
    }
