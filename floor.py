from elevator_panel import HallPanel
from display import Display
from observer import Subject
from elevator_component_factory import ElevatorComponentFactory # Import the new factory

class Floor:
    """Represents a floor in the building, including its hall panel and display."""
    def __init__(self, floor_number: int, top_floor: int, factory: ElevatorComponentFactory = None) -> None:
        """Initializes a new Floor instance.

        Args:
            floor_number (int): The number of this floor.
            top_floor (int): The highest floor number in the building.
        """
        self.floor_number = floor_number
        self.factory = factory if factory else ElevatorComponentFactory() # Store the factory
        self.panel = self.factory.create_hall_panel(floor_number, top_floor)
        self.display = self.factory.create_floor_display()

    def get_floor_number(self) -> int:
        """Gets the number of this floor.

        Returns:
            int: The floor number.
        """
        return self.floor_number

    def get_panel(self) -> HallPanel:
        """Gets the hall panel for this floor.

        Returns:
            HallPanel: The HallPanel instance for this floor.
        """
        return self.panel

    def get_display(self) -> Display:
        """Gets the display for this floor.

        Returns:
            Display: The Display instance for this floor.
        """
        return self.display
