"""Update manager for Discord Quest Manager."""

import json
import urllib.request
import threading
from typing import Callable, Optional, Dict, Any
from packaging import version

from config.constants import APP_VERSION, GITHUB_RELEASES


class UpdateManager:
    """Manages application updates via GitHub API."""

    def __init__(self):
        self.current_version = APP_VERSION
        self.github_api_url = "https://api.github.com/repos/AliesterEroan/DiscordQuestManager/releases/latest"
        self.latest_release_info: Optional[Dict[str, Any]] = None
        self.update_available = False

    def check_for_updates_async(self, callback: Callable[[bool, Optional[str], Optional[str]], None]) -> None:
        """Check for updates asynchronously.
        
        Args:
            callback: Function to call with (update_available, latest_version, download_url)
        """
        def check():
            try:
                req = urllib.request.Request(
                    self.github_api_url,
                    headers={"User-Agent": "DiscordQuestManager"}
                )
                with urllib.request.urlopen(req) as response:
                    if response.status == 200:
                        data = json.loads(response.read().decode("utf-8"))
                        self.latest_release_info = data
                        
                        # Extract version from tag name (e.g., "v1.1.0" -> "1.1.0")
                        tag_name = data.get("tag_name", "")
                        latest_version = tag_name.lstrip("v")
                        
                        # Compare versions
                        try:
                            current = version.parse(self.current_version)
                            latest = version.parse(latest_version)
                            self.update_available = latest > current
                            
                            # Get download URL for Windows executable
                            download_url = None
                            for asset in data.get("assets", []):
                                if asset.get("name", "").endswith(".exe"):
                                    download_url = asset.get("browser_download_url")
                                    break
                            
                            callback(self.update_available, latest_version, download_url)
                        except Exception:
                            callback(False, None, None)
                    else:
                        callback(False, None, None)
            except Exception:
                callback(False, None, None)

        threading.Thread(target=check, daemon=True).start()

    def check_for_updates(self) -> tuple[bool, Optional[str], Optional[str]]:
        """Check for updates synchronously.
        
        Returns:
            Tuple of (_update_available, latest_version, download_url)
        """
        try:
            req = urllib.request.Request(
                self.github_api_url,
                headers={"User-Agent": "DiscordQuestManager"}
            )
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    self.latest_release_info = data
                    
                    tag_name = data.get("tag_name", "")
                    latest_version = tag_name.lstrip("v")
                    
                    try:
                        current = version.parse(self.current_version)
                        latest = version.parse(latest_version)
                        self.update_available = latest > current
                        
                        download_url = None
                        for asset in data.get("assets", []):
                            if asset.get("name", "").endswith(".exe"):
                                download_url = asset.get("browser_download_url")
                                break
                        
                        return self.update_available, latest_version, download_url
                    except Exception:
                        return False, None, None
        except Exception:
            pass
        
        return False, None, None

    def get_release_notes(self) -> str:
        """Get release notes for the latest version.
        
        Returns:
            Release notes text
        """
        if self.latest_release_info:
            return self.latest_release_info.get("body", "No release notes available.")
        return "No release information available."

    def get_download_url(self) -> Optional[str]:
        """Get download URL for the latest Windows executable.
        
        Returns:
            Download URL or None
        """
        if self.latest_release_info:
            for asset in self.latest_release_info.get("assets", []):
                if asset.get("name", "").endswith(".exe"):
                    return asset.get("browser_download_url")
        return None
