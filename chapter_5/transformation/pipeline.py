from config.log_config import get_logger
import pandas as pd


class CrashDataPipeline:

    """Encapsulates the crash data transformation pipeline for crash data."""

    def __init__(self, crash_file: str, vehicle_file: str):
        self.crash_file = crash_file
        self.vehicle_file = vehicle_file
        self.df_crash = None
        self.df_vehicle = None
        self.df_agg = None
        self.df_output = None
        self.logger = get_logger(self.__class__.__name__)

    # --- pipeline steps -----------------------------------------

    def read_datasources(self, sourcefile:str) -> pd.DataFrane:
        df = pd.read_csv(f"/users/david/building-data-pipelines/chapter_5/data/{sourcefile}")
        return df
    
    # Drop rows with null values
    def drop_rows_with_null_values(self, df: pd.DataFrame) -> pd.DataFrame:
        cleaned = df.dropna(axis='index', thresh=2)  
        return cleaned 

    def fill_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.fillna(value={'report_type': 'ON SCENE'})
        return df

    # Merge DataFrames
    def merge_dataframes(self, df_vehicles: pd.DataFrame, df_crashes: pd.DataFrame) -> pd.DataFrame:
        df = df_crashes.merge(df_vehicles, how='left', on='crash_record_id', suffixes=('_left', '_right'))
        return df

    def read_data_pipeline(self) -> tuple[pd.DataFrame, pd.DataFrame, str]:
        self.logger.info(f"Reading data from {self.crash_file} and {self.vehicle_file}")
        try:
            self.df_crash = self.read_datasources(self.crash_file)
            self.df_vehicle = self.read_datasources(self.vehicle_file)
            status = "<OK>"
            self.logger.info(f"{status} - read_data_pipeline finished successfully")
        except Exception as e:
            status = "<FAILED>"
            self.logger.error(f"{status} - read_data_pipeline failed with error: {e}")
        finally:
            return self.df_crash, self.df_vehicle, status

    def drop_rows_with_null_values_pipeline(self, df_crash: pd.DataFrame, df_vehicle: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, str]:
        self.logger.info("Dropping rows with null values from crash and vehicle data")
        try:
            self.df_crash = self.drop_rows_with_null_values(self.df_crash)
            self.df_vehicle = self.drop_rows_with_null_values(df_vehicle)
            status = "<OK>"
            self.logger.info(f"{status} - drop_rows_with_null_values finished successfully")
        except Exception as e:
            status = "<FAILED>"
            self.logger.error(f"{status} - drop_rows_with_null_values failed with error: {e}")
        finally:
            return self.df_crash, self.df_vehicle, status

    def fill_missing_values_pipeline(self, df_crash: pd.DataFrame, df_vehicle: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, str]:
        self.logger.info("Running fill_missing_values_pipeline")
        try:
            self.df_crash = self.fill_missing_values(self.df_crash)
            self.df_vehicle = self.fill_missing_values(self.df_vehicle)
            status = "<OK>"
            self.logger.info(f"{status} - fill_missing_values finished successfully")
        except Exception as e:
            status = "<FAILED>"
            self.logger.error(f"{status} - fill_missing_values failed with error: {e}")
        finally:
            return self.df_crash, self.df_vehicle, status

    def merge_dataframes_pipeline(self, df_crash: pd.DataFrame, df_vehicle: pd.DataFrame) -> tuple[pd.DataFrame, str]:
        self.logger.info("Running merge_dataframes_pipeline")
        try:
            self.df_agg = self.merge_dataframes(self.df_vehicle, self.df_crash)
            status = "<OK>"
            self.logger.info(f"{status} - merge_dataframes finished successfully")
        except Exception as e:
            status = "<FAILED>"
            self.logger.error(f"{status} - merge_dataframes failed with error: {e}")
        finally:
            return self.df_agg, status
            
def format_dataframes_pipeline(self, df_output: pd.DataFrame) -> tuple [pd.DataFrame, str]:
    self.logger.info("Running format_dataframes_pipeline")
    try:
        df_output = self.rename_columns(df_agg)
        status = "<OK>"
        self.logger.info(f"{status} - rename_columns finished successfully")
    except Exception as e:
        status = "<FAILED>"
        self.logger.error(f"{status} - rename_columns failed with error: {e}")
    finally:
        return df_output, status