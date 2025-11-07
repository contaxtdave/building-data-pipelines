# transformation/pipeline.py
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence, Tuple, Any, Iterable, Optional
import pandas as pd
from config.log_config import get_logger

OK = "<OK>"
FAILED = "<FAILED>"
NOT_EXEC = "<NOT_EXECUTED>"

@dataclass
class StepSpec:
    status_attr: str                      # e.g., "READING_CRASH_DATA_PIPELINE"
    fn: Callable[[], Tuple[Any, ...]]     # returns (*payload, status)
    assign_attrs: Sequence[str]           # names on self to receive payload

class CrashDataPipeline:
    """Encapsulates the crash data transformation pipeline."""

    def __init__(
        self,
        crash_file: str,
        vehicle_file: str,
        data_dir: Optional[Path | str] = None,
        logger_name: Optional[str] = None,
    ):
        self.crash_file = crash_file
        self.vehicle_file = vehicle_file
        self.data_dir = Path(data_dir) if data_dir else None

        # working frames
        self.df_crash: Optional[pd.DataFrame] = None
        self.df_vehicle: Optional[pd.DataFrame] = None
        self.df_agg: Optional[pd.DataFrame] = None
        self.df_output: Optional[pd.DataFrame] = None

        # named step statuses (for compatibility)
        self.READING_CRASH_DATA_PIPELINE = NOT_EXEC
        self.DROPPING_ROW_WITH_NULL_PIPELINE = NOT_EXEC
        self.FILLING_MISSING_VALUE_PIPELINE = NOT_EXEC
        self.MERGE_DATA_FRAME_PIPELINE = NOT_EXEC
        self.FORMAT_DATAFRAME_PIPELINE = NOT_EXEC

        self.logger = get_logger(logger_name or self.__class__.__name__)

    # -------------------- utilities --------------------
    def _resolve_path(self, sourcefile: str) -> Path:
        if self.data_dir:
            return Path(self.data_dir) / sourcefile
        return Path(sourcefile)

    # -------------------- leaf ops --------------------
    def read_datasources(self, sourcefile: str) -> pd.DataFrame:
        path = self._resolve_path(sourcefile)
        return pd.read_csv(path)

    def drop_rows_with_null_values(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.dropna(axis="index", thresh=2)

    def fill_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.fillna(value={"report_type": "ON SCENE"})

    def merge_dataframes(self, df_crashes: pd.DataFrame, df_vehicles: pd.DataFrame) -> pd.DataFrame:
        return df_crashes.merge(df_vehicles, how="left", on="crash_record_id", suffixes=("_left", "_right"))

    # >>> your rename_columns implementation <<<
    def rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        vehicle_mapping = {"vehicle_type": "vehicletypes"}
        return df.rename(columns=vehicle_mapping)

    # -------------------- pipeline steps (return ... , status) --------------------
    def read_data_pipeline(self) -> Tuple[pd.DataFrame, pd.DataFrame, str]:
        self.logger.info(f"Reading data from {self.crash_file} and {self.vehicle_file}")
        try:
            self.df_crash = self.read_datasources(self.crash_file)
            self.df_vehicle = self.read_datasources(self.vehicle_file)
            status = OK
            self.logger.info(f"{status} - read_data_pipeline finished successfully")
        except Exception as e:
            status = FAILED
            self.logger.exception(f"{status} - read_data_pipeline failed: {e}")
        return self.df_crash, self.df_vehicle, status

    def drop_rows_with_null_values_pipeline(self) -> Tuple[pd.DataFrame, pd.DataFrame, str]:
        self.logger.info("Dropping rows with null values (crash & vehicle)")
        try:
            self.df_crash = self.drop_rows_with_null_values(self.df_crash)
            self.df_vehicle = self.drop_rows_with_null_values(self.df_vehicle)
            status = OK
            self.logger.info(f"{status} - drop_rows_with_null_values finished successfully")
        except Exception as e:
            status = FAILED
            self.logger.exception(f"{status} - drop_rows_with_null_values failed: {e}")
        return self.df_crash, self.df_vehicle, status

    def fill_missing_values_pipeline(self) -> Tuple[pd.DataFrame, pd.DataFrame, str]:
        self.logger.info("Filling missing values (crash & vehicle)")
        try:
            self.df_crash = self.fill_missing_values(self.df_crash)
            self.df_vehicle = self.fill_missing_values(self.df_vehicle)
            status = OK
            self.logger.info(f"{status} - fill_missing_values finished successfully")
        except Exception as e:
            status = FAILED
            self.logger.exception(f"{status} - fill_missing_values failed: {e}")
        return self.df_crash, self.df_vehicle, status

    def merge_dataframes_pipeline(self) -> Tuple[pd.DataFrame, str]:
        self.logger.info("Merging dataframes (crash ⟕ vehicle)")
        try:
            self.df_agg = self.merge_dataframes(self.df_crash, self.df_vehicle)
            status = OK
            self.logger.info(f"{status} - merge_dataframes finished successfully")
        except Exception as e:
            status = FAILED
            self.logger.exception(f"{status} - merge_dataframes failed: {e}")
        return self.df_agg, status

    def format_dataframes_pipeline(self) -> Tuple[pd.DataFrame, str]:
        self.logger.info("Formatting output dataframe (rename columns)")
        try:
            self.df_output = self.rename_columns(self.df_agg)
            status = OK
            self.logger.info(f"{status} - format_dataframes finished successfully")
        except Exception as e:
            status = FAILED
            self.logger.exception(f"{status} - format_dataframes failed: {e}")
        return self.df_output, status

    # -------------------- run orchestrator --------------------
    def _run_step(self, spec: StepSpec) -> str:
        name = spec.status_attr
        self.logger.info(f"{name} → starting")
        try:
            result = spec.fn()
        except Exception as exc:
            self.logger.exception(f"{name} → error: {exc}")
            setattr(self, name, FAILED)
            return FAILED

        if not isinstance(result, tuple) or len(result) == 0:
            self.logger.error(f"{name} → invalid return (expected tuple with status at end)")
            setattr(self, name, FAILED)
            return FAILED

        *payload, status = result
        if len(payload) != len(spec.assign_attrs):
            self.logger.error(f"{name} → payload len {len(payload)} != expected {len(spec.assign_attrs)} {spec.assign_attrs}")
            setattr(self, name, FAILED)
            return FAILED

        for attr, value in zip(spec.assign_attrs, payload):
            setattr(self, attr, value)

        setattr(self, name, status)
        self.logger.info(f"{name} → {status}")
        return status

    def run(self, *, fail_fast: bool = True) -> str:
        """Run all steps in order. Returns final status string."""
        steps: Iterable[StepSpec] = [
            StepSpec("READING_CRASH_DATA_PIPELINE",     self.read_data_pipeline,              ("df_crash", "df_vehicle")),
            StepSpec("DROPPING_ROW_WITH_NULL_PIPELINE", self.drop_rows_with_null_values_pipeline, ("df_crash", "df_vehicle")),
            StepSpec("FILLING_MISSING_VALUE_PIPELINE",  self.fill_missing_values_pipeline,    ("df_crash", "df_vehicle")),
            StepSpec("MERGE_DATA_FRAME_PIPELINE",       self.merge_dataframes_pipeline,       ("df_agg",)),
            StepSpec("FORMAT_DATAFRAME_PIPELINE",       self.format_dataframes_pipeline,      ("df_output",)),
        ]

        self.logger.info("Pipeline starting")
        final_status = OK
        for spec in steps:
            s = self._run_step(spec)
            final_status = s
            if s != OK and fail_fast:
                self.logger.warning(f"Stopping after {spec.status_attr} with status {s}")
                break

        if final_status == OK:
            self.logger.info("Pipeline completed successfully")
        else:
            self.logger.warning(f"Pipeline ended with status {final_status}")
        return final_status
