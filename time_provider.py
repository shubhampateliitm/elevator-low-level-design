import time

class TimeProvider:
    def get_time(self):
        return time.time()

class MockTimeProvider(TimeProvider):
    def __init__(self, initial_time=0):
        self._current_time = initial_time

    def get_time(self):
        return self._current_time

    def advance_time(self, seconds):
        self._current_time += seconds
