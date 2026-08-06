"""Pixelated container component for retro UI styling with 8-bit borders."""

import tkinter as tk


class PixelContainer(tk.Canvas):
    """A stable, retro 8-bit container panel with fixed sizing configurations."""
    
    def __init__(self, parent, width: int = None, height: int = None, 
                 bg_color: str = "#1e1e2e", border_color: str = "#000000", 
                 pixel_scale: int = 3, **kwargs):
        
        self.bg_color = bg_color           
        self.border_color = border_color   
        self.pixel_scale = pixel_scale
        self.dynamic_width = width is None
        self.dynamic_height = height is None
        
        # Build canvas kwargs - only include width/height if they're not None
        canvas_kwargs = {
            'bg': parent['bg'] if hasattr(parent, 'config') else "#11111b",
            'highlightthickness': 0,
            'bd': 0
        }
        if not self.dynamic_width:
            canvas_kwargs['width'] = width
        if not self.dynamic_height:
            canvas_kwargs['height'] = height
        
        # Enforce strict pixel dimensions to block collapsing loops
        super().__init__(parent, **canvas_kwargs, **kwargs)     
        
        # Build the interior content container frame layer
        self.content_frame = tk.Frame(self, bg=self.bg_color)
        
        # Always bind to configure event to redraw borders when geometry changes
        # This ensures borders auto-adjust even when fixed dimensions are changed
        self.bind('<Configure>', self._on_configure)
        
        # If dimensions are fixed, draw immediately with those dimensions
        if not self.dynamic_width and not self.dynamic_height:
            self._draw_borders(width, height)
    
    def _draw_borders(self, width: int, height: int) -> None:
        """Draw the pixel borders with given dimensions."""
        self.delete("all")
        w, h = width, height
        s = self.pixel_scale
        w_b, h_b = w - 1, h - 1
        
        # 1. Draw black rounded staircase outline structural borders
        self.create_rectangle(s, 0, w_b - s, h_b, fill=self.border_color, outline="")
        self.create_rectangle(0, s, w_b, h_b - s, fill=self.border_color, outline="")
        
        # 2. Draw main inner card background surface
        self.create_rectangle(s * 2, s, w_b - (s * 2), h_b - s, fill=self.bg_color, outline="")
        self.create_rectangle(s, s * 2, w_b - s, h_b - (s * 2), fill=self.bg_color, outline="")
        
        # 3. Position the host window for inner content components
        self.create_window(s * 2, s * 2, window=self.content_frame, anchor="nw",
                           width=w - (s * 4), height=h - (s * 4))
    
    def _on_configure(self, event) -> None:
        """Handle configure event for dynamic sizing."""
        self._draw_borders(event.width, event.height)
    
    def _redraw(self, width: int, height: int) -> None:
        """Redraw the pixel borders with given dimensions."""
        self._draw_borders(width, height)
    
    def pack(self, **kwargs):
        """Override pack to pack the canvas itself."""
        super().pack(**kwargs)
    
    def grid(self, **kwargs):
        """Override grid to grid the canvas itself."""
        super().grid(**kwargs)
    
    def place(self, **kwargs):
        """Override place to place the canvas itself."""
        super().place(**kwargs)
    
    def config(self, **kwargs):
        """Override config to apply colors and redraw borders on dimension changes."""
        redraw_needed = False
        if 'bg' in kwargs:
            self.bg_color = kwargs['bg']
            self.content_frame.config(bg=kwargs['bg'])
        if 'width' in kwargs or 'height' in kwargs:
            redraw_needed = True
        super().config(**kwargs)
        if redraw_needed:
            # Schedule redraw after config is applied
            self.after_idle(self._trigger_redraw)
    
    def _trigger_redraw(self):
        """Trigger a border redraw with current widget dimensions."""
        self._draw_borders(self.winfo_width(), self.winfo_height())
    
    def update_colors(self, bg_color: str = None, border_color: str = None) -> None:
        """Update the container colors and redraw borders.
        
        Args:
            bg_color: New background color (optional)
            border_color: New border color (optional)
        """
        if bg_color is not None:
            self.bg_color = bg_color
            self.content_frame.config(bg=bg_color)
        if border_color is not None:
            self.border_color = border_color
        self._draw_borders(self.winfo_width(), self.winfo_height())
