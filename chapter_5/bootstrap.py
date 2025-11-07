# bootstrap.py
from pathlib import Path
import sys
import importlib
import logging
import time
import os

def bootstrap(project_root: str | Path | None = None,
              logfile: str | Path | None = None,
              *,
              unique: bool = False,
              level: str | int = "INFO",
              purge_packages: bool = True):
    """
    Notebook-friendly bootstrap:
      - ensures project_root on sys.path
      - (optionally) purges old imports of config/transformation
      - closes stale handlers
      - configures logging to chosen file (optionally unique per run)
      - normalizes logger hierarchy
    Returns: (logger, resolved_logfile_path)
    """
    pr = Path(project_root) if project_root else Path.cwd()
    if str(pr) not in sys.path:
        sys.path.insert(0, str(pr))

    # Optionally purge previously imported copies (prevents stale modules)
    if purge_packages:
        for m in list(sys.modules):
            if m == "config" or m.startswith("config.") or m == "transformation" or m.startswith("transformation."):
                del sys.modules[m]

    # Close any existing handlers before configuring
    root = logging.getLogger()
    for h in list(root.handlers):
        try:
            h.flush(); h.close()
        except Exception:
            pass
        root.removeHandler(h)

    import config.log_config as lc
    importlib.invalidate_caches()
    importlib.reload(lc)

    # Decide logfile
    if logfile is None:
        logfile = pr / "logs" / "etl_DEV.log"
    else:
        logfile = Path(logfile)
        if not logfile.is_absolute():
            logfile = (pr / logfile).resolve()

    if unique:
        ts = time.strftime("%Y%m%d-%H%M%S")
        pid = os.getpid()
        logfile = logfile.with_name(f"{logfile.stem}_{ts}_{pid}{logfile.suffix}")

    resolved = lc.log_config(logfile, level=level)
    lc.normalize_loggers()
    logger = lc.get_logger(__name__)
    logger.info("Notebook logging initialized")

    return logger, resolved

if __name__ == "__main__":
    lg, path = bootstrap(unique=True, level="INFO")
    print("Initialized logging to:", path)
    lg.info("bootstrap.py executed as a script")
