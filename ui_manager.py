import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from config import config
from clipboard_manager import clipboard_manager
from sync_manager import sync_manager

class ModernButton(tk.Canvas):
    def __init__(self, parent, text, command=None, width=100, height=30, 
                 bg_color="#007ACC", text_color="white", corner_radius=6):
        super().__init__(parent, width=width, height=height, 
                        highlightthickness=0, bg=parent.cget("bg"))
        self.command = command
        self.bg_color = bg_color
        self.text_color = text_color
        self.corner_radius = corner_radius
        self.width = width
        self.height = height
        
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
        self._draw_button(text)
    
    def _draw_button(self, text, hover=False):
        self.delete("all")
        
        # Draw rounded rectangle
        color = self.bg_color if not hover else self._lighten_color(self.bg_color, 20)
        
        self.create_rounded_rect(2, 2, self.width-2, self.height-2, 
                               self.corner_radius, fill=color, outline=color)
        
        # Draw text
        self.create_text(self.width//2, self.height//2, text=text, 
                        fill=self.text_color, font=("Segoe UI", 9))
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [x1+radius, y1,
                 x2-radius, y1,
                 x2, y1,
                 x2, y1+radius,
                 x2, y2-radius,
                 x2, y2,
                 x2-radius, y2,
                 x1+radius, y2,
                 x1, y2,
                 x1, y2-radius,
                 x1, y1+radius,
                 x1, y1]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _lighten_color(self, color, percent):
        """Lighten color by percent"""
        # Simple color lightening for demo
        return color
    
    def _on_click(self, event):
        if self.command:
            self.command()
    
    def _on_enter(self, event):
        self._draw_button(self.find_withtag("text")[0], hover=True)
    
    def _on_leave(self, event):
        self._draw_button(self.find_withtag("text")[0], hover=False)

class ClipCard(tk.Frame):
    def __init__(self, parent, clip_data, on_copy, on_delete, on_pin):
        super().__init__(parent, bg="white", relief="raised", bd=1)
        self.clip_data = clip_data
        self.on_copy = on_copy
        self.on_delete = on_delete
        self.on_pin = on_pin
        
        self._create_widgets()
    
    def _create_widgets(self):
        # Header with category and actions
        header_frame = tk.Frame(self, bg="white")
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # Category badge
        category = self.clip_data.get("category", "General")
        category_color = {
            "Code": "#E1F5FE",
            "Chat": "#F3E5F5", 
            "Link": "#E8F5E8",
            "Image": "#FFF3E0"
        }.get(category, "#F5F5F5")
        
        category_text_color = {
            "Code": "#01579B",
            "Chat": "#4A148C",
            "Link": "#1B5E20", 
            "Image": "#E65100"
        }.get(category, "#424242")
        
        category_label = tk.Label(header_frame, text=category.upper(), 
                                bg=category_color, fg=category_text_color,
                                font=("Segoe UI", 8, "bold"), padx=6, pady=2)
        category_label.pack(side=tk.LEFT)
        
        # Action buttons
        actions_frame = tk.Frame(header_frame, bg="white")
        actions_frame.pack(side=tk.RIGHT)
        
        # Copy button
        copy_btn = tk.Label(actions_frame, text="📋", bg="white", 
                           font=("Segoe UI", 10), cursor="hand2")
        copy_btn.pack(side=tk.LEFT, padx=2)
        copy_btn.bind("<Button-1>", lambda e: self.on_copy(self.clip_data["_id"]))
        
        # Delete button  
        delete_btn = tk.Label(actions_frame, text="🗑️", bg="white",
                            font=("Segoe UI", 10), cursor="hand2")
        delete_btn.pack(side=tk.LEFT, padx=2)
        delete_btn.bind("<Button-1>", lambda e: self.on_delete(self.clip_data["_id"]))
        
        # Content
        content_frame = tk.Frame(self, bg="white")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        content = self.clip_data.get("content", "")
        content_preview = content[:100] + "..." if len(content) > 100 else content
        
        content_label = tk.Label(content_frame, text=content_preview, bg="white",
                                fg="#424242", font=("Segoe UI", 9), wraplength=250,
                                justify=tk.LEFT, anchor=tk.W)
        content_label.pack(fill=tk.X)
        
        # Footer with metadata
        footer_frame = tk.Frame(self, bg="white")
        footer_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        timestamp = self._format_time(self.clip_data.get("timestamp"))
        time_label = tk.Label(footer_frame, text=timestamp, bg="white",
                             fg="#757575", font=("Segoe UI", 8))
        time_label.pack(side=tk.LEFT)
        
        source = self.clip_data.get("metadata", {}).get("source", "Unknown")
        source_label = tk.Label(footer_frame, text=f"From {source}", bg="white",
                              fg="#757575", font=("Segoe UI", 8))
        source_label.pack(side=tk.RIGHT)
    
    def _format_time(self, timestamp_str):
        """Format timestamp for display"""
        if not timestamp_str:
            return "Just now"
        
        try:
            from datetime import datetime
            if isinstance(timestamp_str, str):
                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                dt = timestamp_str
            
            now = datetime.now()
            diff = now - dt
            
            if diff.days > 0:
                return f"{diff.days}d ago"
            elif diff.seconds > 3600:
                return f"{diff.seconds // 3600}h ago"
            elif diff.seconds > 60:
                return f"{diff.seconds // 60}m ago"
            else:
                return "Just now"
        except:
            return "Unknown"

class UIManager:
    def __init__(self):
        self.root = None
        self.current_category = "All"
        self.current_context_board = "Global"
        self.search_text = ""
        
        # Colors
        self.colors = {
            "bg": "#F5F7FA",
            "sidebar_bg": "#FFFFFF",
            "card_bg": "#FFFFFF",
            "accent": "#007ACC",
            "accent_light": "#E3F2FD",
            "text_primary": "#424242",
            "text_secondary": "#757575",
            "border": "#E0E0E0"
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the modern glassmorphism UI"""
        self.root = tk.Tk()
        self.root.title(f"{config.app_name} v{config.version}")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        self.root.configure(bg=self.colors["bg"])
        
        # Set window attributes for modern look
        self.root.attributes('-alpha', 0.95)  # Slight transparency
        
        # Create main container with rounded corners simulation
        self._create_main_layout()
        self._setup_bindings()
        
        # Start services
        clipboard_manager.add_callback(self.on_new_clip)
        clipboard_manager.start_monitoring()
        sync_manager.start_sync()
        
        # Load initial data
        self.refresh_clips()
    
    def _create_main_layout(self):
        """Create the main glassmorphism layout"""
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors["bg"], padx=20, pady=20)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header with search and actions
        self._create_header(main_container)
        
        # Main content area
        content_container = tk.Frame(main_container, bg=self.colors["bg"])
        content_container.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # Sidebar and clips area
        self._create_sidebar(content_container)
        self._create_clips_area(content_container)
        
        # Status bar
        self._create_status_bar(main_container)
    
    def _create_header(self, parent):
        """Create the top header with search and actions"""
        header_frame = tk.Frame(parent, bg=self.colors["bg"])
        header_frame.pack(fill=tk.X)
        
        # App icon and name
        icon_frame = tk.Frame(header_frame, bg=self.colors["bg"])
        icon_frame.pack(side=tk.LEFT)
        
        # App icon (simulated with colored circle)
        icon_canvas = tk.Canvas(icon_frame, width=32, height=32, 
                               bg=self.colors["bg"], highlightthickness=0)
        icon_canvas.pack(side=tk.LEFT)
        icon_canvas.create_oval(4, 4, 28, 28, fill=self.colors["accent"], outline="")
        icon_canvas.create_text(16, 16, text="TL", fill="white", 
                               font=("Segoe UI", 10, "bold"))
        
        app_name = tk.Label(icon_frame, text="Thought-Link", 
                           bg=self.colors["bg"], fg=self.colors["text_primary"],
                           font=("Segoe UI", 14, "bold"))
        app_name.pack(side=tk.LEFT, padx=(10, 0))
        
        # Search bar
        search_frame = tk.Frame(header_frame, bg=self.colors["bg"])
        search_frame.pack(side=tk.LEFT, padx=40, fill=tk.X, expand=True)
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                               font=("Segoe UI", 10), relief="flat",
                               bg="white", fg=self.colors["text_primary"],
                               insertbackground=self.colors["text_primary"])
        search_entry.pack(fill=tk.X, ipady=8)
        search_entry.insert(0, "Search all clips...")
        search_entry.bind('<KeyRelease>', self.on_search_changed)
        search_entry.bind('<FocusIn>', lambda e: search_entry.delete(0, tk.END) 
                         if search_entry.get() == "Search all clips..." else None)
        search_entry.bind('<FocusOut>', lambda e: search_entry.insert(0, "Search all clips...") 
                         if not search_entry.get() else None)
        
        # Action buttons
        actions_frame = tk.Frame(header_frame, bg=self.colors["bg"])
        actions_frame.pack(side=tk.RIGHT)
        
        # New Clip button
        new_clip_btn = ModernButton(actions_frame, "New Clip", 
                                  command=self.create_new_clip,
                                  bg_color=self.colors["accent_light"],
                                  text_color=self.colors["accent"],
                                  width=80, height=30)
        new_clip_btn.pack(side=tk.LEFT, padx=5)
        
        # Sync Devices button
        sync_btn = ModernButton(actions_frame, "Sync Devices",
                               command=self.manual_sync,
                               bg_color=self.colors["accent_light"], 
                               text_color=self.colors["accent"],
                               width=100, height=30)
        sync_btn.pack(side=tk.LEFT, padx=5)
        
        # History button
        history_btn = ModernButton(actions_frame, "History",
                                  command=self.show_history,
                                  bg_color=self.colors["accent_light"],
                                  text_color=self.colors["accent"],
                                  width=80, height=30)
        history_btn.pack(side=tk.LEFT, padx=5)
    
    def _create_sidebar(self, parent):
        """Create the left sidebar"""
        sidebar_frame = tk.Frame(parent, bg=self.colors["sidebar_bg"], 
                                relief="raised", bd=1, width=200)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        sidebar_frame.pack_propagate(False)
        
        # All Clips section
        all_clips_frame = tk.Frame(sidebar_frame, bg=self.colors["sidebar_bg"])
        all_clips_frame.pack(fill=tk.X, pady=(20, 10), padx=15)
        
        all_clips_btn = tk.Label(all_clips_frame, text="📋 All Clips", 
                                bg=self.colors["sidebar_bg"], 
                                fg=self.colors["text_primary"],
                                font=("Segoe UI", 11, "bold"),
                                cursor="hand2", anchor=tk.W)
        all_clips_btn.pack(fill=tk.X)
        all_clips_btn.bind("<Button-1>", lambda e: self.select_category("All"))
        
        # Context Boards section
        context_frame = tk.Frame(sidebar_frame, bg=self.colors["sidebar_bg"])
        context_frame.pack(fill=tk.X, pady=(20, 0), padx=15)
        
        context_label = tk.Label(context_frame, text="CONTEXT BOARDS",
                                bg=self.colors["sidebar_bg"],
                                fg=self.colors["text_secondary"],
                                font=("Segoe UI", 9, "bold"),
                                anchor=tk.W)
        context_label.pack(fill=tk.X)
        
        # Context boards list
        boards = clipboard_manager.get_context_boards()
        for board in boards:
            board_btn = tk.Label(context_frame, text=f"• {board}",
                                bg=self.colors["sidebar_bg"],
                                fg=self.colors["text_primary"],
                                font=("Segoe UI", 10),
                                cursor="hand2", anchor=tk.W)
            board_btn.pack(fill=tk.X, pady=(5, 0))
            board_btn.bind("<Button-1>", lambda e, b=board: self.select_context_board(b))
        
        # Bottom section
        bottom_frame = tk.Frame(sidebar_frame, bg=self.colors["sidebar_bg"])
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)
        
        # Settings
        settings_btn = tk.Label(bottom_frame, text="⚙️ Settings",
                              bg=self.colors["sidebar_bg"],
                              fg=self.colors["text_primary"],
                              font=("Segoe UI", 10),
                              cursor="hand2", anchor=tk.W)
        settings_btn.pack(fill=tk.X, padx=15, pady=5)
        settings_btn.bind("<Button-1>", lambda e: self.show_settings())
        
        # App logo at bottom
        logo_frame = tk.Frame(bottom_frame, bg=self.colors["sidebar_bg"])
        logo_frame.pack(fill=tk.X, padx=15, pady=(10, 0))
        
        logo = tk.Label(logo_frame, text="T-L", bg=self.colors["accent"],
                       fg="white", font=("Segoe UI", 8, "bold"),
                       width=4, height=1)
        logo.pack()
    
    def _create_clips_area(self, parent):
        """Create the main clips display area"""
        clips_container = tk.Frame(parent, bg=self.colors["bg"])
        clips_container.pack(fill=tk.BOTH, expand=True)
        
        # Context board tabs
        self._create_context_tabs(clips_container)
        
        # Clips display area
        self._create_clips_display(clips_container)
    
    def _create_context_tabs(self, parent):
        """Create context board tabs"""
        tabs_frame = tk.Frame(parent, bg=self.colors["bg"])
        tabs_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Context board tabs
        boards = clipboard_manager.get_context_boards()
        self.context_buttons = {}
        
        for board in boards:
            btn = tk.Label(tabs_frame, text=board, 
                          bg=self.colors["bg"] if board != self.current_context_board else self.colors["accent"],
                          fg=self.colors["text_primary"] if board != self.current_context_board else "white",
                          font=("Segoe UI", 10, "bold" if board == self.current_context_board else "normal"),
                          padx=15, pady=8, cursor="hand2")
            btn.pack(side=tk.LEFT, padx=(0, 10))
            btn.bind("<Button-1>", lambda e, b=board: self.select_context_board(b))
            self.context_buttons[board] = btn
        
        # Sort by dropdown
        sort_frame = tk.Frame(tabs_frame, bg=self.colors["bg"])
        sort_frame.pack(side=tk.RIGHT)
        
        sort_label = tk.Label(sort_frame, text="Sort by: Newest", 
                             bg=self.colors["bg"], fg=self.colors["text_secondary"],
                             font=("Segoe UI", 9), cursor="hand2")
        sort_label.pack()
        sort_label.bind("<Button-1>", self.show_sort_options)
    
    def _create_clips_display(self, parent):
        """Create the clips cards display"""
        # Categories filter
        categories_frame = tk.Frame(parent, bg=self.colors["bg"])
        categories_frame.pack(fill=tk.X, pady=(0, 15))
        
        categories = clipboard_manager.get_categories()
        self.category_buttons = {}
        
        for category in categories:
            btn = tk.Label(categories_frame, text=category,
                          bg=self.colors["accent"] if category == self.current_category else self.colors["accent_light"],
                          fg="white" if category == self.current_category else self.colors["accent"],
                          font=("Segoe UI", 9, "bold"),
                          padx=12, pady=6, cursor="hand2")
            btn.pack(side=tk.LEFT, padx=(0, 8))
            btn.bind("<Button-1>", lambda e, c=category: self.select_category(c))
            self.category_buttons[category] = btn
        
        # Clips canvas with scrollbar
        canvas_frame = tk.Frame(parent, bg=self.colors["bg"])
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg=self.colors["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.colors["bg"])
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind mousewheel to canvas
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
    
    def _create_status_bar(self, parent):
        """Create bottom status bar"""
        status_frame = tk.Frame(parent, bg=self.colors["sidebar_bg"], height=25)
        status_frame.pack(fill=tk.X, pady=(15, 0))
        status_frame.pack_propagate(False)
        
        status_text = tk.Label(status_frame, 
                              text="Synced across 3 devices • Last update: Just now",
                              bg=self.colors["sidebar_bg"],
                              fg=self.colors["text_secondary"],
                              font=("Segoe UI", 8))
        status_text.pack(side=tk.LEFT, padx=15, pady=4)
        
        self.status_label = status_text
        
        # Update status periodically
        self.update_status()
    
    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def update_status(self):
        """Update status bar periodically"""
        status = sync_manager.get_sync_status()
        if status["last_sync"]:
            from datetime import datetime
            last_sync = datetime.fromtimestamp(status["last_sync"])
            time_diff = datetime.now() - last_sync
            
            if time_diff.seconds < 60:
                time_text = "Just now"
            elif time_diff.seconds < 3600:
                time_text = f"{time_diff.seconds // 60} minutes ago"
            else:
                time_text = f"{time_diff.seconds // 3600} hours ago"
            
            status_text = f"Synced across {status['synced_devices']} devices • Last update: {time_text}"
            self.status_label.config(text=status_text)
        
        self.root.after(30000, self.update_status)  # Update every 30 seconds
    
    def on_new_clip(self, clip_id, content, category):
        """Callback when new clip is detected"""
        self.root.after(0, self.refresh_clips)
    
    def refresh_clips(self):
        """Refresh the clips display"""
        try:
            # Clear current clips
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            
            # Get clips from database
            clips = clipboard_manager.get_clipboard_history(
                category=self.current_category if self.current_category != "All" else None,
                context_board=self.current_context_board,
                search_text=self.search_text if self.search_text != "Search all clips..." else None,
                limit=50
            )
            
            # Display clips in a grid
            row, col = 0, 0
            max_cols = 3
            
            for clip in clips:
                card = ClipCard(self.scrollable_frame, clip, 
                               self.copy_clip, self.delete_clip, self.pin_clip)
                card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            
            # Configure grid weights
            for i in range(max_cols):
                self.scrollable_frame.columnconfigure(i, weight=1)
            
        except Exception as e:
            print(f"Error refreshing clips: {e}")
    
    def copy_clip(self, clip_id):
        """Copy clip to clipboard"""
        clips = clipboard_manager.get_clipboard_history(limit=1000)
        for clip in clips:
            if clip.get("_id") == clip_id:
                if clipboard_manager.copy_to_clipboard(clip.get("content", "")):
                    self.show_notification("Copied to clipboard!")
                break
    
    def delete_clip(self, clip_id):
        """Delete a clip"""
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this clip?"):
            if clipboard_manager.delete_clip(clip_id):
                self.refresh_clips()
                self.show_notification("Clip deleted")
    
    def pin_clip(self, clip_id):
        """Pin a clip (placeholder)"""
        self.show_notification("Clip pinned")
    
    def select_category(self, category):
        """Select a category"""
        self.current_category = category
        
        # Update button styles
        for cat, btn in self.category_buttons.items():
            btn.config(bg=self.colors["accent"] if cat == category else self.colors["accent_light"],
                      fg="white" if cat == category else self.colors["accent"])
        
        self.refresh_clips()
    
    def select_context_board(self, board):
        """Select a context board"""
        self.current_context_board = board
        
        # Update button styles
        for b, btn in self.context_buttons.items():
            btn.config(bg=self.colors["accent"] if b == board else self.colors["bg"],
                      fg="white" if b == board else self.colors["text_primary"],
                      font=("Segoe UI", 10, "bold" if b == board else "normal"))
        
        self.refresh_clips()
    
    def on_search_changed(self, event=None):
        """Handle search text change"""
        self.search_text = self.search_var.get()
        self.root.after(500, self.refresh_clips)
    
    def create_new_clip(self):
        """Create a new manual clip"""
        # Simple implementation - could be enhanced with a dialog
        content = "New clip created at " + time.strftime("%H:%M:%S")
        clipboard_manager.copy_to_clipboard(content)
        self.show_notification("New clip created!")
    
    def manual_sync(self):
        """Trigger manual synchronization"""
        if sync_manager.manual_sync():
            self.show_notification("Sync completed!")
            self.refresh_clips()
        else:
            self.show_notification("Sync failed!")
    
    def show_history(self):
        """Show history view"""
        self.show_notification("History view")
    
    def show_settings(self):
        """Show settings dialog"""
        self.show_notification("Settings")
    
    def show_sort_options(self, event):
        """Show sort options"""
        self.show_notification("Sort options")
    
    def show_notification(self, message):
        """Show a temporary notification"""
        # Simple notification - could be enhanced with a proper toast
        print(f"Notification: {message}")
    
    def _setup_bindings(self):
        """Setup keyboard bindings"""
        self.root.bind('<Control-r>', lambda e: self.refresh_clips())
        self.root.bind('<Control-f>', lambda e: self.search_entry.focus())
        self.root.protocol("WM_DELETE_WINDOW", self.shutdown)
    
    def run(self):
        """Start the UI main loop"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.shutdown()
    
    def shutdown(self):
        """Clean shutdown of the application"""
        clipboard_manager.stop_monitoring()
        sync_manager.stop_sync()
        if self.root:
            self.root.quit()
        print("Application shutdown successfully")

# Global UI instance
ui_manager = UIManager()
