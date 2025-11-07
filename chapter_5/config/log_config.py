# config/log_config.py
from pathlib import Path
import os
import logging
import logging.config

def _resolve_logfile(project_root: Path, log_path: str | Path | None) -> Path:
    """Resolve the final logfile path, ensuring parent dir exists."""
    if log_path is not None:
        p = Path(log_path)
        logfile = p if p.is_absolute() else (project_root / p).resolve()
    else:
        logs_dir = (project_root / "logs").resolve()
        logfile = logs_dir / "etl_pipeline.log"
    logfile.parent.mkdir(parents=True, exist_ok=True)
    return logfile

def _coerce_level(level: int | str) -> int:
    if isinstance(level, int):
        return level
    level = str(level).upper()
    return getattr(logging, level, logging.INFO)

def log_config(log_path: str | Path | None = None, level: int | str = "INFO") -> Path:
    """
    Configure root logging with a console + rotating file handler.
    Safe to call multiple times in Jupyter; closes old handlers first.

    Args:
        log_path: explicit file path (relative paths are resolved against project root).
        level: e.g., "INFO", "DEBUG", or a numeric level.
    Returns:
        Path to the resolved logfile.
    """
    project_root = Path(__file__).resolve().parents[1]
    logfile = _resolve_logfile(project_root, log_path)
    level_num = _coerce_level(level)

    # Close & remove existing root handlers (critical for notebooks)
    root = logging.getLogger()
    for h in list(root.handlers):
        try:
            h.flush(); h.close()
        except Exception:
            pass
        root.removeHandler(h)

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "brief":    {"format": "%(levelname)s | %(message)s"},
            "standard": {"format": "%(asctime)s | %(levelname)-8s | pid=%(process)d | %(name)s | %(message)s"},
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": level_num,
                "formatter": "brief",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": level_num,
                "formatter": "standard",
                "filename": str(logfile),
                "maxBytes": 2_000_000,
                "backupCount": 3,
                "encoding": "utf-8",
                "delay": True,
            },
        },
        "root": {"level": level_num, "handlers": ["console", "file"]},
    }

    logging.config.dictConfig(LOGGING)
    logging.getLogger(__name__).info(f"Logging to {logfile}")
    return logfile

def normalize_loggers() -> None:
    """
    Make all existing named loggers inherit root handlers/levels.
    Prevents swallowed logs in Jupyter.
    """
    for name, obj in list(logging.Logger.manager.loggerDict.items()):
        if isinstance(obj, logging.PlaceHolder):
            continue
        for h in list(getattr(obj, "handlers", [])):
            obj.removeHandler(h)          # drop per-logger handlers
        obj.setLevel(logging.NOTSET)      # inherit effective level
        obj.propagate = True              # bubble to root

def get_logger(name: str | None = None) -> logging.Logger:
    """
    Safe getter that ensures children inherit root configuration.
    """
    if not logging.getLogger().handlers:
        log_config()  # configure with defaults if nothing exists
    lg = logging.getLogger(name)
    lg.setLevel(logging.NOTSET)
    lg.propagate = True
    for h in list(lg.handlers):
        lg.removeHandler(h)
    return lg