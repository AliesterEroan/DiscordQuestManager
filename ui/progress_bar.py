"""Progress bar component for Discord Quest Manager."""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from config.constants import COLORS, FONTS


class ProgressBar:
    """Visual progress bar for quest timer."""

    def __init__(self, parent: tk.Widget, colors: dict):
        self.parent = parent
        self.colors = colors
        self.total_seconds = 900  # Default 15 minutes
        self.elapsed_seconds = 0
        self.on_complete_callback: Optional[Callable] = None
        
        self._setup_progress_bar()

    def _setup_progress_bar(self) -> None:
        """Setup the progress bar UI."""
        self.frame = tk.Frame(self.parent, bg=self.colors["mantle"])
        
        # Progress bar
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "QuestProgress.Horizontal.TProgressbar",
            troughcolor=self.colors["surface0"],
            background=self.colors["green"],
            borderwidth=0,
            thickness=8,
        )
        
        self.progress = ttk.Progressbar(
            self.frame,
            style="QuestProgress.Horizontal.TProgressbar",
            mode='determinate',
            maximum=100,
        )
        self.progress.pack(fill="x", pady=(5, 0))
        
        # Percentage label
        self.lbl_percentage = tk.Label(
            self.frame,
            text="0%",
            font=FONTS["button_small"],
            fg=self.colors["subtext0"],
            bg=self.colors["mantle"],
        )
        self.lbl_percentage.pack(anchor="e", pady=(2, 0))

    def set_total_duration(self, total_seconds: int) -> None:
        """Set the total duration for the progress bar.
        
        Args:
            total_seconds: Total duration in seconds
        """
        self.total_seconds = total_seconds
        self.elapsed_seconds = 0
        self.update_progress()

    def update_progress(self, elapsed_seconds: Optional[int] = None) -> None:
        """Update the progress bar.
        
        Args:
            elapsed_seconds: Elapsed time in seconds (optional)
        """
        if elapsed_seconds is not None:
            self.elapsed_seconds = elapsed_seconds
        
        if self.total_seconds > 0:
            percentage = (self.elapsed_seconds / self.total_seconds) * 100
            percentage = min(percentage, 100)
            self.progress['value'] = percentage
            self.lbl_percentage.config(text=f"{int(percentage)}%")
            
            # Check for completion
            if percentage >= 100 and self.on_complete_callback:
                self.on_complete_callback()

    def reset(self) -> None:
        """Reset the progress bar to 0."""
        self.elapsed_seconds = 0
        self.progress['value'] = 0
        self.lbl_percentage.config(text="0%")

    def set_on_complete(self, callback: Callable) -> None:
        """Set callback for completion.
        
        Args:
            callback: Function to call when progress reaches 100%
        """
        self.on_complete_callback = callback

    def update_colors(self, colors: dict) -> None:
        """Update colors when theme changes.
        
        Args:
            colors: New color dictionary
        """
        self.colors = colors
        self.frame.config(bg=colors["mantle"])
        self.lbl_percentage.config(bg=colors["mantle"], fg=colors["subtext0"])
        
        # Update progress bar style
        style = ttk.Style()
        style.configure(
            "QuestProgress.Horizontal.TProgressbar",
            troughcolor=colors["surface0"],
            background=colors["green"],
        )
