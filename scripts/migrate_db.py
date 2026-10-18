import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "ai-service"))

from app.db.session import init_db
init_db()
print("DATABASE MIGRATION COMPLETED SUCCESSFULLY")
