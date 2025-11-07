# driver.py
from pathlib import Path
import sys

# --- Ensure your project root is on sys.path so imports work ---
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# --- Import and call your bootstrap function ---
from bootstrap import bootstrap

logger, logpath = bootstrap(unique=True, level="INFO")
logger.info(f"Driver initialized. Writing logs to: {logpath}")

# --- Import your pipeline class ---
from transformation.pipeline import CrashDataPipeline

# --- Run the pipeline ---
pipe = CrashDataPipeline("traffic_crashes.csv", "traffic_crash_vehicle.csv")
pipe.run()

logger.info("Pipeline completed.")
