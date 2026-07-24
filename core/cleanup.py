"""Cleanup utility for removing dummy executable files."""

import glob
import os
import sys
from typing import Tuple


class Cleanup:
    """Handles cleanup of dummy executable files."""

    def __init__(self):
        self.target_dir = self._get_target_directory()
        self.current_app_name = self._get_current_app_name()

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
        """Clean up dummy executable files.
        
        Returns:
            Tuple of (deleted_count, skipped_count)
        """
        deleted_count = 0
        skipped_count = 0

        for filepath in glob.glob(os.path.join(self.target_dir, "*.exe")):
            filename = os.path.basename(filepath).lower()
            if filename != self.current_app_name:
                try:
                    os.remove(filepath)
                    deleted_count += 1
                except Exception:
                    skipped_count += 1

        return deleted_count, skipped_count

    def get_target_directory(self) -> str:
        """Get the target directory being cleaned.
        
        Returns:
            Directory path
        """
        return self.target_dir
