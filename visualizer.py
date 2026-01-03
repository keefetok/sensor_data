import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

class SensorVisualizer:
    @staticmethod
    def create_timeseries_chart(df, sensor_name):
        df = df.copy()
        
        #timestamp is datetime type
        #if is, then set timestamp as idx
        if 'timestamp' in df.columns:
            if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.set_index('timestamp')
            df = df.sort_index()
        
        #separate normalized and original columns
        all_cols = [col for col in df.columns if col != 'timestamp']
        normalized_cols = [col for col in all_cols if 'normalized' in col.lower()]
        original_cols = [col for col in all_cols if 'normalized' not in col.lower()]
        
        #determine number of subplots needed
        has_normalized = len(normalized_cols) > 0
        has_original = len(original_cols) > 0
        
        if has_normalized and has_original:
            #vertical for better view
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Original Data', 'Normalized Data (0-1)'),
                vertical_spacing=0.12,
                shared_xaxes=False #each x-axis
            )
            
            for column in original_cols:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df[column],
                        mode='lines',
                        name=column,
                        legendgroup='original',
                        showlegend=True,
                        hovertemplate='<b>Time:</b> %{x|%Y-%m-%d %H:%M:%S}<br><b>Value:</b> %{y:.2f}<extra></extra>'
                    ),
                    row=1, col=1
                )

            for column in normalized_cols:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df[column],
                        mode='lines',
                        name=column,
                        legendgroup='normalized',
                        showlegend=True,
                        hovertemplate='<b>Time:</b> %{x|%Y-%m-%d %H:%M:%S}<br><b>Value:</b> %{y:.3f}<extra></extra>'
                    ),
                    row=2, col=1
                )
            
            fig.update_xaxes(
                title_text="Timestamp",
                row=1, col=1,
                tickformat='%Y-%m-%d<br>%H:%M',
                tickangle=-45
            )
            fig.update_xaxes(
                title_text="Timestamp",
                row=2, col=1,
                tickformat='%Y-%m-%d<br>%H:%M',
                tickangle=-45
            )
            
            fig.update_yaxes(title_text="Value", row=1, col=1)
            fig.update_yaxes(title_text="Normalized Value (0-1)", row=2, col=1)
            height = 900
            
        else:
            #single plot if only one type of data exists
            fig = go.Figure()
            
            cols_to_plot = normalized_cols if has_normalized else original_cols
            
            for column in cols_to_plot:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df[column],
                        mode='lines',
                        name=column,
                        hovertemplate='<b>Time:</b> %{x|%Y-%m-%d %H:%M:%S}<br><b>Value:</b> %{y:.2f}<extra></extra>'
                    )
                )
            
            fig.update_xaxes(
                title_text="Timestamp",
                tickformat='%Y-%m-%d<br>%H:%M',
                tickangle=-45
            )
            fig.update_yaxes(title_text="Normalized Value" if has_normalized else "Value")
            
            height = 500
        
        fig.update_layout(
            title_text=f"{sensor_name} - Time Series Data",
            hovermode='x unified',
            height=height,
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02
            )
        )
        
        return fig
