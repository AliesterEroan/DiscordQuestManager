# 🎮 Discord Quest Manager v1.1.0

![Version](https://img.shields.io/badge/version-1.1.0-blue.svg) ![Architecture](https://img.shields.io/badge/architecture-modular-success.svg) ![Python](https://img.shields.io/badge/python-3.8+-yellow.svg) ![UI](https://img.shields.io/badge/UI-Tkinter-informational.svg)

> A feature-rich desktop utility built with Python & Tkinter that emulates game executable processes to help complete Discord Quests automatically. Now with multi-quest support, dynamic theming, favorites management, and system tray integration.

---

## ✨ Features

* 🔍 **Game Executable Search:** Instantly queries Discord's official detectable registry for precise `.exe` process names.
* ⏱️ **Customizable Quest Timer:** Built-in countdown timer with customizable duration (5, 10, 15, 30 minutes or custom).
* 🎯 **Multi-Quest Support:** Queue and run multiple games simultaneously with configurable concurrency limits.
* ⭐ **Favorites & Recent History:** Save favorite games and track recently played executables for quick access.
* 🎨 **Dynamic Theme System:** Switch between Catppuccin Mocha (dark), Latte (light), or create custom themes with a built-in color picker.
* 🐱 **Animated Cat Characters:** Cute animated cat characters in dummy windows with 6 different cats and multiple animations (run, walk, itch, stretch, sleep).
* ⚙️ **Comprehensive Settings:** Configure quest duration, concurrency limits, auto-cleanup, Discord auto-open, cat selection, and more.
* 🔔 **System Tray Integration:** Minimize to system tray with status overlay and quick access controls.
* 🧹 **Clean Dummies Utility:** Safe, one-click cleanup tool to remove any orphaned process binaries created during emulation.
* 🔄 **Auto-Update Checking:** Built-in GitHub release checker to stay up-to-date with the latest version.
* ℹ️ **Interactive Help Guide:** Built-in HTML help documentation accessible from the main window.
* 🐛 **Debug Logging:** Comprehensive debug logging system for troubleshooting and issue reporting.

---

## 📁 Project Architecture

```text
DiscordQuestManager/
├── discord.png
├── app_icon.ico
├── build.py                # Packaging & executable build script
├── main.py                 # Entry point, orchestrates everything
├── config/
│   ├── constants.py        # Colors, dimensions, URLs, timer settings, fonts
│   └── layout_config.json  # Saved window layout configuration
├── core/
│   ├── database.py         # Discord API fetching, caching
│   ├── search.py           # Game search logic
│   ├── quest_manager.py    # Quest lifecycle (start/stop/process)
│   ├── timer.py            # Countdown timer logic
│   ├── cleanup.py          # Dummy file cleanup
│   ├── settings_manager.py # Settings persistence and management
│   ├── theme_manager.py    # Theme loading and switching
│   ├── favorites_manager.py # Favorites and recent history
│   ├── dummy_registry.py   # Track active dummy processes
│   ├── discord_checker.py  # Discord process detection
│   └── themes/
│       ├── mocha.json      # Catppuccin Mocha theme
│       ├── latte.json      # Catppuccin Latte theme
│       ├── mocha_theme.py  # Mocha theme module
│       └── __init__.py     # Theme registry
├── ui/
│   ├── main_window_simple.py # Main application window (simplified)
│   ├── dummy_window.py     # Fake game process window
│   ├── settings_dialog.py  # Settings and theme configuration dialog
│   ├── about_dialog.py     # About/update dialog
│   ├── smooth_button.py    # Custom shaded vector button widget
│   └── smooth_progress_bar.py # Custom progress bar widget
├── utils/
│   ├── icon_handler.py     # Icon loading logic with theme support
│   ├── process_manager.py  # Process spawning/termination
│   └── tray_manager.py     # System tray integration
└── data/
    └── settings.json      # Persistent user settings
```

---

## 🔍 Module Responsibilities Breakdown

### main.py
* Application entry point.
* Initializes all modules and wires UI callbacks to core logic.
* Sets up theme manager and loads saved settings.

### config/constants.py
* Defines Catppuccin color schemes (Mocha, Latte, Discord themes).
* Stores window dimensions, Discord API URL, and timer settings.
* Holds UI fonts and global styling values.

### core/database.py
* Fetches Discord detectable games API.
* Handles asynchronous loading using threading.
* Manages cache storage and network error handling.

### core/search.py
* Queries the game database by title or `.exe` name.
* Filters for Windows executables exclusively.
* Handles duplicate entries and formats search results.

### core/quest_manager.py
* Manages quest lifecycle states (running/stopped).
* Handles temporary fake executable creation.
* Tracks selected game processes and coordinates with `process_manager`.

### core/timer.py
* Implements countdown timer logic with `MM:SS` formatting.
* Manages tick callbacks and completion events.
* Supports custom duration settings.

### core/cleanup.py
* Scans target directory for dummy executables.
* Excludes the main application binary from deletion.
* Safely removes files with error handling and returns cleanup statistics.

### core/settings_manager.py
* Manages application settings persistence.
* Handles default values and validation.
* Saves/loads settings from JSON file.

### core/theme_manager.py
* Loads and switches between JSON-based themes.
* Handles custom theme creation and persistence.
* Provides theme metadata and icon management.

### core/favorites_manager.py
* Manages favorite games list.
* Tracks recently played executables.
* Persists favorites and recent history to disk.

### core/dummy_registry.py
* Tracks active dummy process instances.
* Prevents duplicate process creation.
* Provides process lookup and cleanup utilities.

### core/discord_checker.py
* Detects if Discord is currently running.
* Provides Discord auto-open functionality.
* Checks Discord process status.

### ui/main_window_simple.py
* Main `SimpleMainWindow` with frame-based layout.
* Contains search bar, favorites/recent lists, queue management.
* Integrates timer display, progress bar, and footer with version details.
* Handles theme updates and layout persistence.

### ui/dummy_window.py
* Implements `DummyWindow` representing the emulated game process.
* Features topmost window behavior and status updates.
* Supports dynamic theming and progress display.
* Includes animated cat characters with multiple animation states.
* Configurable cat selection with 6 unique cat characters.

### ui/settings_dialog.py
* Comprehensive settings dialog with tabbed interface.
* **Theme Tab:** Theme selection (Mocha, Latte, Custom) with color picker and custom color editor.
* **Quest Tab:** Quest duration and concurrency limit configuration.
* **System Tab:** Auto-cleanup, Discord auto-open, minimize to tray, and other system settings.
* **Dummy Tab:** Cat character selection with visual preview and dummy window settings.
* **Updates & About Tab:** Version info, GitHub update checking, and project links.

### ui/about_dialog.py
* Implements the About modal dialog.
* Displays version details, GitHub links, and an interactive update checker button.

### ui/smooth_button.py
* Custom shaded vector button widget with hover effects.
* Supports dynamic color theming and icon integration.
* Provides pressed state animations.

### ui/smooth_progress_bar.py
* Custom progress bar widget with smooth animations.
* Supports dynamic color theming.
* Provides percentage-based progress display.

### utils/icon_handler.py
* Loads application icons with theme support (dark/light mode).
* Handles GIF animations for dummy windows.
* Includes fallback mechanics for missing icon assets.

### utils/process_manager.py
* Spawns subprocesses with proper execution parameters.
* Detects frozen vs. development environments.
* Handles safe process termination and status polling.

### utils/tray_manager.py
* System tray icon with context menu.
* Provides minimize/restore functionality.
* Shows timer overlay and quest status.
* Handles start/stop/quit actions from tray.

---

## 🎨 Theme System

The application features a dynamic theme system with three built-in themes:

### Catppuccin Mocha (Default)
* Dark theme with warm, muted colors
* Perfect for low-light environments
* Base: `#1e1e2e`, Mantle: `#181825`

### Catppuccin Latte
* Light theme with crisp, clean colors
* Ideal for bright environments
* Base: `#eff1f5`, Mantle: `#e6e9ef`

### Custom Theme
* Create your own color scheme
* Built-in color picker for each theme element
* Persists custom colors to settings

Themes are stored as JSON files in `core/themes/` and can be easily extended or modified.

---

## 🚀 Quick Start

### 🛠️ Running in Development Mode

```bash
cd "DiscordQuestManager"
python main.py
```

### 📦 Building Standalone Executable

### Option 1: Automated Build Script (Recommended)
```bash
python build.py
```

### Option 2: Manual PyInstaller Build
```bash
# Install dependencies
pip install pyinstaller pillow numpy psutil pystray

# Compile single-file executable
python -m PyInstaller DiscordQuestManager.spec
```

*Note: The compiled standalone binary will be saved in the dist/ directory.*

---

## ⚙️ Configuration

### Settings File
Settings are automatically saved to `data/settings.json` and include:
* **Theme:** Current theme selection (mocha, latte, custom)
* **Custom Duration:** Default quest duration in minutes
* **Remember Duration:** Whether to remember last used duration
* **Minimize to Tray:** Enable system tray integration
* **Auto Clean on Exit:** Clean dummy files when closing
* **Discord Auto Open:** Prompt to open Discord if not running
* **Multi-Quest Limit:** Maximum simultaneous quests (0 = unlimited)
* **Auto Check Updates:** Check for updates on startup
* **Custom Colors:** Custom theme color values
* **Cat Selection:** Selected cat character for dummy windows
* **Dummy Alarm Settings:** Alarm sound and volume for dummy windows

### Layout Persistence
Window layout (geometry, sidebar width) is automatically saved to `config/layout_config.json` and restored on startup.

---

## ✨ Key Improvements from v1.0.0

* **Multi-Quest Support:** Queue and run multiple games simultaneously
* **Dynamic Theming:** JSON-based theme system with custom color picker
* **Favorites & History:** Save favorites and track recent games
* **System Tray:** Minimize to tray with status overlay
* **Comprehensive Settings:** Full configuration dialog with all options
* **Better UI Components:** Custom buttons and progress bars with animations
* **Auto-Update Checking:** GitHub release integration
* **Layout Persistence:** Remembers window position and size
* **Improved Architecture:** Enhanced modularity with settings and theme managers
* **Better Error Handling:** Robust error handling throughout the application
* **Animated Cat Characters:** Cute animated cats in dummy windows with 6 unique characters
* **Debug Logging System:** Comprehensive logging for troubleshooting
* **Help Documentation:** Built-in HTML help guide
* **Fixed Timer Display:** Timer now shows selected duration correctly
* **Fixed Progress Bar:** Progress bar updates properly for all quest states

---

## 📌 Requirements & Notes

* **Python Version:** Requires Python 3.8 or higher
* **Dependencies:** 
  * `tkinter` (usually included with Python)
  * `pillow` (image processing)
  * `numpy` (array operations)
  * `psutil` (process management)
  * `pystray` (system tray)
* **Asset Dependencies:** Requires icon assets in `assets/` folder and cat animations in `assets/animations/cat/`
* **Discord Detection:** Requires Discord to be running for quest completion
* **Windows Only:** Currently designed for Windows operating system

---

## 🐛 Known Limitations

* Windows-only application (Discord API and process management are platform-specific)
* Requires Discord to be running for quest completion detection
* Dummy executables are created in the application directory

---

## 📄 License

This project is provided as-is for educational and personal use.

---

## 👤 Author

**Aliester Eroan**

* GitHub: [AliesterEroan](https://github.com/AliesterEroan)
* Project: [DiscordQuestManager](https://github.com/AliesterEroan/DiscordQuestManager)

---

## 🙏 Acknowledgments

* **Catppuccin Theme:** Beautiful color palette by [Catppuccin](https://github.com/catppuccin/catppuccin)
* **Discord API:** Game detectable registry provided by Discord
* **PyInstaller:** Application packaging tool
