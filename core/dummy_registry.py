"""Dummy executable registry for safe cleanup tracking."""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional


class DummyRegistry:
    """Tracks dummy executables created by the application."""

    def __init__(self):
        self.registry_file = self._get_registry_file_path()
        self.registry: Dict[str, Dict] = {}
        self._load_registry()

    def _get_registry_file_path(self) -> str:
        """Get the path to the registry file.
        
        Returns:
            Path to dummy_registry.json
        """
        if getattr(sys, "frozen", False):
            base_dir = os.path.dirname(os.path.dirname(sys.executable))
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        return os.path.join(base_dir, "data", "dummy_registry.json")

    def _load_registry(self) -> None:
        """Load registry from file."""
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, "r") as f:
                    self.registry = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.registry = {}

    def _save_registry(self) -> None:
        """Save registry to file."""
        os.makedirs(os.path.dirname(self.registry_file), exist_ok=True)
        try:
            with open(self.registry_file, "w") as f:
                json.dump(self.registry, f, indent=2)
        except IOError:
            pass

    def register_dummy(self, exe_path: str, game_name: str, exe_name: str) -> None:
        """Register a dummy executable.
        
        Args:
            exe_path: Full path to the dummy executable
            game_name: Name of the game
            exe_name: Name of the executable
        """
        self.registry[exe_path] = {
            "created_by": "DiscordQuestManager",
            "created_at": datetime.now().isoformat(),
            "game_name": game_name,
            "exe_name": exe_name,
        }
        self._save_registry()

    def unregister_dummy(self, exe_path: str) -> None:
        """Unregister a dummy executable.
        
        Args:
            exe_path: Full path to the dummy executable
        """
        if exe_path in self.registry:
            del self.registry[exe_path]
            self._save_registry()

    def is_registered(self, exe_path: str) -> bool:
        """Check if an executable is registered as a dummy.
        
        Args:
            exe_path: Full path to the executable
            
        Returns:
            True if registered as a dummy
        """
        return exe_path in self.registry

    def get_registered_dummies(self) -> List[str]:
        """Get all registered dummy paths.
        
        Returns:
            List of dummy executable paths
        """
        return list(self.registry.keys())

    def cleanup_orphaned_entries(self) -> int:
        """Remove registry entries for files that no longer exist.
        
        Returns:
            Number of entries removed
        """
        removed = 0
        for exe_path in list(self.registry.keys()):
            if not os.path.exists(exe_path):
                del self.registry[exe_path]
                removed += 1
        
        if removed > 0:
            self._save_registry()
        
        return removed

    def get_dummy_info(self, exe_path: str) -> Optional[Dict]:
        """Get information about a registered dummy.
        
        Args:
            exe_path: Full path to the dummy executable
            
        Returns:
            Dummy info dictionary or None
        """
        return self.registry.get(exe_path)
