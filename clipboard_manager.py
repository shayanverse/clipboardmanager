import pyperclip
import time
import threading
from datetime import datetime
from database import db_manager
from config import config
import os
from PIL import Image, ImageGrab
import io
import base64

class ClipboardManager:
    def __init__(self):
        self.last_clipboard_content = ""
        self.last_clipboard_image = None
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
                
                current_text = pyperclip.paste()
                
                if (current_text and 
                    current_text != self.last_clipboard_content and 
                    len(current_text.strip()) > 0):
                    
                    self.last_clipboard_content = current_text
                    self._process_new_clip(current_text, "text")
                
                
                if time.time() % 3 < 0.1:  
                    try:
                        image = ImageGrab.grabclipboard()
                        if image and self._is_new_image(image):
                            self.last_clipboard_image = image
                            self._process_image_clip(image)
                    except Exception as e:
                        
                        pass
                
                time.sleep(0.5)  
            except Exception as e:
                print(f"Clipboard monitoring error: {e}")
                time.sleep(5)
    
    def _is_new_image(self, image):
        """Check if image is different from last captured image"""
        if self.last_clipboard_image is None:
            return True
        
        try:
            
            old_bytes = io.BytesIO()
            new_bytes = io.BytesIO()
            
            self.last_clipboard_image.save(old_bytes, format='PNG')
            image.save(new_bytes, format='PNG')
            
            return old_bytes.getvalue() != new_bytes.getvalue()
        except:
            return True
    
    def _process_image_clip(self, image):
        """Process new image from clipboard"""
        try:
            
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
           
            metadata = {
                "width": image.width,
                "height": image.height,
                "format": "PNG",
                "size_bytes": len(img_str),
                "auto_categorized": True
            }
            
            
            clip_id = db_manager.insert_clip(
                content=img_str, 
                content_type="image", 
                category="Images", 
                metadata=metadata
            )
            
            if clip_id:
                print(f"New image clip saved: {image.width}x{image.height}")
                
                
                for callback in self.callbacks:
                    try:
                        callback(clip_id, f"Image: {image.width}x{image.height}", "Images")
                    except Exception as e:
                        print(f"Callback error: {e}")
                        
        except Exception as e:
            print(f"Error processing image clip: {e}")
    
    def _process_new_clip(self, content, content_type="text"):
        """Process new clipboard content"""
        try:
            
            detected_type = self._detect_content_type(content)
            category = self._categorize_content(content, detected_type)
            
            
            metadata = {
                "length": len(content),
                "content_type": detected_type,
                "auto_categorized": True
            }
            

            clip_id = db_manager.insert_clip(content, detected_type, category, metadata)
            
            if clip_id:
                print(f"New clip saved: {content[:50]}...")
                
                
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
            return "url"
        elif any(char in content for char in ['{', '}', ';', '()', 'def ', 'class ', 'import ']):
            return "code"
        elif len(content.splitlines()) > 3:
            return "multiline"
        elif len(content) > 100:
            return "text"
        else:
            return "text"
    
    def _categorize_content(self, content, content_type):
        """Categorize content based on its type and content"""
        content_lower = content.lower()
        
        if content_type == "url":
            return "Links"
        elif content_type == "code":
            return "Code"
        elif any(keyword in content_lower for keyword in ['password', 'login', 'auth', 'secret']):
            return "Secure"
        elif any(keyword in content_lower for keyword in ['@gmail.com', '@yahoo.com', '@outlook.com']):
            return "Emails"
        else:
            return "General"
    
    def add_callback(self, callback):
        """Add callback for new clips"""
        self.callbacks.append(callback)
    
    def copy_to_clipboard(self, content, content_type="text"):
        """Copy content to system clipboard"""
        try:
            if content_type == "image":
                
                try:
                    image_data = base64.b64decode(content)
                    image = Image.open(io.BytesIO(image_data))
                    image.save("temp_clipboard.png")  
                    pyperclip.copy("") 
                   
                   
                    pyperclip.copy(f"Image data available - use paste in image applications")
                except Exception as e:
                    print(f"Error processing image for clipboard: {e}")
                    return False
            else:
                pyperclip.copy(content)
            
            self.last_clipboard_content = content
            return True
        except Exception as e:
            print(f"Error copying to clipboard: {e}")
            return False
    
    def get_clipboard_history(self, category=None, search_text=None, limit=50):
        """Get clipboard history"""
        return db_manager.get_clips(category, limit, search_text)
    
    def delete_clip(self, clip_id):
        """Delete a clip"""
        return db_manager.delete_clip(clip_id)
    
    def update_clip_category(self, clip_id, category):
        """Update clip category"""
        return db_manager.update_clip_category(clip_id, category)
    
    def get_categories(self):
        """Get available categories"""
        return db_manager.get_categories()


clipboard_manager = ClipboardManager()