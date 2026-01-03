from azure.storage.blob import BlobServiceClient
import pandas as pd
from io import BytesIO
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AzureDataLoader:
    def __init__(self, account_name, account_key, container_name):
        """
        Initialize Azure Data Loader
        
        Args:
            account_name: Azure storage account name
            account_key: Azure storage account key
            container_name: Container name (e.g., 'gold')
        """
        self.connection_string = (
            f"DefaultEndpointsProtocol=https;"
            f"AccountName={account_name};"
            f"AccountKey={account_key};"
            f"EndpointSuffix=core.windows.net"
        )
        self.blob_service = BlobServiceClient.from_connection_string(
            self.connection_string
        )
        self.container_name = container_name

    def load_all_sensors(self, path="all_sensors/tables/"):
        """
        Load all sensor data from parquet files in the specified path
        
        Args:
            path: Path to the parquet files (default: "all_sensors/tables/")
        
        Returns:
            pandas.DataFrame: Combined dataframe from all parquet files
        """
        logger.info(f"Loading data from: {path}")
        
        container_client = self.blob_service.get_container_client(
            self.container_name
        )

        # List all blobs in the path
        blob_list = list(container_client.list_blobs(name_starts_with=path))
        
        logger.info(f"Found {len(blob_list)} total blobs in {path}")

        # Filter for parquet files only (exclude folders and _delta_log)
        parquet_files = [
            blob.name for blob in blob_list
            if blob.name.endswith(".parquet") and "/_delta_log/" not in blob.name
        ]

        if not parquet_files:
            # Better error message
            available_paths = self._get_available_paths()
            error_msg = (
                f"No parquet files found in '{path}'. "
                f"Container: '{self.container_name}'. "
                f"Available paths: {available_paths}"
            )
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        logger.info(f"Found {len(parquet_files)} parquet files")
        
        # Load all parquet files
        dfs = []
        for i, parquet_file in enumerate(parquet_files, 1):
            logger.info(f"Loading file {i}/{len(parquet_files)}: {parquet_file}")
            
            blob_client = self.blob_service.get_blob_client(
                container=self.container_name,
                blob=parquet_file
            )

            stream = BytesIO(blob_client.download_blob().readall())
            df_temp = pd.read_parquet(stream)
            dfs.append(df_temp)
            
            logger.info(f"  Loaded {len(df_temp)} rows")

        # Combine all dataframes
        df = pd.concat(dfs, ignore_index=True)
        logger.info(f"Total rows after combining: {len(df)}")

        # Process timestamp column
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.sort_values("timestamp").reset_index(drop=True)
            logger.info(f"Data sorted by timestamp")
        
        logger.info(f"Columns in dataset: {list(df.columns)}")
        
        return df

    def load_sensor_data(self, sensor_name):
        """
        Load data for a specific sensor
        
        Args:
            sensor_name: Name of the sensor (e.g., 'sensor1', 'sensor4')
                        Must be a string like 'sensor1', NOT a number
        
        Returns:
            pandas.DataFrame: Sensor data
        """
        # Ensure sensor_name is a string
        if isinstance(sensor_name, int):
            sensor_name = f"sensor{sensor_name}"
            logger.warning(f"Converted integer sensor ID to string: {sensor_name}")
        
        path = f"{sensor_name}/tables/"
        logger.info(f"Loading data for {sensor_name} from: {path}")
        
        return self.load_all_sensors(path=path)

    def _get_available_paths(self, prefix=""):
        """
        Internal method to get available paths for error messages
        """
        try:
            container_client = self.blob_service.get_container_client(
                self.container_name
            )
            
            blob_list = container_client.list_blobs(name_starts_with=prefix)
            
            paths = set()
            for blob in blob_list:
                # Extract folder structure
                parts = blob.name.split('/')
                if len(parts) > 1:
                    paths.add('/'.join(parts[:-1]) + '/')
            
            return sorted(list(paths))[:10]  # Return first 10 paths
        except Exception as e:
            logger.error(f"Error listing paths: {e}")
            return []

    def list_available_paths(self, prefix=""):
        """
        List all available paths in the container for debugging
        
        Args:
            prefix: Optional prefix to filter paths
        """
        paths = self._get_available_paths(prefix)
        
        logger.info(f"Available paths in container '{self.container_name}':")
        for path in paths:
            logger.info(f"  {path}")
        
        return paths
