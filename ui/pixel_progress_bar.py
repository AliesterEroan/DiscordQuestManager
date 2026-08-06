"""Pixelated progress bar component for retro UI styling."""

import tkinter as tk


class PixelProgressBar(tk.Canvas):
    """Dynamic 8-bit style segmented progress bar that closes its border caps flawlessly."""
    
    def __init__(self, parent, height: int = 16, 
                 bg_color: str = "#1e1e2e", fill_color: str = "#a6e3a1", 
                 colors: dict = None, **kwargs):
        """
        Initialize pixelated progress bar.
        
        Args:
            parent: Parent widget
            height: Bar height
            bg_color: Background color (mantle)
            fill_color: Progress fill color (green)
            colors: Theme colors dictionary
        """
        # Explicitly remove width if passed to allow flexible dynamic layout scaling
        kwargs.pop('width', None)
        
        self.colors = colors or {}
        self.height = height
        self.bg_color = bg_color
        self.fill_color = fill_color
        self.trough_color = self.colors.get("surface0", "#313244") if colors else "#313244"
        
        # Enforce flat retro properties
        super().__init__(parent, height=height, bg=bg_color,
                         highlightthickness=0, bd=0, **kwargs)
        
        self.pixel_scale = 3  # Matches button border thickness
        self.progress = 0.0   # Float percentage from 0.0 to 1.0
        
        # FIX: Bind the resizing configurations to redraw borders automatically
        self.bind("<Configure>", self._on_container_resize)
        
        # CRUCIAL FIX: Force loading trough track outlines to render completely on startup
        self.update()  # Force Tkinter geometry update
        self._redraw(self.winfo_width(), self.winfo_height())

    def _on_container_resize(self, event) -> None:
        """Triggers every time the layout window or parent frame expands/shrinks."""
        self._redraw(event.width, event.height)

    def _redraw(self, w: int, h: int) -> None:
        """Redraw the progress bar with dynamic dimensions."""
        self.delete("all")
        s = self.pixel_scale
        
        # 1. Coordinate boundary definitions
        w_bound = w - 1
        h_bound = h - 1
        
        # 2. Black rounded staircase outline frame
        self.create_rectangle(s, 0, w_bound - s, h_bound, fill="#000000", outline="")
        self.create_rectangle(0, s, w_bound, h_bound - s, fill="#000000", outline="")
        
        # 3. Inner empty trough track container
        self.create_rectangle(s * 2, s, w_bound - (s * 2), h_bound - s, fill=self.trough_color, outline="")
        self.create_rectangle(s, s * 2, w_bound - s, h_bound - (s * 2), fill=self.trough_color, outline="")
        
        # 4. FIX: FLUID PROGRESS FILL (Replaces the chunky 'while' block loop)
        if self.progress > 0.0:
            usable_width = w_bound - (s * 4)
            fill_width = int(usable_width * self.progress)
            
            # Symmetrical top and bottom edge bounds to sit clean inside borders
            chunk_top_y = s * 2
            chunk_bottom_y = h_bound - (s * 2)
            
            # Calculate fluid end coordinates
            start_x = s * 2
            end_x = start_x + fill_width
            
            # Enforce hard limits so the fill never slices past the closed right cap
            if end_x > w_bound - (s * 2):
                end_x = w_bound - (s * 2)
                
            # Draw a single, solid, fluid progress block instead of blocks
            if end_x > start_x:
                self.create_rectangle(
                    start_x, chunk_top_y, 
                    end_x, chunk_bottom_y, 
                    fill=self.fill_color, outline=""
                )

    def set_progress(self, value: float) -> None:
        """Update progress value seamlessly (expects a float between 0.0 and 1.0)."""
        self.progress = max(0.0, min(1.0, value))
        # Re-fetch runtime geometry matrix width metrics safely
        self._redraw(self.winfo_width(), self.winfo_height())
    
    def update_colors(self, bg_color: str, fill_color: str) -> None:
        """Update progress bar colors."""
        self.bg_color = bg_color
        self.fill_color = fill_color
        self.trough_color = self.colors.get("surface0", "#313244") if self.colors else "#313244"
        self.config(bg=bg_color)
        self._redraw(self.winfo_width(), self.winfo_height())
