"""About dialog for Discord Quest Manager."""

import tkinter as tk
from tkinter import messagebox
import webbrowser

from config.constants import WINDOW, FONTS, APP_NAME, APP_VERSION, AUTHOR, GITHUB_PROFILE, GITHUB_RELEASES
from core.update_manager import UpdateManager


class AboutDialog:
    """About dialog with version info and update checker."""

    def __init__(self, parent: tk.Tk, app_icon=None, colors: dict = None):
        self.parent = parent
        self.app_icon = app_icon
        self.colors = colors or {}
        self.update_manager = UpdateManager()
        self.window = tk.Toplevel(parent)
        self._setup_window()
        self._setup_content()

    def _setup_window(self) -> None:
        """Configure the window properties."""
        self.window.title("About")
        self.window.geometry(f"{WINDOW['about_width']}x{WINDOW['about_height']}")
        self.window.resizable(False, False)
        self.window.configure(bg=self.colors.get("base", "#1e1e2e"))
        self.window.grab_set()
        self.window.ui_role = "background_main"

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
            fg=self.colors.get("lavender", "#b4befe"),
            bg=self.colors.get("base", "#1e1e2e"),
            highlightthickness=0,
        ).pack(pady=(18, 2))

        tk.Label(
            self.window,
            text=f"Version {APP_VERSION}",
            font=FONTS["about_version"],
            fg=self.colors.get("subtext0", "#a6adc8"),
            bg=self.colors.get("base", "#1e1e2e"),
            highlightthickness=0,
        ).pack(pady=(0, 10))

        tk.Label(
            self.window,
            text=f"Created by {AUTHOR}\nEmulates game processes to solve Discord quests.",
            font=FONTS["about_text"],
            fg=self.colors.get("text", "#cdd6f4"),
            bg=self.colors.get("base", "#1e1e2e"),
            justify="center",
            highlightthickness=0,
        ).pack(pady=5)

        self.btn_update = tk.Button(
            self.window,
            text="Check for Updates",
            font=FONTS["button_small"],
            bg=self.colors.get("blue", "#89b4fa"),
            fg=self.colors.get("base", "#1e1e2e"),
            relief="flat",
            command=self._check_for_updates,
            pady=3,
            padx=10,
        )
        self.btn_update.pack(pady=15)

    def _check_for_updates(self) -> None:
        """Check for updates using the update manager."""
        btn_update = self.window.winfo_children()[-1]  # Get the update button
        btn_update.config(text="Checking...", state="disabled")
        
        def on_check_complete(update_available: bool, latest_version: str, download_url: str) -> None:
            btn_update.config(text="Check for Updates", state="normal")
            
            if update_available:
                # Show update available dialog
                release_notes = self.update_manager.get_release_notes()
                message = f"A new version ({latest_version}) is available!\n\nCurrent version: {APP_VERSION}\n\nRelease Notes:\n{release_notes[:500]}..."
                
                if messagebox.askyesno("Update Available", message):
                    if download_url:
                        webbrowser.open(download_url)
                    else:
                        webbrowser.open(GITHUB_RELEASES)
            else:
                messagebox.showinfo("No Updates", f"You're already running the latest version ({APP_VERSION}).")
        
        self.update_manager.check_for_updates_async(on_check_complete)

    def _open_releases(self) -> None:
        """Open the GitHub releases page."""
        webbrowser.open(GITHUB_RELEASES)
    
    def update_colors(self, colors: dict) -> None:
        """Update colors when theme changes.
        
        Args:
            colors: New color dictionary
        """
        self.colors = colors
        self.window.configure(bg=colors.get("base", "#1e1e2e"))
        
        # Update all widgets - now set bg on labels explicitly
        for widget in self.window.winfo_children():
            if isinstance(widget, tk.Label):
                # Update both fg and bg colors
                current_fg = widget.cget("fg")
                fg_map = {
                    "#b4befe": colors.get("lavender", "#b4befe"),
                    "#a6adc8": colors.get("subtext0", "#a6adc8"),
                    "#cdd6f4": colors.get("text", "#cdd6f4"),
                }
                if current_fg in fg_map:
                    widget.config(fg=fg_map[current_fg], bg=colors.get("base", "#1e1e2e"))
                else:
                    widget.config(bg=colors.get("base", "#1e1e2e"))
            elif isinstance(widget, tk.Button):
                # Update button colors to match theme
                widget.config(bg=colors.get("blue", "#89b4fa"), fg=colors.get("base", "#1e1e2e"))
