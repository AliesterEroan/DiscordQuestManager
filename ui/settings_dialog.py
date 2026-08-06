"""Settings dialog for Discord Quest Manager."""

import tkinter as tk
from tkinter import colorchooser
from tkinter import ttk
from typing import Callable, Dict
import urllib.request
import json
import webbrowser
import logging
import os
import sys

from config.constants import COLORS, WINDOW, FONTS, APP_NAME, APP_VERSION, GITHUB_RELEASES, APP_DATA_FOLDER
from ui.smooth_button import SmoothShadedVectorButton
from core.themes import THEME_REGISTRY

# Setup logging to file
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.dirname(__file__))

# Create data and log folders
data_dir = os.path.join(base_dir, APP_DATA_FOLDER)
log_dir = os.path.join(data_dir, "log")
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, 'debug.log')

# Clear the log file on each launch
if os.path.exists(log_file):
    open(log_file, 'w').close()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()  # Also output to console during development
    ]
)
logger = logging.getLogger(__name__)
logger.info("Settings dialog logging initialized")


def get_contrast_color(hex_color: str) -> str:
    """Calculate high-contrast text color (black or white) for a given hex background."""
    # Remove # if present
    hex_color = hex_color.lstrip('#')
    
    # Parse RGB values
    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
    except (ValueError, IndexError):
        return "#ffffff"  # Default to white for invalid colors
    
    # Calculate luminance (perceived brightness)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    
    # Return black for bright backgrounds, white for dark backgrounds
    return "#000000" if luminance > 0.5 else "#ffffff"


class SettingsDialog:
    """Settings dialog with theme and configuration options."""

    def __init__(self, parent: tk.Tk, settings: Dict, colors: dict, on_save: Callable, on_theme_change: Callable = None, icon_handler=None):
        self.parent = parent
        self.settings = settings.copy()
        self.colors = colors
        self.on_save = on_save
        self.on_theme_change = on_theme_change
        self.icon_handler = icon_handler
        
        self.window = tk.Toplevel(parent)
        self._setup_window()
        self._setup_content()
        
        # Store reference for theme updates
        self.window.settings_dialog = self

    def _setup_window(self) -> None:
        """Configure the window properties."""
        self.window.title(f"{APP_NAME} - Settings")
        self.window.geometry(f"{WINDOW['settings_width']}x700")  # Back to original height
        self.window.resizable(False, False)
        self.window.configure(bg=self.colors["base"])
        self.window.ui_role = "background_main"
        self.window.grab_set()
        
        # Center window on screen
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (WINDOW['settings_width'] // 2)
        y = (self.window.winfo_screenheight() // 2) - (700 // 2)
        self.window.geometry(f"{WINDOW['settings_width']}x700+{x}+{y}")

    def _setup_content(self) -> None:
        """Setup the dialog content."""
        # Create main container frame
        main_container = tk.Frame(self.window, bg=self.colors["base"])
        main_container.ui_role = "background_main"
        main_container.pack(fill="both", expand=True)
        
        # Bind mouse events for window dragging
        main_container.bind("<ButtonPress-1>", self._start_drag)
        main_container.bind("<B1-Motion>", self._on_drag)
        
        # Save button frame for proper layout (outside notebook, in main container)
        button_frame = tk.Frame(main_container, bg=self.colors["base"])
        button_frame.ui_role = "background_main"
        button_frame.pack(side="bottom", fill="x", padx=15, pady=15)
        
        # Separator line (above button frame)
        separator = tk.Frame(main_container, bg=self.colors["surface2"], height=1)
        separator.pack(side="bottom", fill="x", padx=15, pady=(0, 15))
        
        # Button container for Save and Cancel
        btn_container = tk.Frame(button_frame, bg=self.colors["base"])
        btn_container.pack(expand=True)
        
        # Load icons
        save_icon = None
        cancel_icon = None
        if self.icon_handler:
            try:
                save_icon = self.icon_handler.load_ui_icon("save.png", (22, 22), theme="")
                print("Successfully loaded save.png icon")
            except Exception as e:
                print(f"Warning: Failed to load save icon: {e}")
            try:
                cancel_icon = self.icon_handler.load_ui_icon("cancel.png", (22, 22), theme="")
                print("Successfully loaded cancel.png icon")
            except Exception as e:
                print(f"Warning: Failed to load cancel icon: {e}")
        
        # Cancel button (red)
        self.btn_cancel = SmoothShadedVectorButton(
            btn_container,
            text="Cancel",
            icon_name="cancel.png" if cancel_icon else "",
            base_color="#f38ba8",
            dark_color="#8d0000",
            fg_color="#FFFFFF",
            width=120,
            height=40,
            command=self._cancel_settings
        )
        self.btn_cancel.pack(side="left", padx=5)
        
        # Save button
        self.btn_save = SmoothShadedVectorButton(
            btn_container,
            text="Save Settings",
            icon_name="save.png" if save_icon else "",
            base_color="#87CEEB",
            dark_color="#5a9bc4",
            fg_color="#FFFFFF",
            width=150,
            height=40,
            command=self._save_settings
        )
        self.btn_save.pack(side="left", padx=5)
        
        # Configure ttk.Notebook style before creating notebook
        try:
            style = ttk.Style()
            style.theme_use('default')
            style.configure('TNotebook', background=self.colors["base"])
            style.configure('TNotebook.Tab', 
                          background=self.colors["mantle"], 
                          foreground=self.colors["text"],
                          padding=[12, 8])
            style.map('TNotebook.Tab', 
                     background=[('selected', self.colors["surface"])],
                     foreground=[('selected', self.colors["text"])])
        except Exception as e:
            print(f"Warning: Failed to configure ttk.Notebook style: {e}")
        
        # Create notebook for tabbed interface (in main container, not window)
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=(15, 10))
        
        # Theme tab
        try:
            self._setup_theme_tab()
            print("Theme tab added successfully")
        except Exception as e:
            print(f"Error adding Theme tab: {e}")
        
        # Quest tab
        try:
            self._setup_quest_tab()
            print("Quest tab added successfully")
        except Exception as e:
            print(f"Error adding Quest tab: {e}")
        
        # System tab
        try:
            self._setup_system_tab()
            print("System tab added successfully")
        except Exception as e:
            print(f"Error adding System tab: {e}")
        
        # Dummy tab
        try:
            self._setup_dummy_window_tab()
            print("Dummy tab added successfully")
        except Exception as e:
            print(f"Error adding Dummy tab: {e}")
        
        # Updates & About tab
        try:
            self._setup_updates_tab()
            print("Updates tab added successfully")
        except Exception as e:
            print(f"Error adding Updates tab: {e}")

    def _setup_theme_tab(self) -> None:
        """Setup the theme settings tab."""
        tab = tk.Frame(self.notebook, bg=self.colors["base"])
        tab.ui_role = "background_main"
        self.notebook.add(tab, text="Theme")
        
        # Theme Presets Card (directly in tab)
        presets_card = tk.Frame(tab, bg=self.colors["mantle"], relief="flat", bd=0)
        presets_card.pack(fill="x", padx=15, pady=12)
        
        # Card border
        border_frame = tk.Frame(presets_card, bg=self.colors["surface2"], height=1)
        border_frame.pack(side="bottom", fill="x")
        
        # Card header
        lbl_presets = tk.Label(
            presets_card,
            text="Theme Presets",
            font=("Arial", 10, "bold"),
            fg=self.colors["text"],
            bg=self.colors["mantle"]
        )
        lbl_presets.pack(anchor="w", padx=12, pady=(12, 8))
        
        # Theme selection (inside card)
        self.theme_var = tk.StringVar(value=self.settings.get("theme", "mocha"))
        
        # Theme options with icons and color swatches
        themes = [
            (theme_name, theme_data["display_name"])
            for theme_name, theme_data in THEME_REGISTRY.items()
        ]
        
        # Load theme icons
        theme_icons = {}
        if self.icon_handler:
            try:
                theme_icons["mocha"] = self.icon_handler.load_ui_icon("full-moon.png", (16, 16), theme="")
            except Exception:
                theme_icons["mocha"] = None
            try:
                theme_icons["latte"] = self.icon_handler.load_ui_icon("sun.png", (16, 16), theme="")
            except Exception:
                theme_icons["latte"] = None
            try:
                theme_icons["custom"] = self.icon_handler.load_ui_icon("custom.png", (16, 16), theme="")
            except Exception:
                theme_icons["custom"] = None
        
        for theme_value, theme_name in themes:
            theme_row = tk.Frame(presets_card, bg=self.colors["mantle"])
            theme_row.pack(fill="x", padx=12, pady=6)
            
            # Add icon if available
            if theme_value in theme_icons and theme_icons[theme_value]:
                icon_label = tk.Label(theme_row, image=theme_icons[theme_value], bg=self.colors["mantle"])
                icon_label.image = theme_icons[theme_value]
                icon_label.pack(side="left", padx=(0, 8))
            else:
                # Add color swatch only if icon is not available
                swatch_color = THEME_REGISTRY[theme_value]["colors"]["base"] if theme_value in THEME_REGISTRY else self.colors["base"]
                swatch = tk.Frame(theme_row, bg=swatch_color, width=12, height=12, relief="flat", bd=0)
                swatch.pack(side="left", padx=(0, 8))
            
            rb = tk.Radiobutton(
                theme_row,
                text=theme_name,
                variable=self.theme_var,
                value=theme_value,
                font=("Arial", 9),
                fg=self.colors["text"],
                bg=self.colors["mantle"],
                selectcolor=self.colors["surface0"],
                activebackground=self.colors["mantle"],
                command=self._on_theme_change
            )
            rb.pack(side="left")
        
        # Custom Colors Card (hidden by default)
        self.custom_colors_frame = tk.Frame(tab, bg=self.colors["mantle"], relief="flat", bd=0)
        self.custom_colors_frame.pack_propagate(True)  # Allow geometry propagation
        
        # Store reference for geometry updates
        self.colors_container = None
        
        # Card border
        border_frame2 = tk.Frame(self.custom_colors_frame, bg=self.colors["surface2"], height=1)
        border_frame2.pack(side="bottom", fill="x")
        
        # Card header
        lbl_colors = tk.Label(
            self.custom_colors_frame,
            text="Custom Colors",
            font=("Arial", 10, "bold"),
            fg=self.colors["text"],
            bg=self.colors["mantle"]
        )
        lbl_colors.pack(anchor="w", padx=12, pady=(12, 8))
        
        # Scrollable canvas for color pickers
        canvas = tk.Canvas(self.custom_colors_frame, bg=self.colors["mantle"], highlightthickness=0, height=260)
        scrollbar = ttk.Scrollbar(self.custom_colors_frame, orient="vertical", command=canvas.yview)
        colors_container = tk.Frame(canvas, bg=self.colors["mantle"])
        
        # Bind Configure event to update scrollregion and canvas window width
        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig("inner", width=canvas.winfo_width())
        
        colors_container.bind("<Configure>", on_configure)
        
        canvas.create_window((0, 0), window=colors_container, anchor="nw", tags="inner")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=12, pady=8)
        scrollbar.pack(side="right", fill="y", pady=8)
        
        # Store reference for geometry updates
        self.colors_container = colors_container
        self.canvas = canvas
        
        # Add color pickers
        self.color_vars = {}
        # Load default colors from mocha.json
        import json
        import os
        mocha_file = os.path.join(os.path.dirname(__file__), "..", "core", "themes", "mocha.json")
        mocha_colors = {}
        try:
            with open(mocha_file, "r") as f:
                theme_data = json.load(f)
                mocha_colors = theme_data.get("colors", {})
        except Exception as e:
            logger.error(f"Failed to load mocha.json: {e}")
            mocha_colors = {"base": self.colors["base"], "mantle": self.colors["mantle"]}
        
        for color_key in list(mocha_colors.keys())[:10]:
            try:
                logger.debug(f"Building row for: {color_key}")
                
                # Ensure safe hex color default
                default_color = mocha_colors.get(color_key, self.colors["base"])
                if not default_color.startswith("#") or len(default_color) != 7:
                    default_color = self.colors["base"]
                    logger.debug(f"Invalid color for {color_key}, using default")
                
                # Create row frame and pack it explicitly
                color_row = tk.Frame(colors_container, bg=self.colors["mantle"])
                color_row.pack(fill="x", pady=2)
                
                # Label - pack explicitly
                label = tk.Label(
                    color_row,
                    text=color_key.replace("_", " ").capitalize() + ":",
                    font=("Arial", 9),
                    fg=self.colors["text"],
                    bg=self.colors["mantle"],
                    width=15,
                    anchor="w"
                )
                label.pack(side="left", anchor="w")
                
                color_var = tk.StringVar(value=self.colors.get(color_key, default_color))
                self.color_vars[color_key] = color_var
                
                # Get current color for styling
                current_color = self.colors.get(color_key, default_color)
                text_color = get_contrast_color(current_color)
                
                # Hex entry field with color swatch background
                entry_key = f"{color_key}_entry"
                entry = tk.Entry(
                    color_row,
                    textvariable=color_var,
                    font=("Arial", 9),
                    bg=current_color,
                    fg=text_color,
                    insertbackground=text_color,
                    relief="flat",
                    bd=0,
                    highlightthickness=1,
                    highlightbackground=self.colors["surface1"],
                    highlightcolor=self.colors["blue"],
                    width=10,
                    justify="center"
                )
                entry.pack(side="right")
                
                # Make entry clickable to open color picker
                entry.bind("<Button-1>", lambda e, k=color_key: self._pick_color(k))
                
                # Store entry reference for color updates
                self.color_vars[entry_key] = entry
                
                logger.debug(f"Successfully built row for: {color_key}")
                
            except Exception as e:
                logger.error(f"Failed building row for {color_key}: {e}")
                import traceback
                logger.error(traceback.format_exc())
        
        # Force geometry recalculation after all rows are packed
        colors_container.update_idletasks()
        
        # Update canvas scrollregion and window width
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.itemconfig("inner", width=self.canvas.winfo_width())
        self.canvas.update_idletasks()
        
        # Initially hide custom colors unless custom theme is selected
        self._on_theme_change()

    def _on_theme_change(self) -> None:
        """Handle theme selection change."""
        selected_theme = self.theme_var.get()
        
        # Show/hide custom colors frame
        if selected_theme == "custom":
            self.custom_colors_frame.pack(fill="x", padx=15, pady=(0, 12))
            # Update canvas geometry when showing custom colors
            if hasattr(self, 'canvas'):
                self.canvas.update_idletasks()
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                self.canvas.itemconfig("inner", width=self.canvas.winfo_width())
        else:
            self.custom_colors_frame.pack_forget()
        
        # Trigger theme change for preview
        if self.on_theme_change:
            if selected_theme == "custom":
                custom_colors = {}
                # Load mocha colors from JSON as defaults
                import json
                import os
                mocha_file = os.path.join(os.path.dirname(__file__), "..", "core", "themes", "mocha.json")
                mocha_colors = {}
                try:
                    with open(mocha_file, "r") as f:
                        theme_data = json.load(f)
                        mocha_colors = theme_data.get("colors", {})
                except Exception as e:
                    logger.error(f"Failed to load mocha.json: {e}")
                    mocha_colors = {"base": self.colors["base"], "mantle": self.colors["mantle"]}
                
                for color_key in mocha_colors.keys():
                    custom_colors[color_key] = self.settings.get(f"custom_{color_key}", mocha_colors.get(color_key, self.colors["base"]))
                self.on_theme_change(selected_theme, custom_colors)
            else:
                self.on_theme_change(selected_theme, None)

    def _pick_color(self, color_key: str) -> None:
        """Open color picker dialog."""
        from tkinter import colorchooser
        current_color = self.color_vars[color_key].get()
        logger.info(f"Opening color picker for {color_key}, current color: {current_color}")
        
        color = colorchooser.askcolor(
            initialcolor=current_color,
            title=f"Choose {color_key.capitalize()} Color",
            parent=self.window
        )
        
        logger.info(f"Color picker returned: {color}")
        
        if color[1]:
            logger.info(f"Setting {color_key} to {color[1]}")
            self.color_vars[color_key].set(color[1])
            # Update entry styling with new color
            entry_key = f"{color_key}_entry"
            if entry_key in self.color_vars:
                entry = self.color_vars[entry_key]
                text_color = get_contrast_color(color[1])
                entry.config(bg=color[1], fg=text_color, insertbackground=text_color)
            
            # Trigger real-time theme preview for custom theme
            if self.theme_var.get() == "custom" and self.on_theme_change:
                logger.info("Triggering real-time theme preview")
                custom_colors = {}
                # Load mocha colors from JSON as defaults
                import json
                import os
                mocha_file = os.path.join(os.path.dirname(__file__), "..", "core", "themes", "mocha.json")
                mocha_colors = {}
                try:
                    with open(mocha_file, "r") as f:
                        theme_data = json.load(f)
                        mocha_colors = theme_data.get("colors", {})
                except Exception as e:
                    logger.error(f"Failed to load mocha.json: {e}")
                    mocha_colors = {"base": self.colors["base"], "mantle": self.colors["mantle"]}
                
                for key in mocha_colors.keys():
                    custom_colors[key] = self.color_vars[key].get()
                logger.info(f"Calling on_theme_change with {len(custom_colors)} colors")
                self.on_theme_change("custom", custom_colors)
            else:
                logger.warning(f"Theme not custom or no on_theme_change callback. Theme: {self.theme_var.get()}, Callback: {self.on_theme_change}")

    def _setup_quest_tab(self) -> None:
        """Setup the quest settings tab."""
        tab = tk.Frame(self.notebook, bg=self.colors["base"])
        tab.ui_role = "background_main"
        self.notebook.add(tab, text="Quest")
        
        # Duration Settings Card
        duration_card = tk.Frame(tab, bg=self.colors["mantle"], relief="flat", bd=0)
        duration_card.pack(fill="x", padx=15, pady=12)
        
        # Card border
        border_frame1 = tk.Frame(duration_card, bg=self.colors["surface2"], height=1)
        border_frame1.pack(side="bottom", fill="x")
        
        # Card header
        lbl_duration_header = tk.Label(
            duration_card,
            text="Duration Settings",
            font=("Arial", 10, "bold"),
            fg=self.colors["text"],
            bg=self.colors["mantle"]
        )
        lbl_duration_header.pack(anchor="w", padx=12, pady=(12, 8))
        
        # Duration label
        lbl_duration = tk.Label(
            duration_card,
            text="Quest Duration (minutes)",
            font=("Arial", 9),
            fg=self.colors["text"],
            bg=self.colors["mantle"]
        )
        lbl_duration.pack(anchor="w", padx=12, pady=(0, 6))
        
        # Segment bar for duration presets
        frame_presets = tk.Frame(duration_card, bg=self.colors["mantle"])
        frame_presets.pack(fill="x", padx=12, pady=(0, 8))
        
        self.duration_buttons = {}
        for i, minutes in enumerate([5, 10, 15, 30]):
            btn = tk.Button(
                frame_presets,
                text=str(minutes),
                font=("Arial", 9),
                bg="#45475a",
                fg="#cdd6f4",
                command=lambda m=minutes: self._set_duration(m),
                width=6,
                relief="flat",
                bd=0,
                cursor="hand2"
            )
            self.duration_buttons[minutes] = btn
            btn.pack(side="left", padx=(0 if i == 0 else 1, 1 if i < 3 else 0))
        
        # Custom input
        self.duration_var = tk.StringVar(value=str(self.settings.get("custom_duration", 15)))
        ent_duration = tk.Entry(
            frame_presets,
            textvariable=self.duration_var,
            font=("Arial", 9),
            bg="#313244",
            fg="#cdd6f4",
            insertbackground="white",
            relief="flat",
            bd=0,
            highlightthickness=0,
            width=8,
        )
        ent_duration.pack(side="left", padx=5)
        
        # Remember duration checkbox
        self.remember_duration_var = tk.BooleanVar(
            value=self.settings.get("remember_duration", True)
        )
        cb_remember = tk.Checkbutton(
            duration_card,
            text="Remember last used duration",
            variable=self.remember_duration_var,
            font=("Arial", 9),
            fg=self.colors["text"],
            bg=self.colors["mantle"],
            selectcolor=self.colors["surface0"],
            activebackground=self.colors["mantle"],
        )
        cb_remember.pack(anchor="w", padx=12, pady=(8, 12))
        
        # Concurrency Limits Card
        concurrency_card = tk.Frame(tab, bg=self.colors["mantle"], relief="flat", bd=0)
        concurrency_card.pack(fill="x", padx=15, pady=(0, 12))
        
        # Card border
        border_frame2 = tk.Frame(concurrency_card, bg=self.colors["surface2"], height=1)
        border_frame2.pack(side="bottom", fill="x")
        
        # Card header
        lbl_concurrency_header = tk.Label(
            concurrency_card,
            text="Concurrency Limits",
            font=("Arial", 10, "bold"),
            fg=self.colors["text"],
            bg=self.colors["mantle"]
        )
        lbl_concurrency_header.pack(anchor="w", padx=12, pady=(12, 8))
        
        # Multi-quest limit label
        lbl_multi = tk.Label(
            concurrency_card,
            text="Maximum simultaneous quests",
            font=("Arial", 9),
            fg=self.colors["text"],
            bg=self.colors["mantle"]
        )
        lbl_multi.pack(anchor="w", padx=12, pady=(0, 6))
        
        # Helper text
        tk.Label(
            concurrency_card,
            text="Set how many quests can run at the same time (0 = unlimited)",
            font=("Arial", 8),
            fg=self.colors["subtext0"],
            bg=self.colors["mantle"]
        ).pack(anchor="w", padx=12, pady=(0, 8))
        
        # Multi-quest input with preset buttons
        frame_multi = tk.Frame(concurrency_card, bg=self.colors["mantle"])
        frame_multi.pack(fill="x", padx=12, pady=(0, 8))
        
        self.multi_quest_buttons = {}
        for i, limit in enumerate([1, 2, 3, 5]):
            btn = tk.Button(
                frame_multi,
                text=str(limit),
                font=("Arial", 9),
                bg="#45475a",
                fg="#cdd6f4",
                command=lambda l=limit: self._set_multi_quest(l),
                width=6,
                relief="flat",
                bd=0,
                cursor="hand2"
            )
            self.multi_quest_buttons[limit] = btn
            btn.pack(side="left", padx=(0 if i == 0 else 1, 1 if i < 3 else 0))
        
        # Unlimited button
        btn_unlimited = tk.Button(
            frame_multi,
            text="∞",
            font=("Arial", 9),
            bg="#45475a",
            fg="#cdd6f4",
            command=lambda: self._set_multi_quest(0),
            width=6,
            relief="flat",
            bd=0,
            cursor="hand2"
        )
        self.multi_quest_buttons[0] = btn_unlimited
        btn_unlimited.pack(side="left", padx=1)
        
        # Custom input
        self.multi_quest_var = tk.IntVar(value=self.settings.get("multi_quest_limit", 3))
        ent_multi = tk.Entry(
            frame_multi,
            textvariable=self.multi_quest_var,
            font=("Arial", 9),
            bg="#313244",
            fg="#cdd6f4",
            insertbackground="white",
            relief="flat",
            bd=0,
            highlightthickness=0,
            width=8,
        )
        ent_multi.pack(side="left", padx=5)
        
        # Update button states
        self._update_duration_buttons()
        self._update_multi_quest_buttons()
        
        # Bind variable changes to update button states
        self.duration_var.trace_add("write", lambda *args: self._update_duration_buttons())
        self.multi_quest_var.trace_add("write", lambda *args: self._update_multi_quest_buttons())

    def _update_duration_buttons(self) -> None:
        """Update duration button states based on current value."""
        try:
            current = int(self.duration_var.get())
            for minutes, btn in self.duration_buttons.items():
                if minutes == current:
                    btn.config(bg="#89b4fa", fg="#1e1e2e")
                else:
                    btn.config(bg="#45475a", fg="#cdd6f4")
        except ValueError:
            pass

    def _update_multi_quest_buttons(self) -> None:
        """Update multi-quest button states based on current value."""
        current = self.multi_quest_var.get()
        for limit, btn in self.multi_quest_buttons.items():
            if limit == current:
                btn.config(bg="#89b4fa", fg="#1e1e2e")
            else:
                btn.config(bg="#45475a", fg="#cdd6f4")

    def _setup_system_tab(self) -> None:
        """Setup the system settings tab."""
        tab = tk.Frame(self.notebook, bg=self.colors["base"])
        tab.ui_role = "background_main"
        self.notebook.add(tab, text="System")
        
        # System & Tray Card
        system_card = tk.Frame(tab, bg=self.colors["mantle"], relief="flat", bd=0)
        system_card.pack(fill="x", padx=15, pady=12)
        
        # Card border
        border_frame = tk.Frame(system_card, bg=self.colors["surface2"], height=1)
        border_frame.pack(side="bottom", fill="x")
        
        # Card header
        lbl_system_header = tk.Label(
            system_card,
            text="System & Tray",
            font=("Arial", 10, "bold"),
            fg=self.colors["text"],
            bg=self.colors["mantle"]
        )
        lbl_system_header.pack(anchor="w", padx=12, pady=(12, 8))
        
        # Minimize to tray
        self.minimize_to_tray_var = tk.BooleanVar(
            value=self.settings.get("minimize_to_tray", False)
        )
        cb = tk.Checkbutton(
            system_card,
            text="Minimize to system tray",
            variable=self.minimize_to_tray_var,
            font=("Arial", 9),
            fg=self.colors["text"],
            bg=self.colors["mantle"],
            selectcolor=self.colors["surface0"],
            activebackground=self.colors["mantle"],
        )
        cb.pack(anchor="w", padx=12, pady=6)
        
        # Auto clean on exit
        self.auto_clean_var = tk.BooleanVar(
            value=self.settings.get("auto_clean_on_exit", True)
        )
        cb2 = tk.Checkbutton(
            system_card,
            text="Auto-clean dummy files on exit",
            variable=self.auto_clean_var,
            font=("Arial", 9),
            fg=self.colors["text"],
            bg=self.colors["mantle"],
            selectcolor=self.colors["surface0"],
            activebackground=self.colors["mantle"],
        )
        cb2.pack(anchor="w", padx=12, pady=6)
        
        # Discord auto-open
        self.discord_auto_open_var = tk.BooleanVar(
            value=self.settings.get("discord_auto_open", True)
        )
        cb3 = tk.Checkbutton(
            system_card,
            text="Offer to open Discord if not running",
            variable=self.discord_auto_open_var,
            font=("Arial", 9),
            fg=self.colors["text"],
            bg=self.colors["mantle"],
            selectcolor=self.colors["surface0"],
            activebackground=self.colors["mantle"],
        )
        cb3.pack(anchor="w", padx=12, pady=(6, 12))
        
        # EXE Creation Path
        tk.Label(
            system_card,
            text="Default EXE creation path",
            font=("Arial", 9),
            fg=self.colors["text"],
            bg=self.colors["mantle"]
        ).pack(anchor="w", padx=12, pady=(6, 2))
        
        tk.Label(
            system_card,
            text="Leave empty to use app directory",
            font=("Arial", 8),
            fg=self.colors["subtext0"],
            bg=self.colors["mantle"]
        ).pack(anchor="w", padx=12, pady=(0, 6))
        
        self.exe_path_var = tk.StringVar(value=self.settings.get("exe_creation_path", ""))
        
        path_frame = tk.Frame(system_card, bg=self.colors["mantle"])
        path_frame.pack(fill="x", padx=12, pady=(0, 12))
        
        self.ent_exe_path = tk.Entry(
            path_frame,
            textvariable=self.exe_path_var,
            font=("Arial", 9),
            bg="#313244",
            fg="#cdd6f4",
            insertbackground="white",
            relief="flat",
            bd=0,
            highlightthickness=0,
        )
        self.ent_exe_path.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        btn_browse_path = tk.Button(
            path_frame,
            text="Browse",
            command=self._browse_exe_path,
            bg="#45475a",
            fg="#cdd6f4",
            font=("Arial", 9),
            relief="flat",
            cursor="hand2"
        )
        btn_browse_path.pack(side="right")
        
        # Data Folder Path
        tk.Label(
            system_card,
            text="Data folder location",
            font=("Arial", 9),
            fg=self.colors["text"],
            bg=self.colors["mantle"]
        ).pack(anchor="w", padx=12, pady=(6, 2))
        
        tk.Label(
            system_card,
            text="Where settings, favorites, and data are stored",
            font=("Arial", 8),
            fg=self.colors["subtext0"],
            bg=self.colors["mantle"]
        ).pack(anchor="w", padx=12, pady=(0, 6))
        
        self.data_path_var = tk.StringVar(value=self.settings.get("data_folder_path", ""))
        
        data_path_frame = tk.Frame(system_card, bg=self.colors["mantle"])
        data_path_frame.pack(fill="x", padx=12, pady=(0, 12))
        
        self.ent_data_path = tk.Entry(
            data_path_frame,
            textvariable=self.data_path_var,
            font=("Arial", 9),
            bg="#313244",
            fg="#cdd6f4",
            insertbackground="white",
            relief="flat",
            bd=0,
        )
        self.ent_data_path.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        btn_browse_data_path = tk.Button(
            data_path_frame,
            text="Browse",
            command=self._browse_data_path,
            bg="#45475a",
            fg="#cdd6f4",
            font=("Arial", 9),
            relief="flat",
            cursor="hand2"
        )
        btn_browse_data_path.pack(side="right")

    def _setup_dummy_window_tab(self) -> None:
        """Setup the dummy window settings tab."""
        tab = tk.Frame(self.notebook, bg=self.colors["base"])
        tab.ui_role = "background_main"
        self.notebook.add(tab, text="Dummy")
        
        # Cat Selection Card
        cat_card = tk.Frame(tab, bg=self.colors["mantle"], relief="flat", bd=0)
        cat_card.pack(fill="x", padx=15, pady=12)
        
        # Card border
        border_frame1 = tk.Frame(cat_card, bg=self.colors["surface2"], height=1)
        border_frame1.pack(side="bottom", fill="x")
        
        # Card header
        lbl_cat_header = tk.Label(
            cat_card,
            text="Cat Animation",
            font=("Arial", 10, "bold"),
            fg=self.colors["text"],
            bg=self.colors["mantle"]
        )
        lbl_cat_header.pack(anchor="w", padx=12, pady=(12, 8))
        
        # Cat selection label
        lbl_cat = tk.Label(
            cat_card,
            text="Select cat character for dummy windows",
            font=("Arial", 9),
            fg=self.colors["text"],
            bg=self.colors["mantle"]
        )
        lbl_cat.pack(anchor="w", padx=12, pady=(0, 6))
        
        # Cat selection with radio buttons and PNG icons in 2x3 grid
        cat_options = ["Chestnut", "Midnight", "Misty", "Pebble", "Fluffy", "Salva"]
        cat_internal_names = ["Cat-1", "Cat-2", "Cat-3", "Cat-4", "Cat-5", "Cat-6"]
        self.cat_display_to_internal = dict(zip(cat_options, cat_internal_names))
        self.cat_internal_to_display = dict(zip(cat_internal_names, cat_options))
        
        # Get current cat selection and convert to display name
        cat_internal = self.settings.get("dummy_cat_selection", "Cat-1")
        cat_display = self.cat_internal_to_display.get(cat_internal, "Chestnut")
        self.cat_var = tk.StringVar(value=cat_display)
        
        cat_radio_frame = tk.Frame(cat_card, bg=self.colors["mantle"])
        cat_radio_frame.pack(fill="x", padx=12, pady=(0, 12))
        
        # Create grid layout (2 columns, 3 rows)
        for i, cat_name in enumerate(cat_options):
            row = i // 2
            col = i % 2
            
            cat_cell = tk.Frame(cat_radio_frame, bg=self.colors["mantle"])
            cat_cell.grid(row=row, column=col, padx=5, pady=5, sticky="w")
            
            # Radio button
            rb = tk.Radiobutton(
                cat_cell,
                variable=self.cat_var,
                value=cat_name,
                font=("Arial", 9),
                fg=self.colors["text"],
                bg=self.colors["mantle"],
                selectcolor=self.colors["surface0"],
                activebackground=self.colors["mantle"],
                indicatoron=True,
                highlightthickness=0
            )
            rb.pack(side="left", padx=(0, 5))
            
            # Load cat PNG from assets/animations/cat
            cat_icon = None
            try:
                import os
                from PIL import Image, ImageTk
                
                # Get correct path to cat icons
                base_dir = os.path.dirname(os.path.dirname(__file__))
                cat_icon_path = os.path.join(base_dir, "assets", "animations", "cat", f"Cat-{i+1}.png")
                
                if os.path.exists(cat_icon_path):
                    img = Image.open(cat_icon_path)
                    img = img.resize((48, 48), Image.Resampling.LANCZOS)
                    cat_icon = ImageTk.PhotoImage(img)
            except Exception:
                pass
            
            # Cat name label with icon
            if cat_icon:
                cat_name_label = tk.Label(
                    cat_cell,
                    image=cat_icon,
                    text=cat_name,
                    compound="left",
                    font=("Arial", 9),
                    fg=self.colors["text"],
                    bg=self.colors["mantle"]
                )
                cat_name_label.image = cat_icon
                cat_name_label.pack(side="left")
            else:
                cat_name_label = tk.Label(
                    cat_cell,
                    text=cat_name,
                    font=("Arial", 9),
                    fg=self.colors["text"],
                    bg=self.colors["mantle"]
                )
                cat_name_label.pack(side="left")
            
            # Store internal name for mapping
            cat_cell.internal_name = cat_internal_names[i]
        
        # Alarm Settings Card
        alarm_card = tk.Frame(tab, bg=self.colors["mantle"], relief="flat", bd=0)
        alarm_card.pack(fill="x", padx=15, pady=(0, 12))
        
        # Card border
        border_frame2 = tk.Frame(alarm_card, bg=self.colors["surface2"], height=1)
        border_frame2.pack(side="bottom", fill="x")
        
        # Card header
        lbl_alarm_header = tk.Label(
            alarm_card,
            text="Alarm Sound",
            font=("Arial", 10, "bold"),
            fg=self.colors["text"],
            bg=self.colors["mantle"]
        )
        lbl_alarm_header.pack(anchor="w", padx=12, pady=(12, 8))
        
        # Alarm ON/OFF toggle button
        self.alarm_enabled_var = tk.BooleanVar(value=self.settings.get("dummy_alarm_enabled", True))
        
        alarm_toggle_frame = tk.Frame(alarm_card, bg=self.colors["mantle"])
        alarm_toggle_frame.pack(fill="x", padx=12, pady=(0, 8))
        
        # Load alarm icons from assets/icons
        alarm_disabled_icon = None
        alarm_ringing_icon = None
        if self.icon_handler:
            try:
                alarm_disabled_icon = self.icon_handler.load_ui_icon("alarm_disabled.png", (32, 32), theme="")
                alarm_ringing_icon = self.icon_handler.load_ui_icon("alarm_ringing.png", (32, 32), theme="")
            except Exception:
                pass
        
        # Alarm ON/OFF toggle button (icon only)
        self.alarm_toggle_btn = tk.Button(
            alarm_toggle_frame,
            image=alarm_ringing_icon if self.alarm_enabled_var.get() else alarm_disabled_icon,
            command=self._toggle_alarm_enabled,
            bg=self.colors["mantle"],
            relief="flat",
            cursor="hand2",
            bd=0,
            highlightthickness=0
        )
        if alarm_disabled_icon:
            self.alarm_toggle_btn.image_disabled = alarm_disabled_icon
        if alarm_ringing_icon:
            self.alarm_toggle_btn.image_ringing = alarm_ringing_icon
        self.alarm_toggle_btn.pack(anchor="center")
        
        # Alarm type radio buttons (default/custom)
        self.alarm_type_var = tk.StringVar(value=self.settings.get("dummy_alarm_type", "default"))
        
        alarm_type_frame = tk.Frame(alarm_card, bg=self.colors["mantle"])
        alarm_type_frame.pack(fill="x", padx=12, pady=(0, 8))
        
        rb_default = tk.Radiobutton(
            alarm_type_frame,
            text="Default beep",
            variable=self.alarm_type_var,
            value="default",
            font=("Arial", 9),
            fg=self.colors["text"],
            bg=self.colors["mantle"],
            selectcolor=self.colors["surface0"],
            activebackground=self.colors["mantle"],
            command=self._on_alarm_type_change
        )
        rb_default.pack(anchor="w", pady=2)
        
        rb_custom = tk.Radiobutton(
            alarm_type_frame,
            text="Custom sound",
            variable=self.alarm_type_var,
            value="custom",
            font=("Arial", 9),
            fg=self.colors["text"],
            bg=self.colors["mantle"],
            selectcolor=self.colors["surface0"],
            activebackground=self.colors["mantle"],
            command=self._on_alarm_type_change
        )
        rb_custom.pack(anchor="w", pady=2)
        
        # Custom sound file picker
        self.alarm_sound_path_var = tk.StringVar(value=self.settings.get("dummy_alarm_sound_path", ""))
        
        sound_frame = tk.Frame(alarm_card, bg=self.colors["mantle"])
        sound_frame.pack(fill="x", padx=12, pady=(0, 8))
        
        self.ent_sound_path = tk.Entry(
            sound_frame,
            textvariable=self.alarm_sound_path_var,
            font=("Arial", 9),
            bg="#313244",
            fg="#cdd6f4",
            insertbackground="white",
            relief="flat",
            bd=0,
            highlightthickness=0,
            state="disabled" if self.alarm_type_var.get() == "default" else "normal"
        )
        self.ent_sound_path.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        btn_browse = tk.Button(
            sound_frame,
            text="Browse",
            command=self._browse_alarm_sound,
            font=("Arial", 9),
            bg="#45475a",
            fg="#cdd6f4",
            relief="flat",
            cursor="hand2",
            state="disabled" if self.alarm_type_var.get() == "default" else "normal"
        )
        btn_browse.pack(side="left")
        
        # Volume control with icon button - centered
        vol_frame = tk.Frame(alarm_card, bg=self.colors["mantle"])
        vol_frame.pack(fill="x", padx=12, pady=(0, 8))
        
        lbl_vol = tk.Label(
            vol_frame,
            text="Volume:",
            font=("Arial", 9),
            fg=self.colors["text"],
            bg=self.colors["mantle"]
        )
        lbl_vol.pack(side="left", padx=(0, 8))
        
        # Load volume icon
        volume_icon = None
        if self.icon_handler:
            try:
                volume_icon = self.icon_handler.load_ui_icon("volume.png", (20, 20), theme="")
            except Exception:
                pass
        
        self.volume_var = tk.IntVar(value=self.settings.get("dummy_alarm_volume", 100))
        
        # Volume display label
        self.vol_display = tk.Label(
            vol_frame,
            text=f"{self.volume_var.get()}%",
            font=("Arial", 9),
            fg=self.colors["text"],
            bg=self.colors["mantle"],
            width=5
        )
        self.vol_display.pack(side="left", padx=(0, 8))
        
        # Volume increase button
        btn_vol_up = tk.Button(
            vol_frame,
            text="+",
            font=("Arial", 10, "bold"),
            bg="#45475a",
            fg="#cdd6f4",
            relief="flat",
            cursor="hand2",
            width=3,
            command=lambda: self._adjust_volume(10)
        )
        btn_vol_up.pack(side="left", padx=2)
        
        # Volume decrease button
        btn_vol_down = tk.Button(
            vol_frame,
            text="-",
            font=("Arial", 10, "bold"),
            bg="#45475a",
            fg="#cdd6f4",
            relief="flat",
            cursor="hand2",
            width=3,
            command=lambda: self._adjust_volume(-10)
        )
        btn_vol_down.pack(side="left", padx=2)
        
        # Load volume icon for test button
        volume_icon = None
        if self.icon_handler:
            try:
                volume_icon = self.icon_handler.load_ui_icon("volume.png", (16, 16), theme="")
            except Exception:
                pass
        
        # Test sound button - just icon with text
        if volume_icon:
            btn_test = tk.Button(
                vol_frame,
                image=volume_icon,
                command=self._test_alarm_sound,
                bg="#a6e3a1",
                fg="#1e1e2e",
                relief="flat",
                cursor="hand2"
            )
            btn_test.image = volume_icon
            btn_test.pack(side="left", padx=(10, 2))
        
        # Test sound text label
        lbl_test = tk.Label(
            vol_frame,
            text="Test Sound",
            font=("Arial", 9),
            fg=self.colors["text"],
            bg=self.colors["mantle"],
            cursor="hand2"
        )
        lbl_test.pack(side="left", padx=(0, 5))
        # Make label clickable
        lbl_test.bind("<Button-1>", lambda e: self._test_alarm_sound())
        
        # Center the volume controls
        vol_frame.pack(anchor="center")

    def _on_alarm_type_change(self) -> None:
        """Handle alarm type radio button change."""
        is_custom = self.alarm_type_var.get() == "custom"
        self.ent_sound_path.config(state="normal" if is_custom else "disabled")
        # Find and update browse button state
        for widget in self.ent_sound_path.master.winfo_children():
            if isinstance(widget, tk.Button) and widget.cget("text") == "Browse":
                widget.config(state="normal" if is_custom else "disabled")
                break
    
    def _toggle_alarm_enabled(self) -> None:
        """Toggle alarm ON/OFF."""
        current_state = self.alarm_enabled_var.get()
        new_state = not current_state
        self.alarm_enabled_var.set(new_state)
        
        # Update button icon
        if new_state:
            self.alarm_toggle_btn.config(image=self.alarm_toggle_btn.image_ringing)
        else:
            self.alarm_toggle_btn.config(image=self.alarm_toggle_btn.image_disabled)
    
    def _adjust_volume(self, delta: int) -> None:
        """Adjust volume by delta amount."""
        current_vol = self.volume_var.get()
        new_vol = max(0, min(100, current_vol + delta))
        self.volume_var.set(new_vol)
        self.vol_display.config(text=f"{new_vol}%")

    def _browse_alarm_sound(self) -> None:
        """Browse for custom alarm sound file."""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Select Alarm Sound",
            filetypes=[
                ("Audio Files", "*.wav *.mp3 *.ogg *.flac"),
                ("WAV Files", "*.wav"),
                ("MP3 Files", "*.mp3"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            self.alarm_sound_path_var.set(file_path)

    def _browse_exe_path(self) -> None:
        """Browse for default EXE creation path."""
        from tkinter import filedialog
        folder_path = filedialog.askdirectory(title="Select Default EXE Creation Path")
        if folder_path:
            self.exe_path_var.set(folder_path)

    def _browse_data_path(self) -> None:
        """Browse for data folder location."""
        from tkinter import filedialog
        folder_path = filedialog.askdirectory(title="Select Data Folder Location")
        if folder_path:
            self.data_path_var.set(folder_path)

    def _test_alarm_sound(self) -> None:
        """Test the alarm sound."""
        try:
            try:
                import winsound
            except ImportError:
                winsound = None
            
            if self.alarm_type_var.get() == "default":
                # Play default beep sequence
                if winsound:
                    winsound.Beep(880, 200)
                    self.window.after(250, lambda: winsound.Beep(1100, 200))
                    self.window.after(500, lambda: winsound.Beep(1320, 400))
            else:
                # Play custom sound
                sound_path = self.alarm_sound_path_var.get()
                if sound_path and os.path.exists(sound_path):
                    if sound_path.lower().endswith(".wav") and winsound:
                        winsound.PlaySound(sound_path, winsound.SND_FILENAME)
                    else:
                        # For non-WAV files, try using pygame if available
                        try:
                            import pygame
                            pygame.mixer.init()
                            pygame.mixer.music.load(sound_path)
                            volume = self.volume_var.get() / 100.0
                            pygame.mixer.music.set_volume(volume)
                            pygame.mixer.music.play()
                        except ImportError:
                            # Fallback to default beep if pygame not available
                            if winsound:
                                winsound.Beep(880, 200)
                                self.window.after(250, lambda: winsound.Beep(1100, 200))
                                self.window.after(500, lambda: winsound.Beep(1320, 400))
                else:
                    # No custom sound set, play default
                    if winsound:
                        winsound.Beep(880, 200)
                        self.window.after(250, lambda: winsound.Beep(1100, 200))
                        self.window.after(500, lambda: winsound.Beep(1320, 400))
        except Exception as e:
            print(f"Error testing alarm sound: {e}")

    def _setup_updates_tab(self) -> None:
        """Setup the updates & about settings tab."""
        tab = tk.Frame(self.notebook, bg=self.colors["base"])
        tab.ui_role = "background_main"
        self.notebook.add(tab, text="About")
        
        # About Hero Card (TOP)
        about_card = tk.Frame(tab, bg=self.colors["mantle"], relief="flat", bd=0)
        about_card.pack(fill="x", padx=15, pady=12)
        
        # Card border
        border_frame1 = tk.Frame(about_card, bg=self.colors["surface2"], height=1)
        border_frame1.pack(side="bottom", fill="x")
        
        # Card header
        lbl_about_header = tk.Label(
            about_card,
            text="About",
            font=("Arial", 10, "bold"),
            fg=self.colors["text"],
            bg=self.colors["mantle"]
        )
        lbl_about_header.pack(anchor="w", padx=12, pady=(12, 8))
        
        # App title
        lbl_title = tk.Label(
            about_card,
            text="Discord Quest Manager",
            font=("Arial", 14, "bold"),
            fg=self.colors["pink"],
            bg=self.colors["mantle"]
        )
        lbl_title.pack(anchor="center", pady=8)
        
        # App description
        lbl_desc = tk.Label(
            about_card,
            text="A tool to manage Discord quest playtime",
            font=("Arial", 9),
            fg=self.colors["subtext0"],
            bg=self.colors["mantle"]
        )
        lbl_desc.pack(anchor="center", pady=(0, 8))
        
        # GitHub icon (big and centered)
        github_icon = None
        if self.icon_handler:
            try:
                github_icon = self.icon_handler.load_ui_icon("github.png", (64, 64), theme="")
            except Exception:
                pass
        
        if github_icon:
            github_btn = tk.Button(
                about_card,
                image=github_icon,
                command=lambda: webbrowser.open(GITHUB_RELEASES),
                bg=self.colors["mantle"],
                fg=self.colors["text"],
                relief="flat",
                cursor="hand2",
                activebackground=self.colors["surface0"]
            )
            github_btn.image = github_icon
            github_btn.pack(anchor="center", pady=8)
            
            tk.Label(
                about_card,
                text="Click to check releases",
                font=("Arial", 8),
                fg=self.colors["subtext0"],
                bg=self.colors["mantle"],
                cursor="hand2"
            ).pack(anchor="center", pady=(0, 12))
        else:
            # Fallback to text if icon fails
            tk.Label(
                about_card,
                text=f"GitHub: {GITHUB_RELEASES}",
                font=("Arial", 9),
                fg=self.colors["blue"],
                bg=self.colors["mantle"],
                cursor="hand2",
                wraplength=340
            ).pack(anchor="center", pady=8)
        
        # Updates Card (BOTTOM)
        updates_card = tk.Frame(tab, bg=self.colors["mantle"], relief="flat", bd=0)
        updates_card.pack(fill="x", padx=15, pady=(0, 16))
        
        # Card border
        border_frame2 = tk.Frame(updates_card, bg=self.colors["surface2"], height=1)
        border_frame2.pack(side="bottom", fill="x")
        
        # Card header
        lbl_updates_header = tk.Label(
            updates_card,
            text="Updates",
            font=("Arial", 10, "bold"),
            fg=self.colors["text"],
            bg=self.colors["mantle"]
        )
        lbl_updates_header.pack(anchor="w", padx=12, pady=(12, 8))
        
        # Current version (smaller and centered)
        lbl_version = tk.Label(
            updates_card,
            text=f"v{APP_VERSION}",
            font=("Arial", 9),
            fg=self.colors["subtext0"],
            bg=self.colors["mantle"],
            highlightthickness=0
        )
        lbl_version.pack(anchor="center", pady=(0, 8))
        
        # Check for updates button (prominent accent button)
        btn_check = tk.Button(
            updates_card,
            text="Check for Updates",
            command=self._check_for_updates,
            bg=self.colors["blue"],
            fg=self.colors["base"],
            font=("Arial", 10, "bold"),
            relief="flat",
            width=20,
            height=2,
            cursor="hand2"
        )
        btn_check.pack(anchor="center", pady=8)
        
        # Update status label (centered)
        self.lbl_update_status = tk.Label(
            updates_card,
            text=f"You are using {APP_VERSION}",
            font=("Segoe UI", 9),
            bg=self.colors["mantle"],
            fg=self.colors["subtext0"],
            wraplength=340,
            highlightthickness=0
        )
        self.lbl_update_status.pack(anchor="center", pady=(0, 16))
        
        # Auto-check for updates checkbox (centered)
        self.auto_check_updates_var = tk.BooleanVar(
            value=self.settings.get("auto_check_updates", False)
        )
        cb_updates = tk.Checkbutton(
            updates_card,
            text="Automatically check for updates on startup",
            variable=self.auto_check_updates_var,
            font=("Segoe UI", 9),
            fg=self.colors["text"],
            bg=self.colors["mantle"],
            selectcolor=self.colors["surface0"],
            activebackground=self.colors["mantle"]
        )
        cb_updates.pack(anchor="center", pady=(0, 20))

    def _check_for_updates(self) -> None:
        """Check for updates from GitHub Releases API."""
        self.lbl_update_status.config(text="Checking for updates...", fg=self.colors["yellow"])
        self.window.update()
        
        try:
            api_url = "https://api.github.com/repos/AliesterEroan/DiscordQuestManager/releases/latest"
            request = urllib.request.Request(api_url)
            request.add_header("User-Agent", "DiscordQuestManager")
            
            with urllib.request.urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode())
                latest_version = data["tag_name"].lstrip("v")
                
                if latest_version > APP_VERSION:
                    self.lbl_update_status.config(
                        text=f"Update available: v{latest_version}",
                        fg=self.colors["green"]
                    )
                elif latest_version == APP_VERSION:
                    self.lbl_update_status.config(
                        text="You are using the latest version",
                        fg=self.colors["green"]
                    )
                else:
                    self.lbl_update_status.config(
                        text=f"You are using a development version ({APP_VERSION})",
                        fg=self.colors["yellow"]
                    )
        except Exception as e:
            self.lbl_update_status.config(
                text=f"Failed to check for updates: {str(e)}",
                fg=self.colors["red"]
            )

    def _set_duration(self, minutes: int) -> None:
        """Set duration from preset button."""
        self.duration_var.set(str(minutes))

    def _set_multi_quest(self, limit: int) -> None:
        """Set multi-quest limit from preset button."""
        self.multi_quest_var.set(limit)

    def _start_drag(self, event) -> None:
        """Start dragging the window."""
        self._drag_data = {"x": event.x, "y": event.y}

    def _on_drag(self, event) -> None:
        """Handle window dragging."""
        if hasattr(self, '_drag_data'):
            x = self.window.winfo_x() + (event.x - self._drag_data["x"])
            y = self.window.winfo_y() + (event.y - self._drag_data["y"])
            self.window.geometry(f"+{x}+{y}")

    def _cancel_settings(self) -> None:
        """Cancel settings changes without saving."""
        logger.info("Cancel button clicked - discarding changes")
        # Reload original settings
        self._reload_original_settings()
        logger.info("Reloaded original settings")

    def update_colors(self, colors: dict) -> None:
        """Update colors when theme changes.
        
        Args:
            colors: New color dictionary
        """
        self.colors = colors
        self.window.config(bg=colors["base"])
        
        # Optimized color update - only update widgets that need theme changes
        def update_widget(widget):
            try:
                if not hasattr(widget, 'config'):
                    return
                
                widget_type = type(widget)
                
                # Comprehensive background mapping
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
                
                # Update background based on widget type and ui_role
                if hasattr(widget, 'ui_role'):
                    if widget.ui_role == "background_main":
                        widget.config(bg=colors["base"])
                    elif widget.ui_role == "background_mantle":
                        widget.config(bg=colors["mantle"])
                    elif widget.ui_role == "background_surface":
                        widget.config(bg=colors["surface0"])
                else:
                    try:
                        current_bg = widget.cget("bg")
                        if current_bg in bg_map:
                            widget.config(bg=bg_map[current_bg])
                        elif widget_type == tk.Label:
                            # Labels default to mantle background
                            widget.config(bg=colors["mantle"])
                        elif widget_type == tk.Frame:
                            # Frames default to base background
                            widget.config(bg=colors["base"])
                        elif widget_type == tk.Entry:
                            widget.config(bg=colors["surface0"])
                    except Exception:
                        pass
                
                # Update foreground for text widgets
                if widget_type in (tk.Label, tk.Button):
                    try:
                        current_fg = widget.cget("fg")
                        if current_fg and current_fg != "":
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
                            if current_fg in fg_map:
                                widget.config(fg=fg_map[current_fg])
                    except Exception:
                        pass
                
                # Update specific widget properties
                if widget_type in (tk.Checkbutton, tk.Radiobutton):
                    try:
                        widget.config(selectcolor=colors["surface0"], activebackground=colors["mantle"])
                    except Exception:
                        pass
                
                if widget_type == tk.Entry:
                    try:
                        widget.config(insertbackground=colors["text"])
                    except Exception:
                        pass
                
                # Recursively update children
                for child in widget.winfo_children():
                    update_widget(child)
            except Exception:
                pass
        
        update_widget(self.window)

    def _reload_original_settings(self) -> None:
        """Reload original settings values into the dialog."""
        self.theme_var.set(self.settings.get("theme", "mocha"))
        self.duration_var.set(self.settings.get("custom_duration", 15))
        self.remember_duration_var.set(self.settings.get("remember_duration", False))
        self.minimize_to_tray_var.set(self.settings.get("minimize_to_tray", True))
        self.auto_clean_var.set(self.settings.get("auto_clean_on_exit", True))
        self.discord_auto_open_var.set(self.settings.get("discord_auto_open", True))
        self.multi_quest_var.set(self.settings.get("multi_quest_limit", 5))
        self.auto_check_updates_var.set(self.settings.get("auto_check_updates", True))
        
        # Convert internal cat name to display name for UI
        cat_internal = self.settings.get("dummy_cat_selection", "Cat-1")
        cat_display = self.cat_internal_to_display.get(cat_internal, "Chestnut")
        self.cat_var.set(cat_display)
        
        # Reload custom colors
        for color_key, color_var in self.color_vars.items():
            if isinstance(color_var, tk.StringVar):
                saved_color = self.settings.get(f"custom_{color_key}")
                if saved_color:
                    color_var.set(saved_color)

    def _save_settings(self) -> None:
        """Save settings without closing dialog."""
        logger.info("Save button clicked - starting save process")
        
        # Disable save button to prevent double-clicks
        if hasattr(self, 'btn_save'):
            self.btn_save.config(state="disabled", text="Saving...")
        
        custom_colors = {}
        if self.theme_var.get() == "custom":
            for color_key, color_var in self.color_vars.items():
                # Only save StringVar values, skip Entry widget references
                if isinstance(color_var, tk.StringVar):
                    custom_colors[color_key] = color_var.get()
            logger.debug(f"Collected {len(custom_colors)} custom colors")
            
            # Merge custom colors with mocha defaults for complete palette
            import json
            import os
            mocha_file = os.path.join(os.path.dirname(__file__), "..", "core", "themes", "mocha.json")
            mocha_colors = {}
            try:
                with open(mocha_file, "r") as f:
                    theme_data = json.load(f)
                    mocha_colors = theme_data.get("colors", {})
            except Exception as e:
                logger.error(f"Failed to load mocha.json: {e}")
                mocha_colors = {"base": "#1e1e2e", "mantle": "#181825"}
            
            complete_custom_colors = mocha_colors.copy()
            complete_custom_colors.update(custom_colors)
            custom_colors = complete_custom_colors
            logger.debug(f"Merged with mocha defaults, now have {len(custom_colors)} total colors")
        
        new_settings = {
            "theme": self.theme_var.get(),
            "custom_duration": int(self.duration_var.get()),
            "remember_duration": self.remember_duration_var.get(),
            "minimize_to_tray": self.minimize_to_tray_var.get(),
            "auto_clean_on_exit": self.auto_clean_var.get(),
            "discord_auto_open": self.discord_auto_open_var.get(),
            "multi_quest_limit": int(self.multi_quest_var.get()),
            "auto_check_updates": self.auto_check_updates_var.get(),
            "dummy_cat_selection": self.cat_display_to_internal.get(self.cat_var.get(), "Cat-1"),
            "dummy_alarm_enabled": self.alarm_enabled_var.get(),
            "dummy_alarm_type": self.alarm_type_var.get(),
            "dummy_alarm_sound_path": self.alarm_sound_path_var.get(),
            "dummy_alarm_volume": self.volume_var.get(),
            "exe_creation_path": self.exe_path_var.get(),
            "data_folder_path": self.data_path_var.get(),
        }
        
        # Add custom colors to settings if custom theme is selected
        if self.theme_var.get() == "custom" and custom_colors:
            for color_key, color_value in custom_colors.items():
                new_settings[f"custom_{color_key}"] = color_value
            logger.debug(f"Added {len(custom_colors)} custom colors to new_settings")
        
        logger.debug(f"Created new_settings dict with {len(new_settings)} keys")
        
        theme_changed = new_settings["theme"] != self.settings.get("theme")
        is_custom_theme = new_settings["theme"] == "custom"
        logger.debug(f"Theme changed: {theme_changed}, Is custom theme: {is_custom_theme}")
        
        if self.on_theme_change and (theme_changed or is_custom_theme):
            logger.info("Calling theme change callback")
            if is_custom_theme:
                self.on_theme_change(new_settings["theme"], custom_colors)
            else:
                self.on_theme_change(new_settings["theme"])
        
        logger.info("Calling on_save callback")
        self.on_save(new_settings)
        
        # Update local settings copy
        self.settings = new_settings
        logger.info("Settings saved successfully")
        
        # Re-enable save button
        if hasattr(self, 'btn_save'):
            self.btn_save.config(state="normal", text="Save Settings")
