# Asset/Icon Reference List

**Location:** `C:\Users\user\OneDrive\Desktop\DiscordQuestManager\version 1.1.0\assets\icons`

| Icon Name | Size | Location Used | Line | Purpose |
|-----------|------|---------------|------|---------|
| `app_icon` | - | `main_window.py` | 267 | Main window icon (taskbar/title bar) |
| `github.png` | 12x12 | `main_window.py` | 180 | GitHub profile link in footer |
| `star.png` | 16x16 | `main_window.py` | 337 | Favorites section header |
| `clock.png` | 16x16 | `main_window.py` | 376 | Recent items section header |
| `trash.png` | 18x18 | `main_window.py` | 424 | Clean All Data button |
| `configuration.png` | 18x18 | `main_window.py` | 439 | Settings button |
| `search.png` | 16x16 | `main_window.py` | 464 | Search bar icon |
| `folder.png` | 48x48 | `main_window.py` | 546 | Empty state placeholder |
| `play.png` | 18x18 | `main_window.py` | 697 | Start Quests button |
| `stop-button.png` | 18x18 | `main_window.py` | 698 | Stop Quests button |
| `save.png` | 20x20 | `settings_dialog.py` | 119 | Save Settings button |
| `cancel.png` | 20x20 | `settings_dialog.py` | 124 | Cancel button (red) |
| `sun.png` | 16x16 | `settings_dialog.py` | 248 | Light theme radio button |
| `full-moon.png` | 16x16 | `settings_dialog.py` | 244 | Dark theme radio button |
| `custom.png` | 16x16 | `settings_dialog.py` | 252 | Custom theme radio button |
| `github.png` | 64x64 | `settings_dialog.py` | 717 | GitHub releases link in About card |

## Summary
- **Total unique icons:** 16
- **Most used:** `github.png` (used twice, different sizes)
- **Largest:** `github.png` (64x64 in settings), `folder.png` (48x48)
- **Smallest:** 12x12 icons (github in footer)
- **Button icons:** trash, configuration, play, stop-button, save, cancel
- **Theme icons:** sun, full-moon, custom
- **UI elements:** star, clock, search, folder, github
- **Social links:** github (footer and settings)

## Usage Notes
- All icons are loaded via `IconHandler.load_ui_icon()`
- Icons should be placed in `assets/icons/` folder
- Unified icons are used (no dark/light mode variants)
- Fallback emoji icons are used if PNG files are not found
- Sizes are specified as tuples: `(width, height)`
- Original icons are preserved in `original/` subdirectory
