"""Smooth vector progress bar with PIL-based rendering."""

import tkinter as tk
from PIL import Image, ImageTk, ImageDraw


class SmoothVectorProgressBar(tk.Canvas):
    """
    A smooth vector cartoon progress bar featuring:
    - Dual-tone vertical vector shading matching the button design
    - Smooth animated progress transitions
    - 2x PIL supersampling for crisp anti-aliased pill edges
    """
    def __init__(self, parent, value: float = 0.0, 
                 base_color: str = "#6ec622", dark_color: str = "#437e10", 
                 bg_color: str = "#11111b", border_color: str = "#313244",
                 height: int = 24, **kwargs):
        
        # Remove width if passed to allow flexible dynamic layout scaling
        kwargs.pop('width', None)
        
        super().__init__(parent, height=height, 
                         bg=parent['bg'] if hasattr(parent, 'config') else "#181825",
                         highlightthickness=0, bd=0, **kwargs)
        
        self.w = 300  # Default width, will be updated on resize
        self.h = height
        self.value = max(0.0, min(1.0, value))  # Clamped between 0.0 and 1.0
        
        self.base_color = self._hex_to_rgb(base_color)
        self.dark_color = self._hex_to_rgb(dark_color)
        self.bg_color = bg_color
        self.border_color = border_color
        
        self.photo_img = None
        
        # Bind resize event for dynamic sizing
        self.bind("<Configure>", self._on_container_resize)
        
        # Force initial render
        self.update()
        self._render_bar()

    @staticmethod
    def _hex_to_rgb(hex_str: str):
        hex_str = hex_str.lstrip('#')
        return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

    def set_value(self, value: float):
        """Update progress value (0.0 to 1.0) and redraw."""
        self.value = max(0.0, min(1.0, value))
        self._render_bar()

    def set_progress(self, value: float):
        """Update progress value (0.0 to 1.0) and redraw - alias for set_value."""
        self.set_value(value)

    def _on_container_resize(self, event) -> None:
        """Handle container resize to update progress bar width."""
        self.w = event.width
        self._render_bar()

    def _create_bar_image(self) -> Image.Image:
        scale = 2  # 2x supersampling
        sw, sh = self.w * scale, self.h * scale
        sr = (self.h // 2) * scale

        # 1. Base Canvas & Dark Outer Container
        base_img = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
        draw = ImageDraw.Draw(base_img)

        # Draw outer container border & dark background
        draw.rounded_rectangle([0, 0, sw - 1, sh - 1], radius=sr, 
                               fill=self.bg_color, outline=self.border_color, width=2 * scale)

        # 2. Render Active Fill Bar (if progress > 0)
        fill_w = int((sw - (4 * scale)) * self.value)
        if fill_w > (sr // 2):
            # Create smooth shaded color block
            shade_block = Image.new("RGB", (fill_w, sh - (4 * scale)))
            for y in range(sh - (4 * scale)):
                factor = min(1.0, max(0.0, y / max(1, sh - (4 * scale))))
                r = int(self.base_color[0] + factor * (self.dark_color[0] - self.base_color[0]))
                g = int(self.base_color[1] + factor * (self.dark_color[1] - self.base_color[1]))
                b = int(self.base_color[2] + factor * (self.dark_color[2] - self.base_color[2]))
                for x in range(fill_w):
                    shade_block.putpixel((x, y), (r, g, b))

            # Mask fill bar to rounded pill
            mask = Image.new("L", (fill_w, sh - (4 * scale)), 0)
            p_draw = ImageDraw.Draw(mask)
            p_draw.rounded_rectangle([0, 0, fill_w - 1, sh - (4 * scale) - 1], radius=sr - scale, fill=255)

            # Composite active fill inside the container padding
            fill_layer = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
            fill_layer.paste(shade_block, (2 * scale, 2 * scale), mask)
            
            base_img = Image.alpha_composite(base_img, fill_layer)

        # Downsample to target size with anti-aliasing
        return base_img.resize((self.w, self.h), Image.Resampling.LANCZOS)

    def _render_bar(self):
        self.delete("all")
        self.photo_img = ImageTk.PhotoImage(self._create_bar_image())
        self.create_image(0, 0, image=self.photo_img, anchor="nw")

    def update_colors(self, base_color: str, dark_color: str, bg_color: str = None, border_color: str = None):
        """Update progress bar colors."""
        self.base_color = self._hex_to_rgb(base_color)
        self.dark_color = self._hex_to_rgb(dark_color)
        if bg_color:
            self.bg_color = bg_color
        if border_color:
            self.border_color = border_color
        self._render_bar()
