from threading import Lock
from enums import Direction
from database_manager import DatabaseManager
import logging

class RequestManager:
    """
    Manages system-wide hall call requests (up and down requests).
    Encapsulates request storage, manipulation, and persistence.
    """
    def __init__(self, database_manager: DatabaseManager) -> None:
        self.database_manager = database_manager
        self.up_requests = []
        self.down_requests = []
        self._up_requests_lock = Lock()
        self._down_requests_lock = Lock()
        self._load_requests_from_db()

    def _load_requests_from_db(self) -> None:
        """Loads system-wide hall call requests from the database."""
        loaded_system_requests = self.database_manager.load_system_requests()
        if loaded_system_requests:
            self.up_requests = [req[0] for req in loaded_system_requests if req[1] == Direction.UP]
            self.down_requests = [req[0] for req in loaded_system_requests if req[1] == Direction.DOWN]
            self.up_requests.sort()
            self.down_requests.sort(reverse=True)
            logging.info(f"Loaded system requests: Up - {self.up_requests}, Down - {self.down_requests}")
        else:
            self.database_manager.save_system_requests([]) # Save empty lists initially

    def add_request(self, floor: int, direction: Direction) -> None:
        """Adds a new hall call request."""
        if direction == Direction.UP:
            with self._up_requests_lock:
                if floor not in self.up_requests:
                    self.up_requests.append(floor)
                    self.up_requests.sort()
        elif direction == Direction.DOWN:
            with self._down_requests_lock:
                if floor not in self.down_requests:
                    self.down_requests.append(floor)
                    self.down_requests.sort(reverse=True)

    def remove_request(self, floor: int, direction: Direction) -> None:
        """Removes a fulfilled hall call request."""
        if direction == Direction.UP:
            with self._up_requests_lock:
                if floor in self.up_requests:
                    self.up_requests.remove(floor)
        elif direction == Direction.DOWN:
            with self._down_requests_lock:
                if floor in self.down_requests:
                    self.down_requests.remove(floor)

    def get_up_requests(self) -> list[int]:
        """Returns a copy of the current up requests."""
        with self._up_requests_lock:
            return self.up_requests[:]

    def get_down_requests(self) -> list[int]:
        """Returns a copy of the current down requests."""
        with self._down_requests_lock:
            return self.down_requests[:]

    def get_all_requests_for_persistence(self) -> list[tuple[int, Direction]]:
        """Returns all requests in a format suitable for persistence."""
        all_requests = []
        with self._up_requests_lock:
            for floor in self.up_requests:
                all_requests.append((floor, Direction.UP))
        with self._down_requests_lock:
            for floor in self.down_requests:
                all_requests.append((floor, Direction.DOWN))
        return all_requests

    def save_requests_to_db(self) -> None:
        """Saves the current system-wide hall call requests to the database."""
        self.database_manager.save_system_requests(self.get_all_requests_for_persistence())
