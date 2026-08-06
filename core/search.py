"""Game search functionality for filtering Discord detectable games."""

from typing import List, Tuple, Dict, Any


class Search:
    """Handles game search and filtering."""

    def __init__(self, games_db: List[Dict[str, Any]]):
        self.games_db = games_db

    def search(self, query: str, max_results: int = 100) -> List[Tuple[str, str]]:
        """Search games by name or executable name.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return (default: 100)
            
        Returns:
            List of tuples (game_name, executable_name)
        """
        if not query:
            return []

        query = query.strip().lower()
        matches = []

        for app in self.games_db:
            if len(matches) >= max_results:
                break
                
            app_name = app.get("name", "Unknown Game")
            for exe in app.get("executables", []):
                if exe.get("os") == "win32":
                    raw_exe = exe.get("name", "")
                    if raw_exe:
                        clean_exe = raw_exe.replace("\\", "/").split("/")[-1]
                        if query in app_name.lower() or query in clean_exe.lower():
                            pair = (app_name, clean_exe)
                            if pair not in matches:
                                matches.append(pair)

        return matches

    def format_result(self, game_name: str, exe_name: str) -> str:
        """Format a search result for display.
        
        Args:
            game_name: Name of the game
            exe_name: Name of the executable
            
        Returns:
            Formatted string for display
        """
        return f"{game_name}  ->  {exe_name}"

    def update_database(self, games_db: List[Dict[str, Any]]) -> None:
        """Update the games database.
        
        Args:
            games_db: New games database
        """
        self.games_db = games_db
