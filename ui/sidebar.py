"""Sidebar component for favorites and recent games."""

import tkinter as tk
from typing import Callable, Tuple, List

from config.constants import COLORS, FONTS
from utils.icon_handler import IconHandler


class Sidebar:
    """Sidebar panel for favorites and recent games."""

    def __init__(self, parent: tk.Widget, colors: dict):
        self.parent = parent
        self.colors = colors
        self.icon_handler = IconHandler()
        self.on_game_select_callback: Callable = None
        self.on_add_favorite_callback: Callable = None
        self.on_remove_favorite_callback: Callable = None
        self.on_open_folder_callback: Callable = None
        
        self._setup_sidebar()

    def _setup_sidebar(self) -> None:
        """Setup the sidebar UI."""
        self.frame = tk.Frame(self.parent, bg=self.colors["mantle"], width=200)
        self.frame.pack(side="left", fill="y")
        self.frame.pack_propagate(False)
        
        # Favorites Section
        self._setup_favorites_section()
        
        # Recent Section
        self._setup_recent_section()
        
        # Folder button
        self._setup_folder_button()

    def _setup_favorites_section(self) -> None:
        """Setup the favorites section."""
        # Load bookmark icon
        bookmark_icon = self.icon_handler.load_ui_icon("bookmark.png", (16, 16))
        
        if bookmark_icon:
            lbl_fav = tk.Label(
                self.frame,
                image=bookmark_icon,
                text=" Favorites",
                compound="left",
                font=FONTS["label"],
                fg=self.colors["yellow"],
            )
            lbl_fav.image = bookmark_icon  # Keep reference
        else:
            lbl_fav = tk.Label(
                self.frame,
                text="★ Favorites",
                font=FONTS["label"],
                fg=self.colors["yellow"],
            )
        lbl_fav.pack(pady=(10, 5), padx=10, anchor="w")
        
        self.listbox_favorites = tk.Listbox(
            self.frame,
            font=FONTS["listbox"],
            bg=self.colors["surface0"],
            fg=self.colors["text"],
            selectbackground=self.colors["surface2"],
            selectforeground="white",
            relief="flat",
            highlightthickness=0,
            height=8,
        )
        self.listbox_favorites.pack(fill="x", padx=10, pady=(0, 5))
        self.listbox_favorites.bind("<Double-Button-1>", self._on_favorite_double_click)

    def _setup_recent_section(self) -> None:
        """Setup the recent section."""
        # Load bookmark icon for recent
        bookmark_icon = self.icon_handler.load_ui_icon("bookmark.png", (16, 16))
        
        if bookmark_icon:
            lbl_recent = tk.Label(
                self.frame,
                image=bookmark_icon,
                text=" Recent",
                compound="left",
                font=FONTS["label"],
                fg=self.colors["blue"],
            )
            lbl_recent.image = bookmark_icon  # Keep reference
        else:
            lbl_recent = tk.Label(
                self.frame,
                text="◷ Recent",
                font=FONTS["label"],
                fg=self.colors["blue"],
            )
        lbl_recent.pack(pady=(10, 5), padx=10, anchor="w")
        
        self.listbox_recent = tk.Listbox(
            self.frame,
            font=FONTS["listbox"],
            bg=self.colors["surface0"],
            fg=self.colors["text"],
            selectbackground=self.colors["surface2"],
            selectforeground="white",
            relief="flat",
            highlightthickness=0,
            height=8,
        )
        self.listbox_recent.pack(fill="x", padx=10, pady=(0, 5))
        self.listbox_recent.bind("<Double-Button-1>", self._on_recent_double_click)

    def _setup_folder_button(self) -> None:
        """Setup the folder button to open dummy executables folder."""
        folder_icon = self.icon_handler.load_ui_icon("folder.png", (16, 16))
        
        if folder_icon:
            btn_folder = tk.Button(
                self.frame,
                image=folder_icon,
                text=" Open Dummies Folder",
                compound="left",
                font=FONTS["button_small"],
                fg="#cdd6f4",
                bg="#313244",
                activebackground="#45475a",
                activeforeground="#cdd6f4",
                relief="flat",
                highlightthickness=0,
                padx=10,
                pady=5,
                cursor="hand2",
            )
            btn_folder.image = folder_icon  # Keep reference
        else:
            btn_folder = tk.Button(
                self.frame,
                text="📁 Open Dummies Folder",
                font=FONTS["button_small"],
                fg="#cdd6f4",
                bg="#313244",
                activebackground="#45475a",
                activeforeground="#cdd6f4",
                relief="flat",
                highlightthickness=0,
                padx=10,
                pady=5,
                cursor="hand2",
            )
        
        btn_folder.pack(pady=10, padx=10, fill="x")
        btn_folder.config(command=self._on_folder_click)

    def _on_folder_click(self) -> None:
        """Handle folder button click."""
        if self.on_open_folder_callback:
            self.on_open_folder_callback()

    def _on_favorite_double_click(self, event) -> None:
        """Handle double-click on favorite item."""
        selection = self.listbox_favorites.curselection()
        if selection and self.on_game_select_callback:
            idx = selection[0]
            game_data = self.listbox_favorites.get(idx)
            if " -> " in game_data:
                game_name, exe_name = game_data.split(" -> ")
                self.on_game_select_callback(game_name.strip(), exe_name.strip())

    def _on_recent_double_click(self, event) -> None:
        """Handle double-click on recent item."""
        selection = self.listbox_recent.curselection()
        if selection and self.on_game_select_callback:
            idx = selection[0]
            game_data = self.listbox_recent.get(idx)
            if " -> " in game_data:
                game_name, exe_name = game_data.split(" -> ")
                self.on_game_select_callback(game_name.strip(), exe_name.strip())

    def update_favorites(self, favorites: List[Tuple[str, str]]) -> None:
        """Update the favorites list.
        
        Args:
            favorites: List of (game_name, exe_name) tuples
        """
        self.listbox_favorites.delete(0, tk.END)
        for game_name, exe_name in favorites:
            self.listbox_favorites.insert(tk.END, f"{game_name} -> {exe_name}")

    def update_recent(self, recent: List[Tuple[str, str]]) -> None:
        """Update the recent list.
        
        Args:
            recent: List of (game_name, exe_name) tuples
        """
        self.listbox_recent.delete(0, tk.END)
        for game_name, exe_name in recent:
            self.listbox_recent.insert(tk.END, f"{game_name} -> {exe_name}")

    def set_on_game_select(self, callback: Callable) -> None:
        """Set callback for game selection.
        
        Args:
            callback: Function to call when game is selected
        """
        self.on_game_select_callback = callback

    def set_on_open_folder(self, callback: Callable) -> None:
        """Set callback for open folder button.
        
        Args:
            callback: Function to call when folder button is clicked
        """
        self.on_open_folder_callback = callback

    def update_colors(self, colors: dict) -> None:
        """Update colors when theme changes.
        
        Args:
            colors: New color dictionary
        """
        self.colors = colors
        self.frame.config(bg=colors["mantle"])
        
        # Update all widgets
        for widget in self.frame.winfo_children():
            if isinstance(widget, tk.Label):
                # Only update fg, let bg inherit from parent
                current_fg = widget.cget("fg")
                # Map old fg colors to new theme colors
                fg_map = {
                    "#f9e2af": colors["yellow"],
                    "#89b4fa": colors["blue"],
                }
                if current_fg in fg_map:
                    widget.config(fg=fg_map[current_fg])
            elif isinstance(widget, tk.Listbox):
                widget.config(bg=colors["surface0"], fg=colors["text"])
            # Don't update button colors - they are hardcoded
