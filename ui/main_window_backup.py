"""Main application window for Discord Quest Manager."""

import os
import sys
import tkinter as tk
from tkinter import messagebox
import webbrowser
from typing import List, Tuple

from config.constants import COLORS, COLORS_DARK, COLORS_LIGHT, COLORS_DISCORD_DARK, COLORS_DISCORD_LIGHT, WINDOW, FONTS, APP_NAME, APP_VERSION, AUTHOR, GITHUB_PROFILE, FONT_NAME
from core.database import Database
from core.search import Search
from core.quest_manager import QuestManager
from core.timer import Timer
from core.cleanup import Cleanup
from core.settings_manager import SettingsManager
from utils.icon_handler import IconHandler
from ui.pixel_button import PixelButton
from ui.pixel_progress_bar import PixelProgressBar
from ui.pixel_container import PixelContainer
from ui.layout_manager import LayoutManager
from core.favorites_manager import FavoritesManager
from core.theme_manager import ThemeManager
from core.dummy_registry import DummyRegistry
from core.discord_checker import DiscordChecker
from ui.about_dialog import AboutDialog
from ui.settings_dialog import SettingsDialog
from utils.process_manager import ProcessManager
from utils.tray_manager import TrayManager


class MainWindow:
    """Main application window for Discord Quest Manager."""

    def __init__(self, root: tk.Tk):
        self.root = root
        
        # Initialize core components
        self.database = Database()
        self.search = Search([])
        self.quest_managers: dict = {}  # Multiple quest managers
        self.timers: dict = {}  # Multiple timers
        self.cleanup = Cleanup()
        self.process_manager = ProcessManager()
        self.icon_handler = IconHandler()
        self.settings_manager = SettingsManager()
        self.favorites_manager = FavoritesManager()
        self.theme_manager = ThemeManager()
        self.dummy_registry = DummyRegistry()
        self.discord_checker = DiscordChecker()
        self.tray_manager = TrayManager()
        
        # UI state
        self.found_matches: List[Tuple[str, str]] = []
        self.quest_counter = 0
        self.quests_running = False  # Track if any quests are currently running
        
        # Queue for target executables staging
        self.queue_items: List[Dict] = []  # Each item: {"game_name": str, "exe_name": str, "checked": bool}
        
        # Initialize panel references
        self.main_panel = None  # Legacy reference, will be replaced by main_viewer_panel
        self.master_sidebar_panel = None
        self.main_viewer_panel = None
        
        # Load saved settings and theme first
        self._load_settings()
        
        # Initialize layout manager with current theme colors
        current_colors = self.theme_manager.get_colors()
        self.layout_manager = LayoutManager(self.root, current_colors)
        
        # Setup callbacks
        self._setup_callbacks()
        
        # Setup window
        self._setup_window()
        self._setup_ui()
        
        # Setup tray
        self._setup_tray()
        
        # Load database
        self._load_database()

    def _setup_callbacks(self) -> None:
        """Setup callbacks for core components."""
        self.theme_manager.set_on_theme_change(self._on_theme_change)
        
        # Setup tray callbacks
        self.tray_manager.set_on_restore(self._on_tray_restore)
        self.tray_manager.set_on_start_stop(self._on_tray_start_stop)
        self.tray_manager.set_on_quit(self._on_tray_quit)

    def _load_settings(self) -> None:
        """Load application settings and apply saved theme."""
        # Load saved theme and apply it
        saved_theme = self.settings_manager.get("theme", "mocha")
        
        # Apply the saved theme (theme manager loads from JSON files)
        self.theme_manager.set_theme(saved_theme)

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
        self.root.configure(bg=COLORS["base"])
        self.icon_handler.apply_to_window(self.root)
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)

    def _setup_ui(self) -> None:
        """Setup the user interface with retro terminal layout using grid system."""
        # Setup main grid layout using layout manager
        self.layout_manager.setup_main_grid()
        
        # Create all main containers using layout manager
        containers = self.layout_manager.create_main_containers()
        
        # Assign container references
        self.master_sidebar_panel = containers['sidebar']
        self.main_right_panel = containers['right_panel']
        self.search_bar_card = containers['search_bar']
        self.executables_viewer_card = containers['executables_viewer']
        self.nested_footer_card = containers['footer_card']
        
        # Get content frames
        sidebar_surface = self.master_sidebar_panel.content_frame
        search_surface = self.search_bar_card.content_frame
        viewer_surface = self.executables_viewer_card.content_frame
        footer_surface = self.nested_footer_card.content_frame
        
        # Setup sidebar content
        self._setup_sidebar(sidebar_surface)
        
        # Setup main panel content (search and executables)
        self._setup_main_panel_content(search_surface, viewer_surface)
        
        # Setup footer controls inside nested card
        self._setup_footer_controls(footer_surface)
        
        # ====================================================================
        # [MAIN CONTAINER 3] THE COPYRIGHT RIBBON STRIP (Absolute Floor)
        # ====================================================================
        self.bottom_credit_row = tk.Frame(self.root, bg=COLORS["mantle"], height=24)
        self.bottom_credit_row.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.bottom_credit_row.grid_propagate(False)
        
        # Left-aligned Copyright Label container
        copyright_container = tk.Frame(self.bottom_credit_row, bg=COLORS["mantle"])
        copyright_container.ui_role = "background_sidebar"
        copyright_container.pack(side="left", anchor="w", padx=15, pady=4)
        
        # Copyright text
        copyright_label = tk.Label(
            copyright_container,
            text=" Aliester Eroan | ",
            font=("Press Start 2P", 6),
            fg=COLORS["subtext0"],
            bg=COLORS["mantle"]
        )
        copyright_label.ui_role = "text_secondary"
        copyright_label.pack(side="left", anchor="w")
        
        # GitHub icon and profile link
        github_frame = tk.Frame(copyright_container, bg=COLORS["mantle"])
        github_frame.ui_role = "background_sidebar"
        github_frame.pack(side="left", anchor="w")
        
        github_icon = None
        try:
            github_icon = self.icon_handler.load_ui_icon("github.png", (12, 12), theme="")
        except Exception:
            pass
        
        if github_icon:
            github_icon_label = tk.Label(
                github_frame,
                image=github_icon,
                bg=COLORS["mantle"],
                cursor="hand2"
            )
            github_icon_label.ui_role = "background_sidebar"
            github_icon_label.image = github_icon
            github_icon_label.pack(side="left", padx=(5, 2))
            github_icon_label.bind("<Button-1>", lambda e: webbrowser.open(GITHUB_PROFILE))
        
        # Clickable GitHub Profile link
        github_label = tk.Label(
            github_frame,
            text="GitHub Profile",
            font=("Press Start 2P", 6),
            fg=COLORS["blue"],
            bg=COLORS["mantle"],
            cursor="hand2"
        )
        github_label.ui_role = "text_link"
        github_label.pack(side="left", padx=(0, 5))
        github_label.bind("<Button-1>", lambda e: webbrowser.open(GITHUB_PROFILE))
        github_label.bind("<Enter>", lambda e: github_label.config(fg=COLORS["lavender"]))
        github_label.bind("<Leave>", lambda e: github_label.config(fg=COLORS["blue"]))
        
        # Right-aligned Version Label
        version_label = tk.Label(
            self.bottom_credit_row,
            text="v1.1.0",
            font=("Press Start 2P", 6),
            fg=COLORS["subtext0"],
            bg=COLORS["mantle"]
        )
        version_label.ui_role = "text_secondary"
        version_label.pack(side="right", anchor="e", padx=15, pady=4)
        
        # Load database
        self._load_database()
    
    def _on_sidebar_game_select(self, game_name: str, exe_name: str) -> None:
        """Handle game selection from sidebar (legacy - no longer used)."""
        pass
    
    def create_pixel_divider(self, parent_surface: tk.Frame) -> tk.Frame:
        """Draws a flat retro layout separator line.
        
        Args:
            parent_surface: Parent frame to pack the divider into
            
        Returns:
            The divider frame
        """
        # Forcing padx=0 strips away the side margins so the frame touches the outer black borders flawlessly
        divider = tk.Frame(parent_surface, bg=COLORS["mantle"], height=2)
        divider.pack(side="top", fill="x", padx=0, pady=5)
        return divider

    def _setup_sidebar(self, sidebar_surface: tk.Frame) -> None:
        """Setup the left sidebar with isolated component containers."""
        # Configure grid layout for sidebar to allow vertical expansion
        sidebar_surface.columnconfigure(0, weight=1)
        sidebar_surface.rowconfigure(0, weight=0)  # Header (fixed)
        sidebar_surface.rowconfigure(1, weight=0)  # Status (fixed)
        sidebar_surface.rowconfigure(2, weight=0)  # Favorites (fixed)
        sidebar_surface.rowconfigure(3, weight=0)  # Recent (fixed)
        sidebar_surface.rowconfigure(4, weight=1)  # Spacer (expands vertically)
        sidebar_surface.rowconfigure(5, weight=0)  # Buttons (fixed at bottom)
        
        # CARD 1: BRAND LOGO HEADER (Locked to 250px width, 100px height)
        self.header_card = PixelContainer(sidebar_surface, width=250, height=100, bg_color=COLORS["mantle"], pixel_scale=3)
        self.header_card.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        
        # Pack all header metadata safely inside its internal content surface
        header_content = self.header_card.content_frame
        
        # App icon and title
        icon_row = tk.Frame(header_content, bg=COLORS["mantle"])
        icon_row.ui_role = "background_card"
        icon_row.pack(fill="x", pady=(0, 10))
        
        try:
            app_icon = self.icon_handler.load_icon()
            if app_icon:
                icon_label = tk.Label(icon_row, image=app_icon, bg=COLORS["mantle"])
                icon_label.ui_role = "background_card"
                icon_label.image = app_icon
                icon_label.pack(side="left", padx=(0, 10))
        except Exception:
            pass
        
        title_label = tk.Label(
            icon_row,
            text="Discord Quest\nManager",
            font=("Press Start 2P", 7),
            fg=COLORS["pink"],
            bg=COLORS["mantle"],
            justify="left"
        )
        title_label.ui_role = "text_title"
        title_label.pack(side="left", padx=6)
        
        # Status indicator
        self.lbl_status = tk.Label(
            header_content,
            text="● DATABASE READY",
            font=FONTS["status"],
            fg=COLORS["green"],
            bg=COLORS["mantle"]
        )
        self.lbl_status.ui_role = "text_status_success"
        self.lbl_status.pack(anchor="w")
        
        self.lbl_game_count = tk.Label(
            header_content,
            text="Connecting...",
            font=("Segoe UI", 8),
            fg=COLORS["subtext0"],
            bg=COLORS["mantle"]
        )
        self.lbl_game_count.ui_role = "text_secondary"
        self.lbl_game_count.pack(anchor="w")
        
        # ====================================================================
        # CARD 2: SELECTED GAMES STATUS CARD (250px width, 50px height)
        # ====================================================================
        self.status_card = PixelContainer(sidebar_surface, width=250, height=50, bg_color=COLORS["mantle"], pixel_scale=3)
        self.status_card.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        # Center your selected queue label strings inside this highlight card
        status_content = self.status_card.content_frame
        
        self.lbl_queue = tk.Label(
            status_content,
            text="SELECTED: 0 Games Queued",
            font=(FONT_NAME, 6),
            fg=COLORS["text"],
            bg=COLORS["mantle"]
        )
        self.lbl_queue.ui_role = "text_primary"
        self.lbl_queue.place(relx=0.5, rely=0.5, anchor="center")
        self.lbl_queue.lift()
        
        # ====================================================================
        # CARD 3: FAVORITES PANEL CONTAINER CARD (250px width, 105px height)
        # ====================================================================
        self.favorites_card = PixelContainer(sidebar_surface, width=250, height=105, bg_color=COLORS["mantle"], pixel_scale=3)
        self.favorites_card.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        # Pack the Favorites components inside the new pixelated background layer
        favorites_content = self.favorites_card.content_frame
        
        bookmark_icon = self.icon_handler.load_ui_icon("star.png", (16, 16))
        if bookmark_icon:
            fav_header = tk.Frame(favorites_content, bg=COLORS["mantle"])
            fav_header.ui_role = "background_card"
            fav_header.pack(fill="x", pady=(0, 6))
            
            # Center the header content
            header_container = tk.Frame(fav_header, bg=COLORS["mantle"])
            header_container.pack(anchor="center")
            
            tk.Label(header_container, image=bookmark_icon, bg=COLORS["mantle"]).pack(side="left", padx=(0, 6))
            tk.Label(header_container, image=bookmark_icon).image = bookmark_icon
            tk.Label(header_container, text="Favorites", font=FONTS["label"], fg=COLORS["text"], bg=COLORS["mantle"]).ui_role = "text_primary"
            tk.Label(header_container, text="Favorites", font=FONTS["label"], fg=COLORS["text"], bg=COLORS["mantle"]).pack(side="left")
        else:
            tk.Label(favorites_content, text="★ Favorites", font=FONTS["label"], fg=COLORS["text"], bg=COLORS["mantle"]).ui_role = "text_primary"
            tk.Label(favorites_content, text="★ Favorites", font=FONTS["label"], fg=COLORS["text"], bg=COLORS["mantle"]).pack(anchor="center", pady=(0, 6))
        
        self.listbox_favorites = tk.Listbox(
            favorites_content,
            font=FONTS["listbox"],
            bg=COLORS["surface0"],
            fg=COLORS["text"],
            selectbackground=COLORS["mauve"],
            selectforeground=COLORS["base"],
            relief="flat",
            highlightthickness=0,
            height=5,
            bd=0
        )
        self.listbox_favorites.ui_role = "background_listbox"
        self.listbox_favorites.pack(fill="x", padx=10, pady=(0, 5))
        self.listbox_favorites.bind("<Double-Button-1>", self._on_favorite_double_click)
        
        # ====================================================================
        # CARD 4: RECENT ITEMS HISTORY TRACK CONTAINER CARD (250px width, 155px height)
        # ====================================================================
        self.recent_card = PixelContainer(sidebar_surface, width=250, height=155, bg_color=COLORS["mantle"], pixel_scale=3)
        self.recent_card.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        
        # Map headers and item lists cleanly inside the internal content frame track
        recent_content = self.recent_card.content_frame
        
        clock_icon = self.icon_handler.load_ui_icon("clock.png", (16, 16))
        if clock_icon:
            recent_header = tk.Frame(recent_content, bg=COLORS["mantle"])
            recent_header.ui_role = "background_card"
            recent_header.pack(fill="x", pady=(0, 6))
            
            # Center the header content
            header_container = tk.Frame(recent_header, bg=COLORS["mantle"])
            header_container.pack(anchor="center")
            
            tk.Label(header_container, image=clock_icon, bg=COLORS["mantle"]).pack(side="left", padx=(0, 6))
            tk.Label(header_container, image=clock_icon).image = clock_icon
            tk.Label(header_container, text="Recent", font=FONTS["label"], fg=COLORS["text"], bg=COLORS["mantle"]).ui_role = "text_primary"
            tk.Label(header_container, text="Recent", font=FONTS["label"], fg=COLORS["text"], bg=COLORS["mantle"]).pack(side="left")
        else:
            tk.Label(recent_content, text="⏱ Recent", font=FONTS["label"], fg=COLORS["text"], bg=COLORS["mantle"]).ui_role = "text_primary"
            tk.Label(recent_content, text="⏱ Recent", font=FONTS["label"], fg=COLORS["text"], bg=COLORS["mantle"]).pack(anchor="center", pady=(0, 6))
        
        self.listbox_recent = tk.Listbox(
            recent_content,
            font=FONTS["listbox"],
            bg=COLORS["surface0"],
            fg=COLORS["text"],
            selectbackground=COLORS["mauve"],
            selectforeground=COLORS["base"],
            relief="flat",
            highlightthickness=0,
            height=5,
            bd=0
        )
        self.listbox_recent.ui_role = "background_listbox"
        self.listbox_recent.pack(side="top", fill="both", expand=True, padx=10, pady=(0, 8))
        self.listbox_recent.bind("<Double-Button-1>", self._on_recent_double_click)
        
        # Update with saved data
        self._update_favorites_and_recent()
        
        # ====================================================================
        # ROW 4: VERTICAL SPACER (expands to push buttons to bottom)
        # ====================================================================
        spacer_frame = tk.Frame(sidebar_surface, bg=COLORS["mantle"])
        spacer_frame.ui_role = "background_sidebar"
        spacer_frame.grid(row=4, column=0, sticky="nsew")
        
        # ====================================================================
        # CONTAINER E: SIDEBAR BUTTONS CONTAINER (anchored at bottom)
        # ====================================================================
        button_container = tk.Frame(sidebar_surface, bg=COLORS["mantle"])
        button_container.ui_role = "background_sidebar"
        button_container.grid(row=5, column=0, padx=10, pady=(5, 10), sticky="ew")
        
        # Clean all data button (pixelated)
        trash_icon = self.icon_handler.load_ui_icon("trash.png", (20, 20))
        clean_btn = PixelButton(
            button_container,
            text="Clean All Data",
            command=self._clean_all_data,
            bg_color=COLORS["surface0"],
            fg_color=COLORS["red"],
            icon=trash_icon,
            width=190,
            height=40,
            colors=COLORS
        )
        clean_btn.pack(side="top", anchor="center", padx=5, pady=(5, 5))
        
        # Settings button (pixelated)
        cog_icon = self.icon_handler.load_ui_icon("configuration.png", (20, 20))
        settings_btn = PixelButton(
            button_container,
            text="Settings",
            command=self._show_settings_dialog,
            bg_color=COLORS["surface0"],
            fg_color=COLORS["text"],
            icon=cog_icon,
            width=190,
            height=40,
            colors=COLORS
        )
        settings_btn.pack(side="top", anchor="center", padx=5, pady=(5, 5))
    
    def _setup_main_panel_content(self, search_surface: tk.Frame, viewer_surface: tk.Frame) -> None:
        """Setup the right main panel content (search bar and executables viewer)."""
        # Setup search bar in search_surface
        self._setup_search_bar(search_surface)
        
        # Setup executables viewer in viewer_surface
        self._setup_executables_viewer(viewer_surface)
    
    def _setup_search_bar(self, search_surface: tk.Frame) -> None:
        """Setup the search bar container."""
        # Search icon
        search_icon = self.icon_handler.load_ui_icon("search.png", (16, 16))
        if search_icon:
            search_label = tk.Label(search_surface, image=search_icon, bg=COLORS["surface0"])
            search_label.ui_role = "background_input"
            search_label.image = search_icon
            search_label.pack(side="left", padx=(10, 5), pady=8)
        
        # Search entry
        self.ent_search = tk.Entry(
            search_surface,
            font=FONTS["entry"],
            bg=COLORS["surface0"],
            fg=COLORS["text"],
            insertbackground=COLORS["green"],
            relief="flat",
            bd=0,
            highlightthickness=0
        )
        self.ent_search.ui_role = "background_input"
        self.ent_search.pack(side="left", fill="x", expand=True, padx=(0, 8), ipady=5)
        self.ent_search.bind("<KeyRelease>", self._on_search_key_press)
        self.ent_search.bind("<Escape>", self._hide_search_dropdown)
        self.ent_search.bind("<FocusOut>", self._on_search_focus_out)
        
        # Search dropdown (hidden by default)
        self.search_dropdown = tk.Frame(self.main_right_panel, bg=COLORS["surface0"], relief="flat", bd=0)
        self.search_dropdown.ui_role = "background_input"
    
    def _setup_executables_viewer(self, viewer_surface: tk.Frame) -> None:
        """Setup the target executables viewer container."""
        # Background frame for color layer
        self.exec_bg_frame = tk.Frame(viewer_surface, bg=COLORS["mantle"])
        self.exec_bg_frame.ui_role = "background_card"
        self.exec_bg_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Header
        target_header = tk.Frame(viewer_surface, bg=COLORS["mantle"])
        target_header.ui_role = "background_card"
        target_header.pack(fill="x", padx=15, pady=(10, 5))
        target_header.lift()
        
        tk.Label(
            target_header,
            text="TARGET EXECUTABLES",
            font=FONTS["card_title"],
            fg=COLORS["pink"],
            bg=COLORS["mantle"]
        ).ui_role = "text_title"
        tk.Label(
            target_header,
            text="TARGET EXECUTABLES",
            font=FONTS["card_title"],
            fg=COLORS["pink"],
            bg=COLORS["mantle"]
        ).pack(side="left")
        
        self.lbl_selected_count = tk.Label(
            target_header,
            text="0 Selected",
            font=FONTS["status"],
            fg=COLORS["subtext0"],
            bg=COLORS["mantle"]
        )
        self.lbl_selected_count.ui_role = "text_secondary"
        self.lbl_selected_count.pack(side="right")
        
        # Executables container (Dynamic width/height)
        self.exec_container = PixelContainer(
            viewer_surface,
            bg_color=COLORS["mantle"],
            pixel_scale=3
        )
        self.exec_container.pack(fill="both", expand=True, padx=15, pady=10)
        
        exec_content = self.exec_container.content_frame
        exec_content.pack(fill="both", expand=True)
        
        # Empty state
        self.empty_state = tk.Frame(exec_content, bg=COLORS["surface0"])
        self.empty_state.ui_role = "background_listbox"
        self.empty_state.pack(fill="both", expand=True)
        
        folder_icon_large = self.icon_handler.load_ui_icon("folder.png", (48, 48))
        if folder_icon_large:
            folder_label = tk.Label(self.empty_state, image=folder_icon_large, bg=COLORS["surface0"])
            folder_label.ui_role = "background_listbox"
            folder_label.image = folder_icon_large
            folder_label.place(relx=0.5, y=60, anchor="center")
        
        tk.Label(
            self.empty_state,
            text="NO GAMES ADDED",
            font=FONTS["empty_state"],
            fg=COLORS["text"],
            bg=COLORS["surface0"]
        ).ui_role = "text_primary"
        tk.Label(
            self.empty_state,
            text="NO GAMES ADDED",
            font=FONTS["empty_state"],
            fg=COLORS["text"],
            bg=COLORS["surface0"]
        ).pack(pady=(120, 5))
        
        tk.Label(
            self.empty_state,
            text="Type in the search bar above to select and queue game executables.",
            font=FONTS["body_small"],
            fg=COLORS["subtext0"],
            bg=COLORS["surface0"],
            wraplength=380
        ).ui_role = "text_secondary"
        tk.Label(
            self.empty_state,
            text="Type in the search bar above to select and queue game executables.",
            font=FONTS["body_small"],
            fg=COLORS["subtext0"],
            bg=COLORS["surface0"],
            wraplength=380
        ).pack()
        
        # Results listbox (hidden by default)
        self.results_frame = tk.Frame(exec_content, bg=COLORS["surface0"])
        self.results_frame.ui_role = "background_listbox"
        
        scrollbar = tk.Scrollbar(
            self.results_frame,
            bg=COLORS["mantle"],
            troughcolor=COLORS["surface0"],
            highlightthickness=0,
            relief="flat"
        )
        scrollbar.ui_role = "scrollbar"
        scrollbar.pack(side="right", fill="y")
        
        self.listbox = tk.Listbox(
            self.results_frame,
            font=FONTS["listbox"],
            bg=COLORS["surface0"],
            fg=COLORS["text"],
            selectbackground=COLORS["mauve"],
            selectforeground=COLORS["base"],
            relief="flat",
            highlightthickness=0,
            yscrollcommand=scrollbar.set,
            selectmode="extended",
            bd=0
        )
        self.listbox.ui_role = "background_listbox"
        self.listbox.pack(fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)
        self.listbox.bind("<<ListboxSelect>>", lambda e: self._update_selection_count())
    
    def _setup_footer_controls(self, footer_container: tk.Frame) -> None:
        """Setup the footer control row with timer, progress bar, and button."""
        # --- ROW 1: CONTROLS ROW (Timer, Loading Bar, and Action Button) ---
        top_control_row = tk.Frame(footer_container, bg=COLORS["surface0"])
        top_control_row.ui_role = "background_input"
        top_control_row.pack(side="top", fill="both", expand=True, padx=12, pady=2)
        
        # Configure grid layout for horizontal space distribution
        top_control_row.columnconfigure(0, weight=0)  # Left container column (timer)
        top_control_row.columnconfigure(1, weight=1)  # Center container column (progress bar stretches)
        top_control_row.columnconfigure(2, weight=0)  # Right container column (button)
        top_control_row.rowconfigure(0, weight=1)  # Allow row to expand vertically
        
        # --- CONTAINER 1: TIMER HOLDER with regular Frame (150px × 60px) ---
        timer_container = tk.Frame(top_control_row, bg=COLORS["surface0"], width=150, height=60)
        timer_container.ui_role = "background_input"
        timer_container.grid(row=0, column=0, padx=(15, 10), pady=6, sticky="w")
        timer_container.grid_propagate(False)  # Maintain fixed size
        
        # Timer label
        self.lbl_timer = tk.Label(
            timer_container,
            text="15:00",
            font=FONTS["timer"],
            fg=COLORS["green"],
            bg=COLORS["surface0"]
        )
        self.lbl_timer.ui_role = "text_status_success"
        self.lbl_timer.pack(pady=(5, 2))
        
        # Quest count label
        self.lbl_quest_count = tk.Label(
            timer_container,
            text="0 QUESTS READY",
            font=FONTS["status"],
            fg=COLORS["subtext0"],
            bg=COLORS["surface0"]
        )
        self.lbl_quest_count.ui_role = "text_secondary"
        self.lbl_quest_count.pack(side="top", anchor="center")
        
        # --- CONTAINER 2: PROGRESS BAR HOLDER with regular Frame (Dynamic width × 30px) ---
        bar_container = tk.Frame(top_control_row, bg=COLORS["surface0"], height=30)
        bar_container.ui_role = "background_input"
        bar_container.grid(row=0, column=1, padx=10, pady=6, sticky="ew")
        bar_container.grid_propagate(False)  # Maintain fixed height
        
        # Configure internal grid cells for bar_container
        bar_container.columnconfigure(0, weight=1)  # Progress bar stretches completely
        bar_container.columnconfigure(1, weight=0)  # Text stays fixed to its right side
        bar_container.rowconfigure(0, weight=1)
        
        # Progress bar in the center gap
        self.progress_bar = PixelProgressBar(
            bar_container,
            height=16,
            bg_color=COLORS["surface0"],
            fill_color=COLORS["green"],
            colors=COLORS
        )
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=(0, 15), pady=0)
        
        # Progress percentage label (place to right of progress bar)
        self.lbl_progress_pct = tk.Label(
            bar_container,
            text="0%",
            font=FONTS["status"],
            fg=COLORS["green"],
            bg=COLORS["surface0"]
        )
        self.lbl_progress_pct.ui_role = "text_status_success"
        self.lbl_progress_pct.grid(row=0, column=1, sticky="e", padx=(0, 5), pady=0)
        
        # --- CONTAINER 3: BUTTON HOLDER with regular Frame (Dynamic width × 40px) ---
        button_container = tk.Frame(top_control_row, bg=COLORS["surface0"], height=40)
        button_container.ui_role = "background_input"
        button_container.grid(row=0, column=2, padx=(10, 15), pady=6, sticky="e")
        button_container.grid_propagate(False)  # Maintain fixed height
        
        # Start/Stop button (pixelated)
        play_icon = self.icon_handler.load_ui_icon("play.png", (20, 20))
        stop_icon = self.icon_handler.load_ui_icon("stop-button.png", (20, 20))
        self.btn_start = PixelButton(
            button_container,
            text="Start Quests (0)",
            command=self._on_start_stop_button_click,
            bg_color=COLORS["green"],
            fg_color=COLORS["base"],
            icon=play_icon,
            width=250,
            height=45,
            colors=COLORS,
            state="disabled"
        )
        self.btn_start.play_icon = play_icon
        self.btn_start.stop_icon = stop_icon
        self.btn_start.pack(side="top", anchor="center", pady=5)

    def _on_search_key_press(self, event) -> None:
        """Handle key press in search entry for live autocomplete."""
        query = self.ent_search.get().strip()
        if len(query) >= 2:
            self._show_search_dropdown(query)
        else:
            self._hide_search_dropdown()
    
    def _on_search_focus_out(self, event) -> None:
        """Hide dropdown when focus leaves search."""
        # Small delay to allow clicking on dropdown items
        self.root.after(200, self._hide_search_dropdown)
    
    def _show_search_dropdown(self, query: str) -> None:
        """Show search dropdown with autocomplete results."""
        # Clear existing dropdown
        for widget in self.search_dropdown.winfo_children():
            widget.destroy()
        
        # Search for results
        results = self.search.search(query, max_results=10)
        
        if not results:
            self._hide_search_dropdown()
            return
        
        # Position dropdown below search bar using widget coordinates
        self.search_dropdown.place(
            x=self.ent_search.winfo_x(),
            y=self.ent_search.winfo_y() + self.ent_search.winfo_height() + 2,
            relwidth=1.0
        )
        self.search_dropdown.lift()  # Bring overlay to top z-index
        
        # Add result items
        for game_name, exe_name in results:
            item_frame = tk.Frame(
                self.search_dropdown,
                bg=COLORS["surface0"],
                cursor="hand2"
            )
            item_frame.pack(fill="x", padx=5, pady=2)
            
            # Bind click event to frame
            item_frame.bind("<Button-1>", lambda e, g=game_name, x=exe_name: self._add_to_queue(g, x))
            
            # Create label and bind click event to it as well
            item_label = tk.Label(
                item_frame,
                text=f"{game_name} → {exe_name}",
                font=FONTS["entry"],
                fg=COLORS["text"],
                bg=COLORS["surface0"],
                anchor="w"
            )
            item_label.pack(fill="x", padx=5, pady=3)
            item_label.bind("<Button-1>", lambda e, g=game_name, x=exe_name: self._add_to_queue(g, x))
            
            # Bind hover effects
            def on_enter(e, frame=item_frame):
                frame.config(bg=COLORS["surface1"])
                for child in frame.winfo_children():
                    child.config(bg=COLORS["surface1"])
            
            def on_leave(e, frame=item_frame):
                frame.config(bg=COLORS["surface0"])
                for child in frame.winfo_children():
                    child.config(bg=COLORS["surface0"])
            
            item_frame.bind("<Enter>", on_enter)
            item_frame.bind("<Leave>", on_leave)
            item_label.bind("<Enter>", on_enter)
            item_label.bind("<Leave>", on_leave)
    
    def _hide_search_dropdown(self) -> None:
        """Hide search dropdown."""
        self.search_dropdown.place_forget()
    
    def _add_to_queue(self, game_name: str, exe_name: str) -> None:
        """Add a game to the target executables queue."""
        self._hide_search_dropdown()
        self.ent_search.delete(0, tk.END)
        
        # Check if already in queue
        for item in self.queue_items:
            if item["game_name"] == game_name and item["exe_name"] == exe_name:
                return  # Already queued
        
        # Add to queue
        self.queue_items.append({
            "game_name": game_name,
            "exe_name": exe_name,
            "checked": True
        })
        
        # Update queue display and selection count
        self._update_queue_display()
        self._update_selection_count()
    
    def _update_queue_display(self) -> None:
        """Update the queue display with current items."""
        # Clear existing queue items (but preserve empty state and results frame)
        for widget in self.exec_container.winfo_children():
            if widget != self.empty_state and widget != self.results_frame:
                widget.destroy()
        
        # Hide empty state and results initially
        self.empty_state.pack_forget()
        self.results_frame.pack_forget()
        
        if not self.queue_items:
            # Show empty state when queue is empty
            self.empty_state.pack(fill="both", expand=True)
            # Ensure empty state widgets are visible
            for widget in self.empty_state.winfo_children():
                widget.lift()
        else:
            # Display queue items
            for idx, item in enumerate(self.queue_items):
                item_frame = tk.Frame(
                    self.exec_container,
                    bg=COLORS["surface0"],
                    relief="flat",
                    bd=0
                )
                item_frame.pack(fill="x", padx=5, pady=2)
                
                # Checkbox
                check_var = tk.BooleanVar(value=item["checked"])
                checkbox = tk.Checkbutton(
                    item_frame,
                    variable=check_var,
                    command=lambda i=idx, v=check_var: self._toggle_queue_item(i, v),
                    bg=COLORS["surface0"],
                    fg=COLORS["text"],
                    selectcolor=COLORS["surface0"],
                    activebackground=COLORS["surface0"],
                )
                checkbox.pack(side="left", padx=5)
                
                # Game name
                tk.Label(
                    item_frame,
                    text=item["game_name"],
                    font=FONTS["body"],
                    fg=COLORS["text"],
                    bg=COLORS["surface0"]
                ).pack(side="left", padx=5)
                
                # Favorite button
                favorites = self.favorites_manager.get_favorites()
                is_fav = any(f[0] == item["game_name"] and f[1] == item["exe_name"] for f in favorites)
                bookmark_icon = self.icon_handler.load_ui_icon("bookmark.png", (16, 16))
                if bookmark_icon:
                    fav_btn = tk.Button(
                        item_frame,
                        image=bookmark_icon,
                        command=lambda g=item["game_name"], x=item["exe_name"]: self._toggle_favorite(g, x),
                        bg=COLORS["surface0"],
                        relief="flat",
                        bd=0,
                        highlightthickness=0,
                        cursor="hand2"
                    )
                    fav_btn.image = bookmark_icon
                    fav_btn.pack(side="right", padx=2)
                
                # Remove button
                close_icon = self.icon_handler.load_ui_icon("close.png", (16, 16))
                if close_icon:
                    remove_btn = tk.Button(
                        item_frame,
                        image=close_icon,
                        command=lambda i=idx: self._remove_from_queue(i),
                        bg=COLORS["surface0"],
                        fg=COLORS["red"],
                        relief="flat",
                        bd=0,
                        highlightthickness=0,
                        cursor="hand2"
                    )
                    remove_btn.image = close_icon
                    remove_btn.pack(side="right", padx=2)
        
        # Update selected count and button state
        self._update_selection_count()
    
    def _toggle_queue_item(self, idx: int, var: tk.BooleanVar) -> None:
        """Toggle checked state of a queue item."""
        if idx < len(self.queue_items):
            self.queue_items[idx]["checked"] = var.get()
            self._update_queue_display()
            self._update_selection_count()
    
    def _remove_from_queue(self, idx: int) -> None:
        """Remove an item from the queue."""
        if idx < len(self.queue_items):
            del self.queue_items[idx]
            self._update_queue_display()
            self._update_selection_count()
    
    def _toggle_favorite(self, game_name: str, exe_name: str) -> None:
        """Toggle favorite status for a game."""
        # Check if already favorited
        favorites = self.favorites_manager.get_favorites()
        is_fav = any(f[0] == game_name and f[1] == exe_name for f in favorites)
        
        if is_fav:
            self.favorites_manager.remove_favorite(game_name, exe_name)
        else:
            self.favorites_manager.add_favorite(game_name, exe_name)
        
        # Update favorites display in sidebar
        self._update_favorites_and_recent()

    def _on_theme_change_click(self) -> None:
        """Handle theme selection from radio buttons."""
        theme = self.theme_var.get()
        self.theme_manager.set_theme(theme)
    
    def _show_results(self) -> None:
        """Show results frame and hide empty state."""
        self.empty_state.pack_forget()
        self.results_frame.pack(fill="both", expand=True)
    
    def _show_empty_state(self) -> None:
        """Show empty state and hide results frame."""
        self.results_frame.pack_forget()
        self.empty_state.pack(fill="both", expand=True)

    def _load_database(self) -> None:
        """Load the games database asynchronously."""
        self.database.load_async(self._on_db_loaded)

    def _on_db_loaded(self, success: bool, data: List) -> None:
        """Callback when database is loaded.
        
        Args:
            success: Whether the load was successful
            data: The loaded data
        """
        if success:
            self.search.update_database(data)
            self.lbl_status.config(
                text="● DATABASE READY",
                fg=COLORS["green"],
            )
            self.lbl_game_count.config(
                text=f"{len(data):,} registered",
                fg=COLORS["subtext0"],
            )
            self.btn_start.config(state="normal")
        else:
            self.lbl_status.config(
                text="● DATABASE OFFLINE",
                fg=COLORS["red"],
            )
            self.lbl_game_count.config(
                text="Check network connection",
                fg=COLORS["red"],
            )
            self.btn_start.config(state="disabled")

    def _search_games(self) -> None:
        """Search for games based on the query."""
        query = self.ent_search.get().strip()
        if not query:
            return

        self.listbox.delete(0, tk.END)
        self.found_matches = self.search.search(query, max_results=100)

        for game_name, exe_name in self.found_matches:
            self.listbox.insert(tk.END, self.search.format_result(game_name, exe_name))

        if not self.found_matches:
            self.listbox.insert(tk.END, "No matching games found.")
        else:
            self._show_results()
            self._update_selection_count()

    def _toggle_quest(self) -> None:
        """Toggle quest start/stop (legacy method, now uses multi-quest)."""
        # This method is no longer used in the new UI
        # Use _start_selected_quests instead
        self._start_selected_quests()

    def _start_quest(self) -> None:
        """Start the quest."""
        selection = self.listbox.curselection()
        if not selection or not self.found_matches:
            messagebox.showwarning(
                "Select Game",
                "Please search and select a game from the list first.",
            )
            return

        idx = selection[0]
        if idx >= len(self.found_matches):
            return

        game_name, exe_name = self.found_matches[idx]
        
        # Discord pre-check
        self._check_discord_before_start(game_name, exe_name)

    def _check_discord_before_start(self, game_name: str, exe_name: str) -> None:
        """Check Discord status before starting quest."""
        if not self.discord_checker.is_discord_running():
            if self.settings_manager.get("discord_auto_open", True):
                response = messagebox.askyesno(
                    "Discord Not Running",
                    "Discord is not currently running. Would you like to open it now?",
                )
                if response:
                    self.discord_checker.open_discord()
            else:
                messagebox.showwarning(
                    "Discord Not Running",
                    "Discord is not currently running. Please open Discord to track your quest progress.",
                )
        
        # Proceed with starting quest
        self._create_and_start_quest(game_name, exe_name)

    def _create_and_start_quest(self, game_name: str, exe_name: str) -> None:
        """Create quest manager and start the quest."""
        self.quest_counter += 1
        quest_id = f"quest_{self.quest_counter}"
        
        # Create quest manager for this instance
        quest_manager = QuestManager(quest_id)
        quest_manager.set_selected_game(game_name, exe_name)
        
        # Set custom duration if remembered
        if self.settings_manager.get("remember_duration", True):
            custom_duration = self.settings_manager.get("custom_duration", 15)
            quest_manager.set_custom_duration(custom_duration)
        
        # Create timer for this quest
        timer = Timer()
        timer.set_on_tick(lambda t: self._on_timer_tick(quest_id, t))
        timer.set_on_complete(lambda: self._on_timer_complete(quest_id))
        
        # Setup callbacks
        quest_manager.on_start_callback = lambda: self._on_quest_start(quest_id)
        quest_manager.on_stop_callback = lambda: self._on_quest_stop(quest_id)
        
        # Store managers
        self.quest_managers[quest_id] = quest_manager
        self.timers[quest_id] = timer
        
        try:
            # Create fake executable
            base_dir = quest_manager.get_base_directory()
            fake_exe_path = self.process_manager.create_fake_executable(exe_name, base_dir)
            quest_manager.set_fake_exe_path(fake_exe_path)
            
            # Register dummy in registry
            self.dummy_registry.register_dummy(fake_exe_path, game_name, exe_name)
            
            # Spawn dummy process with current theme colors
            script_path = os.path.abspath(__file__) if not getattr(sys, "frozen", False) else None
            self.process_manager.spawn_dummy_process(quest_id, fake_exe_path, exe_name, game_name, script_path, COLORS)
            
            # Start quest
            quest_manager.start_quest()
            
            # Add to recent
            self.favorites_manager.add_recent(game_name, exe_name)
            self._update_favorites_and_recent()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start process:\n{e}")
            # Cleanup on failure
            if quest_id in self.quest_managers:
                del self.quest_managers[quest_id]
            if quest_id in self.timers:
                del self.timers[quest_id]

    def _start_selected_quests(self) -> None:
        """Start multiple selected quests from the queue."""
        # Get checked items from queue
        checked_items = [item for item in self.queue_items if item["checked"]]
        
        if not checked_items:
            messagebox.showwarning(
                "Select Games",
                "Please select games from the TARGET EXECUTABLES list first.",
            )
            return
        
        # Check multi-quest limit
        limit = self.settings_manager.get("multi_quest_limit", 0)
        if limit > 0 and len(checked_items) > limit:
            messagebox.showwarning(
                "Limit Exceeded",
                f"Multi-quest limit is set to {limit}. You selected {len(checked_items)} games.",
            )
            return
        
        for item in checked_items:
            game_name = item["game_name"]
            exe_name = item["exe_name"]
            self._check_discord_before_start(game_name, exe_name)
        
        # Only update button to stop state if we actually have running quests
        if self.quest_managers:
            self.quests_running = True
            self._update_start_stop_button()
    
    def _on_start_stop_button_click(self) -> None:
        """Handle start/stop button click based on current state."""
        if self.quests_running:
            self._stop_all_quests()
        else:
            # Update button immediately to show stopping state
            self.quests_running = True
            self._update_start_stop_button()
            self._start_selected_quests()
    
    def _stop_all_quests(self) -> None:
        """Stop all currently running quests."""
        if not self.quest_managers:
            return
        
        # Stop all quest managers
        for quest_id in list(self.quest_managers.keys()):
            self._stop_quest(quest_id)
        
        # Clear quest tracking
        self.quest_managers.clear()
        self.timers.clear()
        
        # Update UI state
        self.quests_running = False
        self._update_start_stop_button()
        
        # Reset timer display
        self.lbl_timer.config(text="15:00")
        
        # Reset progress bar
        self.progress_bar.set_progress(0.0)
    
    def _update_start_stop_button(self) -> None:
        """Update start/stop button appearance based on running state."""
        if self.quests_running:
            # Change to stop button
            self.btn_start.update_icon(self.btn_start.stop_icon)
            self.btn_start.update_colors(COLORS["red"], COLORS["base"], "Stop All Quests")
        else:
            # Change to start button
            checked_count = len([item for item in self.queue_items if item["checked"]])
            self.btn_start.update_icon(self.btn_start.play_icon)
            self.btn_start.update_colors(COLORS["green"], COLORS["base"], f"Start Quests ({checked_count})")
    
    def _update_selection_count(self) -> None:
        """Update the selection count display."""
        checked_count = len([item for item in self.queue_items if item["checked"]])
        total_count = len(self.queue_items)
        
        self.lbl_selected_count.config(text=f"{checked_count} Selected")
        self.lbl_queue.config(text=f"SELECTED: {total_count} Games Queued")
        self.lbl_quest_count.config(text=f"{checked_count} QUESTS READY")
        
        # Only update button text if not running
        if not self.quests_running:
            self.btn_start.update_colors(COLORS["green"], COLORS["base"], f"Start Quests ({checked_count})")
        
        # Disable button if no items selected
        if checked_count == 0:
            self.btn_start.config(state="disabled")
        else:
            self.btn_start.config(state="normal")

    def _stop_quest(self, quest_id: str) -> None:
        """Stop a specific quest.
        
        Args:
            quest_id: ID of the quest to stop
        """
        if quest_id in self.quest_managers:
            quest_manager = self.quest_managers[quest_id]
            quest_manager.stop_quest()
            
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

    def _on_quest_start(self, quest_id: str) -> None:
        """Callback when quest starts.
        
        Args:
            quest_id: ID of the quest
        """
        if quest_id not in self.quest_managers:
            return
            
        quest_manager = self.quest_managers[quest_id]
        exe_name = quest_manager.get_exe_name()
        
        # Update UI for single quest mode (backward compatibility)
        if len(self.quest_managers) == 1:
            self.lbl_status.config(text=f"● EMULATING: {exe_name}", fg=COLORS["green"])
            
            # Start timer with custom duration if set
            duration = quest_manager.get_custom_duration()
            if duration:
                self.timers[quest_id].set_duration_minutes(duration)
            self.timers[quest_id].start(self.root.after)
            
            # Update tray
            self.tray_manager.update_menu_state(True)
        else:
            self.lbl_status.config(text=f"● {len(self.quest_managers)} QUESTS RUNNING", fg=COLORS["green"])

    def _on_quest_stop(self, quest_id: str) -> None:
        """Callback when quest stops.
        
        Args:
            quest_id: ID of the quest
        """
        # Update UI
        if not self.quest_managers:
            self.lbl_timer.config(text="15:00")
            self.lbl_status.config(text="● DATABASE READY", fg=COLORS["green"])
            self.progress_bar.set_progress(0.0)
            self.lbl_progress_pct.config(text="0%")
            self.tray_manager.update_menu_state(False)
        else:
            self.lbl_status.config(text=f"● {len(self.quest_managers)} QUESTS RUNNING", fg=COLORS["green"])

    def _on_timer_tick(self, quest_id: str, time_str: str) -> None:
        """Callback when timer ticks.
        
        Args:
            quest_id: ID of the quest
            time_str: Formatted time string
        """
        # Update main timer display for single quest mode
        if len(self.quest_managers) == 1 and quest_id in self.timers:
            self.lbl_timer.config(text=time_str)
            
            # Update progress bar
            elapsed = self.timers[quest_id].get_elapsed_seconds()
            total = self.timers[quest_id].total_seconds
            percentage = (elapsed / total) * 100
            self.progress_bar.set_progress(percentage / 100)
            self.lbl_progress_pct.config(text=f"{int(percentage)}%")
            
            # Update tray overlay
            self.tray_manager.update_timer_overlay(time_str, True)
        else:
            # For multi-quest mode, sync footer with all running quests
            self._sync_footer_with_quests()
        
        # Check if process is still running (with startup delay to prevent false positives)
        timer = self.timers.get(quest_id)
        if timer and timer.get_elapsed_seconds() > 5:  # Increased delay to allow process startup
            if not self.process_manager.is_process_running(quest_id):
                self._stop_quest(quest_id)
                messagebox.showinfo("Status", "Quest window was closed.")
    
    def _sync_footer_with_quests(self) -> None:
        """Synchronize footer timer and progress bar with all running quests."""
        if not self.quest_managers:
            return
        
        # Find the highest progress percentage and lowest remaining time
        max_progress_ratio = 0.0
        lowest_remaining_seconds = float('inf')
        
        for quest_id, timer in self.timers.items():
            if quest_id in self.quest_managers:
                elapsed = timer.get_elapsed_seconds()
                total = timer.total_seconds
                remaining = total - elapsed
                
                if remaining < lowest_remaining_seconds:
                    lowest_remaining_seconds = remaining
                
                ratio = elapsed / total
                if ratio > max_progress_ratio:
                    max_progress_ratio = ratio
        
        # Update timer label with lowest remaining time
        if lowest_remaining_seconds != float('inf'):
            mins = int(lowest_remaining_seconds // 60)
            secs = int(lowest_remaining_seconds % 60)
            self.lbl_timer.config(text=f"{mins:02d}:{secs:02d}")
        
        # Update progress bar with highest progress
        self.progress_bar.set_progress(max_progress_ratio)
        
        # Update percentage label
        pct_value = int(max_progress_ratio * 100)
        self.lbl_progress_pct.config(text=f"{pct_value}%")

    def _on_timer_complete(self, quest_id: str) -> None:
        """Callback when timer completes.
        
        Args:
            quest_id: ID of the quest
        """
        self._stop_quest(quest_id)
        messagebox.showinfo(
            "Quest Complete!",
            "Quest completed! Check Discord to claim your reward.",
        )

    def _clean_all_data(self) -> None:
        """Clean up dummy executable files and clear recent/favorites data."""
        if self.quest_managers:
            messagebox.showwarning(
                "Quest Active", "Stop all quests before cleaning dummy files."
            )
            return

        # Clean dummy files
        deleted_count, _ = self.cleanup.clean_dummies()
        
        # Clear favorites
        favorites_count = len(self.favorites_manager.get_favorites())
        self.favorites_manager.clear_favorites()
        
        # Clear recent
        recent_count = len(self.favorites_manager.get_recent())
        self.favorites_manager.clear_recent()
        
        # Update UI
        self._update_favorites_and_recent()
        
        messagebox.showinfo(
            "Cleanup Complete", 
            f"Cleaned up {deleted_count} dummy executable(s).\n"
            f"Cleared {favorites_count} favorite(s).\n"
            f"Cleared {recent_count} recent item(s)."
        )

    def _show_settings_dialog(self) -> None:
        """Show the settings dialog."""
        current_settings = self.settings_manager.get_all()
        self.settings_dialog_instance = SettingsDialog(
            self.root,
            current_settings,
            COLORS,
            self._on_settings_save,
            self._on_theme_change_from_settings,
            self.icon_handler
        )

    def _on_settings_save(self, new_settings: dict) -> None:
        """Handle settings save.
        
        Args:
            new_settings: New settings dictionary
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"_on_settings_save called with {len(new_settings)} settings")
        for key, value in new_settings.items():
            logger.debug(f"Saving setting: {key} = {value}")
            self.settings_manager.set(key, value)
        logger.info("All settings saved successfully")
    
    def _on_theme_change_from_settings(self, theme: str, custom_colors: dict = None) -> None:
        """Handle theme change from settings dialog.
        
        Args:
            theme: New theme name ("mocha", "latte", "custom")
            custom_colors: Optional custom color dictionary for custom theme
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"_on_theme_change_from_settings called with theme: {theme}, custom_colors: {custom_colors is not None}")
        
        # Simply pass the theme and optional custom colors to theme manager
        # Theme manager will load from JSON or save custom colors to JSON
        self.theme_manager.set_theme(theme, custom_colors=custom_colors)
        logger.info("Theme change completed")

    def _on_theme_change(self, new_theme: str) -> None:
        """Handle theme change event.
        
        Args:
            new_theme: Name of the new theme
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"_on_theme_change called with new_theme: {new_theme}")
        
        try:
            # Update global colors reference
            global COLORS
            COLORS = self.theme_manager.get_current_colors()
            logger.info(f"Updated global COLORS with {len(COLORS)} colors")
            
            # Update icon handler theme
            if new_theme in ["latte"]:
                self.icon_handler.set_theme("light_mode")
                logger.info("Set icon handler to light mode")
            else:
                self.icon_handler.set_theme("dark_mode")
                logger.info("Set icon handler to dark mode")
            
            # Reload all icons
            logger.info("Starting icon reload")
            self._reload_icons()
            logger.info("Reloaded icons")
            
            # Update main window background
            logger.info("Updating main window backgrounds")
            self.root.config(bg=COLORS["base"])
            self.master_sidebar_panel.config(bg=COLORS["mantle"])
            self.main_viewer_panel.config(bg=COLORS["base"])
            logger.info("Updated main window backgrounds")
            
            # Update layout manager containers
            logger.info("Updating layout manager containers")
            self.layout_manager.update_colors(COLORS)
            logger.info("Updated layout manager containers")
            
            # Rebuild entire UI with new colors using role mapping
            logger.info("Starting UI recoloring process")
            try:
                self._recolor_widget_recursive(self.master_sidebar_panel.content_frame, COLORS)
                logger.info("Completed sidebar recoloring")
            except Exception as e:
                logger.error(f"Error during sidebar recoloring: {e}")
            
            try:
                self._recolor_widget_recursive(self.main_viewer_panel.content_frame, COLORS)
                logger.info("Completed main panel recoloring")
            except Exception as e:
                logger.error(f"Error during main panel recoloring: {e}")
            
            logger.info("Completed UI recoloring")
            
            # Update footer
            logger.info("Updating footer colors")
            self.bottom_credit_row.config(bg=COLORS["mantle"])
            for widget in self.bottom_credit_row.winfo_children():
                self._recolor_widget_by_role(widget, COLORS)
            logger.info("Updated footer colors")
            
            # Update sidebar cards (PixelContainers)
            logger.info("Updating sidebar cards")
            if hasattr(self, 'header_card'):
                self.header_card.update_colors(bg_color=COLORS["mantle"])
            if hasattr(self, 'status_card'):
                self.status_card.update_colors(bg_color=COLORS["mantle"])
            if hasattr(self, 'favorites_card'):
                self.favorites_card.update_colors(bg_color=COLORS["mantle"])
            if hasattr(self, 'recent_card'):
                self.recent_card.update_colors(bg_color=COLORS["mantle"])
            logger.info("Updated sidebar cards")
            
            # Update main panel cards (PixelContainers)
            logger.info("Updating main panel cards")
            if hasattr(self, 'search_bar_card'):
                self.search_bar_card.update_colors(bg_color=COLORS["mantle"])
            if hasattr(self, 'executables_viewer_card'):
                self.executables_viewer_card.update_colors(bg_color=COLORS["mantle"])
            if hasattr(self, 'nested_footer_card'):
                self.nested_footer_card.update_colors(bg_color=COLORS["mantle"])
            logger.info("Updated main panel cards")
            
            # Update sidebar component
            logger.info("Updating sidebar component colors")
            if hasattr(self, 'sidebar'):
                self.sidebar.update_colors(COLORS)
            logger.info("Updated sidebar component")
            
            # Update tabs manager component
            logger.info("Updating tabs manager colors")
            if hasattr(self, 'tabs_manager'):
                self.tabs_manager.update_colors(COLORS)
            logger.info("Updated tabs manager")
            
            # Update settings dialog if open
            try:
                if hasattr(self, 'settings_dialog_instance') and self.settings_dialog_instance.window.winfo_exists():
                    self.settings_dialog_instance.update_colors(COLORS)
                    logger.info("Updated settings dialog colors")
            except Exception as e:
                logger.warning(f"Could not update settings dialog: {e}")
            
            logger.info("Theme change completed successfully")
        except Exception as e:
            logger.error(f"Theme change failed with error: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def _reload_icons(self) -> None:
        """Reload all UI icons with the current theme."""
        try:
            # Reload header icons
            if hasattr(self, 'icon_label'):
                self.icon_label.config(image=self.icon_handler.load_ui_icon("app_icon.png", (32, 32)))
                self.icon_label.image = self.icon_handler.load_ui_icon("app_icon.png", (32, 32))
            
            # Reload favorite icon
            if hasattr(self, 'fav_header_icon'):
                self.fav_header_icon.config(image=self.icon_handler.load_ui_icon("bookmark.png", (16, 16)))
                self.fav_header_icon.image = self.icon_handler.load_ui_icon("bookmark.png", (16, 16))
            
            # Reload search icon
            if hasattr(self, 'search_icon_label'):
                self.search_icon_label.config(image=self.icon_handler.load_ui_icon("search.png", (16, 16)))
                self.search_icon_label.image = self.icon_handler.load_ui_icon("search.png", (16, 16))
            
            # Reload folder icon
            if hasattr(self, 'folder_icon_label'):
                self.folder_icon_label.config(image=self.icon_handler.load_ui_icon("folder.png", (48, 48)))
                self.folder_icon_label.image = self.icon_handler.load_ui_icon("folder.png", (48, 48))
            
            # Reload button icons
            if hasattr(self, 'btn_clean'):
                self.btn_clean.update_icon(self.icon_handler.load_ui_icon("trash.png", (20, 20)))
            if hasattr(self, 'btn_settings'):
                self.btn_settings.update_icon(self.icon_handler.load_ui_icon("configuration.png", (20, 20)))
            if hasattr(self, 'btn_start'):
                self.btn_start.update_icon(self.icon_handler.load_ui_icon("play.png", (20, 20)))
            if hasattr(self, 'btn_stop'):
                self.btn_stop.update_icon(self.icon_handler.load_ui_icon("stop-button.png", (20, 20)))
            
            # Reload queue item icons
            self._update_queue_icons()
            
        except Exception:
            pass
    
    def _update_queue_icons(self) -> None:
        """Update icons in queue items."""
        try:
            if hasattr(self, 'listbox_recent'):
                for widget in self.listbox_recent.winfo_children():
                    # Update favorite icons in queue items
                    for child in widget.winfo_children():
                        if hasattr(child, '_is_favorite_icon'):
                            child.config(image=self.icon_handler.load_ui_icon("bookmark.png", (16, 16)))
                            child.image = self.icon_handler.load_ui_icon("bookmark.png", (16, 16))
                        if hasattr(child, '_is_close_icon'):
                            child.config(image=self.icon_handler.load_ui_icon("close.png", (16, 16)))
                            child.image = self.icon_handler.load_ui_icon("close.png", (16, 16))
        except Exception:
            pass
    
    def _recolor_widget_recursive(self, widget, colors: dict) -> None:
        """Recursively recolor a widget and all its children.
        
        Args:
            widget: The widget to recolor
            colors: Theme color dictionary
        """
        try:
            # Recolor the current widget
            self._recolor_widget_by_role(widget, colors)
            
            # Recolor all children recursively
            for child in widget.winfo_children():
                self._recolor_widget_recursive(child, colors)
        except Exception as e:
            pass  # Skip widgets that can't be recolored

    def _recolor_widget_by_role(self, widget, colors: dict) -> None:
        """Recursively recolor a widget and all its children using UI role mapping."""
        from core.themes import get_color_for_role
        from ui.pixel_container import PixelContainer
        from ui.pixel_button import PixelButton
        
        try:
            # Handle PixelContainer specifically
            if isinstance(widget, PixelContainer):
                widget.update_colors(bg_color=colors["mantle"])
                # Recursively process content_frame
                self._recolor_widget_by_role(widget.content_frame, colors)
                return
            
            # Handle PixelButton specifically
            if isinstance(widget, PixelButton):
                widget.colors = colors
                # Get the original bg_color from the widget
                original_bg = widget.bg_color
                # Use theme colors based on the button's original color
                if original_bg == "#313244":  # surface0
                    new_bg = colors["surface0"]
                elif original_bg == "#45475a":  # surface1
                    new_bg = colors["surface1"]
                elif original_bg == "#87CEEB":  # sky blue (save button)
                    new_bg = "#87CEEB"  # Keep custom color
                else:
                    new_bg = colors["surface0"]
                
                # Update foreground color
                new_fg = colors["text"]
                widget.update_colors(new_bg, new_fg)
                # Recursively process children
                for child in widget.winfo_children():
                    self._recolor_widget_by_role(child, colors)
                return
            
            # Check if widget has a UI role attribute
            if hasattr(widget, 'ui_role'):
                role = widget.ui_role
                
                # Apply background color
                try:
                    bg_color = get_color_for_role(colors, role)
                    widget.config(bg=bg_color)
                except Exception:
                    pass
                
                # Apply foreground color if widget has text
                try:
                    if widget.cget("fg") and widget.cget("fg") != "":
                        fg_role = role.replace("background", "text")
                        if fg_role == role:  # If no text role defined, use default
                            fg_role = "text_primary"
                        fg_color = get_color_for_role(colors, fg_role)
                        widget.config(fg=fg_color)
                except Exception:
                    pass
            else:
                # Fallback: Try to match colors by value for widgets without UI roles
                try:
                    bg = widget.cget("bg")
                    # Common dark theme colors to match
                    dark_colors = {
                        "#1e1e2e": colors["base"],  # mocha base
                        "#181825": colors["mantle"],  # mocha mantle
                        "#313244": colors["surface0"],  # mocha surface0
                        "#45475a": colors["surface1"],  # mocha surface1
                        "#11111b": colors["mantle"],  # old dark footer
                        "#585b70": colors["surface2"],  # mocha surface2
                        "#313244": colors["surface0"],  # latte surface0
                        "#ccd0da": colors["surface0"],  # latte surface0
                        "#eff1f5": colors["base"],  # latte base
                        "#e6e9ef": colors["mantle"],  # latte mantle
                    }
                    if bg in dark_colors:
                        widget.config(bg=dark_colors[bg])
                except Exception:
                    pass
                
                try:
                    fg = widget.cget("fg")
                    # Common dark theme text colors to match
                    dark_text_colors = {
                        "#cdd6f4": colors["text"],  # mocha text
                        "#a6adc8": colors["subtext0"],  # mocha subtext0
                        "#bac2de": colors["subtext1"],  # mocha subtext1
                        "#89b4fa": colors["blue"],  # mocha blue
                        "#f5c2e7": colors["pink"],  # mocha pink
                        "#a6e3a1": colors["green"],  # mocha green
                        "#f38ba8": colors["red"],  # mocha red
                        "#4c4f69": colors["text"],  # latte text
                        "#dc8a78": colors["pink"],  # latte pink
                        "#40a02b": colors["green"],  # latte green
                        "#d20f39": colors["red"],  # latte red
                    }
                    if fg in dark_text_colors:
                        widget.config(fg=dark_text_colors[fg])
                except Exception:
                    pass
        except Exception:
            pass
        
        # Recursively process children
        try:
            for child in widget.winfo_children():
                self._recolor_widget_by_role(child, colors)
        except Exception:
            pass

    def _recolor_widget(self, widget, colors: dict) -> None:
        """Recursively recolor a widget and all its children comprehensively."""
        try:
            # Handle background colors
            bg = widget.cget("bg")
            all_theme_colors = {
                **COLORS_DARK, **COLORS_LIGHT,
                **COLORS_DISCORD_DARK, **COLORS_DISCORD_LIGHT
            }
            
            # Comprehensive color mapping for backgrounds
            color_map_bg = {
                "base": colors["base"],
                "mantle": colors["mantle"], 
                "surface": colors["surface"],
                "surface0": colors["surface0"],
                "surface1": colors["surface1"],
                "surface2": colors["surface2"],
            }
            
            for color_key, color_value in all_theme_colors.items():
                if bg == color_value and color_key in color_map_bg:
                    widget.config(bg=color_map_bg[color_key])
                    break
        except Exception:
            pass
        
        try:
            # Handle foreground colors
            fg = widget.cget("fg")
            all_theme_colors = {
                **COLORS_DARK, **COLORS_LIGHT,
                **COLORS_DISCORD_DARK, **COLORS_DISCORD_LIGHT
            }
            
            # Comprehensive color mapping for foregrounds
            color_map_fg = {
                "text": colors["text"],
                "subtext0": colors["subtext0"],
                "subtext1": colors["subtext1"],
                "green": colors["green"],
                "red": colors["red"],
                "blue": colors["blue"],
                "yellow": colors["yellow"],
                "pink": colors["pink"],
                "mauve": colors["mauve"],
            }
            
            for color_key, color_value in all_theme_colors.items():
                if fg == color_value and color_key in color_map_fg:
                    widget.config(fg=color_map_fg[color_key])
                    break
        except Exception:
            pass
        
        try:
            # Handle selectcolor (for checkboxes, radiobuttons)
            selectcolor = widget.cget("selectcolor")
            all_theme_colors = {
                **COLORS_DARK, **COLORS_LIGHT,
                **COLORS_DISCORD_DARK, **COLORS_DISCORD_LIGHT
            }
            
            color_map_select = {
                "surface0": colors["surface0"],
                "surface": colors["surface"],
                "mantle": colors["mantle"],
            }
            
            for color_key, color_value in all_theme_colors.items():
                if selectcolor == color_value and color_key in color_map_select:
                    widget.config(selectcolor=color_map_select[color_key])
                    break
        except Exception:
            pass
        
        try:
            # Handle activebackground (for buttons, checkboxes)
            activebg = widget.cget("activebackground")
            all_theme_colors = {
                **COLORS_DARK, **COLORS_LIGHT,
                **COLORS_DISCORD_DARK, **COLORS_DISCORD_LIGHT
            }
            
            color_map_active = {
                "base": colors["base"],
                "surface0": colors["surface0"],
                "surface": colors["surface"],
            }
            
            for color_key, color_value in all_theme_colors.items():
                if activebg == color_value and color_key in color_map_active:
                    widget.config(activebackground=color_map_active[color_key])
                    break
        except Exception:
            pass
        
        try:
            # Handle insertbackground (for entries)
            insertbg = widget.cget("insertbackground")
            if insertbg in ["white", "#ffffff", "#000000"]:
                widget.config(insertbackground=colors["text"])
        except Exception:
            pass
        
        # Handle specific widget types
        try:
            if isinstance(widget, tk.Canvas):
                # Update canvas background
                canvas_bg = widget.cget("bg")
                all_theme_colors = {
                    **COLORS_DARK, **COLORS_LIGHT,
                    **COLORS_DISCORD_DARK, **COLORS_DISCORD_LIGHT
                }
                color_map_bg = {
                    "base": colors["base"],
                    "mantle": colors["mantle"], 
                    "surface": colors["surface"],
                    "surface0": colors["surface0"],
                }
                for color_key, color_value in all_theme_colors.items():
                    if canvas_bg == color_value and color_key in color_map_bg:
                        widget.config(bg=color_map_bg[color_key])
                        break
                
                # Update canvas items (rectangles, text, etc.)
                for item in widget.find_all():
                    item_type = widget.type(item)
                    if item_type == "rectangle":
                        # Get current fill color
                        fill = widget.itemcget(item, "fill")
                        all_theme_colors = {
                            **COLORS_DARK, **COLORS_LIGHT,
                            **COLORS_DISCORD_DARK, **COLORS_DISCORD_LIGHT
                        }
                        color_map_fill = {
                            "mantle": colors["mantle"],
                            "surface0": colors["surface0"],
                            "green": colors["green"],
                            "surface": colors["surface"],
                        }
                        for color_key, color_value in all_theme_colors.items():
                            if fill == color_value and color_key in color_map_fill:
                                widget.itemconfig(item, fill=color_map_fill[color_key])
                                break
        except Exception:
            pass
        
        # Recurse for children
        for child in widget.winfo_children():
            self._recolor_widget(child, colors)

    def _on_sidebar_game_select(self, game_name: str, exe_name: str) -> None:
        """Handle game selection from sidebar (legacy - no longer used)."""
        pass
    
    def _update_favorites_and_recent(self) -> None:
        """Update favorites and recent lists from saved data."""
        self.listbox_favorites.delete(0, tk.END)
        self.listbox_recent.delete(0, tk.END)
        
        # Update favorites
        favorites = self.favorites_manager.get_favorites()
        for game_name, exe_name in favorites:
            # Display only game name, strip executable details
            display_text = game_name
            # Add text elision for long titles
            if len(display_text) > 25:
                display_text = display_text[:22] + "..."
            self.listbox_favorites.insert(tk.END, display_text)
        
        # Add empty state placeholder for favorites
        if not favorites:
            self.listbox_favorites.insert(tk.END, "No favorites yet")
        
        # Update recent
        recent_list = self.favorites_manager.get_recent()
        for game_name, exe_name in recent_list:
            # Display only game name, strip executable details
            display_text = game_name
            # Add text elision for long titles
            if len(display_text) > 25:
                display_text = display_text[:22] + "..."
            self.listbox_recent.insert(tk.END, display_text)
        
        # Add empty state placeholder for recent
        if not recent_list:
            self.listbox_recent.insert(tk.END, "No recent history")
    
    def _on_favorite_double_click(self, event) -> None:
        """Handle double-click on favorite item - add to queue directly."""
        selection = self.listbox_favorites.curselection()
        if selection:
            game_name = self.listbox_favorites.get(selection[0])
            # Look up exe name from favorites list
            favorites = self.favorites_manager.get_favorites()
            for fav_game_name, exe_name in favorites:
                if fav_game_name == game_name:
                    self._add_to_queue(game_name.strip(), exe_name.strip())
                    break
    
    def _on_recent_double_click(self, event) -> None:
        """Handle double-click on recent item - add to queue directly."""
        selection = self.listbox_recent.curselection()
        if selection:
            game_name = self.listbox_recent.get(selection[0])
            # Look up exe name from recent list
            recent_list = self.favorites_manager.get_recent()
            for recent_game_name, exe_name in recent_list:
                if recent_game_name == game_name:
                    self._add_to_queue(game_name.strip(), exe_name.strip())
                    break

    def _on_open_folder(self) -> None:
        """Handle open folder button click."""
        import subprocess
        try:
            # Get the dummy executables directory
            dummy_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "DiscordQuestManager", "Dummies")
            if not os.path.exists(dummy_dir):
                os.makedirs(dummy_dir, exist_ok=True)
            # Open in Windows Explorer
            subprocess.run(["explorer", dummy_dir], shell=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open folder:\n{e}")

    def _on_tray_restore(self) -> None:
        """Handle tray restore action."""
        self.root.deiconify()
        self.root.state("normal")

    def _on_tray_start_stop(self) -> None:
        """Handle tray start/stop action."""
        if self.quest_managers:
            # Stop all quests
            for quest_id in list(self.quest_managers.keys()):
                self._stop_quest(quest_id)
        else:
            # This would need to know which game to start - simplified for now
            pass

    def _on_tray_quit(self) -> None:
        """Handle tray quit action."""
        self._on_window_close()

    def _on_window_close(self) -> None:
        """Handle window close event."""
        # Auto-clean if setting enabled
        if self.settings_manager.get("auto_clean_on_exit", True):
            self._clean_all_data()
        
        # Stop all processes
        self.process_manager.terminate_all_processes()
        
        # Stop tray
        self.tray_manager.stop()
        
        self.root.destroy()

    def _show_about_dialog(self) -> None:
        """Show the about dialog."""
        app_icon = self.icon_handler.load_icon()
        current_colors = self.theme_manager.get_colors()
        AboutDialog(self.root, app_icon, colors=current_colors)
