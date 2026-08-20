# init_db.py
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

from backend.database import engine
from backend.models import Base

print("Creating database tables...")
Base.metadata.create_all(engine)
print("✅ Tables created successfully.")