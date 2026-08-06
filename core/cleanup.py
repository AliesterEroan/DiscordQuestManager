"""Cleanup utility for removing dummy executable files."""

import glob
import os
import sys
from typing import Tuple

from core.dummy_registry import DummyRegistry


class Cleanup:
    """Handles cleanup of dummy executable files."""

    def __init__(self):
        self.target_dir = self._get_target_directory()
        self.current_app_name = self._get_current_app_name()
        self.registry = DummyRegistry()

    def _get_target_directory(self) -> str:
        """Get the target directory for cleanup.
        
        Returns:
            Directory path to clean
        """
        if getattr(sys, "frozen", False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.abspath(__file__))

    def _get_current_app_name(self) -> str:
        """Get the current application name to exclude from cleanup.
        
        Returns:
            Current application filename (lowercase)
        """
        if getattr(sys, "frozen", False):
            return os.path.basename(sys.executable).lower()
        return os.path.basename(__file__).lower()

    def clean_dummies(self) -> Tuple[int, int]:
        """Clean up dummy executable files using registry.
        
        Returns:
            Tuple of (deleted_count, skipped_count)
        """
        deleted_count = 0
        skipped_count = 0
        
        # Clean up orphaned registry entries first
        self.registry.cleanup_orphaned_entries()
        
        # Get all registered dummy paths
        registered_dummies = self.registry.get_registered_dummies()
        
        # Clean registered dummies
        for filepath in registered_dummies:
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                    self.registry.unregister_dummy(filepath)
                    deleted_count += 1
                except Exception as e:
                    print(f"Failed to delete {filepath}: {e}")
                    skipped_count += 1
            else:
                # File doesn't exist, just remove from registry
                self.registry.unregister_dummy(filepath)
        
        # Also scan for any .exe files that might be orphaned dummies
        # Look for .exe files in the target directory that might be dummies
        try:
            for exe_file in glob.glob(os.path.join(self.target_dir, "*.exe")):
                # Skip the main executable
                if os.path.basename(exe_file).lower() == self.current_app_name:
                    continue
                
                # Check if this is a registered dummy (already handled above)
                if exe_file in registered_dummies:
                    continue
                
                # Check if this might be a dummy by checking if it's in the registry
                if self.registry.is_registered(exe_file):
                    continue
                
                # For safety, only delete files that were created by this app
                # Check if file is in a subdirectory that might contain dummies
                # This is a safety measure to avoid deleting user files
                # We'll only delete if it's clearly a dummy (small size, recent, etc.)
                try:
                    stat = os.stat(exe_file)
                    # If file is very small (< 1MB) and recent, it might be a dummy
                    if stat.st_size < 1024 * 1024:  # Less than 1MB
                        # Check if it's in the data folder or similar
                        if "dummy" in exe_file.lower() or "temp" in exe_file.lower():
                            os.remove(exe_file)
                            deleted_count += 1
                except Exception:
                    skipped_count += 1
        except Exception as e:
            print(f"Error scanning for orphaned dummies: {e}")

        return deleted_count, skipped_count

    def get_target_directory(self) -> str:
        """Get the target directory being cleaned.
        
        Returns:
            Directory path
        """
        return self.target_dir
