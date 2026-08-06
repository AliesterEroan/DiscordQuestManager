"""Icon loading utility for Discord Quest Manager."""

import os
import sys
import tkinter as tk
from PIL import Image, ImageTk

from config.constants import ICON_FILENAME


class IconHandler:
    """Handles application icon loading and dynamic icon loading from assets."""

    def __init__(self):
        self.icon = None
        self._load_icon()
        self.icon_cache = {}

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

    def _get_assets_path(self) -> str:
        """Get the path to the assets directory.
        
        Returns:
            Path to the assets directory
        """
        # Try PyInstaller bundled path first
        base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        assets_path = os.path.join(base_path, "assets")
        
        # Fallback to script directory
        if not os.path.exists(assets_path):
            assets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
        
        return assets_path

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

    def set_theme(self, theme: str) -> None:
        """Set the current theme for icon loading (deprecated - no-op for unified icons).
        
        Args:
            theme: Theme name (ignored - unified icons used)
        """
        # No-op - unified icons are used now
        pass

    def load_ui_icon(self, icon_name: str, size: tuple = (20, 20), theme: str = None) -> tk.PhotoImage:
        """Load a UI icon from assets/icons/.
        
        Args:
            icon_name: Name of the icon file (e.g., 'play.png')
            size: Target size for the icon (width, height)
            theme: Theme subfolder (ignored - unified icons used)
            
        Returns:
            PhotoImage object or None if loading fails
        """
        # Check cache first (without theme)
        cache_key = f"{icon_name}_{size[0]}x{size[1]}"
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]
        
        # Build path directly to icons root (unified icons)
        assets_path = self._get_assets_path()
        icon_path = os.path.join(assets_path, "icons", icon_name)
        
        # Fallback to src directory
        if not os.path.exists(icon_path):
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            icon_path = os.path.join(base_path, "..", "src", icon_name)
        
        if not os.path.exists(icon_path):
            return None
        
        try:
            # Load and resize image
            img = Image.open(icon_path)
            img = img.resize(size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            # Cache the result
            self.icon_cache[cache_key] = photo
            return photo
        except Exception:
            return None

    def load_animation(self, animation_name: str) -> str:
        """Get the path to an animation file.
        
        Args:
            animation_name: Name of the animation file (e.g., 'running.gif')
            
        Returns:
            Path to the animation file or None if not found
        """
        assets_path = self._get_assets_path()
        animation_path = os.path.join(assets_path, "animations", animation_name)
        
        # Fallback to src directory
        if not os.path.exists(animation_path):
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            animation_path = os.path.join(base_path, "..", "src", animation_name)
        
        if os.path.exists(animation_path):
            return animation_path
        return None
