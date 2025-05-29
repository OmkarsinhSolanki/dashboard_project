import os
import pandas as pd
from kiteconnect import KiteConnect
import logging

logging.basicConfig(level=logging.INFO)

# ---- CONFIG ---- #
KITE_API_KEY = "sga0oscku88h6hhi"
KITE_API_SECRET = "3sxovyrdcawudyy33f6yjom964x759tw"
KITE_ACCESS_TOKEN = "HecGS9G6qdNeRQb7LW51ioQoKBPSMnhk"  # You should already have this

INSTRUMENTS_CSV = "nse_instruments.csv"

kite = KiteConnect(api_key=KITE_API_KEY)
kite.set_access_token(KITE_ACCESS_TOKEN)

# ---- 1. Download instrument list if not present ---- #
def download_nse_instruments():
    if not os.path.exists(INSTRUMENTS_CSV):
        logging.info("Downloading NSE instruments list from Kite...")
        instruments = kite.instruments("NSE")
        df = pd.DataFrame(instruments)
        df.to_csv(INSTRUMENTS_CSV, index=False)
        logging.info(f"Saved NSE instruments to {INSTRUMENTS_CSV}")
    else:
        logging.info(f"Using cached file: {INSTRUMENTS_CSV}")

# ---- 2. Fetch tokens from your symbol list ---- #
def get_tokens_from_symbols(symbol_list):
    df = pd.read_csv(INSTRUMENTS_CSV)
    token_map = {}
    missing = []

    for symbol in symbol_list:
        row = df[df['tradingsymbol'] == symbol]
        if not row.empty:
            token_map[symbol] = int(row.iloc[0]['instrument_token'])
        else:
            missing.append(symbol)

    if missing:
        for sym in missing:
            logging.warning(f"Symbol not found in instrument list: {sym}")

    return token_map

# ---- 3. Example Usage ---- #
if __name__ == "__main__":
    download_nse_instruments()
    
    my_symbols = [
        "BLUESTARCO", "WHIRLPOOL", "HAVELLS", "DIXON", "RAJESHEXPO", "TITAN", "VGUARD", "VOLTAS", "BATAINDIA", "CROMPTON", "CERA", "KAJARIACER", "KALYANKJIL", "ORIENTELEC", "BAJAJELEC",
        "NIFTY PHARM", "SUNPHARMA", "GLENMARK", "AUROPHARMA", "LUPIN", "ZYDUSLIFE", "ALKEM", "CIPLA", "TORNTPHARM", "IPCALAB", "DIVISLAB", "DRREDDY", "LALPATHLAB", "APOLLOHOSP",
        "NIFTY INFRA", "GMRP&UI", "BHEL", "BEL", "RECLTD", "PFC", "NTPC", "COALINDIA", "HAL", "CONCOR", "IRCTC", "POWERGRID", "NMDC",
        "NIFTY IT", "WIPRO", "BSOFT", "TECHM", "MPHASIS", "HCLTECH", "INFY", "TCS", "LTTS", "LTIM", "COFORGE", "PERSISTENT",
        "NIFTY PSU BANK", "BANKBARODA", "PNB", "CANBK", "FEDERALBNK", "SBIN", "UNIONBANK", "CENTRALBK", "BANKINDIA", "MAHABANK", "BANDHANBNK",
        "NIFTY AUTO", "TATAMOTORS", "ASHOKLEY", "M&M", "APOLLOTYRE", "TVSMOTOR", "EXIDEIND", "MOTHERSON", "BALKRISIND", "BAJAJ-AUTO", "EICHERMOT",
        "NIFTY PSE", "NTPC", "COALINDIA", "HAL", "CONCOR", "BPCL", "ONGC", "IOC", "OIL", "NHPC",
        "NIFTY FIN SERVICE", "CANFINHOME", "LICHSGFIN", "LTF", "IEX", "MANAPPURAM", "MUTHOOTFIN", "CHOLAFIN", "COROMANDEL",
        "NIFTY FMCG", "ITC", "HINDUNILVR", "BRITANNIA", "TATACONSUM", "GODREJCP", "VBL", "DABUR", "MARICO",
        "NIFTY ENERGY", "GAIL", "HINDPETRO", "BPCL", "ONGC", "IOC", "PETRONET", "MGL",
        "NIFTY METAL", "ADANIENT", "SAIL", "JINDALSTEL", "VEDL", "HINDALCO", "JSWSTEEL", "TATASTEEL",
        "NIFTY PVT BANK", "AXISBANK", "ICICIBANK", "HDFCBANK", "KOTAKBANK", "INDUSINDBK", "IDFCFIRSTB",
        "NIFTY REALTY", "DLF"
    ]
    
    tokens = get_tokens_from_symbols(my_symbols)
    print("Fetched tokens:")
    for sym, tok in tokens.items():
        print(f"'{sym}': {tok},")