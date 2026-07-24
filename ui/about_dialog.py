"""About dialog for Discord Quest Manager."""

import tkinter as tk
import webbrowser

from config.constants import COLORS, WINDOW, FONTS, APP_NAME, APP_VERSION, AUTHOR, GITHUB_PROFILE, GITHUB_RELEASES


class AboutDialog:
    """About dialog with version info and update checker."""

    def __init__(self, parent: tk.Tk, app_icon=None):
        self.parent = parent
        self.app_icon = app_icon
        self.window = tk.Toplevel(parent)
        self._setup_window()
        self._setup_content()

    def _setup_window(self) -> None:
        """Configure the window properties."""
        self.window.title(f"About {APP_NAME}")
        self.window.geometry(f"{WINDOW['about_width']}x{WINDOW['about_height']}")
        self.window.resizable(False, False)
        self.window.configure(bg=COLORS["base"])
        self.window.grab_set()

        if self.app_icon:
            try:
                self.window.iconphoto(True, self.app_icon)
            except Exception:
                pass

    def _setup_content(self) -> None:
        """Setup the dialog content."""
        tk.Label(
            self.window,
            text=APP_NAME,
            font=FONTS["about_title"],
            fg=COLORS["lavender"],
            bg=COLORS["base"],
        ).pack(pady=(18, 2))

        tk.Label(
            self.window,
            text=f"Version {APP_VERSION}",
            font=FONTS["about_version"],
            fg=COLORS["subtext0"],
            bg=COLORS["base"],
        ).pack(pady=(0, 10))

        tk.Label(
            self.window,
            text=f"Created by {AUTHOR}\nEmulates game processes to solve Discord quests.",
            font=FONTS["about_text"],
            fg=COLORS["text"],
            bg=COLORS["base"],
            justify="center",
        ).pack(pady=5)

        btn_update = tk.Button(
            self.window,
            text="Check for Updates",
            font=FONTS["button_small"],
            bg=COLORS["blue"],
            fg=COLORS["mantle"],
            relief="flat",
            command=self._open_releases,
            pady=3,
            padx=10,
        )
        btn_update.pack(pady=15)

    def _open_releases(self) -> None:
        """Open the GitHub releases page."""
        webbrowser.open(GITHUB_RELEASES)
