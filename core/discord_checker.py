"""Discord process detection for Discord Quest Manager."""

import subprocess
from typing import Optional


class DiscordChecker:
    """Checks for Discord process presence."""

    def is_discord_running(self) -> bool:
        """Check if Discord is currently running.
        
        Returns:
            True if Discord process is found
        """
        try:
            # Check for Discord.exe using tasklist
            result = subprocess.run(
                ["tasklist"],
                capture_output=True,
                text=True,
                shell=True
            )
            return "Discord.exe" in result.stdout
        except Exception:
            return False

    def open_discord(self) -> bool:
        """Attempt to open Discord.
        
        Returns:
            True if Discord was opened successfully
        """
        try:
            # Try common Discord installation paths
            discord_paths = [
                r"%LocalAppData%\Discord\Update.exe",
                r"%ProgramFiles%\Discord\Update.exe",
                r"%ProgramFiles(x86)%\Discord\Update.exe",
            ]
            
            for path in discord_paths:
                try:
                    subprocess.Popen(
                        [path, "--processStart", "Discord.exe"],
                        shell=True
                    )
                    return True
                except Exception:
                    continue
            
            # Fallback: try to open via start command
            subprocess.Popen(
                ["start", "discord:"],
                shell=True
            )
            return True
        except Exception:
            return False

    def get_discord_status(self) -> str:
        """Get Discord status message.
        
        Returns:
            Status message string
        """
        if self.is_discord_running():
            return "Discord is running"
        return "Discord is not running"
