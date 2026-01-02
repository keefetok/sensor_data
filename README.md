# sensor_data
ETE sensor pipeline

Files are read in bronze layer for xlsx, csv, parquet, json and pickle formats
Files are passed into silver layer for ETL/ELT (filter, pivot by sensor name indexed by timestamp, forward fill)
Files are then passed into gold layer for data normalisation model for each sensor
