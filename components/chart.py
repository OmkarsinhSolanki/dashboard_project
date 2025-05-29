import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from livedata.live_data_provider import LiveDataProvider
from livedata.live_market_data_services import LiveMarketDataService
import time
from functools import lru_cache


class ChartComponent:
    def __init__(self):
        self.data_provider = LiveDataProvider()
        self.data_service = LiveMarketDataService()
        self.initialize_session_state()

    def initialize_session_state(self):
        """Initialize all required session state variables for the chart component."""
        if 'current_chart' not in st.session_state:
            st.session_state.current_chart = None
        if 'chart_timeframe' not in st.session_state:
            st.session_state.chart_timeframe = "1d"
        if 'chart_interval' not in st.session_state:
            st.session_state.chart_interval = "1h"
        if 'chart_aspect_ratio' not in st.session_state:
            st.session_state.chart_aspect_ratio = 1.0  # Default aspect ratio interval
        if 'candle_colors' not in st.session_state:
            st.session_state.candle_colors = {
                'up': '#089981',  # Default green for up candles
                'down': '#F23645'  # Default red for down candles
            }
        # Variables for data caching and refresh functionality
        if 'chart_data' not in st.session_state:
            st.session_state.chart_data = {}
        if 'last_refresh' not in st.session_state:
            st.session_state.last_refresh = 0

    @lru_cache(maxsize=32)
    def _get_historical_data_cached(self, symbol: str, timeframe: str):
        """
        Fetches historical data for a given symbol and timeframe with caching.
        This method uses lru_cache to store results in memory.
        """
        # Map timeframes to appropriate start dates and Kite Connect intervals
        timeframe_map = {
            "1m": ("2024-05-20", "minute"),
            "5m": ("2024-05-20", "5minute"),
            "15m": ("2024-05-20", "15minute"),
            "30m": ("2024-05-20", "30minute"),
            "1h": ("2024-05-01", "hour"),
            "1d": ("2024-01-01", "day"),
            "5d": ("2024-01-01", "day"),
            "1mo": ("2023-01-01", "day"),
            "3mo": ("2023-01-01", "day"),
            "6mo": ("2022-01-01", "day"),
            "1y": ("2022-01-01", "day")
        }

        # Use "1d" as a fallback if the selected timeframe is not in the map
        if timeframe not in timeframe_map:
            timeframe = "1d"
            
        from_date, interval = timeframe_map[timeframe]
        to_date = "2025-05-20" # Fixed end date for historical data

        try:
            # Call the actual data provider service
            data = self.data_provider.get_historical_data(
                symbol,
                from_date=from_date,
                to_date=to_date,
                interval=interval
            )
            # Ensure the data is a pandas DataFrame
            if isinstance(data, list):
                data = pd.DataFrame(data)
            return data
        except Exception as e:
            st.error(f"Error loading {timeframe} data for {symbol}: {str(e)}")
            return None

    def render_chart(self):
        """Renders the chart analysis section of the Streamlit application."""
        st.subheader("Chart")

        # Chart customization controls within an expander
        with st.expander("Chart Settings", expanded=False):
            col1, col2, col3 = st.columns(3)

            # Aspect ratio control slider
            with col1:
                st.session_state.chart_aspect_ratio = st.slider(
                    "Aspect Ratio",
                    min_value=0.1,
                    max_value=3.0,
                    value=st.session_state.chart_aspect_ratio,
                    step=0.1,
                    help="Adjust the width/height ratio of the chart"
                )

            # Up candle color picker
            with col2:
                st.session_state.candle_colors['up'] = st.color_picker(
                    "Up Candle Color",
                    value=st.session_state.candle_colors['up'],
                    key='up_color'
                )

            # Down candle color picker
            with col3:
                st.session_state.candle_colors['down'] = st.color_picker(
                    "Down Candle Color",
                    value=st.session_state.candle_colors['down'],
                    key='down_color'
                )

        # Search bar, timeframe controls, and refresh button
        # Added an extra column for the refresh button
        col1, col2, col3, col4 = st.columns([3, 1, 1, 0.5])
        with col1:
            search_query = st.text_input("Search Symbol",
                                      value=st.session_state.get('current_chart', ''),
                                      placeholder="Enter symbol name")
        with col2:
            # Updated timeframe options to match the second code's broader range
            timeframe = st.selectbox("Timeframe",
                                   ["1m", "5m", "15m", "30m", "1h", "1d", "5d", "1mo", "3mo", "6mo", "1y"],
                                   index=5, # Default to "1d"
                                   key="chart_timeframe")
        with col4:
            # Add some vertical space to align the button
            st.write("")
            st.write("")
            # Refresh button logic
            if st.button("Refresh"):
                st.session_state.last_refresh = time.time()  # Update last refresh timestamp
                st.session_state.chart_data.clear()  # Clear cached data in session state
                self._get_historical_data_cached.cache_clear()  # Clear lru_cache
                st.rerun()  # Rerun the Streamlit app to force data reload

        # Determine which symbol to display based on search query or session state
        symbol = search_query.upper() if search_query else st.session_state.get('current_chart')

        if symbol:
            st.session_state.current_chart = symbol  # Keep track of the currently displayed symbol
            cache_key = f"{symbol}_{timeframe}"

            # Determine if data needs to be reloaded (not in cache or older than 5 minutes)
            should_reload = (cache_key not in st.session_state.chart_data or
                             time.time() - st.session_state.last_refresh > 300) # 300 seconds = 5 minutes

            historical_data = None
            if should_reload:
                with st.spinner(f"Loading {timeframe} data for {symbol}..."):
                    historical_data = self._get_historical_data_cached(symbol, timeframe)
                    if historical_data is not None:
                        st.session_state.chart_data[cache_key] = historical_data
                        st.session_state.last_refresh = time.time() # Update refresh time after successful load
                    else:
                        st.error("Failed to load data for the selected symbol and timeframe.")
                        return # Exit if data loading failed
            else:
                historical_data = st.session_state.chart_data[cache_key]

            # Check if historical data is available and not empty
            if historical_data is not None and not historical_data.empty:
                # Create candlestick chart with custom colors for lines and fills
                fig = go.Figure(data=[go.Candlestick(
                    x=historical_data['date'],
                    open=historical_data['open'],
                    high=historical_data['high'],
                    low=historical_data['low'],
                    close=historical_data['close'],
                    increasing=dict(
                        line=dict(color=st.session_state.candle_colors['up']),
                        fillcolor=st.session_state.candle_colors['up'] # Use same color for fill
                    ),
                    decreasing=dict(
                        line=dict(color=st.session_state.candle_colors['down']),
                        fillcolor=st.session_state.candle_colors['down'] # Use same color for fill
                    ),
                    name=symbol
                )])

                # Update chart layout for better presentation and responsiveness
                fig.update_layout(
                    title=f"{symbol} - {timeframe} timeframe",
                    xaxis_rangeslider_visible=False, # Hide the range slider at the bottom
                    height=600, # Fixed height for consistency
                    margin=dict(l=20, r=20, t=40, b=20), # Adjust margins
                    autosize=True, # Allow chart to auto-size within its container
                    # Apply aspect ratio to the y-axis for better visual control
                    yaxis=dict(
                        scaleanchor="x",
                        scaleratio=st.session_state.chart_aspect_ratio
                    )
                )

                # Display the Plotly chart, making it use the full container width
                st.plotly_chart(fig, use_container_width=True)

                # Show current price and other live data
                current_data = self.data_provider.get_stock_data(symbol)
                if current_data:
                    st.write(f"""
                    **Current Price:** ₹{current_data.get('price', 0):.2f}
                    **Change:** {current_data.get('pct_change', 0):.2f}%
                    **Zones:** {', '.join(current_data.get('zone_type', []))}
                    """)
            else:
                st.warning(f"No historical data available for {symbol} for the selected timeframe.")

        else:
            st.info("Search for a symbol or click a chart button from other tabs to display a chart.")


def render_chart():
    """Instantiates and renders the ChartComponent."""
    chart = ChartComponent()
    chart.render_chart()


# add this in main app if u wnat a chart 
# render_chart()