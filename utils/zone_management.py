import json
from pathlib import Path

def load_zone_data():
    path = Path(__file__).parent.parent / "data" / "zone_definitions.json"
    if not path.exists():
        return {"sectors": {}, "stocks": {}}
    with open(path) as f:
        return json.load(f)

def get_zones_for_symbol(symbol, is_sector=False):
    zones_data = load_zone_data()
    key = 'sectors' if is_sector else 'stocks'
    return zones_data.get(key, {}).get(symbol, [])

def get_active_zones(symbol, current_price, is_sector=False):
    zones = get_zones_for_symbol(symbol, is_sector)
    active_zones = [
        zone for zone in zones
        if zone['price_low'] <= current_price <= zone['price_high']
    ]
    return active_zones

def get_zones_with_scores(symbol, is_sector=False):
    zones_data = load_zone_data()
    key = 'sectors' if is_sector else 'stocks'
    zones = zones_data.get(key, {}).get(symbol, [])
    return [
        {**zone, 'total_score': zone['strength'] + zone['base']}
        for zone in zones
    ]
