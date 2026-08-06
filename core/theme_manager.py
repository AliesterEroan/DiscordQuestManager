"""Theme management for Discord Quest Manager."""

import logging
import json
import os
from typing import Dict, Callable, Optional

from utils.icon_handler import IconHandler

logger = logging.getLogger(__name__)


class ThemeManager:
    """Manages theme switching and color management using JSON files."""

    def __init__(self):
        self.current_theme = "mocha"  # Default to Mocha
        self.colors = {}
        self.on_theme_change_callback: Optional[Callable] = None
        self.icon_handler = IconHandler()
        
        # Get the directory where theme JSON files are located
        self.themes_dir = os.path.join(os.path.dirname(__file__), "themes")
        
        # Load default theme
        self._load_theme_from_json("mocha")

    def _load_theme_from_json(self, theme_name: str) -> Dict[str, str]:
        """Load theme colors from JSON file.
        
        Args:
            theme_name: Name of the theme to load
            
        Returns:
            Dictionary of colors
        """
        theme_file = os.path.join(self.themes_dir, f"{theme_name}.json")
        
        if not os.path.exists(theme_file):
            logger.warning(f"Theme file not found: {theme_file}, falling back to mocha")
            theme_file = os.path.join(self.themes_dir, "mocha.json")
        
        try:
            with open(theme_file, "r") as f:
                theme_data = json.load(f)
                colors = theme_data.get("colors", {})
                logger.info(f"Loaded {len(colors)} colors from {theme_name}.json")
                return colors
        except Exception as e:
            logger.error(f"Failed to load theme from {theme_file}: {e}")
            # Return mocha defaults as fallback
            return self._load_theme_from_json("mocha")

    def set_theme(self, theme: str, custom_colors: Optional[Dict[str, str]] = None) -> None:
        """Set the current theme.
        
        Args:
            theme: Theme name ("mocha", "latte", "custom")
            custom_colors: Optional custom color dictionary for custom theme (saves to JSON)
        """
        logger.info(f"set_theme called with theme: {theme}, custom_colors: {custom_colors is not None}")
        
        if theme == "custom" and custom_colors:
            logger.info(f"Setting custom theme with {len(custom_colors)} colors")
            self.current_theme = "custom"
            self.colors = custom_colors.copy()
            # Save custom colors to JSON file
            self._save_custom_theme(custom_colors)
        elif theme == "custom":
            # Load custom theme from JSON file
            logger.info("Loading custom theme from JSON file")
            self.current_theme = "custom"
            self.colors = self._load_theme_from_json("custom")
        else:
            # Load built-in theme from JSON file
            logger.info(f"Setting built-in theme: {theme}")
            self.current_theme = theme
            self.colors = self._load_theme_from_json(theme)
        
        logger.info(f"Theme set to: {self.current_theme} with {len(self.colors)} colors")
        
        if self.on_theme_change_callback:
            logger.info("Calling theme change callback")
            self.on_theme_change_callback(self.current_theme)
        else:
            logger.warning("No theme change callback registered")

    def _save_custom_theme(self, colors: Dict[str, str]) -> None:
        """Save custom theme colors to JSON file.
        
        Args:
            colors: Color dictionary to save
        """
        custom_file = os.path.join(self.themes_dir, "custom.json")
        theme_data = {
            "theme_name": "custom",
            "display_name": "Catppuccin Frappé",
            "colors": colors
        }
        
        try:
            with open(custom_file, "w") as f:
                json.dump(theme_data, f, indent=2)
            logger.info(f"Saved custom theme to {custom_file}")
        except Exception as e:
            logger.error(f"Failed to save custom theme: {e}")

    def get_theme(self) -> str:
        """Get the current theme name.
        
        Returns:
            Current theme name
        """
        return self.current_theme

    def get_colors(self) -> Dict[str, str]:
        """Get the current color palette.
        
        Returns:
            Current color dictionary
        """
        return self.colors.copy()

    def get_current_colors(self) -> Dict[str, str]:
        """Get the current color palette (alias for get_colors).
        
        Returns:
            Current color dictionary
        """
        return self.colors.copy()

    def set_on_theme_change(self, callback: Callable) -> None:
        """Set callback for theme changes.
        
        Args:
            callback: Function to call when theme changes
        """
        self.on_theme_change_callback = callback

    def toggle_theme(self) -> None:
        """Toggle between mocha and latte themes."""
        new_theme = "latte" if self.current_theme == "mocha" else "mocha"
        self.set_theme(new_theme)

    def get_available_themes(self) -> Dict[str, str]:
        """Get available themes with display names.
        
        Returns:
            Dictionary mapping theme names to display names
        """
        available = {}
        for theme_name in ["mocha", "latte", "custom"]:
            theme_file = os.path.join(self.themes_dir, f"{theme_name}.json")
            if os.path.exists(theme_file):
                try:
                    with open(theme_file, "r") as f:
                        theme_data = json.load(f)
                        available[theme_name] = theme_data.get("display_name", theme_name.capitalize())
                except Exception as e:
                    logger.error(f"Failed to load theme info for {theme_name}: {e}")
                    available[theme_name] = theme_name.capitalize()
        return available

    def get_theme_toggle_icon(self, size: tuple = (20, 20)):
        """Get the appropriate icon for theme toggle button.
        
        Args:
            size: Icon size tuple (width, height)
            
        Returns:
            PhotoImage object for the toggle icon
        """
        # In dark mode, show sun icon (to switch to light)
        # In light mode, show moon icon (to switch to dark)
        if self.current_theme in ["mocha", "custom"]:
            return self.icon_handler.load_ui_icon("sun.png", size)
        else:
            return self.icon_handler.load_ui_icon("full-moon.png", size)

    def get_theme_toggle_text(self) -> str:
        """Get the text for theme toggle button.
        
        Returns:
            Text string for the button
        """
        if self.current_theme in ["mocha", "custom"]:
            return "Switch to Light"
        else:
            return "Switch to Dark"
