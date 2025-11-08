import json
from datetime import datetime
import uuid
from pathlib import Path
from config import config

class DatabaseManager:
    def __init__(self):
        self.data_file = config.data_dir / "clips.json"
        self.clips = []
        self.is_connected = True
        self.load_clips()
    
    def load_clips(self):
        """Load clips from local JSON file"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.clips = json.load(f)
            else:
                self.clips = []
                self.save_clips()
            print(f"Loaded {len(self.clips)} clips from local storage")
        except Exception as e:
            print(f"Error loading clips: {e}")
            self.clips = []
    
    def save_clips(self):
        """Save clips to local JSON file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.clips, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"Error saving clips: {e}")
    
    def insert_clip(self, content, content_type="text", category="General", metadata=None):
        """Insert a new clip into database"""
        try:
            clip_data = {
                "_id": str(uuid.uuid4()),
                "content": content,
                "content_type": content_type,
                "category": category,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {},
                "device_id": config.get("device_id", "local_device"),
                "sync_status": "local",
                "context_board": "Global"
            }
            
            self.clips.insert(0, clip_data)
            self.save_clips()
            
            # Cleanup old clips
            self.cleanup_old_clips()
            
            return clip_data["_id"]
        except Exception as e:
            print(f"Error inserting clip: {e}")
            return None
    
    def get_clips(self, category=None, context_board=None, search_text=None, limit=50):
        """Retrieve clips from database"""
        try:
            filtered_clips = self.clips.copy()
            
            # Filter by category
            if category and category != "All":
                filtered_clips = [clip for clip in filtered_clips if clip.get("category") == category]
            
            # Filter by context board
            if context_board and context_board != "All":
                filtered_clips = [clip for clip in filtered_clips if clip.get("context_board") == context_board]
            
            # Filter by search text
            if search_text:
                search_text_lower = search_text.lower()
                filtered_clips = [
                    clip for clip in filtered_clips 
                    if search_text_lower in clip.get("content", "").lower()
                ]
            
            # Apply limit
            return filtered_clips[:limit]
        except Exception as e:
            print(f"Error retrieving clips: {e}")
            return []
    
    def delete_clip(self, clip_id):
        """Delete a clip from database"""
        try:
            initial_count = len(self.clips)
            self.clips = [clip for clip in self.clips if clip.get("_id") != clip_id]
            
            if len(self.clips) < initial_count:
                self.save_clips()
                return True
            return False
        except Exception as e:
            print(f"Error deleting clip: {e}")
            return False
    
    def update_clip_category(self, clip_id, category):
        """Update clip category"""
        try:
            for clip in self.clips:
                if clip.get("_id") == clip_id:
                    clip["category"] = category
                    clip["sync_status"] = "updated"
                    self.save_clips()
                    return True
            return False
        except Exception as e:
            print(f"Error updating clip: {e}")
            return False
    
    def update_clip_context_board(self, clip_id, context_board):
        """Update clip context board"""
        try:
            for clip in self.clips:
                if clip.get("_id") == clip_id:
                    clip["context_board"] = context_board
                    clip["sync_status"] = "updated"
                    self.save_clips()
                    return True
            return False
        except Exception as e:
            print(f"Error updating context board: {e}")
            return False
    
    def get_categories(self):
        """Get all unique categories"""
        try:
            categories = set()
            for clip in self.clips:
                categories.add(clip.get("category", "General"))
            
            default_categories = config.get("clip_categories", ["All", "Code", "Chat", "Link", "Image", "Document"])
            return list(categories.union(set(default_categories)))
        except Exception as e:
            print(f"Error getting categories: {e}")
            return config.get("clip_categories", ["All", "Code", "Chat", "Link", "Image", "Document"])
    
    def get_context_boards(self):
        """Get all context boards"""
        try:
            boards = set()
            for clip in self.clips:
                boards.add(clip.get("context_board", "Global"))
            
            default_boards = config.get("context_boards", ["Global", "Coding Project X", "Client Y Chat", "Research Doc"])
            return list(boards.union(set(default_boards)))
        except Exception as e:
            print(f"Error getting context boards: {e}")
            return config.get("context_boards", ["Global", "Coding Project X", "Client Y Chat", "Research Doc"])
    
    def cleanup_old_clips(self):
        """Remove old clips beyond the limit"""
        try:
            max_clips = config.get("max_clipboard_history", 100)
            if len(self.clips) > max_clips:
                self.clips = self.clips[:max_clips]
                self.save_clips()
        except Exception as e:
            print(f"Error cleaning up old clips: {e}")

# Global database instance
db_manager = DatabaseManager()
