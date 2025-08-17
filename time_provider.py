import time

class TimeProvider:
    """Provides the current time. Useful for abstracting time in simulations and tests."""
    def get_time(self) -> float:
        """Returns the current time.

        Returns:
            float: The current time in seconds since the epoch.
        """
        return time.time()

class MockTimeProvider(TimeProvider):
    """A mock implementation of TimeProvider for testing, allowing manual control of time."""
    def __init__(self, initial_time: float = 0) -> None:
        """Initializes the MockTimeProvider.

        Args:
            initial_time (float): The starting time for the mock provider. Defaults to 0.
        """
        self._current_time = initial_time

    def get_time(self) -> float:
        """Returns the current mock time.

        Returns:
            float: The current mock time.
        """
        return self._current_time

    def advance_time(self, seconds: float) -> None:
        """Advances the current mock time by a specified number of seconds.

        Args:
            seconds (float): The number of seconds to advance the time by.
        """
        self._current_time += seconds
