from abc import ABC, abstractmethod
from enums import Direction

class Button(ABC):
    """Abstract base class for all buttons in the elevator system."""
    def __init__(self) -> None:
        """Initializes a new Button instance.

        Attributes:
            pressed (bool): True if the button is pressed, False otherwise.
        """
        self.pressed = False

    def press_down(self) -> None:
        """Sets the button's state to pressed."""
        self.pressed = True

    def reset(self) -> None:
        """Resets the button's state to not pressed."""
        self.pressed = False

    @abstractmethod
    def is_pressed(self) -> bool:
        """Abstract method to check if the button is currently pressed.

        Returns:
            bool: True if the button is pressed, False otherwise.
        """
        pass

class DoorButton(Button):
    """Represents a button for controlling the elevator door (open/close)."""
    def is_pressed(self) -> bool:
        """Checks if the door button is currently pressed.

        Returns:
            bool: True if the button is pressed, False otherwise.
        """
        return self.pressed

class HallButton(Button):
    """Represents a button on a floor's hall panel (up/down call button)."""
    def __init__(self, direction: Direction) -> None:
        """Initializes a new HallButton instance.

        Args:
            direction (Direction): The direction this hall button is for (UP or DOWN).
        """
        super().__init__()
        self.direction = direction

    def is_pressed(self) -> bool:
        """Checks if the hall button is currently pressed.

        Returns:
            bool: True if the button is pressed, False otherwise.
        """
        return self.pressed

    def get_direction(self) -> Direction:
        """Gets the direction associated with this hall button.

        Returns:
            Direction: The direction (UP or DOWN) of the hall call.
        """
        return self.direction

class ElevatorButton(Button):
    """Represents a button inside the elevator car for selecting a destination floor."""
    def __init__(self, floor: int) -> None:
        """Initializes a new ElevatorButton instance.

        Args:
            floor (int): The destination floor number this button represents.
        """
        super().__init__()
        self.destination_floor = floor

    def get_destination_floor(self) -> int:
        """Gets the destination floor number for this elevator button.

        Returns:
            int: The destination floor number.
        """
        return self.destination_floor

    def is_pressed(self) -> bool:
        """Checks if the elevator button is currently pressed.

        Returns:
            bool: True if the button is pressed, False otherwise.
        """
        return self.pressed

class EmergencyButton(Button):
    """Represents an emergency button inside the elevator car."""
    def is_pressed(self) -> bool:
        """Checks if the emergency button is currently pressed.

        Returns:
            bool: True if the button is pressed, False otherwise.
        """
        return self.pressed
