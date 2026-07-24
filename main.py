"""Main entry point for Discord Quest Manager."""

import sys
import tkinter as tk

from ui.main_window import MainWindow
from ui.dummy_window import run_dummy_mode


def main():
    """Main application entry point."""
    # Check if running in dummy mode
    if len(sys.argv) >= 3 and sys.argv[-2] == "--dummy-mode":
        game_exe_name = sys.argv[-1]
        run_dummy_mode(game_exe_name)
    else:
        # Run main application
        root = tk.Tk()
        app = MainWindow(root)
        root.mainloop()


if __name__ == "__main__":
    main()
