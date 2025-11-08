import pyperclip
import time
import threading
from datetime import datetime
from database import db_manager
from config import config

class ClipboardManager:
    def __init__(self):
        self.last_clipboard_content = ""
        self.is_monitoring = False
        self.monitor_thread = None
        self.callbacks = []
    
    def start_monitoring(self):
        """Start monitoring clipboard for changes"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_clipboard, daemon=True)
        self.monitor_thread.start()
        print("Clipboard monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring clipboard"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        print("Clipboard monitoring stopped")
    
    def _monitor_clipboard(self):
        """Monitor clipboard for changes in a separate thread"""
        while self.is_monitoring:
            try:
                current_content = pyperclip.paste()
                
                if (current_content and 
                    current_content != self.last_clipboard_content and 
                    len(current_content.strip()) > 0):
                    
                    self.last_clipboard_content = current_content
                    self._process_new_clip(current_content)
                
                time.sleep(1)
            except Exception as e:
                print(f"Clipboard monitoring error: {e}")
                time.sleep(5)
    
    def _process_new_clip(self, content):
        """Process new clipboard content"""
        try:
            # Determine content type and category
            content_type = self._detect_content_type(content)
            category = self._categorize_content(content, content_type)
            
            # Prepare metadata
            metadata = {
                "length": len(content),
                "content_type": content_type,
                "auto_categorized": True,
                "source": "Unknown"
            }
            
            # Save to database
            clip_id = db_manager.insert_clip(content, content_type, category, metadata)
            
            if clip_id:
                print(f"New clip saved: {content[:50]}...")
                
                # Notify callbacks
                for callback in self.callbacks:
                    try:
                        callback(clip_id, content, category)
                    except Exception as e:
                        print(f"Callback error: {e}")
                        
        except Exception as e:
            print(f"Error processing new clip: {e}")
    
    def _detect_content_type(self, content):
        """Detect the type of content"""
        content_lower = content.lower().strip()
        
        if content_lower.startswith(('http://', 'https://', 'www.')):
            return "link"
        elif any(char in content for char in ['{', '}', ';', '()', 'def ', 'class ', 'import ', 'function ']):
            return "code"
        elif len(content.splitlines()) > 3:
            return "chat"
        else:
            return "text"
    
    def _categorize_content(self, content, content_type):
        """Categorize content based on its type and content"""
        if content_type == "link":
            return "Link"
        elif content_type == "code":
            return "Code"
        elif content_type == "chat":
            return "Chat"
        else:
            return "General"
    
    def add_callback(self, callback):
        """Add callback for new clips"""
        self.callbacks.append(callback)
    
    def copy_to_clipboard(self, content):
        """Copy content to system clipboard"""
        try:
            pyperclip.copy(content)
            self.last_clipboard_content = content
            return True
        except Exception as e:
            print(f"Error copying to clipboard: {e}")
            return False
    
    def get_clipboard_history(self, category=None, context_board=None, search_text=None, limit=50):
        """Get clipboard history"""
        return db_manager.get_clips(category, context_board, search_text, limit)
    
    def delete_clip(self, clip_id):
        """Delete a clip"""
        return db_manager.delete_clip(clip_id)
    
    def update_clip_category(self, clip_id, category):
        """Update clip category"""
        return db_manager.update_clip_category(clip_id, category)
    
    def update_clip_context_board(self, clip_id, context_board):
        """Update clip context board"""
        return db_manager.update_clip_context_board(clip_id, context_board)
    
    def get_categories(self):
        """Get available categories"""
        return db_manager.get_categories()
    
    def get_context_boards(self):
        """Get available context boards"""
        return db_manager.get_context_boards()

# Global clipboard manager instance
clipboard_manager = ClipboardManager()
