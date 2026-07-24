"""Main application window for Discord Quest Manager."""

import os
import sys
import tkinter as tk
from tkinter import messagebox
import webbrowser
from typing import List, Tuple

from config.constants import COLORS, WINDOW, FONTS, APP_NAME, APP_VERSION, AUTHOR, GITHUB_PROFILE
from core.database import Database
from core.search import Search
from core.quest_manager import QuestManager
from core.timer import Timer
from core.cleanup import Cleanup
from ui.about_dialog import AboutDialog
from utils.icon_handler import IconHandler
from utils.process_manager import ProcessManager


class MainWindow:
    """Main application window for Discord Quest Manager."""

    def __init__(self, root: tk.Tk):
        self.root = root
        
        # Initialize core components
        self.database = Database()
        self.search = Search([])
        self.quest_manager = QuestManager()
        self.timer = Timer()
        self.cleanup = Cleanup()
        self.process_manager = ProcessManager()
        self.icon_handler = IconHandler()
        
        # UI state
        self.found_matches: List[Tuple[str, str]] = []
        
        # Setup callbacks
        self._setup_callbacks()
        
        # Setup window
        self._setup_window()
        self._setup_ui()
        
        # Load database
        self._load_database()

    def _setup_callbacks(self) -> None:
        """Setup callbacks for core components."""
        self.quest_manager.on_start_callback = self._on_quest_start
        self.quest_manager.on_stop_callback = self._on_quest_stop
        self.timer.set_on_tick(self._on_timer_tick)
        self.timer.set_on_complete(self._on_timer_complete)

    def _setup_window(self) -> None:
        """Configure the main window."""
        self.root.title(APP_NAME)
        self.root.geometry(f"{WINDOW['main_width']}x{WINDOW['main_height']}")
        self.root.resizable(False, False)
        self.root.configure(bg=COLORS["base"])
        self.icon_handler.apply_to_window(self.root)

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        self._setup_header()
        self._setup_search()
        self._setup_results()
        self._setup_controls()
        self._setup_footer()

    def _setup_header(self) -> None:
        """Setup the header section."""
        header = tk.Label(
            self.root,
            text=APP_NAME,
            font=FONTS["header"],
            fg=COLORS["lavender"],
            bg=COLORS["base"],
        )
        header.pack(pady=(14, 2))

        self.lbl_status = tk.Label(
            self.root,
            text="Connecting to Discord database...",
            fg=COLORS["peach"],
            bg=COLORS["base"],
            font=FONTS["status"],
        )
        self.lbl_status.pack()

    def _setup_search(self) -> None:
        """Setup the search section."""
        search_frame = tk.Frame(self.root, bg=COLORS["base"])
        search_frame.pack(fill="x", padx=25, pady=10)

        tk.Label(
            search_frame,
            text="Search Game Name:",
            font=FONTS["label"],
            fg=COLORS["text"],
            bg=COLORS["base"],
        ).pack(anchor="w")

        self.ent_search = tk.Entry(
            search_frame,
            font=FONTS["entry"],
            bg=COLORS["surface0"],
            fg=COLORS["text"],
            insertbackground="white",
            relief="flat",
        )
        self.ent_search.pack(
            side="left", fill="x", expand=True, padx=(0, 8), ipady=4
        )
        self.ent_search.bind("<Return>", lambda e: self._search_games())

        self.btn_search = tk.Button(
            search_frame,
            text="Search",
            command=self._search_games,
            state="disabled",
            bg=COLORS["blue"],
            fg=COLORS["mantle"],
            font=FONTS["button_small"],
            relief="flat",
            width=10,
        )
        self.btn_search.pack(side="right")

    def _setup_results(self) -> None:
        """Setup the results listbox."""
        results_frame = tk.Frame(self.root, bg=COLORS["base"])
        results_frame.pack(fill="both", expand=True, padx=25, pady=5)

        tk.Label(
            results_frame,
            text="Select Game Executable:",
            font=FONTS["button_small"],
            fg=COLORS["subtext0"],
            bg=COLORS["base"],
        ).pack(anchor="w")

        scrollbar = tk.Scrollbar(results_frame)
        scrollbar.pack(side="right", fill="y")

        self.listbox = tk.Listbox(
            results_frame,
            font=FONTS["listbox"],
            bg=COLORS["surface0"],
            fg=COLORS["text"],
            selectbackground=COLORS["surface2"],
            selectforeground="white",
            relief="flat",
            highlightthickness=0,
            yscrollcommand=scrollbar.set,
        )
        self.listbox.pack(fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)

    def _setup_controls(self) -> None:
        """Setup the control buttons and timer."""
        ctrl_frame = tk.Frame(self.root, bg=COLORS["base"])
        ctrl_frame.pack(fill="x", padx=25, pady=12)

        self.lbl_timer = tk.Label(
            ctrl_frame,
            text="Timer: 15:00",
            font=FONTS["timer"],
            fg=COLORS["text"],
            bg=COLORS["base"],
        )
        self.lbl_timer.pack(side="left")

        self.btn_toggle = tk.Button(
            ctrl_frame,
            text="Start Quest",
            bg=COLORS["green"],
            fg=COLORS["mantle"],
            font=FONTS["button"],
            command=self._toggle_quest,
            state="disabled",
            relief="flat",
            width=12,
            pady=3,
        )
        self.btn_toggle.pack(side="right")

        self.btn_clean = tk.Button(
            ctrl_frame,
            text="Clean Dummies",
            bg=COLORS["yellow"],
            fg=COLORS["mantle"],
            font=FONTS["button_small"],
            command=self._clean_dummies,
            relief="flat",
            width=13,
            pady=3,
        )
        self.btn_clean.pack(side="right", padx=(0, 8))

    def _setup_footer(self) -> None:
        """Setup the footer section."""
        footer_frame = tk.Frame(self.root, bg=COLORS["mantle"], pady=6)
        footer_frame.pack(fill="x", side="bottom")

        lbl_copyright = tk.Label(
            footer_frame,
            text=f"© {AUTHOR} | ",
            font=FONTS["footer"],
            fg=COLORS["subtext0"],
            bg=COLORS["mantle"],
        )
        lbl_copyright.pack(side="left", padx=(15, 0))

        lbl_github = tk.Label(
            footer_frame,
            text="GitHub Profile",
            font=FONTS["footer"],
            underline=True,
            fg=COLORS["blue"],
            bg=COLORS["mantle"],
            cursor="hand2",
        )
        lbl_github.pack(side="left")
        lbl_github.bind("<Button-1>", lambda e: webbrowser.open(GITHUB_PROFILE))

        lbl_version = tk.Label(
            footer_frame,
            text=f"v{APP_VERSION}",
            font=FONTS["footer"],
            fg=COLORS["subtext0"],
            bg=COLORS["mantle"],
            cursor="hand2",
        )
        lbl_version.pack(side="right", padx=(0, 15))
        lbl_version.bind("<Button-1>", lambda e: self._show_about_dialog())

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
                text=f"Database Ready ({len(data)} games registered)",
                fg=COLORS["green"],
            )
            self.btn_search.config(state="normal")
            self.btn_toggle.config(state="normal")
        else:
            self.lbl_status.config(
                text="Database offline. Check network connection.",
                fg=COLORS["red"],
            )

    def _search_games(self) -> None:
        """Search for games based on the query."""
        query = self.ent_search.get().strip()
        if not query:
            return

        self.listbox.delete(0, tk.END)
        self.found_matches = self.search.search(query)

        for game_name, exe_name in self.found_matches:
            self.listbox.insert(tk.END, self.search.format_result(game_name, exe_name))

        if not self.found_matches:
            self.listbox.insert(tk.END, "No matching games found.")

    def _toggle_quest(self) -> None:
        """Toggle quest start/stop."""
        if self.quest_manager.is_running:
            self._stop_quest()
        else:
            self._start_quest()

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
        self.quest_manager.set_selected_game(game_name, exe_name)

        try:
            # Create fake executable
            base_dir = self.quest_manager.get_base_directory()
            fake_exe_path = self.process_manager.create_fake_executable(exe_name, base_dir)
            self.quest_manager.set_fake_exe_path(fake_exe_path)

            # Spawn dummy process
            script_path = os.path.abspath(__file__) if not getattr(sys, "frozen", False) else None
            self.process_manager.spawn_dummy_process(fake_exe_path, exe_name, script_path)

            # Start quest
            self.quest_manager.start_quest()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to start process:\n{e}")

    def _stop_quest(self) -> None:
        """Stop the quest."""
        self.quest_manager.stop_quest()
        self.timer.stop()
        self.process_manager.terminate_process()
        self.quest_manager.cleanup_fake_exe()

    def _on_quest_start(self) -> None:
        """Callback when quest starts."""
        exe_name = self.quest_manager.get_exe_name()
        self.btn_toggle.config(text="Stop Quest", bg=COLORS["red"])
        self.lbl_status.config(text=f"Emulating: {exe_name}", fg=COLORS["blue"])
        self.timer.start(self.root.after)

    def _on_quest_stop(self) -> None:
        """Callback when quest stops."""
        self.btn_toggle.config(text="Start Quest", bg=COLORS["green"])
        self.lbl_timer.config(text="Timer: 15:00")
        self.lbl_status.config(text="Ready", fg=COLORS["green"])

    def _on_timer_tick(self, time_str: str) -> None:
        """Callback when timer ticks.
        
        Args:
            time_str: Formatted time string
        """
        self.lbl_timer.config(text=f"Timer: {time_str}")

        # Check if process is still running
        if not self.process_manager.is_process_running():
            self._stop_quest()
            messagebox.showinfo("Status", "Quest window was closed.")

    def _on_timer_complete(self) -> None:
        """Callback when timer completes."""
        self._stop_quest()
        messagebox.showinfo(
            "Quest Complete!",
            "15 minutes completed! Check Discord to claim your reward.",
        )

    def _clean_dummies(self) -> None:
        """Clean up dummy executable files."""
        if self.quest_manager.is_running:
            messagebox.showwarning(
                "Quest Active", "Stop the current quest before cleaning dummy files."
            )
            return

        deleted_count, _ = self.cleanup.clean_dummies()
        messagebox.showinfo(
            "Cleanup Complete", f"Cleaned up {deleted_count} dummy executable(s)."
        )

    def _show_about_dialog(self) -> None:
        """Show the about dialog."""
        app_icon = self.icon_handler.load_icon()
        AboutDialog(self.root, app_icon)
