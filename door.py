from enums import DoorState

class Door:
    """Represents an elevator door, managing its open and closed states."""
    def __init__(self) -> None:
        """Initializes a new Door instance with its state set to CLOSED."""
        self.state = DoorState.CLOSED

    def open(self) -> None:
        """Opens the elevator door."""
        self.state = DoorState.OPEN

    def close(self) -> None:
        """Closes the elevator door."""
        self.state = DoorState.CLOSED

    def get_state(self) -> DoorState:
        """Gets the current state of the door.

        Returns:
            DoorState: The current state of the door (OPEN or CLOSED).
        """
        return self.state

    def is_open(self) -> bool:
        """Checks if the door is currently open.

        Returns:
            bool: True if the door is open, False otherwise.
        """
        return self.state == DoorState.OPEN
