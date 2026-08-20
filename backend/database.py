# backend/database.py
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

# Load environment
project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

# Use a fixed path in the project root
DB_PATH = project_root / "data" / "prafgid.db"
DB_PATH.parent.mkdir(exist_ok=True)

DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"

connect_args = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Auto-create tables if they don't exist
def ensure_tables():
    from backend.models import Base
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1 FROM intelligence_items LIMIT 1"))
    except OperationalError:
        print("⚠️  Table 'intelligence_items' not found. Creating now...")
        Base.metadata.create_all(engine)
        print("✅ Tables created.")

ensure_tables()