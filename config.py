import json
import os
from pathlib import Path

class Config:
    def __init__(self):
        self.app_name = "Thought-Link"
        self.version = "1.0.0"
        self.data_dir = Path("data")
        self.assets_dir = Path("assets")
        self.config_file = self.data_dir / "config.json"
        
    
        self.data_dir.mkdir(exist_ok=True)
        self.assets_dir.mkdir(exist_ok=True)
        
       
        self.default_config = {
            "mongodb_uri": "mongodb+srv://risegroup:fkjUQXAfU0FMDCn4@cluster0.v7mkgh4.mongodb.net/?appName=Cluster0",
            "database_name": "thoughtlink",
            "sync_interval": 30,
            "max_clipboard_history": 100,
            "auto_start": False,
            "hotkey": "Ctrl+Shift+V",
            "theme": "dark",
            "clip_categories": ["General", "Code", "Links", "Images", "Documents"],
            "device_id": "local_device",
            "use_local_storage": True
        }
        
        self.load_config()
    
    def load_config(self):
        """Load configuration from file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                self.default_config.update(user_config)
            except Exception as e:
                print(f"Error loading config: {e}")
        
        self.save_config()
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.default_config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key, default=None):
        return self.default_config.get(key, default)
    
    def set(self, key, value):
        self.default_config[key] = value
        self.save_config()


config = Config()