"""Pixelated button component for retro UI styling."""

import tkinter as tk
from typing import Optional, Callable


class PixelButton(tk.Canvas):
    """Retro pixelated button with rounded corners and 3D shading."""
    
    def __init__(self, parent, text: str, command: Optional[Callable] = None, 
                 bg_color: str = "#313244", fg_color: str = "#cdd6f4",
                 width: int = 160, height: int = 50, icon: Optional[tk.PhotoImage] = None,
                 colors: dict = None, state: str = "normal", **kwargs):
        """
        Initialize pixelated button.
        
        Args:
            parent: Parent widget
            text: Button text
            command: Button callback
            bg_color: Background color
            fg_color: Text color
            width: Button width
            height: Button height
            icon: Optional icon image
            colors: Theme colors dictionary
            state: Button state ("normal" or "disabled")
        """
        self.width = width
        self.height = height
        self.text = text
        self.command = command
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.icon = icon
        self.colors = colors or {}
        self._state = state
        
        # Calculate theme colors
        self.hover_color = self._lighten_color(bg_color, 15)
        self.shadow_color = self._darken_color(bg_color, 20)
        self.outline_color = "#000000"
        
        # Disabled color
        self.disabled_color = self._darken_color(bg_color, 40)
        
        # Pixel scale for rounded corners (staircasing)
        self.pixel_scale = 3
        
        super().__init__(parent, width=self.width, height=self.height, 
                         bg=parent['bg'] if hasattr(parent, 'config') else bg_color,
                         highlightthickness=0, bd=0, **kwargs)
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        
        self._init_button_shapes()
        self._update_element_colors(self.bg_color, is_pressed=False)
        
        # CRUCIAL FIX: Force canvas button outline matrices to paint immediately on launch
        self.update()  # Force Tkinter geometry update
    
    def _lighten_color(self, color: str, percent: int) -> str:
        """Lighten a hex color by percentage."""
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, int(r + (255 - r) * percent / 100))
        g = min(255, int(g + (255 - g) * percent / 100))
        b = min(255, int(b + (255 - b) * percent / 100))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _darken_color(self, color: str, percent: int) -> str:
        """Darken a hex color by percentage."""
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, int(r * (100 - percent) / 100))
        g = max(0, int(g * (100 - percent) / 100))
        b = max(0, int(b * (100 - percent) / 100))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _init_button_shapes(self) -> None:
        """Initialize button shapes and store element IDs."""
        w, h = self.width, self.height
        s = self.pixel_scale
        
        # 1. Black structural outline blocks
        self.create_rectangle(s, 0, w - s, h, fill=self.outline_color, outline="")
        self.create_rectangle(0, s, w, h - s, fill=self.outline_color, outline="")
        
        # 2. Main Inner Faces (Track IDs for fast lookups)
        f1 = self.create_rectangle(s * 2, s, w - (s * 2), h - s, fill="", outline="")
        f2 = self.create_rectangle(s, s * 2, w - s, h - (s * 2), fill="", outline="")
        self._faces = [f1, f2]
        
        # 3. Retro 3D depth lines
        self._top_light_id = self.create_line(s * 2, s, w - (s * 2), s, fill="", width=s)
        self._bot_dark_id = self.create_line(s * 2, h - s - 1, w - (s * 2), h - s - 1, fill="", width=s)
        
        # 4. Icon & Text placement (icon on left, text centered with spacing)
        text_y = h // 2
        if self.icon:
            # Position icon on the left side with padding
            icon_x = 20  # Fixed position from left
            self._icon_id = self.create_image(icon_x, text_y, image=self.icon, anchor="center")
            
            # Center text in the remaining space with icon-text-spacing
            self._text_id = self.create_text(w // 2 + 15, text_y, text=self.text, fill=self.fg_color,
                                             font=("Courier", 10, "bold"), anchor="center")
        else:
            self._text_id = self.create_text(w // 2, text_y, text=self.text, fill=self.fg_color,
                                             font=("Courier", 10, "bold"), anchor="center")
    
    def _update_element_colors(self, face_color: str, is_pressed: bool = False) -> None:
        """Update element colors without redrawing canvas."""
        h = self.height
        s = self.pixel_scale
        
        for face in self._faces:
            self.itemconfig(face, fill=face_color)
        
        top_light = self._lighten_color(face_color, 25) if not is_pressed else self.shadow_color
        bot_dark = self.shadow_color if not is_pressed else self._lighten_color(face_color, 25)
        self.itemconfig(self._top_light_id, fill=top_light)
        self.itemconfig(self._bot_dark_id, fill=bot_dark)
        
        # FORCE ABSOLUTE RUNTIME RE-CENTERING AND ANCHOR OVERRIDES
        text_y = (h // 2) + (2 if is_pressed else 0)
        if hasattr(self, '_icon_id') and self._icon_id is not None:
            # Layout with active icon asset - icon on left, text centered with spacing
            icon_x = 20  # Fixed position from left
            self.coords(self._icon_id, icon_x, text_y)
            
            # Center text in the remaining space with icon-text-spacing
            self.coords(self._text_id, self.width // 2 + 15, text_y)
        else:
            self.coords(self._text_id, self.width // 2, text_y)
    
    def _on_enter(self, event) -> None:
        """Handle mouse enter."""
        if self._state == "normal":
            self._update_element_colors(self.hover_color)
    
    def _on_leave(self, event) -> None:
        """Handle mouse leave."""
        if self._state == "normal":
            self._update_element_colors(self.bg_color)
        else:
            self._update_element_colors(self.disabled_color)
    
    def _on_press(self, event) -> None:
        """Handle mouse press."""
        if self._state == "normal":
            self._update_element_colors(self.shadow_color, is_pressed=True)
    
    def _on_release(self, event) -> None:
        """Handle mouse release."""
        if self._state == "normal":
            self._update_element_colors(self.hover_color)
            if self.command:
                self.command()
        else:
            self._update_element_colors(self.disabled_color)
    
    def update_colors(self, bg_color: str, fg_color: str, new_text: str = None) -> None:
        """Update button colors and optionally text."""
        self.bg_color = bg_color
        self.fg_color = fg_color
        
        # If a new text string is passed, update the class variable
        if new_text is not None:
            self.text = new_text
        
        self.hover_color = self._lighten_color(bg_color, 15)
        self.shadow_color = self._darken_color(bg_color, 20)
        
        # Update the actual text rendering string properties on the canvas object ID
        if hasattr(self, '_text_id') and self._text_id is not None:
            self.itemconfig(self._text_id, fill=fg_color, text=self.text)
        
        self._update_element_colors(self.bg_color)
    
    def update_text(self, text: str) -> None:
        """Update button text."""
        self.text = text
        self.itemconfig(self._text_id, text=text)
    
    def update_icon(self, icon: tk.PhotoImage) -> None:
        """Update button icon."""
        self.icon = icon
        self.delete("all")
        self._init_button_shapes()
        self._update_element_colors(self.bg_color)
    
    def config(self, **kwargs) -> None:
        """Configure button state (for compatibility with tk.Button)."""
        if "state" in kwargs:
            self._state = kwargs["state"]
            if self._state == "disabled":
                self._update_element_colors(self.disabled_color)
            else:
                self._update_element_colors(self.bg_color)
        if "text" in kwargs:
            self.update_text(kwargs["text"])
