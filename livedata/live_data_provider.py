import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
from kiteconnect import KiteConnect
import logging
from data.settings import API_KEY, ACCESS_TOKEN
import json
from pathlib import Path

SECTOR_INDEX_MAP = {
    "NIFTY CONSR DURBL": "NIFTY CONSR DURBL",
    "NIFTY PHARMA": "NIFTY PHARMA",
    "NIFTY INFRA": "NIFTY INFRA",
    "NIFTY IT": "NIFTY IT",
    "NIFTY PSU BANK": "NIFTY PSU BANK",
    "NIFTY AUTO": "NIFTY AUTO",
    "NIFTY PSE": "NIFTY PSE",
    "NIFTY FIN SERVICE": "NIFTY FIN SERVICE",  
    "NIFTY FMCG": "NIFTY FMCG",
    "NIFTY ENERGY": "NIFTY ENERGY",
    "NIFTY METAL": "NIFTY METAL",
    "NIFTY PVT BANK": "NIFTY PVT BANK", 
    "NIFTY REALTY": "NIFTY REALTY"
}

SECTOR_TOKEN_MAP = {
    "NIFTY CONSR DURBL": 288777,
    "NIFTY PHARMA": 29919,
    "NIFTY INFRA": 29915,  
    "NIFTY IT": 29912,   
    "NIFTY PSU BANK": 29921, 
    "NIFTY AUTO": 29923,    
    "NIFTY PSE": 29920,     
    "NIFTY FIN SERVICE": 257801, 
    "NIFTY FMCG": 29917,   
    "NIFTY ENERGY": 29916,  
    "NIFTY METAL": 29924,   
    "NIFTY PVT BANK": 29951, 
    "NIFTY REALTY": 29914,    
    "NIFTY BANK": 26000, 
    "NIFTY 50": 256265
}

STOCK_TOKEN_MAP = {
    # Consumer Durables
    "BLUESTARCO": 2127617, "WHIRLPOOL": 4610817, "HAVELLS": 2513665, "DIXON": 5552641, 
    "RAJESHEXPO": 1894657, "TITAN": 897537, "VGUARD": 3932673, "VOLTAS": 951809, 
    "BATAINDIA": 94977, "CROMPTON": 4376065, "CERA": 3849985, "KAJARIACER": 462849, 
    "KALYANKJIL": 756481, "ORIENTELEC": 760833, "BAJAJELEC": 3848705,
    # Pharma
    "SUNPHARMA": 857857, "GLENMARK": 1895937, "AUROPHARMA": 70401, "LUPIN": 2672641, 
    "ZYDUSLIFE": 2029825, "ALKEM": 2995969, "CIPLA": 177665, "TORNTPHARM": 900609, 
    "IPCALAB": 418049, "DIVISLAB": 2800641, "DRREDDY": 225537, "LALPATHLAB": 2983425, 
    "APOLLOHOSP": 40193,
    # Infrastructure
    "GMRP&UI": 2183425, "BHEL": 112129, "BEL": 98049, "RECLTD": 3930881, 
    "PFC": 3660545, "NTPC": 2977281, "COALINDIA": 5215745, "HAL": 589569, 
    "CONCOR": 1215745, "IRCTC": 3484417, "POWERGRID": 3834113, "NMDC": 3924993,
    # IT
    "WIPRO": 969473, "BSOFT": 1790465, "TECHM": 3465729, "MPHASIS": 1152769, 
    "HCLTECH": 1850625, "INFY": 408065, "TCS": 2953217, "LTTS": 4752385, 
    "LTIM": 4561409, "COFORGE": 2955009, "PERSISTENT": 4701441,
    # PSU Bank
    "BANKBARODA": 1195009, "PNB": 2730497, "CANBK": 2763265, "FEDERALBNK": 261889, 
    "SBIN": 779521, "UNIONBANK": 2752769, "CENTRALBK": 3812865, "BANKINDIA": 1214721, 
    "MAHABANK": 2912513, "BANDHANBNK": 579329,
    # AUTO
    "TATAMOTORS": 884737, "ASHOKLEY": 54273, "M&M": 519937, "APOLLOTYRE": 41729, 
    "TVSMOTOR": 2170625, "EXIDEIND": 173057, "MOTHERSON": 1076225, "BALKRISIND": 85761, 
    "BAJAJ-AUTO": 4267265, "EICHERMOT": 232961,
    # PSE
    "NTPC": 2977281, "COALINDIA": 5215745, "HAL": 589569, "CONCOR": 1215745, 
    "BPCL": 134657, "ONGC": 633601, "IOC": 415745, "OIL": 4464129, "NHPC": 4454401,
    # FIN SERVICE
    "CANFINHOME": 149249, "LICHSGFIN": 511233, "LTF": 6386689, "IEX": 56321, 
    "MANAPPURAM": 4879617, "MUTHOOTFIN": 6054401, "CHOLAFIN": 175361, "COROMANDEL": 189185,
    # FMCG
    "ITC": 424961, "HINDUNILVR": 356865, "BRITANNIA": 140033, "TATACONSUM": 878593, 
    "GODREJCP": 2585345, "VBL": 4843777, "DABUR": 197633, "MARICO": 1041153,
    # ENERGY
    "GAIL": 1207553, "HINDPETRO": 359937, "BPCL": 134657, "ONGC": 633601, 
    "IOC": 415745, "PETRONET": 2905857, "MGL": 4488705,
    # METAL
    "ADANIENT": 6401, "SAIL": 758529, "JINDALSTEL": 1723649, "VEDL": 784129, 
    "HINDALCO": 348929, "JSWSTEEL": 3001089, "TATASTEEL": 895745, 
    # PVT BANK
    "AXISBANK": 1510401, "ICICIBANK": 1270529, "HDFCBANK": 341249, 
    "KOTAKBANK": 492033, "INDUSINDBK": 1346049, "IDFCFIRSTB": 2863105,
    # REALTY
    "DLF": 3771393,
}

class LiveDataProvider:
    def __init__(self):
        self.last_request_time = 0
        self.request_count = 0
        self.historical_request_times = []
        
        self.kite = KiteConnect(api_key=API_KEY)
        self.kite.set_access_token(ACCESS_TOKEN)
        self.instruments = self._load_instruments()
        self.sector_instruments = self._load_sector_instruments()
        self.sector_tokens = self._load_sector_tokens()
        self.stock_tokens = self._load_stock_tokens()
        logging.basicConfig(level=logging.INFO)

    def _load_sector_tokens(self) -> Dict[str, Dict[str, Any]]:
        """Load sector tokens from sectors.json"""
        sectors_path = Path(__file__).parent.parent / "data" / "sectors.json"
        with open(sectors_path) as f:
            return json.load(f)
    
    def _load_stock_tokens(self):
        """Load all NSE instrument tokens once at startup"""
        self._rate_limit()
        all_instruments = self.kite.instruments("NSE")
        
        stock_tokens = {}
        for inst in all_instruments:
            if inst['instrument_type'] == 'EQ':
                stock_tokens[inst['tradingsymbol']] = inst['instrument_token']
        
        return stock_tokens

    def _load_sector_instruments(self):
        """Load sector index instruments with proper formatting"""
        return {
            symbol: {
                "instrument_token": token,
                "tradingsymbol": symbol,
                "exchange": "NSE"
            }
            for symbol, token in SECTOR_TOKEN_MAP.items()
        }
    
    def _get_instrument_key(self, symbol):
        """Get the proper instrument key for the symbol with robust handling"""
        symbol_mappings = {
            # [Previous symbol mappings remain the same...]
        }
        return f"NSE:{symbol}"
    
    def _fetch_sector_data(self, symbol):
        """Special handling for sector indices"""
        try:
            mapped_symbol = SECTOR_INDEX_MAP.get(symbol)
            if not mapped_symbol:
                return None
                
            instrument_key = f"NSE:{mapped_symbol}"
            self._rate_limit()
            ltp_data = self.kite.ltp([instrument_key])
            
            if instrument_key not in ltp_data:
                logging.warning(f"No data returned for sector {symbol} ({instrument_key})")
                return None
                
            ltp = ltp_data[instrument_key]
            return {
                "price": ltp.get('last_price', 0),
                "pct_change": ltp.get('net_change', 0),
                "zone_type": [],
                "zone_direction": [],
                "strength": 0,
                "base": 0,
                "is_sector": True
            }
        except Exception as e:
            logging.error(f"Error fetching sector data for {symbol}: {str(e)}")
            return None
        
    
    def _rate_limit(self):
        """Enforce rate limiting of 3 requests per second"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < 0.34:  # Slightly more than 1/3 second to stay under 3 req/sec
            time.sleep(0.34 - elapsed)
        self.last_request_time = time.time()

    def _historical_rate_limit(self):
        """Enforce historical data rate limiting (5 per minute)"""
        now = time.time()
        # Remove requests older than 1 minute
        self.historical_request_times = [
            t for t in self.historical_request_times 
            if now - t < 60
        ]
        if len(self.historical_request_times) >= 5:
            sleep_time = 60 - (now - self.historical_request_times[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        self.historical_request_times.append(time.time())

    def _load_instruments(self) -> Dict[str, Any]:
        """Load all NSE instruments once per session"""
        self._rate_limit()
        instruments = self.kite.instruments("NSE")
        return {inst['tradingsymbol']: inst for inst in instruments}
    
    def get_sectors(self) -> List[str]:
        return list(self.sector_tokens.keys())
    
    def get_stock_map(self) -> Dict[str, List[str]]:
        stock_map_path = Path(__file__).parent.parent / "data" / "stock_map.json"
        with open(stock_map_path) as f:
            return json.load(f)
    
    def _get_sector_data(self, symbol: str) -> Dict[str, Any]:
        """Special handling for sector/index data"""
        try:
            if symbol in self.sector_tokens:
                token = self.sector_tokens[symbol].get("token", "256265")
                self._rate_limit()
                ltp = self.kite.ltp([f"NSE:{token}"])[f"NSE:{token}"]
                
                return {
                    "price": ltp.get('last_price', 0),
                    "pct_change": ltp.get('net_change', 0),
                    "zone_type": [],
                    "zone_direction": [],
                    "strength": 0,
                    "base": 0,
                    "is_sector": True
                }
            return {}
        except Exception as e:
            logging.error(f"Error fetching sector data for {symbol}: {e}")
            return {}

    def get_stock_data(self, symbol: str) -> Dict[str, Any]:
        try:
            if symbol in SECTOR_INDEX_MAP:
                sector_data = self._fetch_sector_data(symbol)
                if sector_data:
                    return sector_data
            
            instrument_key = self._get_instrument_key(symbol)
            self._rate_limit()
            ltp_data = self.kite.ltp([instrument_key])
            
            if instrument_key not in ltp_data:
                logging.warning(f"No data returned for {symbol} ({instrument_key})")
                return self._create_default_data()
                
            ltp = ltp_data[instrument_key]
            
            if symbol in SECTOR_INDEX_MAP:
                return {
                    "price": ltp.get('last_price', 0),
                    "pct_change": ltp.get('net_change', 0),
                    "zone_type": [],
                    "zone_direction": [],
                    "strength": 0,
                    "base": 0,
                    "is_sector": True
                }
            
            historical_data = self.get_historical_data(
                symbol,
                datetime.now() - timedelta(days=30),
                datetime.now(),
                "day"
            )
            
            close_prices = [candle['close'] for candle in historical_data]
            current_price = ltp['last_price']
            pct_change = ((current_price - close_prices[-2]) / close_prices[-2]) * 100 if len(close_prices) > 1 else 0
            
            return {
                "price": current_price,
                "pct_change": round(pct_change, 2),
                "zone_type": [],
                "zone_direction": [],
                "strength": 0,
                "base": 0,
                "is_sector": False
            }
        except Exception as e:
            logging.error(f"Error fetching data for {symbol}: {str(e)}")
            return self._create_default_data()

    def get_bulk_data(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        results = {}
        stock_symbols = []
        sector_symbols = []
        
        for symbol in symbols:
            if symbol in SECTOR_INDEX_MAP:
                sector_symbols.append(symbol)
            else:
                stock_symbols.append(symbol)
        
        for sector in sector_symbols:
            try:
                sector_data = self._fetch_sector_data(sector)
                results[sector] = sector_data if sector_data else self._create_default_data()
            except Exception as e:
                logging.error(f"Error processing sector {sector}: {str(e)}")
                results[sector] = self._create_default_data()
        
        batch_size = 50
        for i in range(0, len(stock_symbols), batch_size):
            batch = stock_symbols[i:i + batch_size]
            instrument_keys = [self._get_instrument_key(s) for s in batch]
            
            try:
                self._rate_limit()
                ltp_data = self.kite.ltp(instrument_keys)
                
                for symbol, instrument_key in zip(batch, instrument_keys):
                    if instrument_key in ltp_data:
                        ltp = ltp_data[instrument_key]
                        results[symbol] = {
                            "price": ltp.get('last_price', 0),
                            "pct_change": ltp.get('net_change', 0),
                            "zone_type": [],
                            "zone_direction": [],
                            "strength": 0,
                            "base": 0,
                            "is_sector": False
                        }
                    else:
                        logging.warning(f"No data for {symbol} ({instrument_key})")
                        results[symbol] = self._create_default_data()
            except Exception as e:
                logging.error(f"Error in batch {i//batch_size}: {str(e)}")
                for symbol in batch:
                    try:
                        results[symbol] = self.get_stock_data(symbol)
                    except Exception as e:
                        logging.error(f"Error fetching {symbol}: {str(e)}")
                        results[symbol] = self._create_default_data()
        
        return results

    def _create_default_data(self):
        return {
            "price": 0,
            "pct_change": 0,
            "zone_type": [],
            "zone_direction": [],
            "strength": 0,
            "base": 0,
            "is_sector": False
        }

    def get_price(self, symbol: str) -> float:
        try:
            ltp = self.kite.ltp([f"NSE:{symbol}"])[f"NSE:{symbol}"]
            return ltp['last_price']
        except Exception as e:
            logging.error(f"Error getting price for {symbol}: {e}")
            return 0.0
    
    def get_historical_data(self, symbol: str, 
                          from_date: datetime, 
                          to_date: datetime,
                          interval: str) -> List[Dict[str, Any]]:
        self._historical_rate_limit()
        
        try:
            kite_interval = {
                "day": "day",
                "minute": "minute",
                "5minute": "5minute",
                "15minute": "15minute"
            }.get(interval, "day")
            
            instrument_token = self.instruments[symbol]['instrument_token']
            
            self._rate_limit()
            data = self.kite.historical_data(
                instrument_token,
                from_date=from_date,
                to_date=to_date,
                interval=kite_interval
            )
            
            return [{
                'date': candle['date'],
                'open': candle['open'],
                'high': candle['high'],
                'low': candle['low'],
                'close': candle['close'],
                'volume': candle['volume']
            } for candle in data]
        except Exception as e:
            logging.error(f"Error fetching historical data for {symbol}: {e}")
            return []
            
    def subscribe_to_ticks(self, symbols: List[str], callback):
        try:
            tokens = [self.instruments[sym]['instrument_token'] for sym in symbols]
            self.kite.subscribe(tokens)
            logging.info(f"Subscribed to ticks for {len(symbols)} symbols")
        except Exception as e:
            logging.error(f"Error subscribing to ticks: {e}")
    
    def get_instrument_details(self, symbol: str) -> Dict[str, Any]:
        inst = self.instruments.get(symbol, {})
        return {
            "symbol": symbol,
            "token": inst.get("instrument_token", 0),
            "lot_size": inst.get("lot_size", 1),
            "tick_size": inst.get("tick_size", 0.05),
            "instrument_type": inst.get("instrument_type", "EQ"),
            "segment": inst.get("segment", "NSE"),
            "exchange": inst.get("exchange", "NSE")
        }
