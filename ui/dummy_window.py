"""Dummy window for emulating game processes."""

import os
import sys
import tkinter as tk
import threading
import time
from typing import Optional, Dict

try:
    import winsound
except ImportError:
    winsound = None

from config.constants import COLORS, WINDOW, FONTS, ICON_FILENAME, TIMER_DURATION_MINUTES
from core.themes import THEME_REGISTRY
from utils.icon_handler import IconHandler
from core.dummy_registry import DummyRegistry
from core.settings_manager import SettingsManager


class DummyWindow:
    """Fake game process window for Discord quest emulation."""

    def __init__(self, game_exe_name: str, game_name: str = "Unknown", duration_minutes: int = TIMER_DURATION_MINUTES, theme_colors: Optional[Dict] = None, cat_selection: str = "Cat-1"):
        self.game_exe_name = game_exe_name
        self.game_name = game_name
        self.duration_seconds = duration_minutes * 60
        self.elapsed_seconds = 0
        self.is_complete = False
        self.cat_selection = cat_selection
        
        print(f"[DummyWindow] Initializing dummy window")
        print(f"[DummyWindow] Game: {game_name}, Exe: {game_exe_name}")
        print(f"[DummyWindow] Duration: {duration_minutes} minutes ({self.duration_seconds} seconds)")
        print(f"[DummyWindow] Cat selection: {cat_selection}")
        
        # Map cat selection to animation action
        self.cat_to_animation = {
            "Cat-1": "run",
            "Cat-2": "itch", 
            "Cat-3": "stretch",
            "Cat-4": "walk",
            "Cat-5": "run",
            "Cat-6": "itch"
        }
        self.animation_action = self.cat_to_animation.get(cat_selection, "run")
        
        # Map cat selection to display names
        self.cat_display_names = {
            "Cat-1": "Chestnut",
            "Cat-2": "Midnight",
            "Cat-3": "Misty",
            "Cat-4": "Pebble",
            "Cat-5": "Fluffy",
            "Cat-6": "Salva"
        }
        self.cat_display_name = self.cat_display_names.get(cat_selection, "Chestnut")
        
        # Load theme from settings or use provided colors
        self.colors = theme_colors if theme_colors else self._load_theme_from_settings()
        
        self.root = tk.Tk()
        self.icon_handler = IconHandler()
        self._register_dummy()
        self._setup_window()
        self._setup_icon()
        self._setup_content()
        
        # Show window
        print(f"[DummyWindow] Showing window...")
        self.root.after(200, self._start_timer_thread)  # Start timer after window is shown (increased delay)
        self.root.mainloop()
    
    def _load_theme_from_settings(self) -> Dict:
        """Load theme colors from settings using JSON files or custom colors."""
        try:
            import json
            import os
            
            settings_manager = SettingsManager()
            theme = settings_manager.get("theme", "mocha")
            
            # If custom theme, load custom colors from settings
            if theme == "custom":
                custom_colors = {}
                # Collect all custom_* settings
                for key in settings_manager.get_all().keys():
                    if key.startswith("custom_"):
                        color_key = key.replace("custom_", "")
                        custom_colors[color_key] = settings_manager.get(key)
                
                # If we have custom colors, return them
                if custom_colors:
                    return custom_colors
            
            # Otherwise, load from JSON theme file
            themes_dir = os.path.join(os.path.dirname(__file__), "..", "core", "themes")
            theme_file = os.path.join(themes_dir, f"{theme}.json")
            
            if not os.path.exists(theme_file):
                theme_file = os.path.join(themes_dir, "mocha.json")
            
            with open(theme_file, "r") as f:
                theme_data = json.load(f)
                return theme_data.get("colors", {})
        except Exception:
            # Return mocha defaults as fallback
            return {
                "base": "#1e1e2e",
                "mantle": "#181825",
                "surface": "#313244",
                "surface0": "#45475a",
                "surface1": "#585b70",
                "surface2": "#45475a",
                "text": "#cdd6f4",
                "subtext0": "#a6adc8",
                "subtext1": "#bac2de",
                "overlay0": "#6c7086",
                "overlay1": "#7f849c",
                "overlay2": "#9399b2",
                "blue": "#89b4fa",
                "lavender": "#b4befe",
                "sapphire": "#74c7ec",
                "sky": "#89dceb",
                "teal": "#94e2d5",
                "green": "#a6e3a1",
                "yellow": "#f9e2af",
                "peach": "#fab387",
                "maroon": "#eba0ac",
                "red": "#f38ba8",
                "mauve": "#cba6f7",
                "pink": "#f5c2e7",
                "flamingo": "#f2cdcd",
                "rosewater": "#f5e0dc"
            }

    def _register_dummy(self) -> None:
        """Register this dummy executable in the registry."""
        try:
            registry = DummyRegistry()
            current_exe = sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__)
            registry.register_dummy(current_exe, self.game_name, self.game_exe_name)
        except Exception:
            pass

    def _setup_window(self) -> None:
        """Configure the window properties."""
        self.root.title(self.game_exe_name)
        self.root.geometry(f"{WINDOW['dummy_width']}x{WINDOW['dummy_height']}")
        self.root.resizable(False, False)
        self.root.configure(bg=self.colors["base"])

        # Show on top briefly
        self.root.attributes("-topmost", True)
        self.root.after(500, lambda: self.root.attributes("-topmost", False))

    def _setup_icon(self) -> None:
        """Set the window icon."""
        icon = self.icon_handler.load_icon()
        if icon:
            try:
                self.root.iconphoto(True, icon)
            except Exception:
                pass

    def _setup_content(self) -> None:
        """Setup the window content with animation and progress."""
        # Load specific cat icon based on selection
        cat_icon = None
        cat_icon_name = f"cat-{self.cat_selection.lower()}.png"  # e.g., cat-cat-1.png
        if self.icon_handler:
            try:
                cat_icon = self.icon_handler.load_ui_icon(cat_icon_name, (20, 20), theme="")
            except Exception:
                # Fallback to generic cat icon
                try:
                    cat_icon = self.icon_handler.load_ui_icon("cat.png", (20, 20), theme="")
                except Exception:
                    pass
        
        # Cat name label with icon and special font
        if cat_icon:
            self.cat_name_label = tk.Label(
                self.root,
                image=cat_icon,
                text=f" {self.cat_display_name}",
                font=("Comic Sans MS", 14, "bold"),
                fg=self.colors["pink"],
                bg=self.colors["base"],
                compound="left"
            )
            self.cat_name_label.image = cat_icon
        else:
            self.cat_name_label = tk.Label(
                self.root,
                text=f"🐱 {self.cat_display_name}",
                font=("Comic Sans MS", 14, "bold"),
                fg=self.colors["pink"],
                bg=self.colors["base"]
            )
        self.cat_name_label.pack(pady=(5, 0))
        
        # Animation frame
        self.animation_frame = tk.Frame(self.root, bg=self.colors["base"])
        self.animation_frame.pack(pady=10)
        
        # Load cat animation based on selection
        cat_animation_path = self._get_cat_animation("running")
        if cat_animation_path:
            print(f"[DummyWindow] Loading animation from: {cat_animation_path}")
            try:
                self.animation_label = tk.Label(self.animation_frame, bg=self.colors["base"])
                self.animation_label.pack()
                
                # Check if it's a GIF or PNG
                if cat_animation_path.lower().endswith('.gif'):
                    print(f"[DummyWindow] Loading as GIF animation")
                    self._animate_gif(cat_animation_path)
                else:
                    print(f"[DummyWindow] Loading as static image")
                    self._load_static_image(cat_animation_path)
            except Exception as e:
                print(f"[DummyWindow] Failed to load animation: {e}")
                # Load cat icon as fallback
                cat_icon = None
                if self.icon_handler:
                    try:
                        cat_icon = self.icon_handler.load_ui_icon("cat.png", (100, 100), theme="")
                    except Exception:
                        pass
                
                if cat_icon:
                    self.animation_label = tk.Label(
                        self.animation_frame,
                        image=cat_icon,
                        bg=self.colors["base"]
                    )
                    self.animation_label.image = cat_icon
                    self.animation_label.pack()
                    print(f"[DummyWindow] Using fallback cat icon")
                else:
                    self.animation_label = tk.Label(
                        self.animation_frame,
                        text="🐱",
                        font=("Arial", 48),
                        fg=self.colors["green"],
                        bg=self.colors["base"]
                    )
                    self.animation_label.pack()
                    print(f"[DummyWindow] Using fallback cat emoji")
        else:
            print(f"[DummyWindow] No animation path found, using fallback")
            # Load cat icon as fallback
            cat_icon = None
            if self.icon_handler:
                try:
                    cat_icon = self.icon_handler.load_ui_icon("cat.png", (100, 100), theme="")
                except Exception:
                    pass
            
            if cat_icon:
                self.animation_label = tk.Label(
                    self.animation_frame,
                    image=cat_icon,
                    bg=self.colors["base"]
                )
                self.animation_label.image = cat_icon
                self.animation_label.pack()
                print(f"[DummyWindow] Using fallback cat icon")
            else:
                self.animation_label = tk.Label(
                    self.animation_frame,
                    text="🐱",
                    font=("Arial", 48),
                    fg=self.colors["green"],
                    bg=self.colors["base"]
                )
                self.animation_label.pack()
                print(f"[DummyWindow] Using fallback cat emoji")
        
        # Add ground line inside animation frame (under the cat) - positioned absolutely
        self.ground_canvas = tk.Canvas(
            self.animation_frame,
            width=200,
            height=15,
            bg=self.colors["base"],
            highlightthickness=0
        )
        self.ground_canvas.place(x=0, y=130)  # Position under the cat's feet
        
        # Draw ground line
        self.ground_canvas.create_line(
            20, 8, 180, 8,
            fill=self.colors["surface1"],
            width=2
        )
        
        # EXE name display under ground
        location_icon = None
        if self.icon_handler:
            try:
                location_icon = self.icon_handler.load_ui_icon("location.png", (12, 12), theme="")
            except Exception:
                pass
        
        if location_icon:
            self.exe_label = tk.Label(
                self.animation_frame,
                image=location_icon,
                text=f" {self.game_exe_name}",
                font=("Arial", 8),
                fg=self.colors["subtext0"],
                bg=self.colors["base"],
                compound="left"
            )
            self.exe_label.image = location_icon
        else:
            self.exe_label = tk.Label(
                self.animation_frame,
                text=f"📁 {self.game_exe_name}",
                font=("Arial", 8),
                fg=self.colors["subtext0"],
                bg=self.colors["base"]
            )
        self.exe_label.pack(pady=(5, 0))
        
        # Progress bar
        self.progress_frame = tk.Frame(self.root, bg=self.colors["base"])
        self.progress_frame.pack(fill="x", padx=20, pady=5)
        
        self.progress_bar = tk.Canvas(
            self.progress_frame,
            height=16,
            bg=self.colors["mantle"],
            highlightthickness=0,
            relief="flat"
        )
        self.progress_bar.pack(fill="x")
        
        # Dark trough background
        self.progress_trough = self.progress_bar.create_rectangle(
            0, 0, 1000, 16,
            fill=self.colors["mantle"],
            outline=""
        )
        
        self.progress_fill = self.progress_bar.create_rectangle(
            0, 0, 0, 16,
            fill=self.colors["green"],
            outline=""
        )
        
        # Telemetry text
        total_min = int(self.duration_seconds // 60)
        self.telemetry_label = tk.Label(
            self.root,
            text=f"00:00 / {total_min:02d}:00 • 0%",
            font=FONTS["timer"],
            fg=self.colors["text"],
            bg=self.colors["base"]
        )
        self.telemetry_label.pack(pady=5)
        
        # Status text
        self.status_label = tk.Label(
            self.root,
            text=f"Running: {self.game_exe_name}",
            font=FONTS["status"],
            fg=self.colors["subtext0"],
            bg=self.colors["base"]
        )
        self.status_label.pack(pady=5)
    
    def _get_cat_animation(self, state: str) -> Optional[str]:
        """Get path to cat animation GIF based on selected cat and random action.
        
        Args:
            state: "running" or "finished"
            
        Returns:
            Path to cat animation GIF or None if not found
        """
        import random
        import os
        
        print(f"[DummyWindow] _get_cat_animation called: state={state}, cat_selection={self.cat_selection}")
        
        # Available animations
        animations = ["run", "itch", "walk", "stretch", "sleep"]
        
        # For finished state, use stretch animation
        if state == "finished":
            animations = ["stretch"]
        
        # Try each animation until we find one that exists for this cat
        random.shuffle(animations)
        print(f"[DummyWindow] Trying animations in order: {animations}")
        
        # Get correct base directory for both dev and PyInstaller environments
        if getattr(sys, 'frozen', False):
            # Running in PyInstaller bundle
            base_dir = sys._MEIPASS
        else:
            # Running in development
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        print(f"[DummyWindow] Base directory: {base_dir}")
        
        # New folder structure: assets/animations/cat/{cat_selection}/{cat_file}
        cat_dir = os.path.join(base_dir, "assets", "animations", "cat", self.cat_selection)
        print(f"[DummyWindow] Cat directory: {cat_dir}")
        
        if not os.path.exists(cat_dir):
            print(f"[DummyWindow] Cat directory does not exist: {cat_dir}")
            # Fallback to static cat PNG
            static_cat_path = os.path.join(base_dir, "assets", "animations", "cat", f"{self.cat_selection}.png")
            print(f"[DummyWindow] Checking static cat PNG: {static_cat_path}")
            if os.path.exists(static_cat_path):
                print(f"[DummyWindow] Found static cat PNG: {static_cat_path}")
                return static_cat_path
            print(f"[DummyWindow] Static cat PNG does not exist: {static_cat_path}")
            return None
        
        for animation in animations:
            # Build file name based on animation type
            if animation == "stretch":
                cat_file = f"{self.cat_selection}-Stretching_b.gif"
            elif animation == "sleep":
                cat_file = f"{self.cat_selection}-Sleeping1.png"
            else:
                cat_file = f"{self.cat_selection}-{animation.capitalize()}_b.gif"
            
            animation_path = os.path.join(cat_dir, cat_file)
            print(f"[DummyWindow] Checking animation file: {animation_path}")
            
            if os.path.exists(animation_path):
                print(f"[DummyWindow] Found animation: {animation_path}")
                return animation_path
            else:
                print(f"[DummyWindow] Animation file does not exist: {animation_path}")
        
        print(f"[DummyWindow] No animation found for cat {self.cat_selection}, trying fallback to static PNG")
        
        # Fallback to static cat PNG
        static_cat_path = os.path.join(base_dir, "assets", "animations", "cat", f"{self.cat_selection}.png")
        print(f"[DummyWindow] Checking static cat PNG: {static_cat_path}")
        
        if os.path.exists(static_cat_path):
            print(f"[DummyWindow] Found static cat PNG: {static_cat_path}")
            return static_cat_path
        
        print(f"[DummyWindow] Static cat PNG does not exist: {static_cat_path}")
        return None

    def _animate_gif(self, gif_path: str) -> None:
        """Animate a GIF file with scaling to fit window bounds."""
        try:
            from PIL import Image, ImageTk
            img = Image.open(gif_path)
            
            # Calculate scaled size to fit within window bounds
            max_width = 200
            max_height = 150
            original_width, original_height = img.size
            
            # Calculate aspect ratio
            aspect_ratio = original_width / original_height
            
            # Scale to fit within max bounds while maintaining aspect ratio
            if original_width > max_width or original_height > max_height:
                if aspect_ratio > 1:
                    # Width is the limiting factor
                    new_width = max_width
                    new_height = int(max_width / aspect_ratio)
                else:
                    # Height is the limiting factor
                    new_height = max_height
                    new_width = int(max_height * aspect_ratio)
            else:
                new_width = original_width
                new_height = original_height
            
            frames = []
            
            try:
                while True:
                    # Resize frame
                    frame = img.copy()
                    frame = frame.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    frames.append(ImageTk.PhotoImage(frame))
                    img.seek(len(frames))
            except EOFError:
                pass
            
            self.current_frame = 0
            self.gif_frames = frames
            
            def update_frame():
                if not self.is_complete:
                    self.animation_label.config(image=self.gif_frames[self.current_frame])
                    self.current_frame = (self.current_frame + 1) % len(self.gif_frames)
                    self.root.after(50, update_frame)  # 50ms = 20 FPS for smoother animation
            
            update_frame()
        except Exception as e:
            print(f"[DummyWindow] GIF animation failed: {e}")
            raise

    def _load_static_image(self, image_path: str) -> None:
        """Load a static image (PNG) with scaling to fit window bounds."""
        try:
            from PIL import Image, ImageTk
            img = Image.open(image_path)
            
            # Calculate scaled size to fit within window bounds
            max_width = 200
            max_height = 150
            original_width, original_height = img.size
            
            # Calculate aspect ratio
            aspect_ratio = original_width / original_height
            
            # Scale to fit within max bounds while maintaining aspect ratio
            if original_width > max_width or original_height > max_height:
                if aspect_ratio > 1:
                    # Width is the limiting factor
                    new_width = max_width
                    new_height = int(max_width / aspect_ratio)
                else:
                    # Height is the limiting factor
                    new_height = max_height
                    new_width = int(max_height * aspect_ratio)
            else:
                new_width = original_width
                new_height = original_height
            
            # Resize and display
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            self.animation_label.config(image=photo)
            self.animation_label.image = photo  # Keep reference
            print(f"[DummyWindow] Static image loaded successfully: {new_width}x{new_height}")
        except Exception as e:
            print(f"[DummyWindow] Static image loading failed: {e}")
            raise

    def _start_timer_thread(self) -> None:
        """Start the timer thread after window is shown."""
        print(f"[DummyWindow] Starting timer thread... duration={self.duration_seconds}s")
        self.timer_thread = threading.Thread(target=self._run_timer, daemon=True)
        self.timer_thread.start()
        print(f"[DummyWindow] Timer thread started successfully")

    def _run_timer(self) -> None:
        """Run the quest timer in background thread."""
        print(f"[DummyWindow] Timer started: duration={self.duration_seconds}s")
        while self.elapsed_seconds < self.duration_seconds:
            time.sleep(1)
            self.elapsed_seconds += 1
            print(f"[DummyWindow] Timer tick: {self.elapsed_seconds}/{self.duration_seconds}s")
            
            # Update UI on main thread
            self.root.after(0, self._update_progress)
        
        # Timer complete
        print(f"[DummyWindow] Timer complete, calling _on_complete")
        self.root.after(0, self._on_complete)

    def _update_progress(self) -> None:
        """Update progress bar and telemetry."""
        if self.is_complete:
            return
        
        print(f"[DummyWindow] _update_progress called: elapsed={self.elapsed_seconds}, duration={self.duration_seconds}")
        
        # Calculate percentage
        percentage = (self.elapsed_seconds / self.duration_seconds) * 100
        print(f"[DummyWindow] Calculated percentage: {percentage}%")
        
        # Update progress bar
        canvas_width = self.progress_bar.winfo_width()
        print(f"[DummyWindow] Canvas width: {canvas_width}")
        if canvas_width <= 1:
            canvas_width = 300
            print(f"[DummyWindow] Forcing canvas width to 300")
        progress_width = (percentage / 100) * canvas_width
        print(f"[DummyWindow] Progress width: {progress_width}")
        self.progress_bar.coords(self.progress_fill, 0, 0, progress_width, 16)
        self.progress_bar.update()  # Force canvas update
        self.telemetry_label.config(fg=self.colors["text"], bg=self.colors["base"])
        self.status_label.config(fg=self.colors["subtext0"], bg=self.colors["base"])
        
        elapsed_min = int(self.elapsed_seconds // 60)
        elapsed_sec = int(self.elapsed_seconds % 60)
        total_min = int(self.duration_seconds // 60)
        total_sec = int(self.duration_seconds % 60)
        
        self.telemetry_label.config(
            text=f"{elapsed_min:02d}:{elapsed_sec:02d} / {total_min:02d}:{total_sec:02d} • {int(percentage)}%"
        )

    def _on_complete(self) -> None:
        """Handle quest completion."""
        self.is_complete = True
        
        # Swap to cat finish animation
        cat_animation_path = self._get_cat_animation("finished")
        if cat_animation_path:
            try:
                from PIL import Image, ImageTk
                img = Image.open(cat_animation_path)
                finish_photo = ImageTk.PhotoImage(img)
                self.animation_label.config(image=finish_photo, bg=self.colors["base"])
            except Exception:
                self.animation_label.config(text="🎉", font=("Segoe UI", 32), bg=self.colors["base"])
        else:
            self.animation_label.config(text="🎉", font=("Segoe UI", 32), bg=self.colors["base"])
        
        # Update progress bar to 100%
        self.progress_bar.coords(self.progress_fill, 0, 0, self.progress_bar.winfo_width(), 8)
        total_min = int(self.duration_seconds // 60)
        self.telemetry_label.config(text=f"{total_min:02d}:00 / {total_min:02d}:00 • 100%")
        
        # Update status
        self.status_label.config(
            text="🎉 Quest Complete! Check Discord to claim your reward!",
            fg=self.colors["green"]
        )
        
        # Play victory sound
        self._play_victory_sound()
        
        # Auto-exit after 5 seconds
        self.root.after(5000, self._auto_exit)

    def update_colors(self, colors: dict) -> None:
        """Update colors when theme changes with comprehensive mapping.
        
        Args:
            colors: New color dictionary
        """
        print(f"[DummyWindow] update_colors called")
        self.colors = colors
        
        # Comprehensive color mapping for all theme colors
        bg_map = {
            # Mocha theme colors
            "#1e1e2e": colors["base"],
            "#181825": colors["mantle"],
            "#313244": colors["surface"],
            "#45475a": colors["surface0"],
            "#585b70": colors["surface1"],
            "#6c7086": colors["overlay0"],
            "#7f849c": colors["overlay1"],
            "#9399b2": colors["overlay2"],
            # Latte theme colors
            "#eff1f5": colors["base"],
            "#e6e9ef": colors["mantle"],
            "#dcdee5": colors["surface"],
            "#ccd0da": colors["surface0"],
            "#bcc0cc": colors["surface1"],
            "#acb0be": colors["surface2"],
        }
        
        fg_map = {
            # Mocha text colors
            "#cdd6f4": colors["text"],
            "#a6adc8": colors["subtext0"],
            "#bac2de": colors["subtext1"],
            "#f5e0dc": colors["overlay2"],
            # Mocha accent colors
            "#f38ba8": colors["red"],
            "#fab387": colors["peach"],
            "#f9e2af": colors["yellow"],
            "#a6e3a1": colors["green"],
            "#94e2d5": colors["teal"],
            "#89dceb": colors["sky"],
            "#74c7ec": colors["sapphire"],
            "#89b4fa": colors["blue"],
            "#b4befe": colors["lavender"],
            "#cba6f7": colors["mauve"],
            "#f5c2e7": colors["pink"],
            "#f2cdcd": colors["flamingo"],
            # Latte text colors
            "#202231": colors["text"],
            "#4c4f69": colors["subtext0"],
            "#5c5f77": colors["subtext1"],
            # Latte accent colors
            "#d20f39": colors["red"],
            "#fe640b": colors["peach"],
            "#df8e1d": colors["yellow"],
            "#40a02b": colors["green"],
            "#179299": colors["teal"],
            "#04a5e5": colors["sky"],
            "#209fb5": colors["sapphire"],
            "#1e66f5": colors["blue"],
            "#7287fd": colors["lavender"],
            "#8839ef": colors["mauve"],
            "#ea76cb": colors["pink"],
            "#dd7878": colors["flamingo"],
        }
        
        # Recursively update all widgets
        def update_widget(widget):
            try:
                if hasattr(widget, 'config'):
                    # Update background
                    try:
                        current_bg = widget.cget("bg")
                        if current_bg in bg_map:
                            widget.config(bg=bg_map[current_bg])
                    except Exception:
                        pass
                    
                    # Update foreground
                    try:
                        current_fg = widget.cget("fg")
                        if current_fg and current_fg != "" and current_fg in fg_map:
                            widget.config(fg=fg_map[current_fg])
                    except Exception:
                        pass
                
                # Special handling for Canvas items
                if isinstance(widget, tk.Canvas):
                    try:
                        for item_id in widget.find_all():
                            try:
                                item_type = widget.type(item_id)
                                if item_type == "line":
                                    current_fill = widget.itemcget(item_id, "fill")
                                    if current_fill in fg_map:
                                        widget.itemconfig(item_id, fill=fg_map[current_fill])
                                elif item_type == "rectangle":
                                    current_fill = widget.itemcget(item_id, "fill")
                                    if current_fill in bg_map:
                                        widget.itemconfig(item_id, fill=bg_map[current_fill])
                            except Exception:
                                pass
                    except Exception:
                        pass
                
                for child in widget.winfo_children():
                    update_widget(child)
            except Exception:
                pass
        
        # Update specific widgets directly
        self.root.config(bg=colors["base"])
        self.cat_name_label.config(fg=colors["pink"], bg=colors["base"])
        self.animation_frame.config(bg=colors["base"])
        self.animation_label.config(bg=colors["base"])
        self.ground_canvas.config(bg=colors["base"])
        self.ground_canvas.itemconfig(self.ground_line, fill=colors["surface1"])
        self.exe_label.config(fg=colors["subtext0"], bg=colors["base"])
        self.progress_frame.config(bg=colors["base"])
        self.progress_bar.config(bg=colors["mantle"])
        self.progress_bar.itemconfig(self.progress_trough, fill=colors["mantle"])
        self.progress_bar.itemconfig(self.progress_fill, fill=colors["green"])
        self.telemetry_label.config(fg=colors["text"], bg=colors["base"])
        self.status_label.config(fg=colors["subtext0"], bg=colors["base"])
        
        # Recursively update all children
        update_widget(self.root)
        
        print(f"[DummyWindow] update_colors completed")

    def _play_victory_sound(self) -> None:
        """Play victory sound effect based on settings."""
        try:
            # Load alarm settings
            settings_manager = SettingsManager()
            alarm_enabled = settings_manager.get("dummy_alarm_enabled", True)
            
            if not alarm_enabled:
                return  # Don't play sound if alarm is disabled
            
            alarm_type = settings_manager.get("dummy_alarm_type", "default")
            
            if alarm_type == "default":
                # Play default beep sequence
                if winsound:
                    winsound.Beep(880, 200)  # A5 note
                    self.root.after(250, lambda: winsound.Beep(1100, 200))  # C#6 note
                    self.root.after(500, lambda: winsound.Beep(1320, 400))  # E6 note
            else:
                # Play custom sound
                sound_path = settings_manager.get("dummy_alarm_sound_path", "")
                volume = settings_manager.get("dummy_alarm_volume", 100)
                
                if sound_path and os.path.exists(sound_path):
                    # For WAV files, use winsound
                    if sound_path.lower().endswith(".wav") and winsound:
                        try:
                            winsound.PlaySound(sound_path, winsound.SND_FILENAME)
                        except Exception:
                            # Fallback to default
                            if winsound:
                                winsound.Beep(880, 200)
                                self.root.after(250, lambda: winsound.Beep(1100, 200))
                                self.root.after(500, lambda: winsound.Beep(1320, 400))
                    else:
                        # For other formats, try using pygame for volume control
                        try:
                            import pygame
                            pygame.mixer.init()
                            pygame.mixer.music.load(sound_path)
                            pygame.mixer.music.set_volume(volume / 100.0)
                            pygame.mixer.music.play()
                        except ImportError:
                            # Fallback to default beep if pygame not available
                            if winsound:
                                winsound.Beep(880, 200)
                                self.root.after(250, lambda: winsound.Beep(1100, 200))
                                self.root.after(500, lambda: winsound.Beep(1320, 400))
                        except Exception:
                            # Fallback to default beep
                            if winsound:
                                winsound.Beep(880, 200)
                                self.root.after(250, lambda: winsound.Beep(1100, 200))
                                self.root.after(500, lambda: winsound.Beep(1320, 400))
                else:
                    # Fallback to default beep if custom sound not available
                    if winsound:
                        winsound.Beep(880, 200)
                        self.root.after(250, lambda: winsound.Beep(1100, 200))
                        self.root.after(500, lambda: winsound.Beep(1320, 400))
        except Exception as e:
            print(f"Error playing victory sound: {e}")

    def _auto_exit(self) -> None:
        """Auto-exit the dummy window."""
        try:
            self.root.destroy()
        except Exception:
            pass

    def run(self) -> None:
        """Start the dummy window main loop."""
        self.root.mainloop()


def run_dummy_mode(game_exe_name: str, game_name: str = "Unknown", duration_minutes: int = TIMER_DURATION_MINUTES, theme_colors: Optional[Dict] = None, cat_selection: str = "Cat-1") -> None:
    """Run the dummy window with the given executable name.
    
    Args:
        game_exe_name: Name of the game executable to emulate
        game_name: Name of the game
        duration_minutes: Duration of the quest in minutes
        theme_colors: Optional theme colors dictionary to use
        cat_selection: Cat character selection for animations
    """
    dummy = DummyWindow(game_exe_name, game_name, duration_minutes, theme_colors, cat_selection)
    dummy.run()
