from pathlib import Path
import sys
BACKEND_DIR = Path(__file__).resolve().parents[1] / "apps" / "backend"
sys.path.append(str(BACKEND_DIR))
from app.core.database import init_db, SessionLocal
from app.services.inference.registry import detector_registry


def main():
    init_db()
    detector_registry.load_builtin_detectors()
    db = SessionLocal()
    try:
        detector_registry.sync_registry_to_database(db)
    finally:
        db.close()
    print("Seeded database successfully.")

if __name__ == "__main__":
    main()
