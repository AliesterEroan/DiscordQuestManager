# Changelog

All notable changes to Discord Quest Manager will be documented in this file.

## [1.1.0] - 2024-08-06

### Added
- **Multi-Quest Support:** Queue and run multiple games simultaneously with configurable concurrency limits
- **Dynamic Theme System:** JSON-based theme system with Catppuccin Mocha (dark) and Latte (light) themes
- **Custom Theme Editor:** Built-in color picker for creating custom color schemes
- **Favorites & Recent History:** Save favorite games and track recently played executables
- **System Tray Integration:** Minimize to system tray with timer overlay and quick access controls
- **Animated Cat Characters:** 6 unique cat characters with multiple animations (run, walk, itch, stretch, sleep)
- **Cat Selection Settings:** Choose your preferred cat character for dummy windows
- **Debug Logging System:** Comprehensive debug logging to `dist/DiscordQuestManager-data/log/debug.log`
- **Interactive Help Guide:** Built-in HTML help documentation accessible from main window
- **Auto-Update Checking:** GitHub release checker to stay up-to-date with latest version
- **Layout Persistence:** Remembers window position, size, and sidebar width
- **Settings Dialog:** Comprehensive tabbed settings interface (Theme, Quest, System, Dummy, Updates & About)
- **Custom UI Components:** Smooth shaded vector buttons and progress bars with animations

### Fixed
- **Timer Display:** Timer now correctly shows selected custom duration instead of default 15:00
- **Progress Bar:** Progress bar updates properly for all quest states and multiple active quests
- **Recent/Favorites Double-Click:** Fixed issue where double-clicking recent items didn't add to queue
- **Equalizer Animation:** Fixed Tkinter canvas error when window closes during animation
- **Cat Animation Path Resolution:** Fixed PyInstaller path resolution using `sys._MEIPASS`
- **Radio Button Selection:** Fixed visual issue where all cat selection radio buttons appeared selected
- **Logging Recursion:** Fixed infinite recursion error in logging system by removing StreamHandler

### Changed
- **Architecture:** Enhanced modularity with dedicated settings and theme managers
- **UI Framework:** Migrated to simplified frame-based layout in main window
- **Asset Structure:** Reorganized cat animations to per-cat folder structure
- **Error Handling:** Improved error handling throughout the application
- **Build Process:** Updated PyInstaller build script with proper asset bundling

### Technical Details
- Added `core/settings_manager.py` for settings persistence
- Added `core/theme_manager.py` for theme loading and switching
- Added `core/favorites_manager.py` for favorites and recent history
- Added `core/dummy_registry.py` for tracking active dummy processes
- Added `core/discord_checker.py` for Discord process detection
- Added `utils/tray_manager.py` for system tray integration
- Added `ui/smooth_button.py` for custom button widget
- Added `ui/smooth_progress_bar.py` for custom progress bar widget
- Refactored `ui/main_window_simple.py` with improved layout and functionality
- Enhanced `ui/dummy_window.py` with animated cat characters
- Enhanced `ui/settings_dialog.py` with tabbed interface
- Updated `config/constants.py` with theme colors and new settings
- Updated build script to bundle help.html and cat animations

## [1.0.0] - Initial Release

### Features
- Game executable search using Discord's official detectable registry
- Customizable quest timer with preset durations
- Single quest execution with dummy window
- Basic settings configuration
- Clean dummies utility
- About dialog with version information
