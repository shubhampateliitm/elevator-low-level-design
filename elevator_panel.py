from button import ElevatorButton, DoorButton, EmergencyButton, HallButton
from enums import Direction


class ElevatorPanel:
    """Represents the control panel inside an elevator car."""

    def __init__(self, num_floors: int) -> None:
        """Initializes a new ElevatorPanel instance.

        Args:
            num_floors (int): The total number of floors in the building.
        """
        self.floor_buttons = [ElevatorButton(i) for i in range(num_floors)]
        self.open_button = DoorButton()
        self.close_button = DoorButton()
        self.emergency_button = EmergencyButton()

    def get_floor_buttons(self) -> list[ElevatorButton]:
        """Gets the list of floor selection buttons.

        Returns:
            list[ElevatorButton]: A list of ElevatorButton instances.
        """
        return self.floor_buttons

    def get_open_button(self) -> DoorButton:
        """Gets the door open button.

        Returns:
            DoorButton: The DoorButton instance for opening the door.
        """
        return self.open_button

    def get_close_button(self) -> DoorButton:
        """Gets the door close button.

        Returns:
            DoorButton: The DoorButton instance for closing the door.
        """
        return self.close_button

    def get_emergency_button(self) -> EmergencyButton:
        """Gets the emergency button.

        Returns:
            EmergencyButton: The EmergencyButton instance.
        """
        return self.emergency_button

    def press_floor_button(self, floor_number: int) -> None:
        """Simulates pressing a floor selection button.

        Args:
            floor_number (int): The number of the floor button to press.
        """
        self.floor_buttons[floor_number].press_down()

    def press_open_button(self) -> None:
        """Simulates pressing the door open button."""
        self.open_button.press_down()

    def press_close_button(self) -> None:
        """Simulates pressing the door close button."""
        self.close_button.press_down()

    def press_emergency_button(self) -> None:
        """Simulates pressing the emergency button."""
        self.emergency_button.press_down()


class HallPanel:
    """Represents a hall panel on a specific floor, with up and down call buttons."""
    def __init__(self, floor_number: int, top_floor: int) -> None:
        """Initializes a new HallPanel instance.

        Args:
            floor_number (int): The number of the floor this panel is on.
            top_floor (int): The highest floor number in the building.
        """
        self.floor_number = floor_number
        self.up = None
        self.down = None
        if floor_number < top_floor:
            self.up = HallButton(Direction.UP)
        if floor_number > 0:
            self.down = HallButton(Direction.DOWN)

    def get_up_button(self) -> HallButton | None:
        """Gets the up call button for this floor.

        Returns:
            HallButton | None: The HallButton instance for UP, or None if not available (e.g., top floor).
        """
        return self.up

    def get_down_button(self) -> HallButton | None:
        """Gets the down call button for this floor.

        Returns:
            HallButton | None: The HallButton instance for DOWN, or None if not available (e.g., ground floor).
        """
        return self.down

    def press_up_button(self) -> None:
        """Simulates pressing the up call button."""
        if self.up:
            self.up.press_down()

    def press_down_button(self) -> None:
        """Simulates pressing the down call button."""
        if self.down:
            self.down.press_down()

    def __repr__(self) -> str:
        """Returns a string representation of the HallPanel.

        Returns:
            str: A string like "HallPanel(floor=X)".
        """
        return f"HallPanel(floor={self.floor_number})"
