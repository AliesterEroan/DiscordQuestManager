"""Debug build for Discord Quest Manager - Tests all features and logs results."""

import os
import sys
import logging
import traceback
import datetime
from pathlib import Path

# Get parent directory (project root)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
os.chdir(PROJECT_ROOT)

# Add project root to path for imports
sys.path.insert(0, PROJECT_ROOT)

# Create logs folder
LOGS_DIR = Path(PROJECT_ROOT) / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Setup logging
log_file = LOGS_DIR / f"debug_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DebugTester:
    """Debug tester for Discord Quest Manager."""
    
    def __init__(self):
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        logger.info("=" * 60)
        logger.info("Discord Quest Manager Debug Build")
        logger.info(f"Log file: {log_file}")
        logger.info("=" * 60)
    
    def log_test(self, test_name, passed, message=""):
        """Log test result."""
        status = "PASS" if passed else "FAIL"
        logger.info(f"[{status}] {test_name}: {message}")
        if passed:
            self.results['passed'] += 1
        else:
            self.results['failed'] += 1
            self.results['errors'].append(f"{test_name}: {message}")
    
    def test_imports(self):
        """Test all imports."""
        logger.info("\n--- Testing Imports ---")
        try:
            import tkinter as tk
            self.log_test("tkinter import", True)
        except Exception as e:
            self.log_test("tkinter import", False, str(e))
        
        try:
            from config.constants import COLORS, FONTS, WINDOW
            self.log_test("config.constants import", True)
        except Exception as e:
            self.log_test("config.constants import", False, str(e))
        
        try:
            from core.quest_manager import QuestManager
            self.log_test("core.quest_manager import", True)
        except Exception as e:
            self.log_test("core.quest_manager import", False, str(e))
        
        try:
            from core.favorites_manager import FavoritesManager
            self.log_test("core.favorites_manager import", True)
        except Exception as e:
            self.log_test("core.favorites_manager import", False, str(e))
        
        try:
            from core.settings_manager import SettingsManager
            self.log_test("core.settings_manager import", True)
        except Exception as e:
            self.log_test("core.settings_manager import", False, str(e))
        
        try:
            from core.theme_manager import ThemeManager
            self.log_test("core.theme_manager import", True)
        except Exception as e:
            self.log_test("core.theme_manager import", False, str(e))
        
        try:
            from core.dummy_registry import DummyRegistry
            self.log_test("core.dummy_registry import", True)
        except Exception as e:
            self.log_test("core.dummy_registry import", False, str(e))
        
        try:
            from core.discord_checker import DiscordChecker
            self.log_test("core.discord_checker import", True)
        except Exception as e:
            self.log_test("core.discord_checker import", False, str(e))
        
        try:
            from core.search import Search
            self.log_test("core.search import", True)
        except Exception as e:
            self.log_test("core.search import", False, str(e))
        
        try:
            from core.timer import Timer
            self.log_test("core.timer import", True)
        except Exception as e:
            self.log_test("core.timer import", False, str(e))
        
        try:
            from core.cleanup import Cleanup
            self.log_test("core.cleanup import", True)
        except Exception as e:
            self.log_test("core.cleanup import", False, str(e))
        
        try:
            from core.database import Database
            self.log_test("core.database import", True)
        except Exception as e:
            self.log_test("core.database import", False, str(e))
        
        try:
            from ui.main_window import MainWindow
            self.log_test("ui.main_window import", True)
        except Exception as e:
            self.log_test("ui.main_window import", False, str(e))
        
        try:
            from ui.pixel_progress_bar import PixelProgressBar
            self.log_test("ui.pixel_progress_bar import", True)
        except Exception as e:
            self.log_test("ui.pixel_progress_bar import", False, str(e))
        
        try:
            from ui.pixel_button import PixelButton
            self.log_test("ui.pixel_button import", True)
        except Exception as e:
            self.log_test("ui.pixel_button import", False, str(e))
        
        try:
            from ui.progress_bar import ProgressBar
            self.log_test("ui.progress_bar import", True)
        except Exception as e:
            self.log_test("ui.progress_bar import", False, str(e))
        
        try:
            from ui.settings_dialog import SettingsDialog
            self.log_test("ui.settings_dialog import", True)
        except Exception as e:
            self.log_test("ui.settings_dialog import", False, str(e))
        
        try:
            from ui.about_dialog import AboutDialog
            self.log_test("ui.about_dialog import", True)
        except Exception as e:
            self.log_test("ui.about_dialog import", False, str(e))
        
        try:
            from ui.dummy_window import DummyWindow
            self.log_test("ui.dummy_window import", True)
        except Exception as e:
            self.log_test("ui.dummy_window import", False, str(e))
        
        try:
            from utils.icon_handler import IconHandler
            self.log_test("utils.icon_handler import", True)
        except Exception as e:
            self.log_test("utils.icon_handler import", False, str(e))
        
        try:
            from utils.process_manager import ProcessManager
            self.log_test("utils.process_manager import", True)
        except Exception as e:
            self.log_test("utils.process_manager import", False, str(e))
        
        try:
            from utils.tray_manager import TrayManager
            self.log_test("utils.tray_manager import", True)
        except Exception as e:
            self.log_test("utils.tray_manager import", False, str(e))
    
    def test_constants(self):
        """Test configuration constants."""
        logger.info("\n--- Testing Configuration Constants ---")
        try:
            from config.constants import COLORS, FONTS, WINDOW
            
            # Test COLORS
            self.log_test("COLORS dictionary exists", bool(COLORS))
            self.log_test("COLORS has base", 'base' in COLORS)
            self.log_test("COLORS has mantle", 'mantle' in COLORS)
            self.log_test("COLORS has green", 'green' in COLORS)
            self.log_test("COLORS has red", 'red' in COLORS)
            
            # Test FONTS
            self.log_test("FONTS dictionary exists", bool(FONTS))
            self.log_test("FONTS has app_title", 'app_title' in FONTS)
            self.log_test("FONTS has button", 'button' in FONTS)
            self.log_test("FONTS has status", 'status' in FONTS)
            self.log_test("FONTS has pixel_timer", 'pixel_timer' in FONTS)
            self.log_test("FONTS has footer", 'footer' in FONTS)
            
            # Test WINDOW
            self.log_test("WINDOW dictionary exists", bool(WINDOW))
            self.log_test("WINDOW has main_width", 'main_width' in WINDOW)
            self.log_test("WINDOW has main_height", 'main_height' in WINDOW)
            self.log_test("WINDOW has sidebar_width", 'sidebar_width' in WINDOW)
            
            # Test font sizes are integers
            font_sizes_valid = all(isinstance(f[1], int) for f in FONTS.values() if isinstance(f, tuple) and len(f) > 1)
            self.log_test("All font sizes are integers", font_sizes_valid)
            
        except Exception as e:
            self.log_test("Configuration constants test", False, str(e))
    
    def test_quest_manager(self):
        """Test QuestManager functionality."""
        logger.info("\n--- Testing QuestManager ---")
        try:
            from core.quest_manager import QuestManager
            
            # Test initialization
            qm = QuestManager("test_quest")
            self.log_test("QuestManager initialization", True)
            
            # Test game selection
            qm.set_selected_game("Test Game", "test.exe")
            game = qm.get_selected_game()
            self.log_test("Set/get selected game", game == ("Test Game", "test.exe"))
            
            # Test quest lifecycle
            started = qm.start_quest()
            self.log_test("Start quest", started)
            
            is_running = qm.is_running
            self.log_test("Quest is running", is_running)
            
            qm.stop_quest()
            self.log_test("Stop quest", not qm.is_running)
            
            # Test fake exe path
            qm.set_fake_exe_path("C:\\test\\fake.exe")
            path = qm.get_fake_exe_path()
            self.log_test("Set/get fake exe path", path == "C:\\test\\fake.exe")
            
            # Test custom duration
            qm.set_custom_duration(30)
            duration = qm.get_custom_duration()
            self.log_test("Set/get custom duration", duration == 30)
            
        except Exception as e:
            self.log_test("QuestManager test", False, str(e))
    
    def test_favorites_manager(self):
        """Test FavoritesManager functionality."""
        logger.info("\n--- Testing FavoritesManager ---")
        try:
            from core.favorites_manager import FavoritesManager
            
            fm = FavoritesManager()
            self.log_test("FavoritesManager initialization", True)
            
            # Test add favorite
            fm.add_favorite("Game 1", "game1.exe")
            self.log_test("Add favorite", True)
            
            # Test get favorites
            favorites = fm.get_favorites()
            self.log_test("Get favorites", len(favorites) > 0)
            
            # Test remove favorite
            fm.remove_favorite("Game 1", "game1.exe")
            favorites_after = fm.get_favorites()
            self.log_test("Remove favorite", len(favorites_after) == 0)
            
            # Test recent
            fm.add_recent("Recent Game", "recent.exe")
            recent = fm.get_recent()
            self.log_test("Add/get recent", len(recent) > 0)
            
        except Exception as e:
            self.log_test("FavoritesManager test", False, str(e))
    
    def test_settings_manager(self):
        """Test SettingsManager functionality."""
        logger.info("\n--- Testing SettingsManager ---")
        try:
            from core.settings_manager import SettingsManager
            
            sm = SettingsManager()
            self.log_test("SettingsManager initialization", True)
            
            # Test get/set
            sm.set("test_key", "test_value")
            value = sm.get("test_key")
            self.log_test("Set/get setting", value == "test_value")
            
            # Test default value
            default = sm.get("nonexistent_key", "default")
            self.log_test("Get with default", default == "default")
            
            # Test multi-quest limit
            sm.set("multi_quest_limit", 5)
            limit = sm.get("multi_quest_limit", 0)
            self.log_test("Multi-quest limit", limit == 5)
            
        except Exception as e:
            self.log_test("SettingsManager test", False, str(e))
    
    def test_theme_manager(self):
        """Test ThemeManager functionality."""
        logger.info("\n--- Testing ThemeManager ---")
        try:
            from core.theme_manager import ThemeManager
            
            tm = ThemeManager()
            self.log_test("ThemeManager initialization", True)
            
            # Test get current theme
            theme = tm.get_theme()
            self.log_test("Get current theme", theme in ["dark", "light"])
            
            # Test set theme
            tm.set_theme("light")
            self.log_test("Set theme to light", tm.get_theme() == "light")
            
            tm.set_theme("dark")
            self.log_test("Set theme to dark", tm.get_theme() == "dark")
            
            # Test get colors
            colors = tm.get_colors()
            self.log_test("Get colors", bool(colors) and "base" in colors)
            
        except Exception as e:
            self.log_test("ThemeManager test", False, str(e))
    
    def test_dummy_registry(self):
        """Test DummyRegistry functionality."""
        logger.info("\n--- Testing DummyRegistry ---")
        try:
            from core.dummy_registry import DummyRegistry
            
            dr = DummyRegistry()
            self.log_test("DummyRegistry initialization", True)
            
            # Test register dummy
            dr.register_dummy("C:\\test\\dummy.exe", "Test Game", "test.exe")
            self.log_test("Register dummy", True)
            
            # Test get registered dummies
            dummies = dr.get_registered_dummies()
            self.log_test("Get registered dummies", len(dummies) > 0)
            
            # Test unregister dummy
            dr.unregister_dummy("C:\\test\\dummy.exe")
            dummies_after = dr.get_registered_dummies()
            self.log_test("Unregister dummy", len(dummies_after) == 0)
            
        except Exception as e:
            self.log_test("DummyRegistry test", False, str(e))
    
    def test_discord_checker(self):
        """Test DiscordChecker functionality."""
        logger.info("\n--- Testing DiscordChecker ---")
        try:
            from core.discord_checker import DiscordChecker
            
            dc = DiscordChecker()
            self.log_test("DiscordChecker initialization", True)
            
            # Test is_discord_running (should return bool)
            is_running = dc.is_discord_running()
            self.log_test("Check Discord running", isinstance(is_running, bool))
            
        except Exception as e:
            self.log_test("DiscordChecker test", False, str(e))
    
    def test_search(self):
        """Test Search functionality."""
        logger.info("\n--- Testing Search ---")
        try:
            from core.search import Search
            
            # Search requires a games_db parameter
            search = Search([])
            self.log_test("Search initialization", True)
            
            # Test search method (will return empty with empty database)
            results = search.search("test", max_results=10)
            self.log_test("Search method", isinstance(results, list))
            
            # Test format_result
            formatted = search.format_result("Game Name", "game.exe")
            self.log_test("Format result", isinstance(formatted, str))
            
        except Exception as e:
            self.log_test("Search test", False, str(e))
    
    def test_timer(self):
        """Test Timer functionality."""
        logger.info("\n--- Testing Timer ---")
        try:
            from core.timer import Timer
            import time
            
            timer = Timer()  # Timer takes no arguments
            self.log_test("Timer initialization", True)
            
            # Test set duration
            timer.set_duration_minutes(1)  # 1 minute
            self.log_test("Set duration", True)
            
            # Test get display time
            display = timer.get_display_time()
            self.log_test("Get display time", isinstance(display, str))
            
            # Test get elapsed (before start)
            elapsed = timer.get_elapsed_seconds()
            self.log_test("Get elapsed seconds (before start)", elapsed == 0)
            
            # Test stop
            timer.stop()
            self.log_test("Stop timer", True)
            
            # Test reset
            timer.reset()
            self.log_test("Reset timer", True)
            
        except Exception as e:
            self.log_test("Timer test", False, str(e))
    
    def test_database(self):
        """Test Database functionality."""
        logger.info("\n--- Testing Database ---")
        try:
            from core.database import Database
            
            db = Database()
            self.log_test("Database initialization", True)
            
            # Test get games
            games = db.get_games()
            self.log_test("Get games", isinstance(games, list))
            
        except Exception as e:
            self.log_test("Database test", False, str(e))
    
    def test_process_manager(self):
        """Test ProcessManager functionality."""
        logger.info("\n--- Testing ProcessManager ---")
        try:
            from utils.process_manager import ProcessManager
            
            pm = ProcessManager()
            self.log_test("ProcessManager initialization", True)
            
            # Test is_process_running with fake ID
            is_running = pm.is_process_running("fake_quest_id")
            self.log_test("Check process running (fake ID)", not is_running)
            
        except Exception as e:
            self.log_test("ProcessManager test", False, str(e))
    
    def test_icon_handler(self):
        """Test IconHandler functionality."""
        logger.info("\n--- Testing IconHandler ---")
        try:
            from utils.icon_handler import IconHandler
            
            ih = IconHandler()
            self.log_test("IconHandler initialization", True)
            
            # Test load_ui_icon (may return None if icon doesn't exist)
            icon = ih.load_ui_icon("bookmark.png", (16, 16))
            self.log_test("Load UI icon", True)  # Pass even if None (icon may not exist)
            
        except Exception as e:
            self.log_test("IconHandler test", False, str(e))
    
    def test_ui_components(self):
        """Test UI component creation (without showing windows)."""
        logger.info("\n--- Testing UI Components ---")
        try:
            import tkinter as tk
            from ui.pixel_progress_bar import PixelProgressBar
            from ui.pixel_button import PixelButton
            from config.constants import COLORS
            
            # Create hidden root
            root = tk.Tk()
            root.withdraw()
            
            # Test PixelProgressBar
            ppb = PixelProgressBar(root, width=400, height=16, 
                                   bg_color=COLORS["mantle"], 
                                   fill_color=COLORS["green"],
                                   colors=COLORS)
            self.log_test("PixelProgressBar creation", True)
            
            # Test set_progress
            ppb.set_progress(0.5)
            self.log_test("PixelProgressBar set_progress", True)
            
            # Test update_colors
            ppb.update_colors(COLORS["mantle"], COLORS["green"])
            self.log_test("PixelProgressBar update_colors", True)
            
            # Test PixelButton
            pb = PixelButton(root, text="Test Button", 
                           bg_color=COLORS["surface0"],
                           fg_color=COLORS["text"],
                           colors=COLORS)
            self.log_test("PixelButton creation", True)
            
            # Test update_colors
            pb.update_colors(COLORS["green"], COLORS["base"])
            self.log_test("PixelButton update_colors", True)
            
            # Test update_text
            pb.update_text("New Text")
            self.log_test("PixelButton update_text", True)
            
            root.destroy()
            
        except Exception as e:
            self.log_test("UI components test", False, str(e))
    
    def test_sidebar_container_sizes(self):
        """Test sidebar container sizes after UI initialization."""
        logger.info("\n--- Testing Sidebar Container Sizes ---")
        try:
            import tkinter as tk
            from ui.main_window import MainWindow
            
            # Create root window
            root = tk.Tk()
            root.withdraw()  # Hide window
            
            # Create MainWindow instance
            app = MainWindow(root)
            
            # Update UI to ensure layout is calculated
            root.update()
            
            # Wait for layout to settle
            import time
            time.sleep(0.5)
            root.update()
            
            # Print container sizes
            logger.info("=== Sidebar Container Sizes ===")
            logger.info(f"Header Card: {app.header_card.winfo_width()}x{app.header_card.winfo_height()}")
            logger.info(f"Status Card: {app.status_card.winfo_width()}x{app.status_card.winfo_height()}")
            logger.info(f"Favorites Card: {app.favorites_card.winfo_width()}x{app.favorites_card.winfo_height()}")
            logger.info(f"Recent Card: {app.recent_card.winfo_width()}x{app.recent_card.winfo_height()}")
            logger.info(f"Header Content Frame: {app.header_card.content_frame.winfo_width()}x{app.header_card.content_frame.winfo_height()}")
            logger.info(f"Status Content Frame: {app.status_card.content_frame.winfo_width()}x{app.status_card.content_frame.winfo_height()}")
            logger.info(f"Favorites Content Frame: {app.favorites_card.content_frame.winfo_width()}x{app.favorites_card.content_frame.winfo_height()}")
            logger.info(f"Recent Content Frame: {app.recent_card.content_frame.winfo_width()}x{app.recent_card.content_frame.winfo_height()}")
            logger.info("================================")
            
            self.log_test("Sidebar container sizes test", True)
            
            # Cleanup
            root.destroy()
            
        except Exception as e:
            self.log_test("Sidebar container sizes test", False, str(e))
    
    def run_all_tests(self):
        """Run all debug tests."""
        logger.info("\n" + "=" * 60)
        logger.info("Starting Debug Tests")
        logger.info("=" * 60)
        
        try:
            self.test_imports()
        except Exception as e:
            logger.error(f"Imports test crashed: {e}")
            logger.error(traceback.format_exc())
        
        try:
            self.test_constants()
        except Exception as e:
            logger.error(f"Constants test crashed: {e}")
            logger.error(traceback.format_exc())
        
        try:
            self.test_quest_manager()
        except Exception as e:
            logger.error(f"QuestManager test crashed: {e}")
            logger.error(traceback.format_exc())
        
        try:
            self.test_favorites_manager()
        except Exception as e:
            logger.error(f"FavoritesManager test crashed: {e}")
            logger.error(traceback.format_exc())
        
        try:
            self.test_settings_manager()
        except Exception as e:
            logger.error(f"SettingsManager test crashed: {e}")
            logger.error(traceback.format_exc())
        
        try:
            self.test_theme_manager()
        except Exception as e:
            logger.error(f"ThemeManager test crashed: {e}")
            logger.error(traceback.format_exc())
        
        try:
            self.test_dummy_registry()
        except Exception as e:
            logger.error(f"DummyRegistry test crashed: {e}")
            logger.error(traceback.format_exc())
        
        try:
            self.test_discord_checker()
        except Exception as e:
            logger.error(f"DiscordChecker test crashed: {e}")
            logger.error(traceback.format_exc())
        
        try:
            self.test_search()
        except Exception as e:
            logger.error(f"Search test crashed: {e}")
            logger.error(traceback.format_exc())
        
        try:
            self.test_timer()
        except Exception as e:
            logger.error(f"Timer test crashed: {e}")
            logger.error(traceback.format_exc())
        
        try:
            self.test_database()
        except Exception as e:
            logger.error(f"Database test crashed: {e}")
            logger.error(traceback.format_exc())
        
        try:
            self.test_process_manager()
        except Exception as e:
            logger.error(f"ProcessManager test crashed: {e}")
            logger.error(traceback.format_exc())
        
        try:
            self.test_icon_handler()
        except Exception as e:
            logger.error(f"IconHandler test crashed: {e}")
            logger.error(traceback.format_exc())
        
        try:
            self.test_ui_components()
        except Exception as e:
            logger.error(f"UI components test crashed: {e}")
            logger.error(traceback.format_exc())
        
        try:
            self.test_sidebar_container_sizes()
        except Exception as e:
            logger.error(f"Sidebar container sizes test crashed: {e}")
            logger.error(traceback.format_exc())
        
        self.print_summary()
    
    def print_summary(self):
        """Print test summary."""
        logger.info("\n" + "=" * 60)
        logger.info("Debug Test Summary")
        logger.info("=" * 60)
        logger.info(f"Total Tests Passed: {self.results['passed']}")
        logger.info(f"Total Tests Failed: {self.results['failed']}")
        logger.info(f"Total Tests: {self.results['passed'] + self.results['failed']}")
        
        if self.results['errors']:
            logger.info("\nFailed Tests:")
            for error in self.results['errors']:
                logger.info(f"  - {error}")
        
        logger.info("=" * 60)
        
        # Save summary to file
        summary_file = LOGS_DIR / "debug_summary.txt"
        with open(summary_file, 'w') as f:
            f.write(f"Debug Test Summary - {datetime.datetime.now()}\n")
            f.write("=" * 60 + "\n")
            f.write(f"Total Tests Passed: {self.results['passed']}\n")
            f.write(f"Total Tests Failed: {self.results['failed']}\n")
            f.write(f"Total Tests: {self.results['passed'] + self.results['failed']}\n")
            
            if self.results['errors']:
                f.write("\nFailed Tests:\n")
                for error in self.results['errors']:
                    f.write(f"  - {error}\n")
        
        logger.info(f"Summary saved to: {summary_file}")

if __name__ == "__main__":
    try:
        tester = DebugTester()
        tester.run_all_tests()
        
        logger.info("\nDebug build completed successfully!")
        logger.info("Press Enter to exit...")
        input()
        
    except Exception as e:
        logger.error(f"Debug build crashed: {e}")
        logger.error(traceback.format_exc())
        logger.info("Press Enter to exit...")
        input()
