"""Main entry point for Discord Quest Manager."""

import sys
import os
import tkinter as tk
import json
import logging

# Add current directory and parent to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
for dir_path in [current_dir, parent_dir]:
    if dir_path not in sys.path:
        sys.path.insert(0, dir_path)

# Setup logging for main application
from config.constants import APP_DATA_FOLDER

if getattr(sys, 'frozen', False):
    # Running as compiled executable
    base_dir = os.path.dirname(sys.executable)
else:
    # Running as script
    base_dir = os.path.dirname(os.path.abspath(__file__))

# Create data and log folders
data_dir = os.path.join(base_dir, APP_DATA_FOLDER)
log_dir = os.path.join(data_dir, "log")
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, 'debug.log')
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file)
    ]
)
logger = logging.getLogger(__name__)
logger.info("Application starting...")

# Redirect stdout and stderr to capture print statements
class LoggerWriter:
    def __init__(self, level):
        self.level = level
    
    def write(self, message):
        if message.strip():
            self.level(message.rstrip())
    
    def flush(self):
        pass

sys.stdout = LoggerWriter(logger.info)
sys.stderr = LoggerWriter(logger.warning)

from ui.main_window_simple import SimpleMainWindow
from ui.dummy_window import run_dummy_mode


def main():
    """Main application entry point."""
    # Check if running in dummy mode
    if "--dummy-mode" in sys.argv:
        dummy_index = sys.argv.index("--dummy-mode")
        
        # Check if there are enough arguments after --dummy-mode
        if dummy_index + 2 < len(sys.argv):
            game_exe_name = sys.argv[dummy_index + 1]
            game_name = sys.argv[dummy_index + 2]
            
            # Check if duration is provided (4th argument after --dummy-mode)
            duration_minutes = 15  # Default
            if dummy_index + 3 < len(sys.argv):
                try:
                    duration_minutes = int(sys.argv[dummy_index + 3])
                except (ValueError, IndexError):
                    duration_minutes = 15
            
            # Check if cat selection is provided (5th argument after --dummy-mode)
            cat_selection = "Cat-1"  # Default
            if dummy_index + 4 < len(sys.argv):
                try:
                    cat_selection = sys.argv[dummy_index + 4]
                except (ValueError, IndexError):
                    cat_selection = "Cat-1"
            
            # Check if theme colors are provided
            theme_colors = None
            if "--theme-colors" in sys.argv:
                theme_index = sys.argv.index("--theme-colors")
                if theme_index + 1 < len(sys.argv):
                    try:
                        theme_colors = json.loads(sys.argv[theme_index + 1])
                    except Exception:
                        theme_colors = None
            
            run_dummy_mode(game_exe_name, game_name, duration_minutes=duration_minutes, theme_colors=theme_colors, cat_selection=cat_selection)
            return  # Exit after running dummy mode
        else:
            print("Error: Invalid arguments for dummy mode")
            return
    
    # Run main application
    root = tk.Tk()
    app = SimpleMainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
