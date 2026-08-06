"""Discord detectable games database fetching and caching."""

import json
import threading
import urllib.request
from typing import Callable, List, Dict, Any

from config.constants import DISCORD_API_URL, USER_AGENT


class Database:
    """Manages Discord detectable games database."""

    def __init__(self):
        self.games_db: List[Dict[str, Any]] = []
        self._loading = False

    def load_async(self, callback: Callable[[bool, List[Dict[str, Any]]], None]) -> None:
        """Load database asynchronously from Discord API."""
        if self._loading:
            return

        self._loading = True

        def fetch():
            try:
                req = urllib.request.Request(
                    DISCORD_API_URL,
                    headers={"User-Agent": USER_AGENT},
                )
                with urllib.request.urlopen(req) as response:
                    if response.status == 200:
                        data = json.loads(response.read().decode("utf-8"))
                        self.games_db = data
                        callback(True, data)
                        return
            except Exception:
                pass
            callback(False, [])
            self._loading = False

        threading.Thread(target=fetch, daemon=True).start()

    def get_games(self) -> List[Dict[str, Any]]:
        """Return the loaded games database."""
        return self.games_db

    def is_loaded(self) -> bool:
        """Check if database has been loaded."""
        return len(self.games_db) > 0

    def get_game_count(self) -> int:
        """Return the number of games in the database."""
        return len(self.games_db)
