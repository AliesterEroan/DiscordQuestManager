"""Dummy window for emulating game processes."""

import os
import sys
import tkinter as tk

from config.constants import COLORS, WINDOW, FONTS, ICON_FILENAME
from utils.icon_handler import IconHandler


class DummyWindow:
    """Fake game process window for Discord quest emulation."""

    def __init__(self, game_exe_name: str):
        self.game_exe_name = game_exe_name
        self.root = tk.Tk()
        self._setup_window()
        self._setup_icon()
        self._setup_content()

    def _setup_window(self) -> None:
        """Configure the window properties."""
        self.root.title(self.game_exe_name)
        self.root.geometry(f"{WINDOW['dummy_width']}x{WINDOW['dummy_height']}")
        self.root.resizable(False, False)
        self.root.configure(bg=COLORS["base"])

        # Show on top briefly
        self.root.attributes("-topmost", True)
        self.root.after(500, lambda: self.root.attributes("-topmost", False))

    def _setup_icon(self) -> None:
        """Set the window icon."""
        icon_handler = IconHandler()
        icon = icon_handler.load_icon()
        if icon:
            try:
                self.root.iconphoto(True, icon)
            except Exception:
                pass

    def _setup_content(self) -> None:
        """Setup the window content."""
        lbl = tk.Label(
            self.root,
            text=(
                f"Discord Quest Process Running\n\n"
                f"Executable: {self.game_exe_name}\n"
                f"Keep this window open during the quest!"
            ),
            font=FONTS["about_text"],
            fg=COLORS["text"],
            bg=COLORS["base"],
            justify="center",
        )
        lbl.pack(expand=True, fill="both", padx=15, pady=15)

    def run(self) -> None:
        """Start the dummy window main loop."""
        self.root.mainloop()


def run_dummy_mode(game_exe_name: str) -> None:
    """Run the dummy window with the given executable name.
    
    Args:
        game_exe_name: Name of the game executable to emulate
    """
    dummy = DummyWindow(game_exe_name)
    dummy.run()
