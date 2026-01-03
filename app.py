import streamlit as st
from data_loader import AzureDataLoader
from data_cache import DataCache
from visualizer import SensorVisualizer
from config import AZURE_STORAGE_ACCOUNT, AZURE_STORAGE_KEY, CONTAINER_NAME 

class SensorDashboard:
    def __init__(self):
        if 'cache' not in st.session_state:
            st.session_state.cache = DataCache()
        
        self.cache = st.session_state.cache
        self.loader = AzureDataLoader(
            AZURE_STORAGE_ACCOUNT,
            AZURE_STORAGE_KEY,
            CONTAINER_NAME
        )
        self.visualizer = SensorVisualizer()
    
    def load_data_with_cache(self, sensor_id):
        """Load data with caching mechanism"""
        cache_key = f"sensor_{sensor_id}"
        
        # Requirement said to cache for repeat selection
        if self.cache.has(cache_key):
            st.info("📦 Data loaded from cache")  # Tell cache used
            return self.cache.get(cache_key)
        
        st.info("☁️ Loading data from Azure Data Lake...")  # Tell from data lake
        df = self.loader.load_sensor_data(sensor_id)
        
        self.cache.set(cache_key, df)
        
        return df
    
    def run(self):
        st.title("Sensor Data Visualization Dashboard")
        
        # FIXED: Use proper sensor names (sensor1, sensor2, etc.) instead of numbers
        sensor_options = {
            "Sensor 1": "sensor1",  # ← Changed from 1 to "sensor1"
            "Sensor 2": "sensor2",  # ← Changed from 2 to "sensor2"
            "Sensor 4": "sensor4",  # ← Changed from 4 to "sensor4"
            "Sensor 5": "sensor5"   # ← Changed from 5 to "sensor5"
        }
        
        selected_sensor = st.selectbox(
            "Select Sensor:",
            options=list(sensor_options.keys())
        )
        
        sensor_id = sensor_options[selected_sensor]
        
        try:
            df = self.load_data_with_cache(sensor_id)
            
            # Show data info
            st.success(f"✅ Loaded {len(df):,} rows from {selected_sensor}")
            
            # Create visualization
            fig = self.visualizer.create_timeseries_chart(df, selected_sensor)
            st.plotly_chart(fig, use_container_width=True)
            
            # Data summary in expander
            with st.expander("📊 Data Summary"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Shape:**")
                    st.write(f"Rows: {df.shape[0]:,}")
                    st.write(f"Columns: {df.shape[1]}")
                with col2:
                    st.write("**Columns:**")
                    st.write(list(df.columns))
                
                st.write("**Statistics:**")
                st.dataframe(df.describe())
                
                st.write("**Sample Data:**")
                st.dataframe(df.head(10))
                
        except Exception as e:
            st.error(f"❌ Error loading data: {str(e)}")
            st.write("**Troubleshooting:**")
            st.write(f"- Looking for data in path: `{sensor_id}/tables/`")
            st.write(f"- Container: `{CONTAINER_NAME}`")
            st.write(f"- Storage Account: `{AZURE_STORAGE_ACCOUNT}`")

if __name__ == "__main__":
    dashboard = SensorDashboard()
    dashboard.run()
