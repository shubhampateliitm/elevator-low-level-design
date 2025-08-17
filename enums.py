from enum import Enum


class Direction(Enum):
    """Represents the direction of elevator movement."""
    UP = 1
    DOWN = 2
    STOP = 3

class DoorState(Enum):
    """Represents the state of an elevator door."""
    OPEN = 1
    CLOSED = 2


