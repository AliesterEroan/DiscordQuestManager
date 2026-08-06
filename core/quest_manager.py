"""Quest lifecycle management for Discord Quest Manager."""

import os
import sys
from typing import Optional, Tuple, Callable


class QuestManager:
    """Manages quest state and lifecycle."""

    def __init__(self):
        self.is_running = False
        self.selected_game: Optional[Tuple[str, str]] = None
        self.fake_exe_path: Optional[str] = None
        self.on_start_callback: Optional[Callable] = None
        self.on_stop_callback: Optional[Callable] = None

    def set_selected_game(self, game_name: str, exe_name: str) -> None:
        """Set the currently selected game.
        
        Args:
            game_name: Name of the game
            exe_name: Name of the executable
        """
        self.selected_game = (game_name, exe_name)

    def get_selected_game(self) -> Optional[Tuple[str, str]]:
        """Get the currently selected game.
        
        Returns:
            Tuple of (game_name, exe_name) or None
        """
        return self.selected_game

    def start_quest(self) -> bool:
        """Start the quest.
        
        Returns:
            True if quest started successfully
        """
        if self.is_running:
            return False

        if not self.selected_game:
            return False

        self.is_running = True
        if self.on_start_callback:
            self.on_start_callback()
        return True

    def stop_quest(self) -> None:
        """Stop the quest."""
        if not self.is_running:
            return

        self.is_running = False
        if self.on_stop_callback:
            self.on_stop_callback()

    def get_exe_name(self) -> Optional[str]:
        """Get the executable name of the selected game.
        
        Returns:
            Executable name or None
        """
        if not self.selected_game:
            return None
        return self.selected_game[1]

    def set_fake_exe_path(self, path: str) -> None:
        """Set the path to the fake executable.
        
        Args:
            path: Path to the fake executable
        """
        self.fake_exe_path = path

    def get_fake_exe_path(self) -> Optional[str]:
        """Get the path to the fake executable.
        
        Returns:
            Path to fake executable or None
        """
        return self.fake_exe_path

    def get_base_directory(self) -> str:
        """Get the base directory for the application.
        
        Returns:
            Base directory path
        """
        if getattr(sys, "frozen", False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.abspath(__file__))

    def cleanup_fake_exe(self) -> None:
        """Remove the fake executable file."""
        if self.fake_exe_path and os.path.exists(self.fake_exe_path):
            try:
                os.remove(self.fake_exe_path)
            except OSError:
                pass
            self.fake_exe_path = None
