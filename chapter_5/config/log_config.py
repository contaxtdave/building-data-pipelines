# config/log_config.py
from pathlib import Path
import logging
import logging.config

def log_config():
    project_root = Path(__file__).resolve().parents[1]
    logs_dir = project_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    logfile = logs_dir / "etl_pipeline.log"

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,

        "formatters": {
            "brief":    {"format": "%(levelname)s | %(message)s"},
            "standard": {"format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"},
        },

        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "brief",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "standard",
                "filename": str(logfile),
                "maxBytes": 2_000_000,
                "backupCount": 3,
                "encoding": "utf-8",
            },
        },

        # Root logger uses only handlers we defined above
        "root": {
            "level": "INFO",
            "handlers": ["console", "file"]
        },
    }

    # On 3.8+, force=True clears earlier handlers (useful in notebooks/VS Code)
    try:
        logging.config.dictConfig({**LOGGING, "force": True})
    except TypeError:
        root = logging.getLogger()
        for h in list(root.handlers):
            root.removeHandler(h)
        logging.config.dictConfig(LOGGING)

    logging.getLogger(__name__).info(f"Logging to {logfile}")
