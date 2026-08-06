"""Configuration constants for Discord Quest Manager."""

# Catppuccin Dark Theme Colors
COLORS = {
    "base": "#1e1e2e",
    "mantle": "#181825",
    "surface0": "#313244",
    "surface1": "#45475a",
    "surface2": "#585b70",
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

# Window Dimensions
WINDOW = {
    "main_width": 500,
    "main_height": 540,
    "dummy_width": 380,
    "dummy_height": 140,
    "about_width": 340,
    "about_height": 220,
}

# Timer Settings
TIMER_DURATION_MINUTES = 15
TIMER_TICK_MS = 1000

# Discord API
DISCORD_API_URL = "https://discord.com/api/v9/applications/detectable"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

# Fonts
FONTS = {
    "header": ("Segoe UI", 16, "bold"),
    "status": ("Segoe UI", 9, "italic"),
    "label": ("Segoe UI", 10, "bold"),
    "entry": ("Segoe UI", 10),
    "listbox": ("Segoe UI", 9),
    "timer": ("Segoe UI", 12, "bold"),
    "button": ("Segoe UI", 10, "bold"),
    "button_small": ("Segoe UI", 9, "bold"),
    "footer": ("Segoe UI", 8),
    "about_title": ("Segoe UI", 14, "bold"),
    "about_version": ("Segoe UI", 9, "italic"),
    "about_text": ("Segoe UI", 9),
}

# Application Info
APP_NAME = "Discord Quest Manager"
APP_VERSION = "1.0.0"
AUTHOR = "Aliester Eroan"
GITHUB_PROFILE = "https://github.com/AliesterEroan"
GITHUB_RELEASES = "https://github.com/AliesterEroan/DiscordQuestManager/releases"

# Icon filename
ICON_FILENAME = "discord.png"
