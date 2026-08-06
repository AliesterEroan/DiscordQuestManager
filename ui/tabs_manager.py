"""Tabs manager for multi-quest support in Discord Quest Manager."""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Callable, Optional

from config.constants import COLORS, FONTS
from utils.icon_handler import IconHandler


class TabsManager:
    """Manages tabs for multiple concurrent quests."""

    def __init__(self, parent: tk.Widget, colors: dict):
        self.parent = parent
        self.colors = colors
        self.icon_handler = IconHandler()
        self.tabs: Dict[str, tk.Frame] = {}
        self.tab_counter = 0
        self.on_tab_close_callback: Optional[Callable] = None
        
        self._setup_tabs()

    def _setup_tabs(self) -> None:
        """Setup the tabs UI."""
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(fill="both", expand=True)
        
        # Configure tab style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "TNotebook",
            background=self.colors["base"],
            borderwidth=0,
        )
        style.configure(
            "TNotebook.Tab",
            background=self.colors["surface0"],
            foreground=self.colors["text"],
            padding=[10, 5],
            borderwidth=0,
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", self.colors["surface1"])],
            foreground=[("selected", self.colors["lavender"])],
        )

    def add_search_tab(self) -> tk.Frame:
        """Add the search tab with icon.
        
        Returns:
            The search tab frame widget
        """
        # Load search icon
        search_icon = self.icon_handler.load_ui_icon("search.png", (16, 16))
        
        # Create search tab frame
        search_frame = tk.Frame(self.notebook, bg=self.colors["base"])
        
        if search_icon:
            self.notebook.add(search_frame, text="🔍 Search")
        else:
            self.notebook.add(search_frame, text="🔍 Search")
        
        tab_id = "search"
        self.tabs[tab_id] = {
            "frame": search_frame,
            "game_name": "Search",
            "exe_name": "search",
        }
        
        return search_frame

    def add_tab(self, game_name: str, exe_name: str) -> tk.Frame:
        """Add a new tab for a quest.
        
        Args:
            game_name: Name of the game
            exe_name: Name of the executable
            
        Returns:
            The tab frame widget
        """
        self.tab_counter += 1
        tab_id = f"quest_{self.tab_counter}"
        
        # Create tab frame
        tab_frame = tk.Frame(self.notebook, bg=self.colors["base"])
        self.notebook.add(tab_frame, text=f"{game_name[:15]}...")
        
        self.tabs[tab_id] = {
            "frame": tab_frame,
            "game_name": game_name,
            "exe_name": exe_name,
        }
        
        return tab_frame

    def close_tab(self, tab_id: str) -> None:
        """Close a tab.
        
        Args:
            tab_id: ID of the tab to close
        """
        if tab_id in self.tabs:
            tab_data = self.tabs[tab_id]
            self.notebook.forget(tab_data["frame"])
            del self.tabs[tab_id]
            
            if self.on_tab_close_callback:
                self.on_tab_close_callback(tab_id)

    def close_current_tab(self) -> None:
        """Close the currently selected tab."""
        current_tab = self.notebook.select()
        if current_tab:
            tab_id = self._get_tab_id_from_widget(current_tab)
            if tab_id:
                self.close_tab(tab_id)

    def get_tab_frame(self, tab_id: str) -> Optional[tk.Frame]:
        """Get the frame for a tab.
        
        Args:
            tab_id: ID of the tab
            
        Returns:
            Tab frame or None
        """
        if tab_id in self.tabs:
            return self.tabs[tab_id]["frame"]
        return None

    def get_current_tab_id(self) -> Optional[str]:
        """Get the ID of the currently selected tab.
        
        Returns:
            Current tab ID or None
        """
        current_tab = self.notebook.select()
        if current_tab:
            return self._get_tab_id_from_widget(current_tab)
        return None

    def _get_tab_id_from_widget(self, widget) -> Optional[str]:
        """Get tab ID from widget.
        
        Args:
            widget: Tab widget
            
        Returns:
            Tab ID or None
        """
        for tab_id, tab_data in self.tabs.items():
            if tab_data["frame"] == widget:
                return tab_id
        return None

    def get_all_tabs(self) -> Dict[str, Dict]:
        """Get all tabs.
        
        Returns:
            Dictionary of all tabs
        """
        return self.tabs.copy()

    def set_on_tab_close(self, callback: Callable) -> None:
        """Set callback for tab close events.
        
        Args:
            callback: Function to call when tab is closed
        """
        self.on_tab_close_callback = callback

    def update_colors(self, colors: dict) -> None:
        """Update colors when theme changes.
        
        Args:
            colors: New color dictionary
        """
        self.colors = colors
        
        # Update notebook style
        style = ttk.Style()
        style.configure(
            "TNotebook",
            background=colors["base"],
        )
        style.configure(
            "TNotebook.Tab",
            background=colors["surface0"],
            foreground=colors["text"],
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", colors["surface1"])],
            foreground=[("selected", colors["lavender"])],
        )
        
        # Update all tab frames
        for tab_data in self.tabs.values():
            tab_data["frame"].config(bg=colors["base"])

    def update_tab_title(self, tab_id: str, new_title: str) -> None:
        """Update the title of a tab.
        
        Args:
            tab_id: ID of the tab
            new_title: New title for the tab
        """
        if tab_id in self.tabs:
            tab_data = self.tabs[tab_id]
            self.notebook.tab(tab_data["frame"], text=new_title[:15] + "...")
