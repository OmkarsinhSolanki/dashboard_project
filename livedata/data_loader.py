from .live_data_provider import LiveDataProvider
import pandas as pd
# from .mock_data_provider import MockDataProvider
from data.settings import USE_LIVE_DATA
from utils.decorators import handle_data_errors

class DataLoader:
    def __init__(self):
        if USE_LIVE_DATA:
            self.provider = LiveDataProvider()
    
    @handle_data_errors
    def load_sectors(self):
        """Load sector list"""
        return self.provider.get_sectors()
    
    @handle_data_errors
    def load_stock_map(self):
        """Load sector to stocks mapping"""
        return self.provider.get_stock_map()
    
    @handle_data_errors
    def get_bulk_data(self, symbols):
        """Get data for multiple symbols with validation"""
        # First validate symbols
        valid_symbols = [s for s in symbols if self._is_valid_symbol(s)]
        data = self.provider.get_bulk_data(valid_symbols)
        
        # Ensure all requested symbols have data
        for symbol in symbols:
            if symbol not in data:
                data[symbol] = {
                    "price": 0,
                    "pct_change": 0,
                    "zone_type": [],
                    "zone_direction": [],
                    "strength": 0,
                    "base": 0,
                    "is_sector": False
                }
        return data     
    
    def _is_valid_symbol(self, symbol):
        """Check if symbol is valid for the provider"""
        return True

    def get_stock_data(self, symbol):
        """Get data for single symbol"""
        return self.provider.get_stock_data(symbol)
    
    def get_price(self, symbol):
        """Get current price for symbol"""
        return self.provider.get_price(symbol)
    
    def get_historical_data(self, instrument_token, interval="day", from_date="2024-01-01", to_date="2024-05-20"):
        data = self.kite.historical_data(
            instrument_token=instrument_token,
            interval=interval,
            from_date=from_date,
            to_date=to_date
        )
        return pd.DataFrame(data)
    
    def get_instrument_token(symbol, instruments_df):
        row = instruments_df[instruments_df["tradingsymbol"] == symbol]
        if not row.empty:
            return int(row.iloc[0]["instrument_token"])
        else:
            return None

