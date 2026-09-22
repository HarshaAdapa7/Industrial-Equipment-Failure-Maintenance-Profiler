import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from app.db.supabase_client import Base

def generate_uuid():
    return str(uuid.uuid4())

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    plan_type = Column(String(50), default="Enterprise")
    created_at = Column(DateTime, default=datetime.utcnow)

    machines = relationship("Machine", back_populates="organization", cascade="all, delete-orphan")
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="Technician")
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="users")

class Machine(Base):
    __tablename__ = "machines"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(100), nullable=False)
    product_type = Column(String(10), default="M")  # L, M, or H
    description = Column(Text, nullable=True)
    asset_criticality = Column(Float, default=1.5)  # Multiplier e.g. 1.0 to 3.0
    failure_cost = Column(Float, default=180000.0)  # Estimated cost of unplanned breakdown in $
    pm_cost = Column(Float, default=15000.0)        # Cost of preventive maintenance in $
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="machines")
    readings = relationship("SensorReading", back_populates="machine", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="machine", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="machine", cascade="all, delete-orphan")
    actions = relationship("MaintenanceAction", back_populates="machine", cascade="all, delete-orphan")

class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    machine_id = Column(String(36), ForeignKey("machines.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    air_temp = Column(Float, nullable=False)
    process_temp = Column(Float, nullable=False)
    rpm = Column(Float, nullable=False)
    torque = Column(Float, nullable=False)
    tool_wear = Column(Float, nullable=False)
    derived_features = Column(JSON, nullable=True)

    machine = relationship("Machine", back_populates="readings")

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    machine_id = Column(String(36), ForeignKey("machines.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    any_failure = Column(Boolean, default=False)
    risk_score = Column(Float, nullable=False)
    health_score = Column(Float, nullable=False)
    anomaly_score = Column(Float, nullable=False)
    label_probs = Column(JSON, nullable=False)  # {"TWF": 0.82, "HDF": 0.01, ...}
    shap_values = Column(JSON, nullable=True)   # Top feature attributions

    machine = relationship("Machine", back_populates="predictions")

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    machine_id = Column(String(36), ForeignKey("machines.id"), nullable=False)
    prediction_id = Column(String(36), ForeignKey("predictions.id"), nullable=True)
    alert_type = Column(String(50), nullable=False)  # e.g., TWF, HDF, ANOMALY
    severity = Column(String(20), default="HIGH")    # CRITICAL, HIGH, MODERATE, LOW
    priority_score = Column(Float, default=50.0)     # Calculated cost-weighted score
    message = Column(Text, nullable=False)
    status = Column(String(20), default="ACTIVE")    # ACTIVE, ACKNOWLEDGED, RESOLVED
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    acknowledged_at = Column(DateTime, nullable=True)

    machine = relationship("Machine", back_populates="alerts")

class MaintenanceAction(Base):
    __tablename__ = "maintenance_actions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    machine_id = Column(String(36), ForeignKey("machines.id"), nullable=False)
    alert_id = Column(String(36), ForeignKey("alerts.id"), nullable=True)
    action_taken = Column(Text, nullable=False)
    performed_by = Column(String(100), default="Maintenance Tech")
    cost = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow)
    result = Column(String(50), default="SUCCESS")

    machine = relationship("Machine", back_populates="actions")
