"""Configuration constants for Discord Quest Manager."""

# Discord Dark Theme Colors
COLORS_DISCORD_DARK = {
    "base": "#313338",  # Discord Main Background
    "mantle": "#2b2d31",  # Discord Sidebar / Card Background
    "surface": "#1e1f22",  # Discord Darkest Canvas / Header
    "surface0": "#2b2d31",  # Input Background
    "surface1": "#1e1f22",  # Border
    "surface2": "#5865f2",  # Hover (using accent)
    "text": "#f2f3f5",  # Discord Primary Light Text
    "subtext0": "#949ba4",  # Discord Muted Text
    "subtext1": "#949ba4",
    "overlay0": "#5865f2",
    "overlay1": "#5865f2",
    "overlay2": "#5865f2",
    "blue": "#5865f2",  # Discord Blurple
    "lavender": "#5865f2",
    "sapphire": "#5865f2",
    "sky": "#5865f2",
    "teal": "#57f287",  # Discord Green
    "green": "#57f287",  # Status & Clock Accent
    "yellow": "#fee75c",  # Discord Yellow
    "peach": "#faa61a",  # Discord Orange
    "maroon": "#ed4245",  # Discord Red
    "red": "#ed4245",
    "mauve": "#5865f2",  # Border Highlights
    "pink": "#eb459e",  # Discord Pink
    "flamingo": "#eb459e",
    "rosewater": "#f2f3f5",
}

# Discord Light Theme Colors
COLORS_DISCORD_LIGHT = {
    "base": "#ffffff",  # Discord Light Main Background
    "mantle": "#f2f3f5",  # Discord Light Sidebar / Card Background
    "surface": "#e3e5e8",  # Discord Light Border / Secondary Surface
    "surface0": "#ebedef",  # Input Background
    "surface1": "#e3e5e8",  # Border
    "surface2": "#5865f2",  # Hover (using accent)
    "text": "#060607",  # Discord Dark Text
    "subtext0": "#4e5058",  # Discord Dark Muted Text
    "subtext1": "#4e5058",
    "overlay0": "#5865f2",
    "overlay1": "#5865f2",
    "overlay2": "#5865f2",
    "blue": "#5865f2",  # Discord Blurple
    "lavender": "#5865f2",
    "sapphire": "#5865f2",
    "sky": "#5865f2",
    "teal": "#57f287",  # Discord Green
    "green": "#57f287",  # Status & Clock Accent
    "yellow": "#fee75c",  # Discord Yellow
    "peach": "#faa61a",  # Discord Orange
    "maroon": "#ed4245",  # Discord Red
    "red": "#ed4245",
    "mauve": "#5865f2",  # Border Highlights
    "pink": "#eb459e",  # Discord Pink
    "flamingo": "#eb459e",
    "rosewater": "#060607",
}

# Catppuccin Mocha Theme Colors (Default)
COLORS_DARK = {
    "base": "#1e1e2e",
    "mantle": "#181825",
    "surface": "#313244",
    "surface0": "#45475a",
    "surface1": "#585b70",
    "surface2": "#45475a",
    "text": "#cdd6f4",
    "subtext0": "#a6adc8",
    "subtext1": "#bac2de",
    "overlay0": "#6c7086",
    "overlay1": "#7f849c",
    "overlay2": "#9399b2",
    "blue": "#89b4fa",
    "lavender": "#b4befe",
    "sapphire": "#74c7ec",
    "sky": "#89dceb",
    "teal": "#94e2d5",
    "green": "#a6e3a1",
    "yellow": "#f9e2af",
    "peach": "#fab387",
    "maroon": "#eba0ac",
    "red": "#f38ba8",
    "mauve": "#cba6f7",
    "pink": "#f5c2e7",
    "flamingo": "#f2cdcd",
    "rosewater": "#f5e0dc",
}

# Catppuccin Light Theme Colors (Latte)
COLORS_LIGHT = {
    "base": "#eff1f5",
    "mantle": "#e6e9ef",
    "surface": "#e6e9ef",
    "surface0": "#ccd0da",
    "surface1": "#bcc0cc",
    "surface2": "#acb0be",
    "text": "#1e1e2e",  # Darker primary text for better contrast
    "subtext0": "#6c7086",  # Better contrast secondary text
    "subtext1": "#5c5f77",
    "overlay0": "#9ca0b0",
    "overlay1": "#8c8fa1",
    "overlay2": "#7c7f93",
    "blue": "#1e66f5",
    "lavender": "#7287fd",
    "sapphire": "#209fb5",
    "sky": "#04a5e5",
    "teal": "#179299",
    "green": "#40a02b",
    "yellow": "#df8e1d",
    "peach": "#fe640b",
    "maroon": "#e64553",
    "red": "#d20f39",
    "mauve": "#8839ef",
    "pink": "#ea76cb",
    "flamingo": "#dd7878",
    "rosewater": "#dc8a78",
}

# Default to original dark theme
COLORS = COLORS_DARK

# Window Dimensions
WINDOW = {
    "main_width": 1000,
    "main_height": 650,
    "dummy_width": 380,
    "dummy_height": 400,
    "about_width": 340,
    "about_height": 220,
    "settings_width": 400,
    "settings_height": 500,
    "sidebar_width": 250,
}

# Layout Container Dimensions
LAYOUT = {
    # Main containers
    "sidebar_width": 250,
    "sidebar_height": None,  # No fixed height - allow dynamic vertical expansion
    "right_panel_width": None,  # Dynamic width
    "right_panel_height": None,  # No fixed height - allow dynamic vertical expansion
    
    # Right panel sub-containers
    "search_bar_height": 48,
    "search_bar_width": None,  # Dynamic width
    "executables_viewer_width": None,  # Dynamic width
    "executables_viewer_height": None,  # Dynamic height (stretches)
    "footer_card_height": 100,  # Fixed height for footer
    "footer_card_width": None,  # Dynamic width
    
    # Grid padding
    "main_padx": (10, 5),
    "main_pady": 10,
    "right_panel_padx": (5, 10),
    "right_panel_pady": 10,
    
    # Sub-container padding
    "search_bar_pady": (0, 10),
    "executables_viewer_pady": 0,
    "footer_card_pady": (10, 0),
}

# Timer Settings
TIMER_DURATION_MINUTES = 15
TIMER_TICK_MS = 1000

# App Data Folder
APP_DATA_FOLDER = "DiscordQuestManager-data"

# Discord API
DISCORD_API_URL = "https://discord.com/api/v9/applications/detectable"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

# Fonts (Retro Terminal Theme - Press Start 2P or fallback to Consolas)
# Pixel fonts have wide letter spacing; use exact proportional sizes
# Note: Tkinter requires integer font sizes
FONT_NAME = "Press Start 2P"

FONTS = {
    # App Header Title ("Discord Quest Manager")
    "app_title": (FONT_NAME, 7),
    
    # Panel Titles ("TARGET EXECUTABLES", "Favorites", "Recent")
    "section_title": (FONT_NAME, 7),
    
    # Counter Badges ("SELECTED: X Games Queued", "2 Selected")
    "badge": (FONT_NAME, 5),
    
    # Queue Items & Dropdown Row Text ("EVE Online ➔ exefile.exe")
    "item_label": (FONT_NAME, 7),
    
    # Helper / Placeholder Subtext ("Type in the search bar above...")
    "body_small": (FONT_NAME, 6),
    
    # Buttons (Settings, Clean Dummies, Start Selected Quests)
    "button": ("VCR_OSD_MONO_1.001", 7),
    
    # Footer Credits & Version ("© Aliester Eroan | GitHub Profile", "v1.1.0")
    "footer": (FONT_NAME, 5),
    
    # Large Timer Readout ("15:00")
    "timer": (FONT_NAME, 13),
    
    # Legacy font keys for backward compatibility
    "header": (FONT_NAME, 7),
    "status": (FONT_NAME, 6, "italic"),
    "label": (FONT_NAME, 7, "bold"),
    "entry": (FONT_NAME, 7),
    "listbox": (FONT_NAME, 6),
    "button_small": (FONT_NAME, 6, "bold"),
    "about_title": (FONT_NAME, 7, "bold"),
    "about_version": (FONT_NAME, 6, "italic"),
    "about_text": (FONT_NAME, 6),
    "pixel_timer": (FONT_NAME, 13, "bold"),
    "pixel_timer_small": (FONT_NAME, 10, "bold"),
    "card_title": (FONT_NAME, 7, "bold"),
    "empty_state": (FONT_NAME, 7, "bold"),
    "dropdown": (FONT_NAME, 7),
    "body": (FONT_NAME, 6),
}

# Application Info
APP_NAME = "Discord Quest Manager"
APP_VERSION = "1.1.0"
AUTHOR = "Aliester Eroan"
GITHUB_PROFILE = "https://github.com/AliesterEroan"
GITHUB_RELEASES = "https://github.com/AliesterEroan/DiscordQuestManager/releases"

# Icon filename
ICON_FILENAME = "discord.png"
