from datetime import datetime
from typing import Dict, Any, List

class DataNormalizer:
    @staticmethod
    def normalize_tick(tick_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize live tick data to our standard format"""
        return {
            'price': tick_data.get('last_price', 0),
            'pct_change': tick_data.get('change', 0),
            'volume': tick_data.get('volume', 0),
            'ohlc': tick_data.get('ohlc', {}),
            'timestamp': datetime.now().isoformat(),
            # Add other normalized fields as needed
        }

    @staticmethod
    def normalize_historical(candles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize historical candle data"""
        return [
            {
                'date': candle['date'],
                'open': candle['open'],
                'high': candle['high'],
                'low': candle['low'],
                'close': candle['close'],
                'volume': candle['volume']
            }
            for candle in candles
        ]
