"""Process management for spawning and terminating game emulation processes."""

import os
import shutil
import subprocess
import sys
import time
from typing import Optional, Dict


class ProcessManager:
    """Manages subprocess spawning for game emulation."""

    def __init__(self):
        self.active_processes: Dict[str, subprocess.Popen] = {}

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
        
        # In development mode, don't create a fake executable - just return a placeholder
        # The spawn_dummy_process will handle running the script directly
        if not getattr(sys, "frozen", False):
            logger = __import__('logging').getLogger(__name__)
            logger.info(f"Development mode: Skipping fake executable creation for {exe_name}")
            return fake_exe_path  # Return path but won't be used
        
        # Copy the current executable to create the fake one (packaged mode)
        source = sys.executable
        
        try:
            shutil.copyfile(source, fake_exe_path)
            logger = __import__('logging').getLogger(__name__)
            logger.info(f"Created fake executable: {fake_exe_path} from {source}")
        except Exception as e:
            logger = __import__('logging').getLogger(__name__)
            logger.error(f"Failed to create fake executable: {e}")
            raise
        
        return fake_exe_path

    def spawn_dummy_process(self, quest_id: str, fake_exe_path: str, exe_name: str, game_name: str, script_path: Optional[str] = None, theme_colors: Optional[Dict] = None, duration_minutes: int = 15, cat_selection: str = "Cat-1") -> subprocess.Popen:
        """Spawn a dummy process for game emulation.
        
        Args:
            quest_id: Unique identifier for the quest
            fake_exe_path: Path to the fake executable
            exe_name: Name of the executable being emulated
            game_name: Name of the game
            script_path: Path to the main script (for dev mode)
            theme_colors: Optional theme colors dictionary to pass to dummy window
            duration_minutes: Duration in minutes for the quest timer
            cat_selection: Cat character selection for animations
            
        Returns:
            Popen object for the spawned process
        """
        import os
        import json
        
        if getattr(sys, "frozen", False):
            # Packaged mode - run the fake executable directly
            cmd = [fake_exe_path, "--dummy-mode", exe_name, game_name, str(duration_minutes), cat_selection]
            # Add theme colors as JSON argument if provided
            if theme_colors:
                cmd.append("--theme-colors")
                cmd.append(json.dumps(theme_colors))
            process = subprocess.Popen(cmd)
        else:
            # Development mode - run python with the script
            # Get the project root directory
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(script_path)))
            cmd = [sys.executable, script_path, "--dummy-mode", exe_name, game_name, str(duration_minutes), cat_selection]
            # Add theme colors as JSON argument if provided
            if theme_colors:
                cmd.append("--theme-colors")
                cmd.append(json.dumps(theme_colors))
            process = subprocess.Popen(cmd, cwd=project_root)
        
        self.active_processes[quest_id] = process
        return process

    def terminate_process(self, quest_id: str) -> None:
        """Terminate a specific process with forceful cleanup.
        
        Args:
            quest_id: Unique identifier for the quest
        """
        if quest_id in self.active_processes:
            process = self.active_processes[quest_id]
            if process.poll() is None:
                # Forceful termination for Windows
                if os.name == 'nt':
                    try:
                        subprocess.run(
                            ['taskkill', '/F', '/T', '/PID', str(process.pid)],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            check=False
                        )
                    except Exception as e:
                        print(f"Forceful termination failed for PID {process.pid}: {e}")
                        # Fallback to standard terminate
                        process.terminate()
                else:
                    # Unix fallback - terminate process group
                    try:
                        import signal
                        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    except Exception as e:
                        print(f"Process group termination failed: {e}")
                        process.terminate()
                
                # Give it time to terminate
                time.sleep(0.5)
            del self.active_processes[quest_id]

    def terminate_all_processes(self) -> None:
        """Terminate all active processes."""
        for quest_id in list(self.active_processes.keys()):
            self.terminate_process(quest_id)

    def is_process_running(self, quest_id: str) -> bool:
        """Check if a specific process is still running.
        
        Args:
            quest_id: Unique identifier for the quest
            
        Returns:
            True if process is running
        """
        if quest_id in self.active_processes:
            return self.active_processes[quest_id].poll() is None
        return False

    def get_active_process(self, quest_id: str) -> Optional[subprocess.Popen]:
        """Get a specific process object.
        
        Args:
            quest_id: Unique identifier for the quest
            
        Returns:
            Popen object or None
        """
        return self.active_processes.get(quest_id)

    def get_all_processes(self) -> Dict[str, subprocess.Popen]:
        """Get all active processes.
        
        Returns:
            Dictionary of quest_id to Popen objects
        """
        return self.active_processes.copy()
