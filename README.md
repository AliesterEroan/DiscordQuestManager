# 🎮 Discord Quest Manager v1.1.0

![Version](https://img.shields.io/badge/version-1.1.0-blue.svg) ![Architecture](https://img.shields.io/badge/architecture-modular-success.svg) ![Python](https://img.shields.io/badge/python-3.8+-yellow.svg) ![UI](https://img.shields.io/badge/UI-Tkinter-informational.svg)

> A feature-rich Windows desktop utility built with Python & Tkinter that emulates game executable processes to help complete Discord Quests automatically. v1.1.0 adds multi-quest support, dynamic theming, favorites, and system tray integration on top of the v1.0.0 modular base.

---

## 📜 Table of Contents

- [✨ Features](#-features)
- [🚀 Installation](#-installation)
- [📖 Usage](#-usage)
- [⚙️ Settings](#-settings)
- [🏗️ Architecture](#-architecture)
- [🛠️ Technologies Used](#-technologies-used)
- [⚠️ Limitations](#-limitations)
- [📜 License](#-license)
- [🙏 Acknowledgments](#-acknowledgments)
- [📧 Contact](#-contact)

---

## ✨ Features

### Quest Management
- **Game executable search** — queries Discord's official detectable registry and filters for Windows `.exe` names.
- **Customizable quest timer** — countdown with preset or custom durations (5, 10, 15, 30 minutes or custom); the timer correctly reflects the selected duration.
- **Multi-quest support** — queue and run multiple games at once with a configurable concurrency limit.
- **Favorites & recent history** — save favorite games and quickly re-run recently used executables.

### UI & Customization
- **Dynamic theme system** — Catppuccin Mocha (dark), Catppuccin Latte (light), or a custom theme built with the integrated color picker; themes are JSON files under `core/themes/`.
- **Animated cat characters** — dummy windows show one of 6 animated cats (run, walk, itch, stretch, sleep animations); selection is a setting.
- **Custom widgets** — shaded vector buttons and animated progress bars that follow the active theme.
- **Layout persistence** — window geometry and sidebar width are saved and restored (`config/layout_config.json`).

### System Integration
- **System tray** — minimize to tray with a status overlay and start/stop/quit quick actions.
- **Clean Dummies utility** — safe one-click removal of orphaned dummy executables.
- **Discord auto-open** — optionally prompts to launch Discord if it isn't running.
- **Auto-update checking** — built-in GitHub release checker (About dialog / settings).
- **Built-in help** — `help.html` documentation accessible from the main window.
- **Debug logging** — comprehensive logging to `DiscordQuestManager-data/log/debug.log` for troubleshooting.

---

## 🚀 Installation

### Prerequisites
- Windows (relies on `.exe` processes and Discord's Windows detection)
- Python 3.8+ with `tkinter`
- Discord running for quest completion
- Asset folders `assets/` (icons) and `assets/animations/cat/` (cat animations) must be present

### Steps
1. Get the code:
   ```bash
   git clone https://github.com/AliesterEroan/DiscordQuestManager.git
   cd DiscordQuestManager/version\ 1.1.0
   ```
2. Install dependencies:
   ```bash
   pip install pillow numpy psutil pystray
   ```
3. Run in development mode:
   ```bash
   python main.py
   ```

### Building a Standalone Executable
```bash
pip install pyinstaller pillow numpy psutil pystray
python build.py
```
The compiled binary is written to `dist/`. (A manual `python -m PyInstaller DiscordQuestManager.spec` build is also supported if a spec file is present.)

---

## 📖 Usage

### Run quests
1. Open the app and wait for the game database to load (fetched from Discord's detectable registry).
2. Search for a game, then add it to the queue — use favorites/recent lists or double-click results.
3. Press **Start**. Dummy executables spawn up to your concurrency limit; each gets a themed dummy window with an animated cat and its own countdown.
4. **Stop** ends running quests; the **Clean** utility removes leftover dummy files. Minimize to the system tray to keep quests running in the background.

### Configure
- Open **Settings** (tabbed dialog): Theme, Quest (duration/concurrency), System (auto-cleanup, Discord auto-open, tray), Dummy (cat choice, alarm), and Updates & About tabs.
- Change themes live — Mocha, Latte, or a custom scheme via the color picker.

### Update check
- The About dialog and settings have an update checker that queries the project's GitHub releases.

---

## ⚙️ Settings

Settings persist to `DiscordQuestManager-data/settings.json` (a data folder next to the exe or repo root, per `APP_DATA_FOLDER` in `config/constants.py`) and include:

- **Theme** — `mocha` (default), `latte`, or `custom`.
- **Custom duration / remember duration** — default quest length in minutes and whether to remember the last choice.
- **Multi-quest limit** — max simultaneous quests (`0` = unlimited).
- **Minimize to tray** — enable system tray integration.
- **Auto clean on exit** — remove dummy files when closing.
- **Discord auto-open** — prompt to open Discord if not detected.
- **Auto check updates** — check GitHub releases on startup.
- **Custom colors** — per-element color overrides for the custom theme.
- **Cat selection** — which of the 6 cat characters appears in dummy windows.
- **Dummy alarm settings** — alarm sound/volume for dummy windows.

Window layout (geometry, sidebar width) is stored separately in `config/layout_config.json`.

---

## 🏗️ Architecture

```text
version 1.1.0/
├── main.py                     # Entry point; wires UI to core; loads theme + settings
├── build.py                    # Packaging & executable build script
├── discord.png / app_icon.ico  # App icon assets
├── config/
│   ├── constants.py            # Colors, dimensions, URLs, timer settings, fonts
│   ├── layout_config.json      # Saved window layout
│   └── themes/                 # (theme JSON/Python modules live under core/themes/)
├── core/
│   ├── database.py             # Discord detectable-games API fetch + cache
│   ├── search.py               # Game search (.exe filter, dedup)
│   ├── quest_manager.py        # Quest lifecycle (start/stop/process)
│   ├── timer.py                # Countdown timer logic
│   ├── cleanup.py              # Dummy file cleanup
│   ├── settings_manager.py     # Settings persistence (DiscordQuestManager-data/settings.json)
│   ├── theme_manager.py        # Theme load/switch, custom themes
│   ├── favorites_manager.py    # Favorites + recent history
│   ├── dummy_registry.py       # Active dummy process tracking
│   ├── discord_checker.py      # Discord process detection / auto-open
│   └── themes/                 # mocha.json, latte.json, mocha_theme.py, ...
├── ui/
│   ├── main_window_simple.py   # Main window (frame layout; active)
│   ├── main_window.py          # Alternative main window
│   ├── main_window_backup.py   # Backup of main window
│   ├── dummy_window.py         # Emulated game window + animated cats
│   ├── settings_dialog.py      # Tabbed settings (Theme/Quest/System/Dummy/Updates)
│   ├── about_dialog.py         # About + update checker
│   ├── smooth_button.py        # Themed vector button
│   ├── smooth_progress_bar.py  # Themed animated progress bar
│   ├── progress_bar.py         # Alternative progress bar
│   ├── pixel_button.py / pixel_container.py / pixel_progress_bar.py  # Experimental pixel widgets
│   ├── sidebar.py / tabs_manager.py / layout_manager.py              # Experimental layout widgets
│   └── __init__.py
├── utils/
│   ├── icon_handler.py         # Icon/GIF loading with theme + packaged fallbacks
│   ├── process_manager.py      # Subprocess spawn/terminate (frozen vs dev aware)
│   └── tray_manager.py         # System tray icon, overlay, quick actions
├── DiscordQuestManager-data/   # Runtime data dir (settings.json, favorites, log/) — created at runtime
├── docs/                       # Help/documentation sources
└── help.html                   # Built-in help guide
```

### Component Overview
- **`ui/main_window_simple.py`** — active main window: search bar, favorites/recent lists, queue, timer, progress bar, footer with version.
- **`core/quest_manager.py` + `core/dummy_registry.py`** — quest lifecycle and duplicate-process prevention.
- **`core/theme_manager.py` + `core/themes/`** — JSON-driven theming shared by main window, dummy windows, and settings dialog.
- **`utils/tray_manager.py`** — tray icon with timer overlay and start/stop/quit menu.

### Data Flow
1. Startup → `main.py` → `settings_manager` loads `DiscordQuestManager-data/settings.json` → `theme_manager` applies theme → registry/database caches load.
2. Search → `core/database.py` (Discord API, background thread) → `core/search.py` → results/favorites/recent lists.
3. Start → `quest_manager` spawns dummy exe via `process_manager` → `dummy_window` shows themed window + cat → `timer` counts down per quest.
4. Settings change → `settings_manager` persists JSON → theme/layout managers re-render UI live.

---

## 🛠️ Technologies Used

### Core
- **Python 3.8+** — runtime.
- **Tkinter** — UI toolkit (standard library); custom-drawn buttons/progress bars on `tk.Canvas`.
- **Pillow** — image/GIF handling for icons and cat animations.
- **NumPy** — array operations for image/animation processing.

### System & Packaging
- **psutil** — process management helpers.
- **pystray** — system tray integration.
- **PyInstaller** — standalone `.exe` builds (`build.py`).
- **Discord detectable-apps API** — public game registry for search.
- **GitHub Releases API** — update checking.

---

## ⚠️ Limitations

### Platform / Behavior
- **Windows-only** — Discord game detection and `.exe` handling are Windows-specific.
- **Discord must be running** — quests complete only while Discord observes the dummy process.
- **Dummy executables touch disk** — created in the app directory (or configured path); use Clean Dummies if the app exits abnormally.
- **Asset-dependent** — missing `assets/` or cat animation folders degrade icons/animations (fallbacks exist but look plain).
- **Experimental widgets present** — `pixel_*`, `sidebar.py`, `tabs_manager.py`, `layout_manager.py`, `main_window.py`, `main_window_backup.py`, and `progress_bar.py` are alternate/experimental UI pieces; `main_window_simple.py` is the active window.

### Testing Limitations
- **What a clone can re-check**: `pip install -r requirements.txt`-equivalent deps, `python main.py` on Windows, theme switching, settings persistence, Clean utility.
- **What a clone cannot re-check**: actual Discord quest crediting (needs a logged-in Discord client + live quest), system-tray behavior on non-Windows, and the GitHub update check against the real releases feed.
- **Automated tests**: `tests/` contains only `debug_build.py` (build debugging) — there is no unit-test suite.

---

## 📜 License

Discord Quest Manager is distributed under a custom license — see [LICENSE](LICENSE) for the full terms.

**Copyright © 2026 Aliester Eroan.**

In short: free for personal and educational use, modification allowed for your own use, and code study encouraged — but **no commercial use without explicit permission**, no claiming the software as your own, and the copyright notice must not be removed. The software is provided "as is" without warranty.

---

## 🙏 Acknowledgments

- **[Catppuccin](https://github.com/catppuccin/catppuccin)** — Mocha and Latte color palettes used by the theme system.
- **Discord** — detectable-apps registry API that powers game search.
- **PyInstaller** — packaging tool for standalone executables.

---

## 📧 Contact

- **GitHub**: [AliesterEroan](https://github.com/AliesterEroan)
- **Project**: [DiscordQuestManager](https://github.com/AliesterEroan/DiscordQuestManager)
- **Issues**: [Create an issue](https://github.com/AliesterEroan/DiscordQuestManager/issues)

---

*Built with ❤️ by AliesterEroan*
