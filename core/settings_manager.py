"""Settings management for Discord Quest Manager."""

import json
import os
import sys
import logging
from typing import Any, Dict

# Setup logging for settings backend
from config.constants import APP_DATA_FOLDER

if getattr(sys, 'frozen', False):
    # Running as compiled executable
    base_dir = os.path.dirname(sys.executable)
else:
    # Running as script
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Create data and log folders
data_dir = os.path.join(base_dir, APP_DATA_FOLDER)
log_dir = os.path.join(data_dir, "log")
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, 'settings_debug.log')
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SettingsManager:
    """Manages application settings persistence."""

    def __init__(self):
        self.settings_file = self._get_settings_file_path()
        logger.info(f"Settings file path: {self.settings_file}")
        self.settings = self._load_default_settings()
        logger.debug(f"Loaded default settings with {len(self.settings)} keys")
        self._load_settings()
        logger.info(f"SettingsManager initialized with {len(self.settings)} total settings")

    def _get_settings_file_path(self) -> str:
        """Get the path to the settings file.
        
        Returns:
            Path to settings.json
        """
        from config.constants import APP_DATA_FOLDER
        
        if getattr(sys, "frozen", False):
            # Running as compiled executable - use executable directory for persistence
            base_dir = os.path.dirname(sys.executable)
            logger.debug(f"Running in frozen mode, base_dir: {base_dir}")
        else:
            # Running as script - use project root
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            logger.debug(f"Running in script mode, base_dir: {base_dir}")
        
        # Create app-specific data folder
        data_dir = os.path.join(base_dir, APP_DATA_FOLDER)
        os.makedirs(data_dir, exist_ok=True)
        
        settings_path = os.path.join(data_dir, "settings.json")
        logger.debug(f"Settings file path: {settings_path}")
        return settings_path

    def _load_default_settings(self) -> Dict[str, Any]:
        """Load default settings.
        
        Returns:
            Default settings dictionary
        """
        from core.themes.mocha_theme import COLORS as MOCHA_COLORS
        
        defaults = {
            "theme": "mocha",
            "custom_duration": 15,
            "remember_duration": True,
            "minimize_to_tray": False,
            "auto_clean_on_exit": False,
            "discord_auto_open": True,
            "multi_quest_limit": 0,  # 0 = unlimited
            "dummy_cat_selection": "Cat-1",  # Internal name, will be mapped to display name
            "dummy_alarm_enabled": True,
            "dummy_alarm_type": "default",
            "dummy_alarm_sound_path": "",
            "dummy_alarm_volume": 100,
        }
        
        # Add default custom colors based on mocha theme
        for color_key, color_value in MOCHA_COLORS.items():
            defaults[f"custom_{color_key}"] = color_value
        
        return defaults

    def _load_settings(self) -> None:
        """Load settings from file."""
        logger.debug(f"Attempting to load settings from: {self.settings_file}")
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r") as f:
                    loaded = json.load(f)
                    logger.info(f"Successfully loaded {len(loaded)} settings from file")
                    logger.debug(f"Loaded settings keys: {list(loaded.keys())}")
                    self.settings.update(loaded)
                    logger.debug(f"Updated settings, now have {len(self.settings)} total keys")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse settings JSON: {e}")
                logger.warning("Using default settings due to JSON parse error")
            except IOError as e:
                logger.error(f"Failed to read settings file: {e}")
                logger.warning("Using default settings due to IO error")
        else:
            logger.info(f"Settings file does not exist at {self.settings_file}, using defaults")

    def _save_settings(self) -> None:
        """Save settings to file."""
        logger.debug(f"Attempting to save {len(self.settings)} settings to: {self.settings_file}")
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        try:
            with open(self.settings_file, "w") as f:
                json.dump(self.settings, f, indent=2)
            logger.info(f"Successfully saved settings to file")
            logger.debug(f"Saved settings keys: {list(self.settings.keys())}")
        except IOError as e:
            logger.error(f"Failed to save settings file: {e}")
            logger.error("Settings were not persisted to disk")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value.
        
        Args:
            key: Setting key
            default: Default value if key not found
            
        Returns:
            Setting value or default
        """
        value = self.settings.get(key, default)
        logger.debug(f"GET setting '{key}': {value} (default: {default})")
        return value

    def set(self, key: str, value: Any) -> None:
        """Set a setting value.
        
        Args:
            key: Setting key
            value: New value
        """
        logger.debug(f"SET setting '{key}': {value} (previous: {self.settings.get(key, 'NOT SET')})")
        self.settings[key] = value
        self._save_settings()
        logger.info(f"Setting '{key}' updated and saved")

    def get_all(self) -> Dict[str, Any]:
        """Get all settings.
        
        Returns:
            All settings dictionary
        """
        logger.debug(f"GET_ALL: Returning {len(self.settings)} settings")
        return self.settings.copy()

    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults."""
        logger.warning("Resetting all settings to defaults")
        self.settings = self._load_default_settings()
        logger.debug(f"Reset to defaults with {len(self.settings)} keys")
        self._save_settings()
        logger.info("Settings reset to defaults and saved")

    def validate_settings(self) -> bool:
        """Validate current settings for integrity.
        
        Returns:
            True if settings are valid, False otherwise
        """
        logger.info("Validating settings integrity")
        issues = []
        
        # Check for required settings
        required_keys = ["theme", "custom_duration", "remember_duration"]
        for key in required_keys:
            if key not in self.settings:
                issues.append(f"Missing required key: {key}")
                logger.error(f"Validation failed: Missing required key '{key}'")
        
        # Validate theme value
        valid_themes = ["mocha", "latte", "custom"]
        if self.settings.get("theme") not in valid_themes:
            issues.append(f"Invalid theme: {self.settings.get('theme')}")
            logger.error(f"Validation failed: Invalid theme '{self.settings.get('theme')}'")
        
        # Validate custom_duration is positive integer
        try:
            duration = int(self.settings.get("custom_duration", 15))
            if duration <= 0:
                issues.append(f"Invalid custom_duration: {duration}")
                logger.error(f"Validation failed: Invalid custom_duration '{duration}'")
        except (ValueError, TypeError):
            issues.append(f"Invalid custom_duration type: {self.settings.get('custom_duration')}")
            logger.error(f"Validation failed: Invalid custom_duration type")
        
        # Validate custom colors if present
        from core.themes.mocha_theme import COLORS as MOCHA_COLORS
        for color_key in MOCHA_COLORS.keys():
            custom_key = f"custom_{color_key}"
            if custom_key in self.settings:
                color_value = self.settings[custom_key]
                if not isinstance(color_value, str) or not color_value.startswith("#") or len(color_value) != 7:
                    issues.append(f"Invalid color format for {custom_key}: {color_value}")
                    logger.error(f"Validation failed: Invalid color format for '{custom_key}'")
        
        if issues:
            logger.error(f"Settings validation failed with {len(issues)} issues:")
            for issue in issues:
                logger.error(f"  - {issue}")
            return False
        else:
            logger.info("Settings validation passed")
            return True
