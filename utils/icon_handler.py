"""Icon loading utility for Discord Quest Manager."""

import os
import sys
import tkinter as tk

from config.constants import ICON_FILENAME


class IconHandler:
    """Handles application icon loading."""

    def __init__(self):
        self.icon = None
        self._load_icon()

    def _get_icon_path(self) -> str:
        """Get the path to the icon file.
        
        Returns:
            Path to the icon file
        """
        # Try PyInstaller bundled path first
        base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_path, ICON_FILENAME)
        
        # Fallback to executable directory
        if not os.path.exists(icon_path):
            icon_path = os.path.join(os.path.dirname(sys.executable), ICON_FILENAME)
        
        return icon_path

    def _load_icon(self) -> None:
        """Load the icon image."""
        icon_path = self._get_icon_path()
        if os.path.exists(icon_path):
            try:
                self.icon = tk.PhotoImage(file=icon_path)
            except Exception:
                pass

    def load_icon(self) -> tk.PhotoImage:
        """Load and return the icon.
        
        Returns:
            PhotoImage object or None
        """
        if self.icon is None:
            self._load_icon()
        return self.icon

    def apply_to_window(self, window: tk.Tk) -> None:
        """Apply the icon to a window.
        
        Args:
            window: Tkinter window to apply icon to
        """
        icon = self.load_icon()
        if icon:
            try:
                window.iconphoto(True, icon)
            except Exception:
                pass
