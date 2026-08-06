"""
Layout Manager for Discord Quest Manager
Handles all container setup and layout configuration
"""

import tkinter as tk
from config.constants import LAYOUT
from ui.pixel_container import PixelContainer


class LayoutManager:
    """Manages the layout of all UI containers"""
    
    def __init__(self, root: tk.Tk, colors: dict):
        self.root = root
        self.colors = colors
        self.containers = {}
        
    def setup_main_grid(self):
        """Configure the main window grid layout"""
        self.root.columnconfigure(0, weight=0, minsize=250)  # Left Sidebar maintains fixed width
        self.root.columnconfigure(1, weight=1)  # Right Panel expands horizontally (stretch factor 1)
        self.root.rowconfigure(0, weight=1)     # Workspace row stretches vertically
        self.root.rowconfigure(1, weight=0)     # Copyright ribbon stays snug at bottom
        
    def create_main_containers(self):
        """Create and setup the main containers"""
        # ====================================================================
        # [MAIN CONTAINER 1] THE LEFT SIDEBAR PANEL
        # ====================================================================
        sidebar_kwargs = {
            "width": LAYOUT["sidebar_width"],
            "bg_color": self.colors["mantle"],
            "border_color": "#000000",
            "pixel_scale": 3
        }
        # Only set height if it's not None
        if LAYOUT["sidebar_height"]:
            sidebar_kwargs["height"] = LAYOUT["sidebar_height"]
            
        sidebar_panel = PixelContainer(self.root, **sidebar_kwargs)
        sidebar_panel.grid(row=0, column=0, padx=LAYOUT["main_padx"], pady=LAYOUT["main_pady"], sticky="nsew")
        self.containers['sidebar'] = sidebar_panel
        
        # ====================================================================
        # [MAIN CONTAINER 2] THE RIGHT SIDE VIEWPORT PANEL
        # ====================================================================
        right_panel_kwargs = {
            "bg_color": self.colors["mantle"],
            "border_color": "#000000",
            "pixel_scale": 3
        }
        # Only set width/height if they're not None
        if LAYOUT["right_panel_width"]:
            right_panel_kwargs["width"] = LAYOUT["right_panel_width"]
        if LAYOUT["right_panel_height"]:
            right_panel_kwargs["height"] = LAYOUT["right_panel_height"]
            
        right_panel = PixelContainer(self.root, **right_panel_kwargs)
        right_panel.grid(row=0, column=1, padx=LAYOUT["right_panel_padx"], pady=LAYOUT["right_panel_pady"], sticky="nsew")
        self.containers['right_panel'] = right_panel
        
        # Configure vertical row priorities inside Main Container 2
        right_surface = right_panel.content_frame
        right_surface.columnconfigure(0, weight=1)
        right_surface.rowconfigure(0, weight=0)  # Search Bar (compact height)
        right_surface.rowconfigure(1, weight=1)  # Executables Viewer (stretches vertically)
        right_surface.rowconfigure(2, weight=0)  # Footer Controls (compact height)
        
        # ====================================================================
        # RIGHT PANEL SUB-CONTAINERS
        # ====================================================================
        
        # Sub-container A: Search Bar
        search_bar_kwargs = {
            "height": LAYOUT["search_bar_height"],
            "bg_color": self.colors["surface0"],
            "pixel_scale": 3
        }
        if LAYOUT["search_bar_width"]:
            search_bar_kwargs["width"] = LAYOUT["search_bar_width"]
            
        search_bar = PixelContainer(right_surface, **search_bar_kwargs)
        search_bar.grid(row=0, column=0, pady=LAYOUT["search_bar_pady"], sticky="ew")
        # Keep grid_propagate(False) since height is explicit (48px)
        search_bar.grid_propagate(False)
        self.containers['search_bar'] = search_bar
        
        # Sub-container B: Target Executables Viewer
        executables_viewer_kwargs = {
            "bg_color": self.colors["mantle"],
            "pixel_scale": 3
        }
        if LAYOUT["executables_viewer_width"]:
            executables_viewer_kwargs["width"] = LAYOUT["executables_viewer_width"]
        if LAYOUT["executables_viewer_height"]:
            executables_viewer_kwargs["height"] = LAYOUT["executables_viewer_height"]
            
        executables_viewer = PixelContainer(right_surface, **executables_viewer_kwargs)
        executables_viewer.grid(row=1, column=0, pady=LAYOUT["executables_viewer_pady"], sticky="nsew")
        # No grid_propagate(False) - allow dynamic vertical expansion via row weight=1
        self.containers['executables_viewer'] = executables_viewer
        
        # Sub-container C: Lower Control Bar
        footer_card_kwargs = {
            "height": LAYOUT["footer_card_height"],
            "bg_color": self.colors["surface0"],
            "pixel_scale": 3
        }
        if LAYOUT["footer_card_width"]:
            footer_card_kwargs["width"] = LAYOUT["footer_card_width"]
            
        footer_card = PixelContainer(right_surface, **footer_card_kwargs)
        footer_card.grid(row=2, column=0, pady=LAYOUT["footer_card_pady"], sticky="ew")
        # Keep grid_propagate(False) since height is now explicit (42px)
        footer_card.grid_propagate(False)
        self.containers['footer_card'] = footer_card
        
        return self.containers
    
    def get_container(self, name: str):
        """Get a specific container by name"""
        return self.containers.get(name)
    
    def get_all_containers(self):
        """Get all containers"""
        return self.containers
    
    def update_colors(self, colors: dict) -> None:
        """Update colors when theme changes.
        
        Args:
            colors: New color dictionary
        """
        self.colors = colors
        # Use a darker shade for borders (surface0 is darker than mantle)
        border_color = colors.get("surface0", "#000000")
        # Update all containers
        for container in self.containers.values():
            if hasattr(container, 'update_colors'):
                # Update background based on container type
                if 'search_bar' in str(container) or 'footer' in str(container):
                    bg_color = colors["surface0"]
                else:
                    bg_color = colors["mantle"]
                container.update_colors(bg_color=bg_color, border_color=border_color)
