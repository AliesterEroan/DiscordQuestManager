"""Theme registry and utilities for Discord Quest Manager."""

import logging
from typing import Dict

from core.themes.mocha_theme import COLORS as MOCHA_COLORS, THEME_NAME as MOCHA_NAME, THEME_DISPLAY_NAME as MOCHA_DISPLAY
from core.themes.latte_theme import COLORS as LATTE_COLORS, THEME_NAME as LATTE_NAME, THEME_DISPLAY_NAME as LATTE_DISPLAY
from core.themes.custom_theme import COLORS as CUSTOM_COLORS, THEME_NAME as CUSTOM_NAME, THEME_DISPLAY_NAME as CUSTOM_DISPLAY

logger = logging.getLogger(__name__)

# Theme registry
THEME_REGISTRY = {
    MOCHA_NAME: {
        "display_name": MOCHA_DISPLAY,
        "colors": MOCHA_COLORS,
        "module": "mocha_theme"
    },
    LATTE_NAME: {
        "display_name": LATTE_DISPLAY,
        "colors": LATTE_COLORS,
        "module": "latte_theme"
    },
    CUSTOM_NAME: {
        "display_name": CUSTOM_DISPLAY,
        "colors": CUSTOM_COLORS,
        "module": "custom_theme"
    }
}

# UI Role to Color Key Mappings
# Each UI role maps to a specific color key in the theme
UI_ROLE_MAPPING = {
    # Background roles
    "background_main": "base",
    "background_sidebar": "mantle",
    "background_card": "mantle",
    "background_input": "surface0",
    "background_button": "surface0",
    "background_button_hover": "surface1",
    "background_button_active": "surface2",
    "background_listbox": "surface0",
    "background_progress": "surface0",
    
    # Text roles
    "text_primary": "text",
    "text_secondary": "subtext0",
    "text_tertiary": "subtext1",
    "text_accent": "pink",
    "text_link": "blue",
    "text_link_hover": "lavender",
    "text_status_success": "green",
    "text_status_warning": "yellow",
    "text_status_error": "red",
    "text_title": "pink",
    
    # Border roles
    "border": "mantle",
    "border_highlight": "mauve",
    "border_divider": "mantle",
    
    # Highlight roles
    "highlight": "mauve",
    "highlight_text": "base",
    
    # Special roles
    "scrollbar": "mantle",
    "scrollbar_trough": "surface0",
    "cursor": "green",
}


def get_color_for_role(colors: dict, role: str) -> str:
    """Get the color for a UI role from the theme colors.
    
    Args:
        colors: Theme color dictionary
        role: UI role name
        
    Returns:
        Color hex string for the role
    """
    color_key = UI_ROLE_MAPPING.get(role, "base")
    return colors.get(color_key, "#1e1e2e")


def load_from_settings(settings_manager) -> dict:
    """Load custom theme colors from settings.
    
    Args:
        settings_manager: SettingsManager instance
        
    Returns:
        Dictionary of custom colors
    """
    from core.themes.mocha_theme import COLORS as MOCHA_DEFAULT
    
    logger.info("load_from_settings called")
    custom_colors = MOCHA_DEFAULT.copy()
    logger.debug(f"Starting with mocha defaults: {len(custom_colors)} colors")
    
    # Load all custom color settings
    loaded_count = 0
    for color_key in MOCHA_DEFAULT.keys():
        saved_color = settings_manager.get(f"custom_{color_key}")
        if saved_color:
            custom_colors[color_key] = saved_color
            loaded_count += 1
            logger.debug(f"Loaded custom color: {color_key} = {saved_color}")
    
    logger.info(f"Loaded {loaded_count} custom colors from settings, returning {len(custom_colors)} total colors")
    return custom_colors
