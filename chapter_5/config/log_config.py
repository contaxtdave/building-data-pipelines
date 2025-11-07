# config/log_config.py
from pathlib import Path
import logging, logging.config

def log_config(log_path: str | Path, level: int | str = "INFO") -> Path:
    """
    Configure root logging to the explicit log_path.
    No default path; nothing happens unless you call this.
    """
    logfile = Path(log_path).resolve()
    logfile.parent.mkdir(parents=True, exist_ok=True)

    level_num = getattr(logging, str(level).upper(), logging.INFO)

    # Hard reset handlers (important for notebooks and re-runs)
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
            "standard": {"format": "%(asctime)s | %(levelname)-8s | pid=%(process)d | %(name)s | %(funcName)s | %(message)s"},
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
    """Make all existing named loggers inherit the root handlers/levels."""
    for name, obj in list(logging.Logger.manager.loggerDict.items()):
        if isinstance(obj, logging.PlaceHolder):
            continue
        # keep NullHandlers on children; drop real handlers so root handles output
        for h in list(getattr(obj, "handlers", [])):
            if not isinstance(h, logging.NullHandler):
                obj.removeHandler(h)
        obj.setLevel(logging.NOTSET)
        obj.propagate = True

def get_logger(name: str | None = None) -> logging.Logger:
    """
    Get a logger without configuring root.
    If root isn't configured yet, attach a NullHandler so we don't create files.
    """
    root = logging.getLogger()
    lg = logging.getLogger(name)
    if not root.handlers and not any(isinstance(h, logging.NullHandler) for h in lg.handlers):
        lg.addHandler(logging.NullHandler())
    lg.setLevel(logging.NOTSET)
    lg.propagate = True
    # remove any non-null direct handlers so root config wins later
    for h in list(lg.handlers):
        if not isinstance(h, logging.NullHandler):
            lg.removeHandler(h)
    return lg
