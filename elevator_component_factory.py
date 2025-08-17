from door import Door
from elevator_panel import ElevatorPanel, HallPanel
from display import Display
from time_provider import TimeProvider
from database_manager import DatabaseManager
from config import DOOR_OPEN_DURATION

class ElevatorComponentFactory:
    """
    A factory class for creating and providing elevator components.
    This helps in decoupling the creation of components from their usage,
    making the system more flexible and testable.
    """
    def create_door(self) -> Door:
        return Door()

    def create_elevator_panel(self, num_floors: int) -> ElevatorPanel:
        return ElevatorPanel(num_floors)

    def create_display(self) -> Display:
        return Display()

    def create_time_provider(self) -> TimeProvider:
        return TimeProvider()

    def get_door_open_duration(self) -> float:
        return DOOR_OPEN_DURATION

    def create_elevator_car_dependencies(self, num_floors: int, database_manager: DatabaseManager) -> dict:
        """
        Creates and returns a dictionary of dependencies required for an ElevatorCar.
        """
        return {
            "door": self.create_door(),
            "panel": self.create_elevator_panel(num_floors),
            "display": self.create_display(),
            "time_provider": self.create_time_provider(),
            "door_open_duration": self.get_door_open_duration(),
            "database_manager": database_manager
        }

    def create_hall_panel(self, floor_number: int, top_floor: int) -> HallPanel:
        """
        Creates and returns a HallPanel instance.
        """
        return HallPanel(floor_number, top_floor)

    def create_floor_display(self) -> Display:
        """
        Creates and returns a Display instance for a floor.
        """
        return Display()
