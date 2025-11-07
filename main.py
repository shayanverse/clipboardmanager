import sys
import os
import traceback
from ui_manager import ui_manager
from config import config

def main():
    """Main application entry point"""
    try:
        print(f"Starting {config.app_name} v{config.version}...")
        
        
        if getattr(sys, 'frozen', False):
          
            base_path = sys._MEIPASS
        else:
           
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        print(f"Base path: {base_path}")
        print("Application initialized successfully")
        
   
        ui_manager.run()
        
    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()