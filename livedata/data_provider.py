from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime

class DataProvider(ABC):
    @abstractmethod
    def get_sectors(self) -> List[str]:
        """Return list of sector names"""
        pass
    
    @abstractmethod
    def get_stock_map(self) -> Dict[str, List[str]]:
        """Return mapping of sectors to their stocks"""
        pass
    
    @abstractmethod
    def get_stock_data(self, symbol: str) -> Dict[str, Any]:
        """Return complete stock data including zones, indicators"""
        pass
    
    @abstractmethod
    def get_bulk_data(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Return data for multiple stocks"""
        pass
    
    @abstractmethod
    def get_price(self, symbol: str) -> float:
        """Return current price"""
        pass
    
    @abstractmethod
    def get_historical_data(self, symbol: str, 
                          from_date: datetime, 
                          to_date: datetime,
                          interval: str) -> List[Dict[str, Any]]:
        """Return historical candle data"""
        pass
    
    @abstractmethod
    def subscribe_to_ticks(self, symbols: List[str], callback):
        """Subscribe to live updates"""
        pass
    
    @abstractmethod
    def get_instrument_details(self, symbol: str) -> Dict[str, Any]:
        """Get instrument metadata (token, lot size, etc.)"""
        pass

