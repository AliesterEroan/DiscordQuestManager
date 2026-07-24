"""Process management for spawning and terminating game emulation processes."""

import os
import shutil
import subprocess
import sys
import time
from typing import Optional


class ProcessManager:
    """Manages subprocess spawning for game emulation."""

    def __init__(self):
        self.active_process: Optional[subprocess.Popen] = None

    def create_fake_executable(self, exe_name: str, base_dir: str) -> str:
        """Create a fake executable by copying the application.
        
        Args:
            exe_name: Name of the executable to create
            base_dir: Directory to create the executable in
            
        Returns:
            Path to the created executable
        """
        if not exe_name.lower().endswith(".exe"):
            exe_name += ".exe"

        fake_exe_path = os.path.join(base_dir, exe_name)
        
        # Copy the current executable to create the fake one
        if getattr(sys, "frozen", False):
            source = sys.executable
        else:
            source = sys.executable  # Python interpreter
        
        shutil.copyfile(source, fake_exe_path)
        return fake_exe_path

    def spawn_dummy_process(self, fake_exe_path: str, exe_name: str, script_path: Optional[str] = None) -> subprocess.Popen:
        """Spawn a dummy process for game emulation.
        
        Args:
            fake_exe_path: Path to the fake executable
            exe_name: Name of the executable being emulated
            script_path: Path to the main script (for dev mode)
            
        Returns:
            Popen object for the spawned process
        """
        if getattr(sys, "frozen", False):
            # Packaged mode
            cmd = [fake_exe_path, "--dummy-mode", exe_name]
        else:
            # Development mode
            cmd = [fake_exe_path, script_path, "--dummy-mode", exe_name]

        self.active_process = subprocess.Popen(cmd)
        return self.active_process

    def terminate_process(self) -> None:
        """Terminate the active process."""
        if self.active_process and self.active_process.poll() is None:
            self.active_process.terminate()
            # Give it time to terminate
            time.sleep(0.5)

    def is_process_running(self) -> bool:
        """Check if the active process is still running.
        
        Returns:
            True if process is running
        """
        if self.active_process:
            return self.active_process.poll() is None
        return False

    def get_active_process(self) -> Optional[subprocess.Popen]:
        """Get the active process object.
        
        Returns:
            Popen object or None
        """
        return self.active_process
