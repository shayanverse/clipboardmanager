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
        
        # Create directories
        self.data_dir.mkdir(exist_ok=True)
        self.assets_dir.mkdir(exist_ok=True)
        
        # Default configuration
        self.default_config = {
            "mongodb_uri": "",
            "database_name": "thoughtlink",
            "sync_interval": 30,
            "max_clipboard_history": 100,
            "auto_start": False,
            "hotkey": "Ctrl+Shift+V",
            "theme": "light",
            "clip_categories": ["All", "Code", "Chat", "Link", "Image", "Document"],
            "context_boards": ["Global", "Coding Project X", "Client Y Chat", "Research Doc"],
            "device_id": "local_device",
            "use_local_storage": True,
            "blur_effect": True,
            "rounded_corners": True
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

# Global config instance
config = Config()
