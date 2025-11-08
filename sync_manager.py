import threading
import time
from database import db_manager
from config import config

class SyncManager:
    def __init__(self):
        self.is_syncing = False
        self.sync_thread = None
        self.last_sync_time = None
        self.synced_devices = 1
    
    def start_sync(self):
        """Start automatic synchronization"""
        if self.is_syncing:
            return
        
        self.is_syncing = True
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()
        print("Sync manager started")
    
    def stop_sync(self):
        """Stop synchronization"""
        self.is_syncing = False
        if self.sync_thread:
            self.sync_thread.join(timeout=1)
        print("Sync manager stopped")
    
    def _sync_loop(self):
        """Main sync loop"""
        while self.is_syncing:
            try:
                # For demo purposes, simulate device count
                self.synced_devices = 3
                self.last_sync_time = time.time()
                
                sync_interval = config.get("sync_interval", 30)
                time.sleep(sync_interval)
                
            except Exception as e:
                print(f"Sync error: {e}")
                time.sleep(60)
    
    def manual_sync(self):
        """Trigger manual synchronization"""
        try:
            self.last_sync_time = time.time()
            return True
        except Exception as e:
            print(f"Manual sync failed: {e}")
            return False
    
    def get_sync_status(self):
        """Get current sync status"""
        status = {
            "is_syncing": self.is_syncing,
            "last_sync": self.last_sync_time,
            "synced_devices": self.synced_devices,
            "storage_type": "Local"
        }
        return status

# Global sync manager instance
sync_manager = SyncManager()
