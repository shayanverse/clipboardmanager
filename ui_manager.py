# import tkinter as tk
# from tkinter import ttk, messagebox, scrolledtext
# import threading
# from PIL import Image, ImageTk, ImageGrab
# import os
# import io
# import base64
# from config import config
# from clipboard_manager import clipboard_manager
# from sync_manager import sync_manager

# class UIManager:
#     def __init__(self):
#         self.root = None
#         self.current_category = "All"
#         self.search_text = ""
#         self.clips_tree = None
#         self.category_var = None
#         self.search_var = None
#         self.status_label = None
#         self.setup_ui()
    
#     def setup_ui(self):
#         """Setup the main UI"""
#         self.root = tk.Tk()
#         self.root.title(f"{config.app_name} v{config.version}")
#         self.root.geometry("900x700")
#         self.root.minsize(700, 500)
        
#         # Set window icon
#         try:
#             icon_path = config.assets_dir / "icon.ico"
#             if icon_path.exists():
#                 self.root.iconbitmap(str(icon_path))
#         except:
#             pass
        
#         self._create_menu()
#         self._create_main_layout()
#         self._setup_bindings()
        
#         # Start clipboard monitoring
#         clipboard_manager.add_callback(self.on_new_clip)
#         clipboard_manager.start_monitoring()
        
#         # Start sync manager
#         sync_manager.start_sync()
        
#         # Load initial data
#         self.refresh_clips()
    
#     def _create_menu(self):
#         """Create application menu"""
#         menubar = tk.Menu(self.root)
        
#         # File menu
#         file_menu = tk.Menu(menubar, tearoff=0)
#         file_menu.add_command(label="Settings", command=self.show_settings)
#         file_menu.add_separator()
#         file_menu.add_command(label="Exit", command=self.shutdown)
#         menubar.add_cascade(label="File", menu=file_menu)
        
#         # Edit menu
#         edit_menu = tk.Menu(menubar, tearoff=0)
#         edit_menu.add_command(label="Clear All", command=self.clear_all_clips)
#         menubar.add_cascade(label="Edit", menu=edit_menu)
        
#         # View menu
#         view_menu = tk.Menu(menubar, tearoff=0)
#         view_menu.add_command(label="Refresh", command=self.refresh_clips)
#         view_menu.add_command(label="Clear Search", command=self.clear_search)
#         menubar.add_cascade(label="View", menu=view_menu)
        
#         # Sync menu
#         sync_menu = tk.Menu(menubar, tearoff=0)
#         sync_menu.add_command(label="Sync Now", command=self.manual_sync)
#         sync_menu.add_command(label="Sync Status", command=self.show_sync_status)
#         menubar.add_cascade(label="Sync", menu=sync_menu)
        
#         self.root.config(menu=menubar)
    
#     def _create_main_layout(self):
#         """Create main UI layout"""
#         # Main container
#         main_container = ttk.Frame(self.root, padding="10")
#         main_container.pack(fill=tk.BOTH, expand=True)
        
#         # Header
#         header_frame = ttk.Frame(main_container)
#         header_frame.pack(fill=tk.X, pady=(0, 10))
        
#         ttk.Label(header_frame, text=config.app_name, font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        
#         # Status label
#         self.status_label = ttk.Label(header_frame, text="Ready", foreground="green")
#         self.status_label.pack(side=tk.RIGHT)
        
#         # Controls frame
#         controls_frame = ttk.Frame(main_container)
#         controls_frame.pack(fill=tk.X, pady=(0, 10))
        
#         # Category filter
#         ttk.Label(controls_frame, text="Category:").grid(row=0, column=0, padx=(0, 5))
#         self.category_var = tk.StringVar(value="All")
#         categories = ["All"] + clipboard_manager.get_categories()
#         self.category_combo = ttk.Combobox(controls_frame, textvariable=self.category_var, 
#                                          values=categories, state="readonly", width=15)
#         self.category_combo.grid(row=0, column=1, padx=(0, 10))
#         self.category_combo.bind('<<ComboboxSelected>>', self.on_category_changed)
        
#         # Search box
#         ttk.Label(controls_frame, text="Search:").grid(row=0, column=2, padx=(10, 5))
#         self.search_var = tk.StringVar()
#         self.search_entry = ttk.Entry(controls_frame, textvariable=self.search_var, width=30)
#         self.search_entry.grid(row=0, column=3, padx=(0, 10))
#         self.search_entry.bind('<KeyRelease>', self.on_search_changed)
        
#         # Clear search button
#         ttk.Button(controls_frame, text="Clear", command=self.clear_search).grid(row=0, column=4)
        
#         # Clips frame with scrollbar
#         tree_frame = ttk.Frame(main_container)
#         tree_frame.pack(fill=tk.BOTH, expand=True)
        
#         # Create treeview for clips
#         columns = ("Time", "Category", "Content", "Type", "ID")
#         self.clips_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)
        
#         # Configure columns
#         self.clips_tree.heading("Time", text="Time", command=lambda: self.sort_treeview("Time", False))
#         self.clips_tree.heading("Category", text="Category", command=lambda: self.sort_treeview("Category", False))
#         self.clips_tree.heading("Content", text="Content", command=lambda: self.sort_treeview("Content", False))
#         self.clips_tree.heading("Type", text="Type", command=lambda: self.sort_treeview("Type", False))
#         self.clips_tree.heading("ID", text="ID")
        
#         self.clips_tree.column("Time", width=120)
#         self.clips_tree.column("Category", width=100)
#         self.clips_tree.column("Content", width=450)
#         self.clips_tree.column("Type", width=80)
#         self.clips_tree.column("ID", width=0, stretch=False)  # Hidden column
        
#         # Scrollbar
#         scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.clips_tree.yview)
#         self.clips_tree.configure(yscrollcommand=scrollbar.set)
        
#         # Grid treeview and scrollbar
#         self.clips_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
#         scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
#         # Bind events
#         self.clips_tree.bind("<Double-1>", self.on_clip_double_click)
#         self.clips_tree.bind("<Button-3>", self.show_context_menu)
        
#         # Action buttons frame
#         buttons_frame = ttk.Frame(main_container)
#         buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
#         ttk.Button(buttons_frame, text="Copy Selected", command=self.copy_selected_clip).pack(side=tk.LEFT, padx=(0, 10))
#         ttk.Button(buttons_frame, text="Delete Selected", command=self.delete_selected_clip).pack(side=tk.LEFT, padx=(0, 10))
#         ttk.Button(buttons_frame, text="Change Category", command=self.change_category).pack(side=tk.LEFT, padx=(0, 10))
#         ttk.Button(buttons_frame, text="Refresh", command=self.refresh_clips).pack(side=tk.LEFT)
#         ttk.Button(buttons_frame, text="Clear All", command=self.clear_all_clips).pack(side=tk.LEFT, padx=(10, 0))
    
#     def _setup_bindings(self):
#         """Setup keyboard bindings"""
#         self.root.bind('<Control-r>', lambda e: self.refresh_clips())
#         self.root.bind('<Control-f>', lambda e: self.search_entry.focus())
#         self.root.bind('<Delete>', lambda e: self.delete_selected_clip())
#         self.root.protocol("WM_DELETE_WINDOW", self.shutdown)
    
#     def show_context_menu(self, event):
#         """Show right-click context menu"""
#         item = self.clips_tree.identify_row(event.y)
#         if item:
#             self.clips_tree.selection_set(item)
#             context_menu = tk.Menu(self.root, tearoff=0)
#             context_menu.add_command(label="Copy", command=self.copy_selected_clip)
#             context_menu.add_command(label="Delete", command=self.delete_selected_clip)
#             context_menu.add_separator()
#             context_menu.add_command(label="View Details", command=self.show_clip_details)
#             context_menu.tk_popup(event.x_root, event.y_root)
    
#     def show_clip_details(self):
#         """Show detailed view of selected clip"""
#         selection = self.clips_tree.selection()
#         if not selection:
#             return
        
#         item = selection[0]
#         values = self.clips_tree.item(item, "values")
#         clip_id = values[4]
     
#         clips = clipboard_manager.get_clipboard_history(limit=1000)
#         clip_data = None
#         for clip in clips:
#             if clip.get("_id") == clip_id:
#                 clip_data = clip
#                 break
        
#         if not clip_data:
#             return
        
        
#         details_window = tk.Toplevel(self.root)
#         details_window.title("Clip Details")
#         details_window.geometry("600x400")
#         details_window.transient(self.root)
#         details_window.grab_set()
        
        
#         content_frame = ttk.Frame(details_window)
#         content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
#         ttk.Label(content_frame, text="Content:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
#         content_text = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, width=70, height=15)
#         content_text.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
#         if clip_data.get("content_type") == "image":
#             content_text.insert(tk.END, f"Image Data: {clip_data.get('metadata', {}).get('width', 'Unknown')}x{clip_data.get('metadata', {}).get('height', 'Unknown')} pixels")
#             content_text.config(state=tk.DISABLED)
#         else:
#             content_text.insert(tk.END, clip_data.get("content", ""))
        
        
#         meta_frame = ttk.Frame(content_frame)
#         meta_frame.pack(fill=tk.X, pady=(10, 0))
        
#         metadata = clip_data.get("metadata", {})
#         ttk.Label(meta_frame, text=f"Type: {clip_data.get('content_type', 'Unknown')}").grid(row=0, column=0, sticky=tk.W)
#         ttk.Label(meta_frame, text=f"Category: {clip_data.get('category', 'General')}").grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
#         ttk.Label(meta_frame, text=f"Length: {metadata.get('length', 'N/A')}").grid(row=1, column=0, sticky=tk.W)
#         ttk.Label(meta_frame, text=f"Time: {self._format_time_detailed(clip_data.get('timestamp'))}").grid(row=1, column=1, sticky=tk.W, padx=(20, 0))
    
#     def sort_treeview(self, column, reverse):
#         """Sort treeview by column"""
#         data = [(self.clips_tree.set(child, column), child) for child in self.clips_tree.get_children('')]
#         data.sort(reverse=reverse)
        
#         for index, (_, child) in enumerate(data):
#             self.clips_tree.move(child, '', index)
        
#         self.clips_tree.heading(column, command=lambda: self.sort_treeview(column, not reverse))
    
#     def on_new_clip(self, clip_id, content, category):
#         """Callback when new clip is detected"""
#         self.root.after(0, self._add_clip_to_ui, clip_id, content, category)
    
#     def _add_clip_to_ui(self, clip_id, content, category):
#         """Add new clip to UI (thread-safe)"""
#         try:
            
#             clips = clipboard_manager.get_clipboard_history(limit=1)
#             clip_data = clips[0] if clips else None
            
#             content_type = clip_data.get("content_type", "text") if clip_data else "text"
#             display_content = self._truncate_content(content, content_type)
            
         
#             self.clips_tree.insert("", 0, values=(
#                 self._format_time(None),
#                 category,
#                 display_content,
#                 content_type.title(),
#                 clip_id
#             ))
            
           
#             max_display = min(config.get("max_clipboard_history", 100), 50)
#             if len(self.clips_tree.get_children()) > max_display:
#                 children = self.clips_tree.get_children()
#                 self.clips_tree.delete(children[-1])
            
#             self.status_label.config(text="New clip added!", foreground="blue")
#             self.root.after(3000, lambda: self.status_label.config(text="Ready", foreground="green"))
            
#         except Exception as e:
#             print(f"Error adding clip to UI: {e}")
    
#     def refresh_clips(self):
#         """Refresh the clips list"""
#         try:
        
#             for item in self.clips_tree.get_children():
#                 self.clips_tree.delete(item)
            
            
#             category = self.current_category if self.current_category != "All" else None
#             clips = clipboard_manager.get_clipboard_history(category, self.search_text, limit=100)
            
#             # Add clips to treeview
#             for clip in clips:
#                 content_type = clip.get("content_type", "text")
#                 display_content = self._truncate_content(clip.get("content", ""), content_type)
                
#                 self.clips_tree.insert("", "end", values=(
#                     self._format_time(clip.get("timestamp")),
#                     clip.get("category", "General"),
#                     display_content,
#                     content_type.title(),
#                     clip.get("_id")
#                 ))
            
#             self.status_label.config(text=f"Loaded {len(clips)} clips", foreground="green")
#             self.root.after(3000, lambda: self.status_label.config(text="Ready", foreground="green"))
            
#         except Exception as e:
#             messagebox.showerror("Error", f"Failed to refresh clips: {e}")
    
#     def on_category_changed(self, event=None):
#         """Handle category filter change"""
#         self.current_category = self.category_var.get()
#         self.refresh_clips()
    
#     def on_search_changed(self, event=None):
#         """Handle search text change"""
#         self.search_text = self.search_var.get().strip()
#         self.root.after(500, self.refresh_clips)  
    
#     def clear_search(self):
#         """Clear search text"""
#         self.search_var.set("")
#         self.search_text = ""
#         self.refresh_clips()
    
#     def on_clip_double_click(self, event):
#         """Handle double-click on clip"""
#         self.copy_selected_clip()
    
#     def copy_selected_clip(self):
#         """Copy selected clip to clipboard"""
#         selection = self.clips_tree.selection()
#         if not selection:
#             messagebox.showwarning("Warning", "Please select a clip to copy")
#             return
        
#         item = selection[0]
#         values = self.clips_tree.item(item, "values")
#         clip_id = values[4]
#         content_type = values[3].lower()
        
        
#         clips = clipboard_manager.get_clipboard_history(limit=1000)
#         clip_content = ""
#         for clip in clips:
#             if clip.get("_id") == clip_id:
#                 clip_content = clip.get("content", "")
#                 content_type = clip.get("content_type", "text")
#                 break
        
#         if clip_content and clipboard_manager.copy_to_clipboard(clip_content, content_type):
#             self.status_label.config(text="Copied to clipboard!", foreground="blue")
#             self.root.after(2000, lambda: self.status_label.config(text="Ready", foreground="green"))
#         else:
#             messagebox.showerror("Error", "Failed to copy to clipboard")
    
#     def delete_selected_clip(self):
#         """Delete selected clip"""
#         selection = self.clips_tree.selection()
#         if not selection:
#             messagebox.showwarning("Warning", "Please select a clip to delete")
#             return
        
#         item = selection[0]
#         values = self.clips_tree.item(item, "values")
#         clip_id = values[4]
        
#         if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this clip?"):
#             if clipboard_manager.delete_clip(clip_id):
#                 self.clips_tree.delete(item)
#                 self.status_label.config(text="Clip deleted", foreground="orange")
#                 self.root.after(3000, lambda: self.status_label.config(text="Ready", foreground="green"))
#             else:
#                 messagebox.showerror("Error", "Failed to delete clip")
    
#     def clear_all_clips(self):
#         """Clear all clips"""
#         if messagebox.askyesno("Confirm Clear", "Are you sure you want to delete ALL clips? This cannot be undone."):
           
#             messagebox.showinfo("Info", "This feature will be implemented in the next version")
    
#     def change_category(self):
#         """Change category of selected clip"""
#         selection = self.clips_tree.selection()
#         if not selection:
#             messagebox.showwarning("Warning", "Please select a clip to categorize")
#             return
        
#         item = selection[0]
#         values = self.clips_tree.item(item, "values")
#         clip_id = values[4]
#         current_category = values[1]
        

#         category_dialog = tk.Toplevel(self.root)
#         category_dialog.title("Change Category")
#         category_dialog.geometry("300x150")
#         category_dialog.transient(self.root)
#         category_dialog.grab_set()
        
#         ttk.Label(category_dialog, text="Select new category:").pack(pady=10)
        
#         category_var = tk.StringVar(value=current_category)
#         categories = clipboard_manager.get_categories()
#         category_combo = ttk.Combobox(category_dialog, textvariable=category_var, 
#                                     values=categories, state="readonly")
#         category_combo.pack(pady=5)
        
#         def apply_category():
#             new_category = category_var.get()
#             if new_category and new_category != current_category:
#                 if clipboard_manager.update_clip_category(clip_id, new_category):
#                     # Update UI
#                     self.clips_tree.set(item, "Category", new_category)
#                     category_dialog.destroy()
#                     self.status_label.config(text="Category updated", foreground="blue")
#                     self.root.after(3000, lambda: self.status_label.config(text="Ready", foreground="green"))
#                 else:
#                     messagebox.showerror("Error", "Failed to update category")
        
#         ttk.Button(category_dialog, text="Apply", command=apply_category).pack(pady=10)
    
#     def manual_sync(self):
#         """Trigger manual synchronization"""
#         if sync_manager.manual_sync():
#             self.status_label.config(text="Sync completed", foreground="green")
#             self.refresh_clips()
#         else:
#             self.status_label.config(text="Sync failed", foreground="red")
#         self.root.after(3000, lambda: self.status_label.config(text="Ready", foreground="green"))
    
#     def show_sync_status(self):
#         """Show synchronization status"""
#         status = sync_manager.get_sync_status()
        
#         status_text = f"Storage Type: {status['storage_type']}\n"
#         status_text += f"Database Connected: {'Yes' if status['db_connected'] else 'No'}\n"
#         status_text += f"Sync Active: {'Yes' if status['is_syncing'] else 'No'}\n"
        
#         if status['last_sync']:
#             from datetime import datetime
#             last_sync = datetime.fromtimestamp(status['last_sync'])
#             status_text += f"Last Sync: {last_sync.strftime('%Y-%m-%d %H:%M:%S')}"
#         else:
#             status_text += "Last Sync: Never"
        
#         messagebox.showinfo("Sync Status", status_text)
    
#     def show_settings(self):
#         """Show settings dialog"""
#         settings_window = tk.Toplevel(self.root)
#         settings_window.title("Settings")
#         settings_window.geometry("400x300")
#         settings_window.transient(self.root)
#         settings_window.grab_set()
        
#         ttk.Label(settings_window, text="Settings", font=("Arial", 12, "bold")).pack(pady=10)
        
        
#         history_frame = ttk.Frame(settings_window)
#         history_frame.pack(fill=tk.X, padx=20, pady=10)
        
#         ttk.Label(history_frame, text="Max Clipboard History:").grid(row=0, column=0, sticky=tk.W)
#         history_var = tk.StringVar(value=str(config.get("max_clipboard_history", 100)))
#         history_spin = ttk.Spinbox(history_frame, from_=10, to=1000, textvariable=history_var, width=10)
#         history_spin.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
#         def save_settings():
#             try:
#                 max_history = int(history_var.get())
#                 config.set("max_clipboard_history", max_history)
#                 settings_window.destroy()
#                 messagebox.showinfo("Success", "Settings saved!")
#             except ValueError:
#                 messagebox.showerror("Error", "Please enter a valid number")
        
#         ttk.Button(settings_window, text="Save Settings", command=save_settings).pack(pady=20)
    
#     def _format_time(self, timestamp_str):
#         """Format timestamp for display"""
#         if not timestamp_str:
#             return "Just now"
        
#         try:
#             from datetime import datetime
#             if isinstance(timestamp_str, str):
#                 dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
#             else:
#                 dt = timestamp_str
            
#             return dt.strftime("%H:%M:%S")
#         except:
#             return "Unknown"
    
#     def _format_time_detailed(self, timestamp_str):
#         """Format timestamp for detailed display"""
#         if not timestamp_str:
#             return "Just now"
        
#         try:
#             from datetime import datetime
#             if isinstance(timestamp_str, str):
#                 dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
#             else:
#                 dt = timestamp_str
            
#             return dt.strftime("%Y-%m-%d %H:%M:%S")
#         except:
#             return "Unknown time"
    
#     def _truncate_content(self, content, content_type="text", max_length=60):
#         """Truncate content for display"""
#         if not content:
#             return ""
        
#         if content_type == "image":
#             return "[Image Data]"
        
#         content = content.replace('\n', ' ').replace('\r', ' ')
#         if len(content) > max_length:
#             return content[:max_length] + "..."
#         return content
    
#     def run(self):
#         """Start the UI main loop"""
#         try:
#             self.root.mainloop()
#         except KeyboardInterrupt:
#             self.shutdown()
    
#     def shutdown(self):
#         """Clean shutdown of the application"""
#         clipboard_manager.stop_monitoring()
#         sync_manager.stop_sync()
#         if self.root:
#             self.root.quit()
#         print("Application shutdown successfully")



# ui_manager = UIManager()




import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import os
from config import config
from clipboard_manager import clipboard_manager
from sync_manager import sync_manager

class UIManager:
    def __init__(self):
        self.root = None
        self.current_category = "All"
        self.search_text = ""
        self.clips_tree = None
        self.category_var = None
        self.search_var = None
        self.status_label = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the main UI"""
        self.root = tk.Tk()
        self.root.title(f"{config.app_name} v{config.version}")
        self.root.geometry("900x700")
        self.root.minsize(700, 500)
        
        # Set window icon
        try:
            icon_path = config.assets_dir / "icon.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except:
            pass
        
        self._create_menu()
        self._create_main_layout()
        self._setup_bindings()
        
        # Start clipboard monitoring
        clipboard_manager.add_callback(self.on_new_clip)
        clipboard_manager.start_monitoring()
        
        # Start sync manager
        sync_manager.start_sync()
        
        # Load initial data
        self.refresh_clips()
    
    def _create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Settings", command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.shutdown)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Clear All", command=self.clear_all_clips)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Refresh", command=self.refresh_clips)
        view_menu.add_command(label="Clear Search", command=self.clear_search)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Sync menu
        sync_menu = tk.Menu(menubar, tearoff=0)
        sync_menu.add_command(label="Sync Now", command=self.manual_sync)
        sync_menu.add_command(label="Sync Status", command=self.show_sync_status)
        menubar.add_cascade(label="Sync", menu=sync_menu)
        
        self.root.config(menu=menubar)
    
    def _create_main_layout(self):
        """Create main UI layout"""
        # Main container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text=config.app_name, font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        
        # Status label
        self.status_label = ttk.Label(header_frame, text="Ready", foreground="green")
        self.status_label.pack(side=tk.RIGHT)
        
        # Controls frame
        controls_frame = ttk.Frame(main_container)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Category filter
        ttk.Label(controls_frame, text="Category:").grid(row=0, column=0, padx=(0, 5))
        self.category_var = tk.StringVar(value="All")
        categories = ["All"] + clipboard_manager.get_categories()
        self.category_combo = ttk.Combobox(controls_frame, textvariable=self.category_var, 
                                         values=categories, state="readonly", width=15)
        self.category_combo.grid(row=0, column=1, padx=(0, 10))
        self.category_combo.bind('<<ComboboxSelected>>', self.on_category_changed)
        
        # Search box
        ttk.Label(controls_frame, text="Search:").grid(row=0, column=2, padx=(10, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(controls_frame, textvariable=self.search_var, width=30)
        self.search_entry.grid(row=0, column=3, padx=(0, 10))
        self.search_entry.bind('<KeyRelease>', self.on_search_changed)
        
        # Clear search button
        ttk.Button(controls_frame, text="Clear", command=self.clear_search).grid(row=0, column=4)
        
        # Clips frame with scrollbar
        tree_frame = ttk.Frame(main_container)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for clips
        columns = ("Time", "Category", "Content", "Type", "ID")
        self.clips_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)
        
        # Configure columns
        self.clips_tree.heading("Time", text="Time", command=lambda: self.sort_treeview("Time", False))
        self.clips_tree.heading("Category", text="Category", command=lambda: self.sort_treeview("Category", False))
        self.clips_tree.heading("Content", text="Content", command=lambda: self.sort_treeview("Content", False))
        self.clips_tree.heading("Type", text="Type", command=lambda: self.sort_treeview("Type", False))
        self.clips_tree.heading("ID", text="ID")
        
        self.clips_tree.column("Time", width=120)
        self.clips_tree.column("Category", width=100)
        self.clips_tree.column("Content", width=450)
        self.clips_tree.column("Type", width=80)
        self.clips_tree.column("ID", width=0, stretch=False)  # Hidden column
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.clips_tree.yview)
        self.clips_tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid treeview and scrollbar
        self.clips_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind events
        self.clips_tree.bind("<Double-1>", self.on_clip_double_click)
        self.clips_tree.bind("<Button-3>", self.show_context_menu)
        
        # Action buttons frame
        buttons_frame = ttk.Frame(main_container)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(buttons_frame, text="Copy Selected", command=self.copy_selected_clip).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Delete Selected", command=self.delete_selected_clip).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Change Category", command=self.change_category).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Refresh", command=self.refresh_clips).pack(side=tk.LEFT)
        ttk.Button(buttons_frame, text="Clear All", command=self.clear_all_clips).pack(side=tk.LEFT, padx=(10, 0))
    
    def _setup_bindings(self):
        """Setup keyboard bindings"""
        self.root.bind('<Control-r>', lambda e: self.refresh_clips())
        self.root.bind('<Control-f>', lambda e: self.search_entry.focus())
        self.root.bind('<Delete>', lambda e: self.delete_selected_clip())
        self.root.protocol("WM_DELETE_WINDOW", self.shutdown)
    
    def show_context_menu(self, event):
        """Show right-click context menu"""
        item = self.clips_tree.identify_row(event.y)
        if item:
            self.clips_tree.selection_set(item)
            context_menu = tk.Menu(self.root, tearoff=0)
            context_menu.add_command(label="Copy", command=self.copy_selected_clip)
            context_menu.add_command(label="Delete", command=self.delete_selected_clip)
            context_menu.add_separator()
            context_menu.add_command(label="View Details", command=self.show_clip_details)
            context_menu.tk_popup(event.x_root, event.y_root)
    
    def show_clip_details(self):
        """Show detailed view of selected clip"""
        selection = self.clips_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.clips_tree.item(item, "values")
        clip_id = values[4]
        
        # Get clip data from database
        clips = clipboard_manager.get_clipboard_history(limit=1000)
        clip_data = None
        for clip in clips:
            if clip.get("_id") == clip_id:
                clip_data = clip
                break
        
        if not clip_data:
            return
        
        # Create details window
        details_window = tk.Toplevel(self.root)
        details_window.title("Clip Details")
        details_window.geometry("600x400")
        details_window.transient(self.root)
        details_window.grab_set()
        
        # Content frame
        content_frame = ttk.Frame(details_window)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(content_frame, text="Content:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        content_text = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, width=70, height=15)
        content_text.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        content_text.insert(tk.END, clip_data.get("content", ""))
        
        # Metadata frame
        meta_frame = ttk.Frame(content_frame)
        meta_frame.pack(fill=tk.X, pady=(10, 0))
        
        metadata = clip_data.get("metadata", {})
        ttk.Label(meta_frame, text=f"Type: {clip_data.get('content_type', 'Unknown')}").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(meta_frame, text=f"Category: {clip_data.get('category', 'General')}").grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        ttk.Label(meta_frame, text=f"Length: {metadata.get('length', 'N/A')}").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(meta_frame, text=f"Time: {self._format_time_detailed(clip_data.get('timestamp'))}").grid(row=1, column=1, sticky=tk.W, padx=(20, 0))
    
    def sort_treeview(self, column, reverse):
        """Sort treeview by column"""
        data = [(self.clips_tree.set(child, column), child) for child in self.clips_tree.get_children('')]
        data.sort(reverse=reverse)
        
        for index, (_, child) in enumerate(data):
            self.clips_tree.move(child, '', index)
        
        self.clips_tree.heading(column, command=lambda: self.sort_treeview(column, not reverse))
    
    def on_new_clip(self, clip_id, content, category):
        """Callback when new clip is detected"""
        self.root.after(0, self._add_clip_to_ui, clip_id, content, category)
    
    def _add_clip_to_ui(self, clip_id, content, category):
        """Add new clip to UI (thread-safe)"""
        try:
            # Get the latest clip data
            clips = clipboard_manager.get_clipboard_history(limit=1)
            clip_data = clips[0] if clips else None
            
            content_type = clip_data.get("content_type", "text") if clip_data else "text"
            display_content = self._truncate_content(content, content_type)
            
            # Insert new clip at top
            self.clips_tree.insert("", 0, values=(
                self._format_time(None),
                category,
                display_content,
                content_type.title(),
                clip_id
            ))
            
            # Limit displayed items
            max_display = min(config.get("max_clipboard_history", 100), 50)
            if len(self.clips_tree.get_children()) > max_display:
                children = self.clips_tree.get_children()
                self.clips_tree.delete(children[-1])
            
            self.status_label.config(text="New clip added!", foreground="blue")
            self.root.after(3000, lambda: self.status_label.config(text="Ready", foreground="green"))
            
        except Exception as e:
            print(f"Error adding clip to UI: {e}")
    
    def refresh_clips(self):
        """Refresh the clips list"""
        try:
            # Clear current items
            for item in self.clips_tree.get_children():
                self.clips_tree.delete(item)
            
            # Get clips from database
            category = self.current_category if self.current_category != "All" else None
            clips = clipboard_manager.get_clipboard_history(category, self.search_text, limit=100)
            
            # Add clips to treeview
            for clip in clips:
                content_type = clip.get("content_type", "text")
                display_content = self._truncate_content(clip.get("content", ""), content_type)
                
                self.clips_tree.insert("", "end", values=(
                    self._format_time(clip.get("timestamp")),
                    clip.get("category", "General"),
                    display_content,
                    content_type.title(),
                    clip.get("_id")
                ))
            
            self.status_label.config(text=f"Loaded {len(clips)} clips", foreground="green")
            self.root.after(3000, lambda: self.status_label.config(text="Ready", foreground="green"))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh clips: {e}")
    
    def on_category_changed(self, event=None):
        """Handle category filter change"""
        self.current_category = self.category_var.get()
        self.refresh_clips()
    
    def on_search_changed(self, event=None):
        """Handle search text change"""
        self.search_text = self.search_var.get().strip()
        self.root.after(500, self.refresh_clips)  # Debounce search
    
    def clear_search(self):
        """Clear search text"""
        self.search_var.set("")
        self.search_text = ""
        self.refresh_clips()
    
    def on_clip_double_click(self, event):
        """Handle double-click on clip"""
        self.copy_selected_clip()
    
    def copy_selected_clip(self):
        """Copy selected clip to clipboard"""
        selection = self.clips_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a clip to copy")
            return
        
        item = selection[0]
        values = self.clips_tree.item(item, "values")
        clip_id = values[4]
        
        # Find the actual clip content
        clips = clipboard_manager.get_clipboard_history(limit=1000)
        clip_content = ""
        for clip in clips:
            if clip.get("_id") == clip_id:
                clip_content = clip.get("content", "")
                break
        
        if clip_content and clipboard_manager.copy_to_clipboard(clip_content):
            self.status_label.config(text="Copied to clipboard!", foreground="blue")
            self.root.after(2000, lambda: self.status_label.config(text="Ready", foreground="green"))
        else:
            messagebox.showerror("Error", "Failed to copy to clipboard")
    
    def delete_selected_clip(self):
        """Delete selected clip"""
        selection = self.clips_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a clip to delete")
            return
        
        item = selection[0]
        values = self.clips_tree.item(item, "values")
        clip_id = values[4]
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this clip?"):
            if clipboard_manager.delete_clip(clip_id):
                self.clips_tree.delete(item)
                self.status_label.config(text="Clip deleted", foreground="orange")
                self.root.after(3000, lambda: self.status_label.config(text="Ready", foreground="green"))
            else:
                messagebox.showerror("Error", "Failed to delete clip")
    
    def clear_all_clips(self):
        """Clear all clips"""
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to delete ALL clips? This cannot be undone."):
            # This would need to be implemented in the database manager
            messagebox.showinfo("Info", "This feature will be implemented in the next version")
    
    def change_category(self):
        """Change category of selected clip"""
        selection = self.clips_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a clip to categorize")
            return
        
        item = selection[0]
        values = self.clips_tree.item(item, "values")
        clip_id = values[4]
        current_category = values[1]
        
        # Create category selection dialog
        category_dialog = tk.Toplevel(self.root)
        category_dialog.title("Change Category")
        category_dialog.geometry("300x150")
        category_dialog.transient(self.root)
        category_dialog.grab_set()
        
        ttk.Label(category_dialog, text="Select new category:").pack(pady=10)
        
        category_var = tk.StringVar(value=current_category)
        categories = clipboard_manager.get_categories()
        category_combo = ttk.Combobox(category_dialog, textvariable=category_var, 
                                    values=categories, state="readonly")
        category_combo.pack(pady=5)
        
        def apply_category():
            new_category = category_var.get()
            if new_category and new_category != current_category:
                if clipboard_manager.update_clip_category(clip_id, new_category):
                    # Update UI
                    self.clips_tree.set(item, "Category", new_category)
                    category_dialog.destroy()
                    self.status_label.config(text="Category updated", foreground="blue")
                    self.root.after(3000, lambda: self.status_label.config(text="Ready", foreground="green"))
                else:
                    messagebox.showerror("Error", "Failed to update category")
        
        ttk.Button(category_dialog, text="Apply", command=apply_category).pack(pady=10)
    
    def manual_sync(self):
        """Trigger manual synchronization"""
        if sync_manager.manual_sync():
            self.status_label.config(text="Sync completed", foreground="green")
            self.refresh_clips()
        else:
            self.status_label.config(text="Sync failed", foreground="red")
        self.root.after(3000, lambda: self.status_label.config(text="Ready", foreground="green"))
    
    def show_sync_status(self):
        """Show synchronization status"""
        status = sync_manager.get_sync_status()
        
        status_text = f"Storage Type: {status['storage_type']}\n"
        status_text += f"Database Connected: {'Yes' if status['db_connected'] else 'No'}\n"
        status_text += f"Sync Active: {'Yes' if status['is_syncing'] else 'No'}\n"
        
        if status['last_sync']:
            from datetime import datetime
            last_sync = datetime.fromtimestamp(status['last_sync'])
            status_text += f"Last Sync: {last_sync.strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            status_text += "Last Sync: Never"
        
        messagebox.showinfo("Sync Status", status_text)
    
    def show_settings(self):
        """Show settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        ttk.Label(settings_window, text="Settings", font=("Arial", 12, "bold")).pack(pady=10)
        
        # History limit setting
        history_frame = ttk.Frame(settings_window)
        history_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(history_frame, text="Max Clipboard History:").grid(row=0, column=0, sticky=tk.W)
        history_var = tk.StringVar(value=str(config.get("max_clipboard_history", 100)))
        history_spin = ttk.Spinbox(history_frame, from_=10, to=1000, textvariable=history_var, width=10)
        history_spin.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        def save_settings():
            try:
                max_history = int(history_var.get())
                config.set("max_clipboard_history", max_history)
                settings_window.destroy()
                messagebox.showinfo("Success", "Settings saved!")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number")
        
        ttk.Button(settings_window, text="Save Settings", command=save_settings).pack(pady=20)
    
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
            
            return dt.strftime("%H:%M:%S")
        except:
            return "Unknown"
    
    def _format_time_detailed(self, timestamp_str):
        """Format timestamp for detailed display"""
        if not timestamp_str:
            return "Just now"
        
        try:
            from datetime import datetime
            if isinstance(timestamp_str, str):
                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                dt = timestamp_str
            
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return "Unknown time"
    
    def _truncate_content(self, content, content_type="text", max_length=60):
        """Truncate content for display"""
        if not content:
            return ""
        
        content = content.replace('\n', ' ').replace('\r', ' ')
        if len(content) > max_length:
            return content[:max_length] + "..."
        return content
    
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


ui_manager = UIManager()
