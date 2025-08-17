from enums import Direction
# No longer need to import IdleState here as we store state as string

class Display:
    """Represents the display panel inside an elevator car, showing current floor, direction, and state."""
    def __init__(self) -> None:
        """Initializes a new Display instance.

        Attributes:
            floor (int): The current floor number displayed.
            direction (Direction): The current direction displayed (UP, DOWN, STOP).
            state (str): The current operational state of the elevator (e.g., "IdleState", "MovingUpState").
        """
        self.floor = 0
        self.direction = Direction.STOP
        self.state = None  # Will be set by ElevatorCar's initial update

    def update(self, floor: int, direction: Direction, state: object) -> None:
        """Updates the display with new elevator information.

        Args:
            floor (int): The new current floor number.
            direction (Direction): The new direction.
            state (object): The current state object of the elevator car. Its class name will be used for display.
        """
        self.floor = floor
        self.direction = direction
        self.state = state # Store the actual state object

    def show_elevator_display(self, car_id: int) -> None:
        """Prints the current display information to the console.

        Args:
            car_id (int): The ID of the elevator car this display belongs to.
        """
        print(f"Elevator {car_id} Display: Floor - {self.floor}, Direction - {self.direction.name}, State - {self.state.__class__.__name__}")
