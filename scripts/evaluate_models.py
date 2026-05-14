"""
Simple offline evaluation entry-point.
"""
from pathlib import Path
import sys
BACKEND_DIR = Path(__file__).resolve().parents[1] / "apps" / "backend"
sys.path.append(str(BACKEND_DIR))
from app.services.inference.registry import detector_registry

if __name__ == "__main__":
    detector_registry.load_builtin_detectors()
    print("Loaded models:", detector_registry.list_keys())
    print("Extend this script with offline benchmarks or threshold sweeps.")
