import hashlib
import pickle
import os
from datetime import datetime, timedelta

class DataCache:
    def __init__(self, cache_dir=".cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_path(self, key):
        # Create a hash of the key for the filename
        key_hash = hashlib.md5(key.encode('utf-8')).hexdigest()
        return os.path.join(self.cache_dir, f"{key_hash}.pkl")
    
    def get(self, key, max_age_minutes=60):
        path = self._get_cache_path(key)
        if not os.path.exists(path):
            return None
        
        file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(path))
        if file_age > timedelta(minutes=max_age_minutes):
            return None
            
        with open(path, 'rb') as f:
            return pickle.load(f)
    
    def set(self, key, value):
        path = self._get_cache_path(key)
        with open(path, 'wb') as f:
            pickle.dump(value, f)



