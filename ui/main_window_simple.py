"""Simple main application window for Discord Quest Manager - Frame-based layout."""

import os
import sys
import tkinter as tk
from tkinter import messagebox
import webbrowser
from typing import List, Tuple
import json

from config.constants import COLORS, COLORS_DARK, COLORS_LIGHT, COLORS_DISCORD_DARK, COLORS_DISCORD_LIGHT, WINDOW, FONTS, APP_NAME, APP_VERSION, AUTHOR, GITHUB_PROFILE, FONT_NAME
from core.database import Database
from core.search import Search
from core.quest_manager import QuestManager
from core.timer import Timer
from core.cleanup import Cleanup
from core.settings_manager import SettingsManager
from utils.icon_handler import IconHandler
from ui.smooth_button import SmoothShadedVectorButton
from ui.smooth_progress_bar import SmoothVectorProgressBar
from core.favorites_manager import FavoritesManager
from core.theme_manager import ThemeManager
from core.dummy_registry import DummyRegistry
from core.discord_checker import DiscordChecker
from core.update_manager import UpdateManager
from ui.about_dialog import AboutDialog
from ui.settings_dialog import SettingsDialog
from utils.process_manager import ProcessManager
from utils.tray_manager import TrayManager


class SimpleMainWindow:
    """Simple main application window with frame-based layout and layout saving."""

    def __init__(self, root: tk.Tk):
        self.root = root
        
        # Initialize core components
        self.database = Database()
        self.search = Search([])
        self.quest_managers: dict = {}
        self.timers: dict = {}
        self.cleanup = Cleanup()
        self.process_manager = ProcessManager()
        self.icon_handler = IconHandler()
        self.settings_manager = SettingsManager()
        self.favorites_manager = FavoritesManager()
        self.theme_manager = ThemeManager()
        self.dummy_registry = DummyRegistry()
        self.discord_checker = DiscordChecker()
        self.tray_manager = TrayManager()
        self.update_manager = UpdateManager()
        
        # UI state
        self.found_matches: List[Tuple[str, str]] = []
        self.quest_counter = 0
        self.quests_running = False
        self.queue_items: List[Dict] = []
        
        # Layout state
        self.layout_config = {}
        self.layout_file = os.path.join(os.path.dirname(__file__), "..", "config", "layout_config.json")
        
        # Colors - will be loaded from theme manager in _load_settings
        self.colors = {}
        
        # Load saved settings and theme
        self._load_settings()
        
        # Setup callbacks
        self._setup_callbacks()
        
        # Setup window
        self._setup_window()
        
        # Setup UI
        self._setup_ui()
        
        # Load saved layout
        self._load_layout()
        
        # Setup tray
        self._setup_tray()
        
        # Load database
        self._load_database()
        
        # Auto-check for updates if enabled
        if self.auto_check_updates:
            self._auto_check_updates()

    def _setup_callbacks(self) -> None:
        """Setup callbacks for core components."""
        self.theme_manager.set_on_theme_change(self._on_theme_change)
        self.tray_manager.set_on_restore(self._on_tray_restore)
        self.tray_manager.set_on_start_stop(self._on_tray_start_stop)
        self.tray_manager.set_on_quit(self._on_tray_quit)

    def _load_settings(self) -> None:
        """Load application settings and apply saved theme."""
        saved_theme = self.settings_manager.get("theme", "mocha")
        
        # Load custom colors if custom theme is selected
        custom_colors = None
        if saved_theme == "custom":
            custom_colors = {}
            # Collect all custom_* settings
            for key in self.settings_manager.get_all().keys():
                if key.startswith("custom_"):
                    color_key = key.replace("custom_", "")
                    custom_colors[color_key] = self.settings_manager.get(key)
        
        self.theme_manager.set_theme(saved_theme, custom_colors=custom_colors)
        self.colors = self.theme_manager.get_current_colors()
        
        # Load timer duration setting
        self.custom_duration = self.settings_manager.get("custom_duration", 15)
        
        # Load multi-quest limit setting
        self.multi_quest_limit = self.settings_manager.get("multi_quest_limit", 0)
        
        # Load other settings
        self.remember_duration = self.settings_manager.get("remember_duration", True)
        self.minimize_to_tray = self.settings_manager.get("minimize_to_tray", False)
        self.auto_clean_on_exit = self.settings_manager.get("auto_clean_on_exit", True)
        self.discord_auto_open = self.settings_manager.get("discord_auto_open", True)
        self.auto_check_updates = self.settings_manager.get("auto_check_updates", True)
        
        # Load dummy window settings
        self.dummy_cat_selection = self.settings_manager.get("dummy_cat_selection", "Cat-1")
        self.default_exe_path = self.settings_manager.get("exe_creation_path", "")
        self.custom_data_dir = self.settings_manager.get("data_folder_path", "")

    def _setup_tray(self) -> None:
        """Setup system tray icon."""
        if self.tray_manager.is_available():
            icon_path = self.icon_handler._get_icon_path()
            self.tray_manager.create_icon(icon_path)
            self.tray_manager.run()

    def _setup_window(self) -> None:
        """Configure the main window."""
        self.root.title(APP_NAME)
        self.root.geometry(f"{WINDOW['main_width']}x{WINDOW['main_height']}")
        self.root.resizable(True, True)
        self.root.configure(bg=self.colors["base"])
        self.icon_handler.apply_to_window(self.root)
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)

    def _setup_ui(self) -> None:
        """Setup the simple frame-based UI."""
        # Main container
        self.main_container = tk.Frame(self.root, bg=self.colors["base"])
        self.main_container.pack(fill="both", expand=True)
        
        # Sidebar frame
        self.sidebar_frame = tk.Frame(self.main_container, bg=self.colors["mantle"], width=280)
        self.sidebar_frame.pack(side="left", fill="y", padx=5, pady=5)
        self.sidebar_frame.pack_propagate(False)
        
        # Main content frame
        self.content_frame = tk.Frame(self.main_container, bg=self.colors["base"])
        self.content_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # Setup sidebar content
        self._setup_sidebar_content()
        
        # Setup main content
        self._setup_main_content()
        
        # Setup footer
        self._setup_footer()
        
        # Setup copyright bar
        self._setup_copyright_bar()

    def _setup_sidebar_content(self) -> None:
        """Setup sidebar content with simple frames."""
        # Header frame
        self.header_frame = tk.Frame(self.sidebar_frame, bg=self.colors["mantle"])
        self.header_frame.pack(fill="x", padx=5, pady=5)
        
        # App icon and title
        try:
            app_icon = self.icon_handler.load_icon()
            if app_icon:
                icon_label = tk.Label(self.header_frame, image=app_icon, bg=self.colors["mantle"])
                icon_label.image = app_icon
                icon_label.pack(pady=5)
        except Exception:
            pass
        
        tk.Label(
            self.header_frame,
            text="Discord Quest Manager",
            font=("Press Start 2P", 8),
            fg=self.colors["pink"],
            bg=self.colors["mantle"]
        ).pack(pady=5)
        
        # Status label
        # Status equalizer animation
        self.eq_canvas = tk.Canvas(self.header_frame, width=60, height=20, bg=self.colors["mantle"], highlightthickness=0)
        self.eq_canvas.pack(pady=2)
        self.eq_step = 0
        self.animate_equalizer()
        
        self.lbl_game_count = tk.Label(
            self.header_frame,
            text="Loading games...",
            font=("Segoe UI", 8, "bold"),
            fg=self.colors["subtext0"],
            bg=self.colors["mantle"]
        )
        self.lbl_game_count.pack(pady=2)
        
        # Divider
        tk.Frame(self.header_frame, bg=self.colors["surface0"], height=2).pack(fill="x", pady=10)
        
        # Queue status
        self.lbl_queue = tk.Label(
            self.header_frame,
            text="SELECTED: 0 Games Queued",
            font=("Segoe UI", 8),
            fg=self.colors["text"],
            bg=self.colors["mantle"]
        )
        self.lbl_queue.pack(pady=5)
        
        # Divider
        tk.Frame(self.header_frame, bg=self.colors["surface0"], height=2).pack(fill="x", pady=10)
        
        # Favorites frame
        self.favorites_frame = tk.Frame(self.sidebar_frame, bg=self.colors["mantle"])
        self.favorites_frame.pack(fill="x", padx=5, pady=5)
        
        fav_header_frame = tk.Frame(self.favorites_frame, bg=self.colors["mantle"])
        fav_header_frame.pack(fill="x", pady=2)
        
        # Center container for favorites header
        fav_center_container = tk.Frame(fav_header_frame, bg=self.colors["mantle"])
        fav_center_container.pack(expand=True)
        
        star_icon = self.icon_handler.load_ui_icon("star.png", (16, 16))
        if star_icon:
            star_label = tk.Label(fav_center_container, image=star_icon, bg=self.colors["mantle"])
            star_label.image = star_icon
            star_label.pack(side="left", padx=2)
        
        tk.Label(
            fav_center_container,
            text="Favorites",
            font=FONTS["label"],
            fg=self.colors["text"],
            bg=self.colors["mantle"]
        ).pack(side="left", padx=2)
        
        self.listbox_favorites = tk.Listbox(
            self.favorites_frame,
            font=FONTS["listbox"],
            bg=self.colors["surface0"],
            fg=self.colors["text"],
            selectbackground=self.colors["mauve"],
            selectforeground=self.colors["base"],
            relief="flat",
            height=5
        )
        self.listbox_favorites.pack(fill="x", padx=5, pady=5)
        self.listbox_favorites.bind("<Double-Button-1>", self._on_favorite_double_click)
        
        # Recent frame
        self.recent_frame = tk.Frame(self.sidebar_frame, bg=self.colors["mantle"])
        self.recent_frame.pack(fill="x", padx=5, pady=5)
        
        recent_header_frame = tk.Frame(self.recent_frame, bg=self.colors["mantle"])
        recent_header_frame.pack(fill="x", pady=2)
        
        # Center container for recent header
        recent_center_container = tk.Frame(recent_header_frame, bg=self.colors["mantle"])
        recent_center_container.pack(expand=True)
        
        clock_icon = self.icon_handler.load_ui_icon("clock.png", (16, 16))
        if clock_icon:
            clock_label = tk.Label(recent_center_container, image=clock_icon, bg=self.colors["mantle"])
            clock_label.image = clock_icon
            clock_label.pack(side="left", padx=2)
        
        tk.Label(
            recent_center_container,
            text="Recent",
            font=FONTS["label"],
            fg=self.colors["text"],
            bg=self.colors["mantle"]
        ).pack(side="left", padx=2)
        
        self.listbox_recent = tk.Listbox(
            self.recent_frame,
            font=FONTS["listbox"],
            bg=self.colors["surface0"],
            fg=self.colors["text"],
            selectbackground=self.colors["mauve"],
            selectforeground=self.colors["base"],
            relief="flat",
            height=5
        )
        self.listbox_recent.pack(fill="x", padx=5, pady=5)
        self.listbox_recent.bind("<Double-Button-1>", self._on_recent_double_click)
        
        # Update favorites and recent
        self._update_favorites_and_recent()
        
        # Help section
        help_frame = tk.Frame(self.sidebar_frame, bg=self.colors["mantle"])
        help_frame.pack(fill="x", padx=5, pady=(10, 5))
        
        help_label = tk.Label(
            help_frame,
            text="Help",
            font=("Arial", 9, "bold"),
            fg=self.colors["text"],
            bg=self.colors["mantle"]
        )
        help_label.pack(anchor="w", padx=2)
        
        help_btn_frame = tk.Frame(help_frame, bg=self.colors["mantle"])
        help_btn_frame.pack(fill="x", pady=2)
        
        help_icon = self.icon_handler.load_ui_icon("help.png", (16, 16))
        if help_icon:
            help_icon_label = tk.Label(help_btn_frame, image=help_icon, cursor="hand2", bg=self.colors["mantle"])
            help_icon_label.image = help_icon
            help_icon_label.pack(side="left", padx=2)
            help_icon_label.bind("<Button-1>", self._open_help)
        
        help_text_label = tk.Label(
            help_btn_frame,
            text="Open Help Guide",
            font=("Arial", 8),
            fg=self.colors["subtext0"],
            cursor="hand2",
            bg=self.colors["mantle"]
        )
        help_text_label.pack(side="left", padx=2)
        help_text_label.bind("<Button-1>", self._open_help)
        
        # Spacer
        tk.Frame(self.sidebar_frame, bg=self.colors["mantle"]).pack(fill="both", expand=True)
        
        # Buttons frame
        self.buttons_frame = tk.Frame(self.sidebar_frame, bg=self.colors["mantle"])
        self.buttons_frame.pack(fill="x", padx=5, pady=5)
        
        # Clean button
        clean_btn = SmoothShadedVectorButton(
            self.buttons_frame,
            text="Clean All Data",
            icon_name="trash.png",
            base_color="#8eaecf",
            dark_color="#444866",
            fg_color="#ffffff",
            width=250,
            height=40,
            command=self._clean_all_data
        )
        clean_btn.pack(fill="x", pady=2)
        
        # Settings button
        settings_btn = SmoothShadedVectorButton(
            self.buttons_frame,
            text="Settings",
            icon_name="configuration.png",
            base_color="#3d8ebd",
            dark_color="#1f597d",
            fg_color="#ffffff",
            width=250,
            height=40,
            command=self._show_settings_dialog
        )
        settings_btn.pack(fill="x", pady=2)

    def _setup_main_content(self) -> None:
        """Setup main content area."""
        # Search frame
        self.search_frame = tk.Frame(self.content_frame, bg=self.colors["surface0"])
        self.search_frame.pack(fill="x", padx=5, pady=5)
        
        search_icon = self.icon_handler.load_ui_icon("search.png", (16, 16))
        if search_icon:
            tk.Label(self.search_frame, image=search_icon, bg=self.colors["surface0"]).pack(side="left", padx=5)
        
        self.ent_search = tk.Entry(
            self.search_frame,
            font=FONTS["entry"],
            bg=self.colors["surface0"],
            fg=self.colors["text"],
            insertbackground=self.colors["green"],
            relief="flat"
        )
        self.ent_search.pack(side="left", fill="x", expand=True, padx=5)
        self.ent_search.bind("<KeyRelease>", self._on_search_key_press)
        
        # Search dropdown
        self.search_dropdown = tk.Frame(self.content_frame, bg=self.colors["surface0"], relief="flat")
        
        # Executables frame
        self.exec_frame = tk.Frame(self.content_frame, bg=self.colors["mantle"])
        self.exec_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Header
        tk.Label(
            self.exec_frame,
            text="TARGET EXECUTABLES",
            font=FONTS["card_title"],
            fg=self.colors["pink"],
            bg=self.colors["mantle"]
        ).pack(pady=5)
        
        self.lbl_selected_count = tk.Label(
            self.exec_frame,
            text="0 Selected",
            font=FONTS["status"],
            fg=self.colors["subtext0"],
            bg=self.colors["mantle"]
        ).pack(pady=2)
        
        # Queue display
        self.queue_frame = tk.Frame(self.exec_frame, bg=self.colors["surface0"])
        self.queue_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Empty state
        self.empty_state = tk.Frame(self.queue_frame, bg=self.colors["surface0"])
        self.empty_state.pack(fill="both", expand=True)
        
        folder_icon_large = self.icon_handler.load_ui_icon("folder.png", (48, 48))
        if folder_icon_large:
            folder_label = tk.Label(self.empty_state, image=folder_icon_large, bg=self.colors["surface0"])
            folder_label.image = folder_icon_large
            folder_label.pack(pady=(20, 5))
        
        tk.Label(
            self.empty_state,
            text="NO GAMES ADDED",
            font=FONTS["empty_state"],
            fg=self.colors["text"],
            bg=self.colors["surface0"]
        ).pack(pady=5)
        
        tk.Label(
            self.empty_state,
            text="Type in the search bar above to select and queue game executables.",
            font=FONTS["body_small"],
            fg=self.colors["subtext0"],
            bg=self.colors["surface0"]
        ).pack(pady=5)

    def _setup_footer(self) -> None:
        """Setup footer controls."""
        self.footer_frame = tk.Frame(self.content_frame, bg=self.colors["base"])
        self.footer_frame.pack(fill="x", padx=5, pady=5)
        
        # Timer container
        timer_container = tk.Frame(self.footer_frame, bg=self.colors["base"])
        timer_container.pack(side="left", padx=10)
        
        # Timer - use custom_duration from settings
        timer_minutes = self.custom_duration if hasattr(self, 'custom_duration') else 15
        timer_text = f"{timer_minutes:02d}:00"
        self.lbl_timer = tk.Label(
            timer_container,
            text=timer_text,
            font=FONTS["timer"],
            fg=self.colors["green"],
            bg=self.colors["base"]
        )
        self.lbl_timer.pack(pady=(0, 2))
        
        # Quest status under timer
        self.lbl_quest_status = tk.Label(
            timer_container,
            text="0 Quest Rdy",
            font=("Segoe UI", 8),
            fg=self.colors["green"],
            bg=self.colors["base"]
        )
        self.lbl_quest_status.pack(pady=(0, 2))
        
        # Progress bar
        self.progress_bar = SmoothVectorProgressBar(
            self.footer_frame,
            value=0.0,
            base_color="#a6e3a1",
            dark_color="#437e10",
            bg_color="#1e1e2e",
            border_color="#45475a",
            height=12
        )
        self.progress_bar.pack(side="left", fill="x", expand=True, padx=5)
        
        # Start button
        self.btn_start = SmoothShadedVectorButton(
            self.footer_frame,
            text="Start Quests (0)",
            icon_name="play.png",
            base_color="#a6e3a1",
            dark_color="#437e10",
            fg_color="#1e1e2e",
            width=160,
            height=46,
            command=self._on_start_stop_button_click
        )
        self.btn_start.play_icon_name = "play.png"
        self.btn_start.stop_icon_name = "stop-button.png"
        self.btn_start.pack(side="right", padx=10)

    def _on_footer_resize(self, event) -> None:
        """Handle footer resize to update progress bar width."""
        pass  # PixelProgressBar handles its own resizing

    def _setup_copyright_bar(self) -> None:
        """Setup copyright bar."""
        self.copyright_frame = tk.Frame(self.root, bg=self.colors["mantle"], height=24)
        self.copyright_frame.pack(side="bottom", fill="x")
        self.copyright_frame.pack_propagate(False)
        
        # Author label (left side)
        tk.Label(
            self.copyright_frame,
            text="Aliester Eroan",
            font=("Press Start 2P", 6),
            fg=self.colors["subtext0"],
            bg=self.colors["mantle"]
        ).pack(side="left", padx=10)
        
        # Separator line
        tk.Frame(self.copyright_frame, bg=self.colors["surface0"], width=1).pack(side="left", fill="y", padx=5)
        
        # GitHub section (next to separator)
        github_frame = tk.Frame(self.copyright_frame, bg=self.colors["mantle"])
        github_frame.pack(side="left", padx=5)
        
        github_icon = self.icon_handler.load_ui_icon("github.png", (16, 16))
        if github_icon:
            github_icon_label = tk.Label(github_frame, image=github_icon, cursor="hand2", bg=self.colors["mantle"])
            github_icon_label.image = github_icon
            github_icon_label.pack(side="left", padx=2)
            github_icon_label.bind("<Button-1>", lambda e: webbrowser.open(GITHUB_PROFILE))
        
        github_label = tk.Label(
            github_frame,
            text="View Profile",
            font=("Arial", 7),
            fg=self.colors["subtext0"],
            bg=self.colors["mantle"]
        )
        github_label.pack(side="left", padx=2)
        
        # Version label (right side)
        tk.Label(
            self.copyright_frame,
            text="v1.1.0",
            font=("Press Start 2P", 6),
            fg=self.colors["subtext0"],
            bg=self.colors["mantle"]
        ).pack(side="right", padx=10)

    def update_colors(self, colors: dict) -> None:
        """Update all colors when theme changes with comprehensive mapping."""
        self.colors = colors
        
        # Update main container
        self.root.config(bg=colors["base"])
        self.main_container.config(bg=colors["base"])
        
        # Update sidebar
        self.sidebar_frame.config(bg=colors["mantle"])
        self.header_frame.config(bg=colors["mantle"])
        self.favorites_frame.config(bg=colors["mantle"])
        self.recent_frame.config(bg=colors["mantle"])
        self.buttons_frame.config(bg=colors["mantle"])
        self.copyright_frame.config(bg=colors["mantle"])
        
        # Update content
        self.content_frame.config(bg=colors["base"])
        self.search_frame.config(bg=colors["surface0"])
        self.exec_frame.config(bg=colors["mantle"])
        self.queue_frame.config(bg=colors["surface0"])
        self.empty_state.config(bg=colors["surface0"])
        self.footer_frame.config(bg=colors["base"])
        
        # Comprehensive color mapping for all theme colors
        bg_map = {
            # Mocha theme colors
            "#1e1e2e": colors["base"],
            "#181825": colors["mantle"],
            "#313244": colors["surface"],
            "#45475a": colors["surface0"],
            "#585b70": colors["surface1"],
            "#6c7086": colors["overlay0"],
            "#7f849c": colors["overlay1"],
            "#9399b2": colors["overlay2"],
            # Latte theme colors
            "#eff1f5": colors["base"],
            "#e6e9ef": colors["mantle"],
            "#dcdee5": colors["surface"],
            "#ccd0da": colors["surface0"],
            "#bcc0cc": colors["surface1"],
            "#acb0be": colors["surface2"],
        }
        
        fg_map = {
            # Mocha text colors
            "#cdd6f4": colors["text"],
            "#a6adc8": colors["subtext0"],
            "#bac2de": colors["subtext1"],
            "#f5e0dc": colors["overlay2"],
            # Mocha accent colors
            "#f38ba8": colors["red"],
            "#fab387": colors["peach"],
            "#f9e2af": colors["yellow"],
            "#a6e3a1": colors["green"],
            "#94e2d5": colors["teal"],
            "#89dceb": colors["sky"],
            "#74c7ec": colors["sapphire"],
            "#89b4fa": colors["blue"],
            "#b4befe": colors["lavender"],
            "#cba6f7": colors["mauve"],
            "#f5c2e7": colors["pink"],
            "#f2cdcd": colors["flamingo"],
            # Latte text colors
            "#202231": colors["text"],
            "#4c4f69": colors["subtext0"],
            "#5c5f77": colors["subtext1"],
            # Latte accent colors
            "#d20f39": colors["red"],
            "#fe640b": colors["peach"],
            "#df8e1d": colors["yellow"],
            "#40a02b": colors["green"],
            "#179299": colors["teal"],
            "#04a5e5": colors["sky"],
            "#209fb5": colors["sapphire"],
            "#1e66f5": colors["blue"],
            "#7287fd": colors["lavender"],
            "#8839ef": colors["mauve"],
            "#ea76cb": colors["pink"],
            "#dd7878": colors["flamingo"],
        }
        
        # Recursively update all widgets
        def update_widget(widget):
            try:
                if hasattr(widget, 'config'):
                    # Update background
                    try:
                        current_bg = widget.cget("bg")
                        if current_bg in bg_map:
                            widget.config(bg=bg_map[current_bg])
                        # Also update based on widget type/role
                        elif hasattr(widget, 'ui_role'):
                            if widget.ui_role == "background_main":
                                widget.config(bg=colors["base"])
                            elif widget.ui_role == "background_mantle":
                                widget.config(bg=colors["mantle"])
                            elif widget.ui_role == "background_surface":
                                widget.config(bg=colors["surface0"])
                    except Exception:
                        pass
                    
                    # Update foreground
                    try:
                        current_fg = widget.cget("fg")
                        if current_fg and current_fg != "" and current_fg in fg_map:
                            widget.config(fg=fg_map[current_fg])
                    except Exception:
                        pass
                    
                    # Update selectbackground/selectforeground for listboxes
                    try:
                        if 'selectbackground' in widget.keys():
                            widget.config(selectbackground=colors["mauve"])
                        if 'selectforeground' in widget.keys():
                            widget.config(selectforeground=colors["base"])
                    except Exception:
                        pass
                
                for child in widget.winfo_children():
                    update_widget(child)
            except Exception:
                pass
        
        update_widget(self.main_container)
        
        # Update footer frame colors
        if hasattr(self, 'footer_frame'):
            self.footer_frame.config(bg=colors["base"])
        
        # Update timer container and labels (no bg - let them inherit)
        if hasattr(self, 'lbl_timer'):
            self.lbl_timer.config(fg=colors["green"])
        if hasattr(self, 'lbl_quest_status'):
            self.lbl_quest_status.config(fg=colors["green"])
        
        # Update progress bar colors
        if hasattr(self, 'progress_bar'):
            self.progress_bar.update_colors(
                base_color=colors["green"],
                dark_color="#437e10",
                bg_color=colors["base"],
                border_color=colors["surface0"]
            )

    def _save_layout(self) -> None:
        """Save current layout configuration."""
        self.layout_config = {
            "window_geometry": self.root.geometry(),
            "sidebar_width": self.sidebar_frame.winfo_width(),
        }
        
        try:
            os.makedirs(os.path.dirname(self.layout_file), exist_ok=True)
            with open(self.layout_file, 'w') as f:
                json.dump(self.layout_config, f, indent=2)
        except Exception as e:
            print(f"Failed to save layout: {e}")

    def _load_layout(self) -> None:
        """Load saved layout configuration."""
        try:
            if os.path.exists(self.layout_file):
                with open(self.layout_file, 'r') as f:
                    self.layout_config = json.load(f)
                
                if "window_geometry" in self.layout_config:
                    self.root.geometry(self.layout_config["window_geometry"])
                if "sidebar_width" in self.layout_config:
                    self.sidebar_frame.config(width=self.layout_config["sidebar_width"])
        except Exception as e:
            print(f"Failed to load layout: {e}")

    def _on_theme_change(self, new_theme: str) -> None:
        """Handle theme change event."""
        self.colors = self.theme_manager.get_current_colors()
        
        # Update icon handler theme
        if new_theme in ["latte"]:
            self.icon_handler.set_theme("light_mode")
        else:
            self.icon_handler.set_theme("dark_mode")
        
        # Update all colors
        self.update_colors(self.colors)
        
        # Update settings dialog if open
        if hasattr(self, 'settings_dialog_instance'):
            self.settings_dialog_instance.update_colors(self.colors)

    # ... (rest of the methods from original main_window - search, queue, quest management, etc.)
    # These would be copied over with minimal changes to work with the new simple UI
    
    def _load_database(self) -> None:
        """Load the games database asynchronously."""
        self.database.load_async(self._on_db_loaded)

    def animate_equalizer(self) -> None:
        """Animate retro pixel equalizer."""
        # Check if canvas still exists (window might be closed)
        if not hasattr(self, 'eq_canvas') or not self.eq_canvas.winfo_exists():
            return
        
        self.eq_canvas.delete("all")
        
        # Equalizer bars - 5 bars with varying heights
        bar_width = 8
        bar_spacing = 4
        start_x = 8
        
        # Generate random heights for arcade vibe
        import random
        heights = [random.randint(4, 16) for _ in range(5)]
        
        for i, height in enumerate(heights):
            x = start_x + i * (bar_width + bar_spacing)
            y = 20 - height
            
            # Draw bar with retro green color
            self.eq_canvas.create_rectangle(
                x, y, x + bar_width, 20,
                fill=self.colors["green"],
                outline=""
            )
        
        # Schedule next frame
        self.eq_animation_id = self.root.after(100, self.animate_equalizer)

    def _on_db_loaded(self, success: bool, data: List) -> None:
        """Callback when database is loaded."""
        # Stop equalizer animation
        if hasattr(self, 'eq_animation_id'):
            self.root.after_cancel(self.eq_animation_id)
        
        # Replace equalizer with status label
        self.eq_canvas.destroy()
        
        # Create status label
        status_text = "● DATABASE READY" if success else "● DATABASE OFFLINE"
        status_color = self.colors["green"] if success else self.colors["red"]
        
        self.lbl_status = tk.Label(
            self.header_frame,
            text=status_text,
            font=("Segoe UI", 8),
            fg=status_color,
            bg=self.colors["mantle"]
        )
        self.lbl_status.pack(pady=2, before=self.lbl_game_count)
        
        if success:
            self.search.update_database(data)
            self.lbl_game_count.config(text=f"{len(data):,} registered", fg=self.colors["subtext0"])
            self.btn_start.config(state="normal")
        else:
            self.lbl_game_count.config(text="Check network connection", fg=self.colors["red"])
            self.btn_start.config(state="disabled")

    def _on_search_key_press(self, event) -> None:
        """Handle search key press."""
        query = self.ent_search.get().strip()
        if len(query) >= 2:
            self._show_search_dropdown(query)
        else:
            self._hide_search_dropdown()

    def _show_search_dropdown(self, query: str) -> None:
        """Show search dropdown."""
        for widget in self.search_dropdown.winfo_children():
            widget.destroy()
        
        results = self.search.search(query, max_results=10)
        if not results:
            self._hide_search_dropdown()
            return
        
        self.search_dropdown.place(x=self.ent_search.winfo_x(), y=self.ent_search.winfo_y() + self.ent_search.winfo_height() + 2)
        self.search_dropdown.lift()  # Bring to front
        
        for idx, (game_name, exe_name) in enumerate(results):
            item_frame = tk.Frame(self.search_dropdown, bg=self.colors["surface0"], cursor="hand2")
            item_frame.pack(fill="x", padx=5, pady=2)
            
            item_label = tk.Label(item_frame, text=f"{game_name} → {exe_name}", font=FONTS["entry"], fg=self.colors["text"], bg=self.colors["surface0"])
            item_label.pack(fill="x", padx=5)
            
            # Bind click to both frame and label
            item_frame.bind("<Button-1>", lambda e, g=game_name, x=exe_name: self._add_to_queue(g, x))
            item_label.bind("<Button-1>", lambda e, g=game_name, x=exe_name: self._add_to_queue(g, x))
            
            # Add separator line (skip after last item)
            if idx < len(results) - 1:
                separator = tk.Frame(self.search_dropdown, height=1, bg=self.colors["surface1"])
                separator.pack(fill="x", padx=5, pady=(0, 1))

    def _hide_search_dropdown(self) -> None:
        """Hide search dropdown."""
        self.search_dropdown.place_forget()

    def _add_to_queue(self, game_name: str, exe_name: str) -> None:
        """Add game to queue."""
        self._hide_search_dropdown()
        self.ent_search.delete(0, tk.END)
        
        for item in self.queue_items:
            if item["game_name"] == game_name and item["exe_name"] == exe_name:
                return
        
        self.queue_items.append({"game_name": game_name, "exe_name": exe_name, "checked": True})
        self._update_queue_display()
        self._update_selection_count()

    def _update_queue_display(self) -> None:
        """Update queue display."""
        for widget in self.queue_frame.winfo_children():
            if widget != self.empty_state:
                widget.destroy()
        
        if not self.queue_items:
            self.empty_state.pack(fill="both", expand=True)
        else:
            self.empty_state.pack_forget()
            for idx, item in enumerate(self.queue_items):
                item_frame = tk.Frame(self.queue_frame, bg=self.colors["surface0"])
                item_frame.pack(fill="x", padx=5, pady=2)
                
                # Checkbox - use a closure to capture the correct index
                check_var = tk.BooleanVar(value=item["checked"])
                
                def make_toggle_callback(i, var):
                    def callback():
                        self._toggle_queue_item(i, var)
                    return callback
                
                checkbox = tk.Checkbutton(
                    item_frame,
                    variable=check_var,
                    command=make_toggle_callback(idx, check_var),
                    bg=self.colors["surface0"],
                    fg=self.colors["text"],
                    selectcolor=self.colors["surface0"],
                    activebackground=self.colors["surface0"],
                )
                checkbox.pack(side="left", padx=5)
                
                # Game name
                game_label = tk.Label(item_frame, text=item["game_name"], font=FONTS["body"], fg=self.colors["text"], bg=self.colors["surface0"])
                game_label.pack(side="left", padx=5)
                
                # Show folder indicator if custom folder is set
                if item.get("custom_folder_path"):
                    location_icon = self.icon_handler.load_ui_icon("location.png", (12, 12))
                    if location_icon:
                        folder_indicator = tk.Label(item_frame, image=location_icon, cursor="hand2", bg=self.colors["surface0"])
                        folder_indicator.image = location_icon
                        folder_indicator.pack(side="left", padx=2)
                        folder_indicator.bind("<Button-1>", lambda e, path=item["custom_folder_path"]: self._open_folder(path))
                    else:
                        folder_indicator = tk.Label(item_frame, text="📁", font=("Segoe UI", 8), fg=self.colors["green"], bg=self.colors["surface0"])
                        folder_indicator.pack(side="left", padx=2)
                
                # Favorite button
                favorites = self.favorites_manager.get_favorites()
                is_fav = any(f[0] == item["game_name"] and f[1] == item["exe_name"] for f in favorites)
                bookmark_icon = self.icon_handler.load_ui_icon("bookmark.png", (16, 16))
                if bookmark_icon:
                    fav_btn = tk.Button(
                        item_frame,
                        image=bookmark_icon,
                        command=lambda g=item["game_name"], x=item["exe_name"]: self._toggle_favorite(g, x),
                        bg=self.colors["surface0"],
                        relief="flat",
                        bd=0,
                        highlightthickness=0,
                        cursor="hand2"
                    )
                    fav_btn.image = bookmark_icon
                    fav_btn.pack(side="right", padx=2)
                
                # Add folder button
                add_icon = self.icon_handler.load_ui_icon("add.png", (16, 16))
                if add_icon:
                    add_btn = tk.Button(
                        item_frame,
                        image=add_icon,
                        command=lambda g=item["game_name"], x=item["exe_name"]: self._create_app_folder(g, x),
                        bg=self.colors["surface0"],
                        relief="flat",
                        bd=0,
                        highlightthickness=0,
                        cursor="hand2"
                    )
                    add_btn.image = add_icon
                    add_btn.pack(side="right", padx=2)
                
                # Remove button
                close_icon = self.icon_handler.load_ui_icon("close.png", (16, 16))
                if close_icon:
                    remove_btn = tk.Button(item_frame, image=close_icon, command=lambda i=idx: self._remove_from_queue(i), bg=self.colors["surface0"], relief="flat", cursor="hand2")
                    remove_btn.image = close_icon
                    remove_btn.pack(side="right", padx=2)
                
                # Add separator line (skip after last item)
                if idx < len(self.queue_items) - 1:
                    separator = tk.Frame(self.queue_frame, height=1, bg=self.colors["surface1"])
                    separator.pack(fill="x", padx=5, pady=(0, 1))
        
        self._update_selection_count()

    def _remove_from_queue(self, idx: int) -> None:
        """Remove item from queue."""
        if idx < len(self.queue_items):
            del self.queue_items[idx]
            self._update_queue_display()
            self._update_selection_count()

    def _toggle_queue_item(self, idx: int, var: tk.BooleanVar) -> None:
        """Toggle queue item checkbox."""
        if idx < len(self.queue_items):
            self.queue_items[idx]["checked"] = var.get()
            self._update_selection_count()

    def _toggle_favorite(self, game_name: str, exe_name: str) -> None:
        """Toggle favorite status."""
        favorites = self.favorites_manager.get_favorites()
        is_fav = any(f[0] == game_name and f[1] == exe_name for f in favorites)
        
        if is_fav:
            self.favorites_manager.remove_favorite(game_name, exe_name)
        else:
            self.favorites_manager.add_favorite(game_name, exe_name)
        
        self._update_favorites_and_recent()
        self._update_queue_display()

    def _create_app_folder(self, game_name: str, exe_name: str) -> None:
        """Create a folder with the app name on the desktop and set it as exe creation path."""
        import os
        try:
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            folder_name = game_name.replace("/", "-").replace("\\", "-").replace(":", "-").replace("*", "-").replace("?", "-").replace('"', "-").replace("<", "-").replace(">", "-").replace("|", "-")
            folder_path = os.path.join(desktop_path, folder_name)
            
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                messagebox.showinfo("Folder Created", f"✓ Created folder: {folder_name}\n📁 Location: {folder_path}\n\nEXE will be created in this folder when quest starts.")
            else:
                messagebox.showinfo("Folder Exists", f"✓ Using existing folder: {folder_name}\n📁 Location: {folder_path}\n\nEXE will be created in this folder when quest starts.")
            
            # Update queue item with custom folder path
            for item in self.queue_items:
                if item["game_name"] == game_name and item["exe_name"] == exe_name:
                    item["custom_folder_path"] = folder_path
                    break
            
            # Update queue display to show folder is set
            self._update_queue_display()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create folder:\n{e}")

    def _open_folder(self, folder_path: str) -> None:
        """Open folder in file explorer."""
        import os
        import subprocess
        try:
            if os.path.exists(folder_path):
                subprocess.Popen(['explorer', folder_path])
            else:
                messagebox.showwarning("Folder Not Found", f"Folder does not exist:\n{folder_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open folder:\n{e}")

    def _open_help(self, event=None) -> None:
        """Open help HTML file in default browser."""
        import os
        import webbrowser
        try:
            # Get the directory where the executable is located
            if getattr(sys, "frozen", False):
                # Running as compiled exe - use PyInstaller's temp directory
                base_dir = sys._MEIPASS
            else:
                # Running as script
                base_dir = os.path.dirname(os.path.dirname(__file__))
            
            help_file = os.path.join(base_dir, "help.html")
            
            if os.path.exists(help_file):
                webbrowser.open(f"file:///{help_file.replace(os.sep, '/')}")
            else:
                messagebox.showerror("Help File Not Found", f"Help file not found at:\n{help_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open help:\n{e}")

    def _auto_check_updates(self) -> None:
        """Auto-check for updates on startup."""
        def on_check_complete(update_available: bool, latest_version: str, download_url: str) -> None:
            if update_available:
                release_notes = self.update_manager.get_release_notes()
                message = f"A new version ({latest_version}) is available!\n\nCurrent version: {APP_VERSION}\n\nRelease Notes:\n{release_notes[:500]}..."
                
                if messagebox.askyesno("Update Available", message):
                    if download_url:
                        webbrowser.open(download_url)
                    else:
                        webbrowser.open(GITHUB_RELEASES)
        
        self.update_manager.check_for_updates_async(on_check_complete)

    def _update_selection_count(self) -> None:
        """Update selection count."""
        checked_count = sum(1 for item in self.queue_items if item["checked"])
        total_count = len(self.queue_items)
        
        if hasattr(self, 'lbl_selected_count') and self.lbl_selected_count:
            self.lbl_selected_count.config(text=f"{checked_count} Selected")
        self.lbl_queue.config(text=f"SELECTED: {total_count} Games Queued")
        self.lbl_quest_status.config(text=f"{checked_count} Quest Rdy")
        
        # Update button text and state
        if not self.quests_running:
            self.btn_start.update_colors(
                base_color=self.colors["green"],
                dark_color="#437e10",
                fg_color="#FFFFFF",
                text=f"Start Quests ({checked_count})"
            )
        
        if checked_count == 0:
            self.btn_start.config(state="disabled")
        else:
            self.btn_start.config(state="normal")

    def _on_start_stop_button_click(self) -> None:
        """Handle start/stop button click."""
        if self.quests_running:
            self._stop_all_quests()
        else:
            self._start_selected_quests()

    def _start_selected_quests(self) -> None:
        """Start selected quests."""
        checked_items = [item for item in self.queue_items if item["checked"]]
        
        if not checked_items:
            messagebox.showwarning("Select Games", "Please check at least one game to start.")
            return
        
        # Update button to stop state
        self.quests_running = True
        self.btn_start.update_colors(
            base_color=self.colors["red"],
            dark_color="#8d0000",
            fg_color="#FFFFFF",
            text="Stop All Quests"
        )
        self.btn_start.update_icon(self.btn_start.stop_icon_name)
        
        for item in checked_items:
            self._check_discord_before_start(item["game_name"], item["exe_name"])

    def _stop_all_quests(self) -> None:
        """Stop all quests."""
        if not self.quest_managers:
            return
        
        for quest_id in list(self.quest_managers.keys()):
            self._stop_quest(quest_id)
        
        self.quest_managers.clear()
        self.timers.clear()
        self.quests_running = False
        # Use custom duration instead of hardcoded 15:00
        minutes = self.custom_duration
        timer_text = f"{minutes:02d}:00"
        self.lbl_timer.config(text=timer_text)
        
        # Reset button to start state
        checked_count = len(self.queue_items)
        self.btn_start.update_colors(
            base_color=self.colors["green"],
            dark_color="#437e10",
            fg_color="#FFFFFF",
            text=f"Start Quests ({checked_count})"
        )
        self.btn_start.update_icon(self.btn_start.play_icon_name)

    def _check_discord_before_start(self, game_name: str, exe_name: str) -> None:
        """Check Discord before starting."""
        if not self.discord_checker.is_discord_running():
            if self.settings_manager.get("discord_auto_open", True):
                response = messagebox.askyesno("Discord Not Running", "Discord is not currently running. Would you like to open it now?")
                if response:
                    self.discord_checker.open_discord()
        
        self._create_and_start_quest(game_name, exe_name)

    def _create_and_start_quest(self, game_name: str, exe_name: str) -> None:
        """Create and start quest."""
        # Check multi-quest limit
        if self.multi_quest_limit > 0:
            active_count = len(self.quest_managers)
            if active_count >= self.multi_quest_limit:
                messagebox.showwarning("Quest Limit Reached", f"Maximum {self.multi_quest_limit} quests allowed at once.")
                return
        
        self.quest_counter += 1
        quest_id = f"quest_{self.quest_counter}"
        
        quest_manager = QuestManager(quest_id, custom_data_dir=self.custom_data_dir)
        quest_manager.set_selected_game(game_name, exe_name)
        
        timer = Timer()
        timer.set_duration_minutes(self.custom_duration)  # Set duration in minutes
        timer.set_on_tick(lambda t: self._on_timer_tick(quest_id, t))
        timer.set_on_complete(lambda: self._on_timer_complete(quest_id))
        
        quest_manager.on_start_callback = lambda: self._on_quest_start(quest_id)
        quest_manager.on_stop_callback = lambda: self._on_quest_stop(quest_id)
        
        self.quest_managers[quest_id] = quest_manager
        self.timers[quest_id] = timer
        
        try:
            # Check if queue item has custom folder path
            custom_folder_path = None
            for item in self.queue_items:
                if item["game_name"] == game_name and item["exe_name"] == exe_name:
                    custom_folder_path = item.get("custom_folder_path")
                    break
            
            # Use custom folder path if set, otherwise use default exe path from settings, then default base directory
            if custom_folder_path:
                base_dir = custom_folder_path
            elif self.default_exe_path:
                base_dir = self.default_exe_path
            else:
                base_dir = quest_manager.get_base_directory()
            
            fake_exe_path = self.process_manager.create_fake_executable(exe_name, base_dir)
            quest_manager.set_fake_exe_path(fake_exe_path)
            self.dummy_registry.register_dummy(fake_exe_path, game_name, exe_name)
            
            script_path = os.path.abspath(__file__) if not getattr(sys, "frozen", False) else None
            self.process_manager.spawn_dummy_process(quest_id, fake_exe_path, exe_name, game_name, script_path, self.colors, self.custom_duration, self.dummy_cat_selection)
            
            quest_manager.start_quest()
            self.favorites_manager.add_recent(game_name, exe_name)
            self._update_favorites_and_recent()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start process:\n{e}")

    def _stop_quest(self, quest_id: str) -> None:
        """Stop a quest."""
        if quest_id in self.quest_managers:
            self.quest_managers[quest_id].stop_quest()
        
        if quest_id in self.timers:
            self.timers[quest_id].stop()
        
        self.process_manager.terminate_process(quest_id)
        
        if quest_id in self.quest_managers:
            quest_manager = self.quest_managers[quest_id]
            fake_exe_path = quest_manager.get_fake_exe_path()
            if fake_exe_path:
                self.dummy_registry.unregister_dummy(fake_exe_path)
                try:
                    os.remove(fake_exe_path)
                except Exception:
                    pass
            del self.quest_managers[quest_id]
        
        if quest_id in self.timers:
            del self.timers[quest_id]
        
        # Reset button state if no more quests
        if not self.quest_managers:
            self.quests_running = False
            checked_count = len(self.queue_items)
            self.btn_start.update_colors(
                base_color=self.colors["green"],
                dark_color="#437e10",
                fg_color="#FFFFFF",
                text=f"Start Quests ({checked_count})"
            )
            self.btn_start.update_icon(self.btn_start.play_icon_name)
            # Use custom duration instead of hardcoded 15:00
            minutes = self.custom_duration
            seconds = minutes * 60
            timer_text = f"{minutes:02d}:00"
            self.lbl_timer.config(text=timer_text)
            self.lbl_status.config(text="● DATABASE READY", fg=self.colors["green"])
            self.tray_manager.update_menu_state(False)

    def _on_quest_start(self, quest_id: str) -> None:
        """Callback when quest starts."""
        if quest_id not in self.quest_managers:
            return
        
        quest_manager = self.quest_managers[quest_id]
        exe_name = quest_manager.get_exe_name()
        
        self.lbl_status.config(text=f"● EMULATING: {exe_name}", fg=self.colors["green"])
        
        if quest_id in self.timers:
            duration = quest_manager.get_custom_duration()
            if duration:
                self.timers[quest_id].set_duration_minutes(duration)
            self.timers[quest_id].start(self.root.after)
            self.tray_manager.update_menu_state(True)

    def _on_quest_stop(self, quest_id: str) -> None:
        """Callback when quest stops."""
        if not self.quest_managers:
            # Use custom duration instead of hardcoded 15:00
            minutes = self.custom_duration
            timer_text = f"{minutes:02d}:00"
            self.lbl_timer.config(text=timer_text)
            self.lbl_status.config(text="● DATABASE READY", fg=self.colors["green"])
            self.tray_manager.update_menu_state(False)

    def _on_timer_tick(self, quest_id: str, time_str: str) -> None:
        """Callback when timer ticks."""
        if quest_id in self.timers:
            self.lbl_timer.config(text=time_str)
            
            elapsed = self.timers[quest_id].get_elapsed_seconds()
            total = self.timers[quest_id].total_seconds
            percentage = (elapsed / total) * 100
            self.progress_bar.set_progress(percentage / 100)
            
            self.tray_manager.update_timer_overlay(time_str, True)

    def _on_timer_complete(self, quest_id: str) -> None:
        """Callback when timer completes."""
        self._stop_quest(quest_id)
        messagebox.showinfo("Quest Complete!", "Quest completed! Check Discord to claim your reward.")

    def _clean_all_data(self) -> None:
        """Clean all data."""
        if self.quest_managers:
            messagebox.showwarning("Quest Active", "Stop all quests before cleaning dummy files.")
            return
        
        deleted_count, _ = self.cleanup.clean_dummies()
        favorites_count = len(self.favorites_manager.get_favorites())
        self.favorites_manager.clear_favorites()
        recent_count = len(self.favorites_manager.get_recent())
        self.favorites_manager.clear_recent()
        
        # Clean custom folders created by add button
        import os
        import shutil
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        folders_deleted = 0
        for item in self.queue_items:
            if "custom_folder_path" in item:
                folder_path = item["custom_folder_path"]
                if os.path.exists(folder_path):
                    try:
                        shutil.rmtree(folder_path)  # Removes folder and all contents
                        folders_deleted += 1
                        del item["custom_folder_path"]
                    except Exception:
                        pass  # Folder not empty or other error
        
        self._update_favorites_and_recent()
        
        messagebox.showinfo("Cleanup Complete", f"Cleaned up {deleted_count} dummy executable(s).\nCleared {favorites_count} favorite(s).\nCleared {recent_count} recent item(s).\nRemoved {folders_deleted} custom folder(s).")

    def _update_favorites_and_recent(self) -> None:
        """Update favorites and recent lists."""
        self.listbox_favorites.delete(0, tk.END)
        self.listbox_recent.delete(0, tk.END)
        
        favorites = self.favorites_manager.get_favorites()
        for game_name, exe_name in favorites:
            display_text = game_name[:25] + "..." if len(game_name) > 25 else game_name
            self.listbox_favorites.insert(tk.END, display_text)
        
        if not favorites:
            self.listbox_favorites.insert(tk.END, "No favorites yet")
        
        recent_list = self.favorites_manager.get_recent()
        for game_name, exe_name in recent_list:
            display_text = game_name[:25] + "..." if len(game_name) > 25 else game_name
            self.listbox_recent.insert(tk.END, display_text)
        
        if not recent_list:
            self.listbox_recent.insert(tk.END, "No recent history")

    def _on_favorite_double_click(self, event) -> None:
        """Handle favorite double-click."""
        selection = self.listbox_favorites.curselection()
        if selection:
            display_text = self.listbox_favorites.get(selection[0])
            favorites = self.favorites_manager.get_favorites()
            for fav_game_name, exe_name in favorites:
                # Match using full game name (display text may be truncated)
                if display_text == fav_game_name or display_text == (fav_game_name[:25] + "..." if len(fav_game_name) > 25 else fav_game_name):
                    self._add_to_queue(fav_game_name.strip(), exe_name.strip())
                    break

    def _on_recent_double_click(self, event) -> None:
        """Handle recent double-click."""
        selection = self.listbox_recent.curselection()
        if selection:
            display_text = self.listbox_recent.get(selection[0])
            recent_list = self.favorites_manager.get_recent()
            for recent_game_name, exe_name in recent_list:
                # Match using full game name (display text may be truncated)
                if display_text == recent_game_name or display_text == (recent_game_name[:25] + "..." if len(recent_game_name) > 25 else recent_game_name):
                    self._add_to_queue(recent_game_name.strip(), exe_name.strip())
                    break

    def _show_settings_dialog(self) -> None:
        """Show settings dialog."""
        current_settings = self.settings_manager.get_all()
        self.settings_dialog_instance = SettingsDialog(
            self.root,
            current_settings,
            self.colors,
            self._on_settings_save,
            self._on_theme_change_from_settings,
            self.icon_handler
        )
        print(f"Settings dialog created with callbacks: save={self._on_settings_save}, theme={self._on_theme_change_from_settings}")

    def _on_settings_save(self, new_settings: dict) -> None:
        """Handle settings save."""
        for key, value in new_settings.items():
            self.settings_manager.set(key, value)
        
        # Reload local settings variables
        self.custom_duration = self.settings_manager.get("custom_duration", 15)
        self.multi_quest_limit = self.settings_manager.get("multi_quest_limit", 0)
        self.remember_duration = self.settings_manager.get("remember_duration", True)
        self.minimize_to_tray = self.settings_manager.get("minimize_to_tray", False)
        self.auto_clean_on_exit = self.settings_manager.get("auto_clean_on_exit", True)
        self.discord_auto_open = self.settings_manager.get("discord_auto_open", True)
        self.auto_check_updates = self.settings_manager.get("auto_check_updates", True)
        self.dummy_cat_selection = self.settings_manager.get("dummy_cat_selection", "Cat-1")
        self.default_exe_path = self.settings_manager.get("exe_creation_path", "")
        self.custom_data_dir = self.settings_manager.get("data_folder_path", "")
        
        # Update timer display with new duration
        if hasattr(self, 'lbl_timer'):
            timer_text = f"{self.custom_duration:02d}:00"
            self.lbl_timer.config(text=timer_text)

    def _on_theme_change_from_settings(self, theme: str, custom_colors: dict = None) -> None:
        """Handle theme change from settings."""
        self.theme_manager.set_theme(theme, custom_colors=custom_colors)
        # Update settings dialog if it's open
        if hasattr(self, 'settings_dialog_instance') and self.settings_dialog_instance:
            new_colors = self.theme_manager.get_current_colors()
            self.settings_dialog_instance.update_colors(new_colors)

    def _on_tray_restore(self) -> None:
        """Handle tray restore."""
        self.root.deiconify()
        self.root.state("normal")

    def _on_tray_start_stop(self) -> None:
        """Handle tray start/stop."""
        if self.quest_managers:
            for quest_id in list(self.quest_managers.keys()):
                self._stop_quest(quest_id)

    def _on_tray_quit(self) -> None:
        """Handle tray quit."""
        self._on_window_close()

    def _on_window_close(self) -> None:
        """Handle window close."""
        # Save layout before closing
        self._save_layout()
        
        if self.settings_manager.get("auto_clean_on_exit", True):
            self._clean_all_data()
        
        self.process_manager.terminate_all_processes()
        self.tray_manager.stop()
        self.root.destroy()
