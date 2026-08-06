"""Favorites and recent games management for Discord Quest Manager."""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple


class FavoritesManager:
    """Manages favorites and recent games lists."""

    def __init__(self):
        self.favorites_file = self._get_favorites_file_path()
        self.data = self._load_default_data()
        self._load_data()

    def _get_favorites_file_path(self) -> str:
        """Get the path to the favorites file.
        
        Returns:
            Path to favorites.json
        """
        if getattr(sys, "frozen", False):
            base_dir = os.path.dirname(os.path.dirname(sys.executable))
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        return os.path.join(base_dir, "data", "favorites.json")

    def _load_default_data(self) -> Dict[str, List[Dict]]:
        """Load default data structure.
        
        Returns:
            Default data dictionary
        """
        return {
            "favorites": [],
            "recent": [],
        }

    def _load_data(self) -> None:
        """Load data from file."""
        if os.path.exists(self.favorites_file):
            try:
                with open(self.favorites_file, "r") as f:
                    loaded = json.load(f)
                    self.data.update(loaded)
            except (json.JSONDecodeError, IOError):
                pass

    def _save_data(self) -> None:
        """Save data to file."""
        os.makedirs(os.path.dirname(self.favorites_file), exist_ok=True)
        try:
            with open(self.favorites_file, "w") as f:
                json.dump(self.data, f, indent=2)
        except IOError:
            pass

    def add_favorite(self, game_name: str, exe_name: str) -> None:
        """Add a game to favorites.
        
        Args:
            game_name: Name of the game
            exe_name: Name of the executable
        """
        # Check if already exists
        for fav in self.data["favorites"]:
            if fav["game_name"] == game_name and fav["exe_name"] == exe_name:
                return
        
        self.data["favorites"].append({
            "game_name": game_name,
            "exe_name": exe_name,
            "added_at": datetime.now().isoformat(),
        })
        self._save_data()

    def remove_favorite(self, game_name: str, exe_name: str) -> None:
        """Remove a game from favorites.
        
        Args:
            game_name: Name of the game
            exe_name: Name of the executable
        """
        self.data["favorites"] = [
            fav for fav in self.data["favorites"]
            if not (fav["game_name"] == game_name and fav["exe_name"] == exe_name)
        ]
        self._save_data()

    def add_recent(self, game_name: str, exe_name: str) -> None:
        """Add a game to recent list.
        
        Args:
            game_name: Name of the game
            exe_name: Name of the executable
        """
        # Remove if already exists (to move to top)
        self.data["recent"] = [
            rec for rec in self.data["recent"]
            if not (rec["game_name"] == game_name and rec["exe_name"] == exe_name)
        ]
        
        # Add to top
        self.data["recent"].insert(0, {
            "game_name": game_name,
            "exe_name": exe_name,
            "last_used": datetime.now().isoformat(),
        })
        
        # Keep only last 10
        self.data["recent"] = self.data["recent"][:10]
        
        self._save_data()

    def get_favorites(self) -> List[Tuple[str, str]]:
        """Get all favorites.
        
        Returns:
            List of (game_name, exe_name) tuples
        """
        return [(fav["game_name"], fav["exe_name"]) for fav in self.data["favorites"]]

    def get_recent(self) -> List[Tuple[str, str]]:
        """Get recent games.
        
        Returns:
            List of (game_name, exe_name) tuples
        """
        return [(rec["game_name"], rec["exe_name"]) for rec in self.data["recent"]]

    def is_favorite(self, game_name: str, exe_name: str) -> bool:
        """Check if a game is in favorites.
        
        Args:
            game_name: Name of the game
            exe_name: Name of the executable
            
        Returns:
            True if game is in favorites
        """
        for fav in self.data["favorites"]:
            if fav["game_name"] == game_name and fav["exe_name"] == exe_name:
                return True
        return False

    def clear_favorites(self) -> None:
        """Clear all favorites."""
        self.data["favorites"] = []
        self._save_data()

    def clear_recent(self) -> None:
        """Clear all recent games."""
        self.data["recent"] = []
        self._save_data()
