# backend/database.py
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Always use a local SQLite file in the 'data' folder
project_root = Path(__file__).parent.parent
data_dir = project_root / "data"
data_dir.mkdir(exist_ok=True)

# Construct absolute path for SQLite
db_path = data_dir / "prafgid.db"
DATABASE_URL = f"sqlite:///{db_path.as_posix()}"

# SQLite needs check_same_thread=False
connect_args = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def ensure_tables():
    from backend.models import Base
    from sqlalchemy.exc import OperationalError
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1 FROM intelligence_items LIMIT 1"))
    except OperationalError:
        print("Creating tables...")
        Base.metadata.create_all(engine)

ensure_tables()