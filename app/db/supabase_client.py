import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from supabase import create_client, Client
from app.config import settings

# 1. Initialize Supabase Client
supabase_client: Client = None
try:
    if settings.SUPABASE_URL and "your-supabase-project" not in settings.SUPABASE_URL:
        supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        print(f"Supabase REST client initialized for {settings.SUPABASE_URL}")
except Exception as e:
    print(f"Notice: Supabase REST client init notice: {e}")

# 2. Initialize SQLAlchemy Engine with Graceful Connection Retry & Fallback
db_url = settings.DATABASE_URL
engine = None

if "[YOUR-PASSWORD]" in db_url or "YOUR_PASSWORD" in db_url:
    print("Notice: Supabase PostgreSQL password placeholder detected in DATABASE_URL. Using local database.")
    db_url = "sqlite:///./predictsense_local.db"

def init_db_engine(url):
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    eng = create_engine(url, connect_args=connect_args, pool_pre_ping=True)
    # Test connection
    try:
        with eng.connect() as conn:
            print(f"Database connected successfully via: {url.split('@')[-1] if '@' in url else url}")
        return eng
    except Exception as err:
        print(f"Notice: Could not connect to primary database URL ({err}). Falling back to local SQLite database...")
        fallback_url = "sqlite:///./predictsense_local.db"
        return create_engine(fallback_url, connect_args={"check_same_thread": False})

engine = init_db_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
