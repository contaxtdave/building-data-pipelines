from transformation.pipeline import CrashDataPipeline

pipe = CrashDataPipeline(
    crash_file="traffic_crashes.csv",
    vehicle_file="traffic_crash_vehicle.csv",
    data_dir="/users/david/building-data-pipelines/chapter_5/data",  # or absolute path
)
status = pipe.run()
df_output = pipe.df_output
