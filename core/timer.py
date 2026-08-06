"""Countdown timer for Discord Quest Manager."""

from typing import Callable, Optional

from config.constants import TIMER_DURATION_MINUTES, TIMER_TICK_MS


class Timer:
    """Manages countdown timer for quest duration."""

    def __init__(self):
        self.remaining_seconds = TIMER_DURATION_MINUTES * 60
        self.total_seconds = TIMER_DURATION_MINUTES * 60
        self.is_running = False
        self.on_tick_callback: Optional[Callable[[str], None]] = None
        self.on_complete_callback: Optional[Callable] = None
        self._tick_function: Optional[Callable] = None

    def start(self, tick_function: Callable) -> None:
        """Start the timer.
        
        Args:
            tick_function: Function to call for each tick (e.g., root.after)
        """
        self.is_running = True
        self.remaining_seconds = self.total_seconds
        self._tick_function = tick_function
        self._tick()

    def stop(self) -> None:
        """Stop the timer."""
        self.is_running = False

    def reset(self) -> None:
        """Reset the timer to initial duration."""
        self.remaining_seconds = self.total_seconds

    def set_duration_minutes(self, minutes: int) -> None:
        """Set the timer duration in minutes.
        
        Args:
            minutes: Duration in minutes
        """
        self.total_seconds = minutes * 60
        self.remaining_seconds = self.total_seconds

    def get_elapsed_seconds(self) -> int:
        """Get the elapsed time in seconds.
        
        Returns:
            Elapsed seconds
        """
        return self.total_seconds - self.remaining_seconds

    def _tick(self) -> None:
        """Internal tick method called every second."""
        if not self.is_running:
            return

        if self.remaining_seconds <= 0:
            self.is_running = False
            if self.on_complete_callback:
                self.on_complete_callback()
            return

        # Format and display time
        mins, secs = divmod(self.remaining_seconds, 60)
        time_str = f"{mins:02d}:{secs:02d}"
        
        if self.on_tick_callback:
            self.on_tick_callback(time_str)

        self.remaining_seconds -= 1

        # Schedule next tick
        if self._tick_function:
            self._tick_function(TIMER_TICK_MS, self._tick)

    def get_display_time(self) -> str:
        """Get the current display time.
        
        Returns:
            Formatted time string (MM:SS)
        """
        mins, secs = divmod(self.remaining_seconds, 60)
        return f"{mins:02d}:{secs:02d}"

    def set_on_tick(self, callback: Callable[[str], None]) -> None:
        """Set callback for timer tick updates.
        
        Args:
            callback: Function called with formatted time string
        """
        self.on_tick_callback = callback

    def set_on_complete(self, callback: Callable) -> None:
        """Set callback for timer completion.
        
        Args:
            callback: Function called when timer reaches zero
        """
        self.on_complete_callback = callback
