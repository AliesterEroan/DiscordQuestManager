"""Smooth shaded vector button with PIL-based rendering."""

import os
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw


class SmoothShadedVectorButton(tk.Canvas):
    """
    A smooth vector cartoon pill button featuring:
    - Clean vertical color interpolation for smooth vector shading
    - Perfectly centered text and left-slot icon alignment
    - 2x PIL supersampling for crisp anti-aliased edges
    """
    def __init__(self, parent, text: str = "Button", icon_name: str = "", 
                 base_color: str = "#6ec622", dark_color: str = "#437e10", 
                 fg_color: str = "#ffffff", width: int = 220, height: int = 46, 
                 command=None, **kwargs):
        
        super().__init__(parent, width=width, height=height, 
                         bg=parent['bg'] if hasattr(parent, 'config') else "#181825",
                         highlightthickness=0, bd=0, cursor="hand2", **kwargs)
        
        self.text = text
        self.icon_name = icon_name
        self.base_color = self._hex_to_rgb(base_color)
        self.dark_color = self._hex_to_rgb(dark_color)
        self.fg_color = fg_color
        self.command = command
        
        self.w = width
        self.h = height
        self.icon_pil = None
        self.photo_normal = None
        self.photo_pressed = None
        
        self._load_icon()
        self._render_button_images()
        
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        
        self._draw_state(is_pressed=False)

    @staticmethod
    def _hex_to_rgb(hex_str: str):
        hex_str = hex_str.lstrip('#')
        return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

    def _load_icon(self):
        if not self.icon_name:
            return
            
        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "assets", "icons", 
            self.icon_name
        )
        
        if os.path.exists(icon_path):
            try:
                img = Image.open(icon_path).convert("RGBA")
                self.icon_pil = img.resize((20, 20), Image.Resampling.LANCZOS)
            except Exception as e:
                print(f"[WARN] Could not load icon '{self.icon_name}': {e}")

    def _create_button_image(self, is_pressed: bool = False) -> Image.Image:
        scale = 2  # 2x supersampling
        sw, sh = self.w * scale, self.h * scale
        sr = (self.h // 2) * scale
        y_off = (2 * scale) if is_pressed else 0
        pill_height = sh - (4 * scale)

        # 1. Create Smooth Vertical Shade Block
        shade_block = Image.new("RGB", (sw, sh))
        for y in range(sh):
            factor = min(1.0, max(0.0, (y - y_off) / max(1, pill_height)))
            r = int(self.base_color[0] + factor * (self.dark_color[0] - self.base_color[0]))
            g = int(self.base_color[1] + factor * (self.dark_color[1] - self.base_color[1]))
            b = int(self.base_color[2] + factor * (self.dark_color[2] - self.base_color[2]))
            for x in range(sw):
                shade_block.putpixel((x, y), (r, g, b))

        # 2. Mask Shade Block to Rounded Pill
        mask = Image.new("L", (sw, sh), 0)
        p_draw = ImageDraw.Draw(mask)
        p_draw.rounded_rectangle([0, y_off, sw - 1, pill_height + y_off], radius=sr, fill=255)

        btn_img = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
        btn_img.paste(shade_block, (0, 0), mask)

        # 3. Left Slot Divider (Exact X = 46px slot)
        if self.icon_pil or self.icon_name:
            div_draw = ImageDraw.Draw(btn_img)
            div_x = 46 * scale
            div_draw.line([(div_x, y_off + (6 * scale)), (div_x, pill_height + y_off - (6 * scale))], 
                          fill="#ffffff", width=1 * scale)

        # Downsample to target dimensions
        btn_img = btn_img.resize((self.w, self.h), Image.Resampling.LANCZOS)

        # 4. Center Icon Perfectly inside Left Slot (0px to 46px)
        center_y = ((self.h - 2) // 2) + (1 if is_pressed else 0)
        if self.icon_pil:
            icon_x = (46 - 20) // 2  # Perfectly centered in 46px slot
            btn_img.paste(self.icon_pil, (icon_x, center_y - 10), self.icon_pil)

        return btn_img

    def _render_button_images(self):
        self.photo_normal = ImageTk.PhotoImage(self._create_button_image(is_pressed=False))
        self.photo_pressed = ImageTk.PhotoImage(self._create_button_image(is_pressed=True))

    def _draw_state(self, is_pressed: bool = False):
        self.delete("all")
        photo = self.photo_pressed if is_pressed else self.photo_normal
        self.create_image(0, 0, image=photo, anchor="nw")
        
        center_y = ((self.h - 2) // 2) + (1 if is_pressed else 0)
        
        # Center text horizontally in remaining right section (46px to width)
        if self.icon_pil or self.icon_name:
            text_x = 46 + ((self.w - 46) // 2)
        else:
            text_x = self.w // 2
            
        self.create_text(text_x, center_y, text=self.text, font=("Segoe UI", 10, "bold"), 
                         fill=self.fg_color, anchor="center")

    def _on_press(self, event):
        self._draw_state(is_pressed=True)

    def _on_release(self, event):
        self._draw_state(is_pressed=False)
        if self.command:
            try:
                self.command()
            except Exception as e:
                print(f"Error executing button command: {e}")
                import traceback
                traceback.print_exc()

    def update_colors(self, base_color: str, dark_color: str, fg_color: str = "#ffffff", text: str = None):
        """Update button colors and optionally text."""
        self.base_color = self._hex_to_rgb(base_color)
        self.dark_color = self._hex_to_rgb(dark_color)
        self.fg_color = fg_color
        if text:
            self.text = text
        self._render_button_images()
        self._draw_state(is_pressed=False)

    def update_icon(self, icon_name: str):
        """Update button icon."""
        self.icon_name = icon_name
        self.icon_pil = None
        self._load_icon()
        self._render_button_images()
        self._draw_state(is_pressed=False)

    def config(self, **kwargs):
        """Override config to handle state changes and text updates."""
        state = kwargs.pop('state', None)
        text = kwargs.pop('text', None)
        
        if state == 'disabled':
            super().config(state='disabled')
        elif state == 'normal':
            super().config(state='normal')
        
        if text is not None:
            self.text = text
            self._render_button_images()
            self._draw_state(is_pressed=False)
        
        # Pass any remaining kwargs to parent (but filter out unsupported options)
        supported_kwargs = {k: v for k, v in kwargs.items() if k in ['cursor', 'bg']}
        super().config(**supported_kwargs)
