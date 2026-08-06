"""System tray manager for Discord Quest Manager."""

import threading
from typing import Callable, Optional

try:
    import pystray
    from PIL import Image, ImageDraw, ImageFont
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False


class TrayManager:
    """Manages system tray icon and menu."""

    def __init__(self):
        self.icon: Optional[pystray.Icon] = None
        self.on_restore_callback: Optional[Callable] = None
        self.on_start_stop_callback: Optional[Callable] = None
        self.on_quit_callback: Optional[Callable] = None
        self.current_timer_text = ""
        self.is_running = False

    def create_icon(self, icon_path: str) -> None:
        """Create the system tray icon.
        
        Args:
            icon_path: Path to the icon image file
        """
        if not PYSTRAY_AVAILABLE:
            return
        
        try:
            # Load base icon
            base_image = Image.open(icon_path)
            
            # Create menu
            menu = pystray.Menu(
                pystray.MenuItem("Restore", self._on_restore),
                pystray.MenuItem("Start Quest" if not self.is_running else "Stop Quest", self._on_start_stop),
                pystray.MenuItem("Quit", self._on_quit),
            )
            
            self.icon = pystray.Icon(
                "DiscordQuestManager",
                base_image,
                menu=menu,
            )
        except Exception:
            pass

    def _on_restore(self) -> None:
        """Handle restore menu item click."""
        if self.on_restore_callback:
            self.on_restore_callback()

    def _on_start_stop(self) -> None:
        """Handle start/stop menu item click."""
        if self.on_start_stop_callback:
            self.on_start_stop_callback()

    def _on_quit(self) -> None:
        """Handle quit menu item click."""
        if self.on_quit_callback:
            self.on_quit_callback()

    def update_timer_overlay(self, time_str: str, is_running: bool) -> None:
        """Update the timer overlay on the icon.
        
        Args:
            time_str: Time string to display (MM:SS)
            is_running: Whether a quest is currently running
        """
        if not PYSTRAY_AVAILABLE or not self.icon:
            return
        
        self.current_timer_text = time_str
        self.is_running = is_running
        
        try:
            # Create overlay image
            base_image = self.icon.icon
            overlay = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            
            if is_running:
                # Draw timer text
                font_size = 18
                try:
                    font = ImageFont.truetype("arial.ttf", font_size, weight="bold")
                except:
                    try:
                        font = ImageFont.truetype("arial.ttf", font_size)
                    except:
                        font = ImageFont.load_default()
                
                # Position text at bottom right
                text_bbox = draw.textbbox((0, 0), time_str, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                x = base_image.width - text_width - 8
                y = base_image.height - text_height - 8
                
                # Draw background for better visibility
                bg_padding = 4
                draw.rectangle(
                    (x - bg_padding, y - bg_padding, x + text_width + bg_padding, y + text_height + bg_padding),
                    fill=(0, 0, 0, 180)
                )
                
                # Draw text with shadow
                draw.text((x + 2, y + 2), time_str, font=font, fill=(0, 0, 0, 255))
                draw.text((x, y), time_str, font=font, fill=(255, 255, 255, 255))
                
                # Combine images
                combined = Image.alpha_composite(base_image.convert("RGBA"), overlay)
                self.icon.icon = combined
                self.icon.update_menu()
        except Exception:
            pass

    def update_menu_state(self, is_running: bool) -> None:
        """Update menu items based on quest state.
        
        Args:
            is_running: Whether a quest is currently running
        """
        if not PYSTRAY_AVAILABLE or not self.icon:
            return
        
        self.is_running = is_running
        
        menu = pystray.Menu(
            pystray.MenuItem("Restore", self._on_restore),
            pystray.MenuItem("Stop Quest" if is_running else "Start Quest", self._on_start_stop),
            pystray.MenuItem("Quit", self._on_quit),
        )
        
        self.icon.menu = menu
        self.icon.update_menu()

    def run(self) -> None:
        """Run the tray icon in a separate thread."""
        if not PYSTRAY_AVAILABLE or not self.icon:
            return
        
        thread = threading.Thread(target=self.icon.run, daemon=True)
        thread.start()

    def stop(self) -> None:
        """Stop the tray icon."""
        if not PYSTRAY_AVAILABLE or not self.icon:
            return
        
        self.icon.stop()

    def set_on_restore(self, callback: Callable) -> None:
        """Set callback for restore action.
        
        Args:
            callback: Function to call when restore is clicked
        """
        self.on_restore_callback = callback

    def set_on_start_stop(self, callback: Callable) -> None:
        """Set callback for start/stop action.
        
        Args:
            callback: Function to call when start/stop is clicked
        """
        self.on_start_stop_callback = callback

    def set_on_quit(self, callback: Callable) -> None:
        """Set callback for quit action.
        
        Args:
            callback: Function to call when quit is clicked
        """
        self.on_quit_callback = callback

    def hide_window(self) -> None:
        """Hide the main window (minimize to tray)."""
        if self.on_restore_callback:
            # This would be called by the main window
            pass

    def is_available(self) -> bool:
        """Check if pystray is available.
        
        Returns:
            True if pystray is available
        """
        return PYSTRAY_AVAILABLE
