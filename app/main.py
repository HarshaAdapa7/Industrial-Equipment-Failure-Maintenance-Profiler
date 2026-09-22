from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.supabase_client import Base, engine, SessionLocal
from app.db.models import Organization, Machine
from app.routers import auth, machines, telemetry, predict, alerts, maintenance, simulator, agent
from app.agent.rag_engine import get_rag_store
from app.ml.model_loader import get_model_service

def seed_demo_data():
    db = SessionLocal()
    try:
        # Check if any organization exists
        org = db.query(Organization).first()
        if not org:
            org = Organization(name="Industrial Manufacturing Co.", plan_type="Enterprise")
            db.add(org)
            db.commit()
            db.refresh(org)

        # Check if machines exist
        if db.query(Machine).count() == 0:
            m1 = Machine(
                org_id=org.id,
                name="CNC Milling Machine #1",
                product_type="M",
                description="3-Axis Vertical CNC Milling Center",
                asset_criticality=2.0,
                failure_cost=200000.0,
                pm_cost=15000.0
            )
            m2 = Machine(
                org_id=org.id,
                name="Precision Lathe #2",
                product_type="L",
                description="High Precision Turning Lathe",
                asset_criticality=1.2,
                failure_cost=120000.0,
                pm_cost=10000.0
            )
            m3 = Machine(
                org_id=org.id,
                name="Heavy Industrial Mill #3",
                product_type="H",
                description="Heavy Duty Production Milling Asset",
                asset_criticality=2.8,
                failure_cost=350000.0,
                pm_cost=25000.0
            )
            db.add_all([m1, m2, m3])
            db.commit()
            print("Seeded demo organization and 3 industrial machines.")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables and seed data
    Base.metadata.create_all(bind=engine)
    seed_demo_data()
    # Pre-warm ML models & RAG vector index
    get_model_service()
    get_rag_store()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Configure CORS Middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(machines.router, prefix=settings.API_V1_STR)
app.include_router(telemetry.router, prefix=settings.API_V1_STR)
app.include_router(predict.router, prefix=settings.API_V1_STR)
app.include_router(alerts.router, prefix=settings.API_V1_STR)
app.include_router(maintenance.router, prefix=settings.API_V1_STR)
app.include_router(simulator.router, prefix=settings.API_V1_STR)
app.include_router(agent.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "title": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "ONLINE",
        "docs_url": "/docs"
    }
