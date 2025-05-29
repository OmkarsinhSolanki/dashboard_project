import time
import threading
from typing import Dict, Callable
from .live_data_provider import LiveDataProvider
from .caching import DataCache
import logging
from typing import Dict, Any, List


class LiveMarketDataService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_service()
        return cls._instance
    
    def _init_service(self):
        self.provider = LiveDataProvider()
        self.cache = DataCache()
        self.subscribers = []
        self.running = False
        self.thread = None
        self.update_interval = 300  # 5 minutes (adjust as needed)
        self.priority_symbols = set()

    def set_priority_symbols(self, symbols: List[str]):
        """Set symbols that should be updated more frequently"""
        self.priority_symbols = set(symbols)
        
    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._update_loop)
            self.thread.daemon = True
            self.thread.start()
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
    
    def _update_loop(self):
        full_update_count = 0
        while self.running:
            try:
                stock_map = self.provider.get_stock_map()
                all_symbols = list(stock_map.keys())
                for sector_stocks in stock_map.values():
                    all_symbols.extend(sector_stocks)
                
                if full_update_count % 5 == 0:
                    symbols_to_update = all_symbols
                else:
                    symbols_to_update = list(self.priority_symbols)
                
                if symbols_to_update:
                    data = self.provider.get_bulk_data(symbols_to_update)
                    
                    for symbol, values in data.items():
                        self.cache.set(symbol, values)
                    
                    for callback in self.subscribers:
                        try:
                            callback(data)
                        except Exception as e:
                            logging.error(f"Error in subscriber callback: {e}")
                
                full_update_count += 1
                time.sleep(self.update_interval)
            except Exception as e:
                logging.error(f"Error in update loop: {e}")
                time.sleep(60)
    
    def subscribe(self, callback: Callable[[Dict[str, Any]], None]):
        """Subscribe to receive market data updates"""
        if callback not in self.subscribers:
            self.subscribers.append(callback)
    
    def unsubscribe(self, callback: Callable[[Dict[str, Any]], None]):
        """Unsubscribe from market data updates"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
    
    def get_current_data(self) -> Dict[str, Any]:
        """Get the latest cached market data"""
        stock_map = self.provider.get_stock_map()
        all_symbols = list(stock_map.keys())
        for sector_stocks in stock_map.values():
            all_symbols.extend(sector_stocks)
        
        return self.provider.get_bulk_data(all_symbols)