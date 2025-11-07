# bootstrap.py
from pathlib import Path
import sys, importlib, logging, time, os

def bootstrap(
        project_root: str | Path | None = None,
        *,
        prefix: str = "transformation_pipeline_",
        level: str | int = "INFO",
        purge_packages: bool = True,) -> tuple[logging.Logger, Path]:
        """
        Initialize logging for notebooks or scipts.
        Creates unique log files like:
            transformation_pipeline_YYYYMMDD-HHMMSS_PID####.log        
        """

        pr = Path(project_root) if project_root else Path.cwd()
        if str(pr) not in sys.path:
            sys.path.insert(0, str(pr))

        # Optionally purge previously imported copies (prevents stale modules)
        if purge_packages:
            for m in list(sys.modules):
                if m == "config" or m.startswith("config.") or m == "transformation" or m.startswith("transformation."):
                    del sys.modules[m]

        # ensure logs exists
        logs_dir = pr / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)

        # Build unique logfile name
        now = datetime.datetime.now()
        ts = now.strftime("%Y%m%d_%H%M%S_%f")[:-3] # trim to milliseconds
        pid = os.getpid()
        logfile = logs_dir / f"{prefix}{ts}_PID{pid}.log"


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

        lc.normalize_loggers()
        logger = lc.get_logger(__name__)
        logger.info("Notebook logging initialized")

        return logger, logfile

if __name__ == "__main__":
    lg, path = bootstrap()
    print("Initialized logging to:", path)
    lg.info("bootstrap.py executed directly, writing to {path}")

