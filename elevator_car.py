from enums import Direction, DoorState
from door import Door
from elevator_panel import ElevatorPanel
from display import Display
from elevator_state import IdleState, MaintenanceState, MovingUpState, MovingDownState
from elevator_state_factory import ElevatorStateFactory # Import ElevatorStateFactory
import time
from time_provider import TimeProvider
from observer import Subject
from database_manager import DatabaseManager # Import DatabaseManager
import logging
from commands import Command # Import Command

class ElevatorCar(Subject):
    """Represents an individual elevator car in the system."""
    def __init__(self,
                 car_id: int,
                 num_floors: int,
                 door_open_duration: float,
                 time_provider: TimeProvider,
                 door: Door,
                 panel: ElevatorPanel,
                 display: Display,
                 database_manager: DatabaseManager) -> None:
        """Initializes a new ElevatorCar instance.

        Args:
            car_id (int): Unique identifier for the elevator car.
            num_floors (int): Total number of floors in the building.
            door_open_duration (float): Duration (in seconds) the door stays open.
            time_provider (TimeProvider): An object providing time-related functionalities.
            door (Door): The door mechanism of the elevator car.
            panel (ElevatorPanel): The control panel inside the elevator car.
            display (Display): The display unit inside the elevator car.
            database_manager (DatabaseManager): Manager for database operations.
        """
        self.car_id = car_id
        self.num_floors = num_floors
        self.door_open_duration = door_open_duration
        self.time_provider = time_provider
        self.door = door
        self.panel = panel
        self.display = display
        self._observers = []
        self.database_manager = database_manager

        # Load state from DB or initialize
        loaded_car_state = self.database_manager.load_car_state(self.car_id)
        if loaded_car_state:
            self.current_floor = loaded_car_state["current_floor"]
            self.direction = loaded_car_state["direction"]
            # Re-instantiate state object using the factory
            state_str = loaded_car_state["current_state"]
            self.state = ElevatorStateFactory.create_state(state_str, self)
            self.door.state = loaded_car_state["door_state"]
            self.door_open_time = loaded_car_state["door_open_time"]
            logging.info(f"Loaded car {self.car_id} state: Floor {self.current_floor}, Dir {self.direction.name}, State {state_str}")
        else:
            self.current_floor = 0
            self.direction = Direction.STOP
            self.up_requests = []
            self.down_requests = []
            self.state = IdleState(self)
            self.door_open_time = 0
            logging.info(f"Initialized new car {self.car_id} state.")
        
        # Load requests from DB
        loaded_requests = self.database_manager.load_car_requests(self.car_id)
        self.up_requests = [req[0] for req in loaded_requests if req[1] == Direction.UP]
        self.down_requests = [req[0] for req in loaded_requests if req[1] == Direction.DOWN]
        self.up_requests.sort()
        self.down_requests.sort(reverse=True)
        if loaded_requests:
            logging.info(f"Loaded car {self.car_id} requests: Up - {self.up_requests}, Down - {self.down_requests}")

        # Initial state will be saved by a higher-level orchestrator

    def save_state(self) -> None:
        """Saves the current state and requests of the elevator car to the database."""
        self.database_manager.save_car_state(
            self.car_id,
            self.current_floor,
            self.direction,
            self.state.__class__.__name__,
            self.door.get_state(),
            self.door_open_time
        )
        all_car_requests = []
        for floor in self.up_requests:
            all_car_requests.append((floor, Direction.UP))
        for floor in self.down_requests:
            all_car_requests.append((floor, Direction.DOWN))
        self.database_manager.save_car_requests(self.car_id, all_car_requests)

    def _open_door_at_current_floor(self) -> None:
        """Opens the door and records the time."""
        self.door.open()
        self.door_open_time = self.time_provider.get_time()

    def get_id(self) -> int:
        """Gets the ID of the elevator car.

        Returns:
            int: The car's ID.
        """
        return self.car_id

    def get_current_floor(self) -> int:
        """Gets the current floor of the elevator car.

        Returns:
            int: The current floor number.
        """
        return self.current_floor

    def get_state(self) -> object:
        """Gets the current state object of the elevator car.

        Returns:
            object: The current state object (e.g., IdleState, MovingUpState).
        """
        return self.state

    def is_idle(self) -> bool:
        """Checks if the elevator car is in an idle state.

        Returns:
            bool: True if the car is idle, False otherwise.
        """
        return isinstance(self.state, IdleState)

    def get_direction(self) -> Direction:
        """Gets the current direction of the elevator car.

        Returns:
            Direction: The current direction (UP, DOWN, STOP).
        """
        return self.direction

    def get_up_requests(self) -> list[int]:
        """Gets the list of pending up requests for the elevator car.

        Returns:
            list[int]: A sorted list of floors for up requests.
        """
        return self.up_requests

    def get_down_requests(self) -> list[int]:
        """Gets the list of pending down requests for the elevator car.

        Returns:
            list[int]: A sorted list of floors for down requests.
        """
        return self.down_requests

    def set_direction(self, direction: Direction) -> None:
        """Sets the direction of the elevator car.

        Args:
            direction (Direction): The new direction.
        """
        self.direction = direction

    def set_state(self, new_state: object) -> None:
        """Sets the state of the elevator car.

        Args:
            new_state (object): The new state object (e.g., IdleState, MovingUpState).
        """
        self.state = new_state

    def increment_floor(self) -> None:
        """Increments the current floor of the elevator car."""
        self.current_floor += 1

    def decrement_floor(self) -> None:
        """Decrements the current floor of the elevator car."""
        self.current_floor -= 1

    def add_up_request(self, floor: int) -> None:
        """Adds an up request to the elevator car's requests.

        Args:
            floor (int): The floor number to add.
        """
        if floor not in self.up_requests:
            self.up_requests.append(floor)
            self.up_requests.sort()

    def add_down_request(self, floor: int) -> None:
        """Adds a down request to the elevator car's requests.

        Args:
            floor (int): The floor number to add.
        """
        if floor not in self.down_requests:
            self.down_requests.append(floor)
            self.down_requests.sort(reverse=True)

    def remove_up_request(self, floor: int) -> None:
        """Removes an up request from the elevator car's requests.

        Args:
            floor (int): The floor number to remove.
        """
        if floor in self.up_requests:
            self.up_requests.remove(floor)

    def remove_down_request(self, floor: int) -> None:
        """Removes a down request from the elevator car's requests.

        Args:
            floor (int): The floor number to remove.
        """
        if floor in self.down_requests:
            self.down_requests.remove(floor)

    def open_door_and_notify(self) -> None:
        """Opens the door, records the time, and notifies observers that a request was fulfilled."""
        self._open_door_at_current_floor()
        self.notify("request_fulfilled", {"floor": self.current_floor})

    def register_request(self, floor: int) -> None:
        """Registers a new request for the elevator car.

        Args:
            floor (int): The floor number to register as a request.
        """
        commands = self.state.register_request(floor)
        command_map = {
            Command.ADD_UP_REQUEST: self.add_up_request,
            Command.ADD_DOWN_REQUEST: self.add_down_request,
            Command.OPEN_DOOR_AND_NOTIFY: self.open_door_and_notify,
        }
        for command, *args in commands:
            if command in command_map:
                command_map[command](*args)
            else:
                logging.warning(f"Unknown command received in register_request: {command}")
        # State will be saved by a higher-level orchestrator

    def move(self) -> None:
        """Executes one step of the elevator car's movement logic.
        Handles door operations and delegates movement to the current state.
        """
        # If door is open and enough time has passed, close it
        if self.door.get_state() == DoorState.OPEN and (self.time_provider.get_time() - self.door_open_time) > self.door_open_duration:
            self.door.close()
            self.door_open_time = 0
            # State will be saved by a higher-level orchestrator

        # If door is closed, proceed with state-based movement
        if self.door.get_state() == DoorState.CLOSED:
            commands = self.state.move()
            command_map = {
                Command.SET_DIRECTION: self.set_direction,
                Command.SET_STATE: self.set_state,
                Command.INCREMENT_FLOOR: self.increment_floor,
                Command.DECREMENT_FLOOR: self.decrement_floor,
                Command.OPEN_DOOR_AND_NOTIFY: self.open_door_and_notify,
                Command.REMOVE_UP_REQUEST: self.remove_up_request,
                Command.REMOVE_DOWN_REQUEST: self.remove_down_request,
            }
            for command, *args in commands:
                if command in command_map:
                    command_map[command](*args)
                else:
                    logging.warning(f"Unknown command received in move: {command}")
            # State will be saved by a higher-level orchestrator

        # Update display after potential state/floor/direction change
        self.display.update(self.current_floor, self.direction, self.state)

    def show_display(self) -> None:
        """Instructs the elevator's display to show its current information."""
        self.display.show_elevator_display(self.car_id)

    def enter_maintenance(self) -> None:
        """Sets the elevator car to maintenance mode."""
        self.state = MaintenanceState(self)
        # State will be saved by a higher-level orchestrator

    def exit_maintenance(self) -> None:
        """Exits maintenance mode and sets the elevator car to idle."""
        self.state = IdleState(self)
        # State will be saved by a higher-level orchestrator

    def attach(self, observer: object) -> None:
        """Attaches an observer to this subject.

        Args:
            observer (object): The observer to attach.
        """
        self._observers.append(observer)

    def detach(self, observer: object) -> None:
        """Detaches an observer from this subject.

        Args:
            observer (object): The observer to detach.
        """
        self._observers.remove(observer)

    def notify(self, event: str, data: dict = None) -> None:
        """Notifies all attached observers about an event.

        Args:
            event (str): The type of event that occurred.
            data (dict, optional): Additional data related to the event. Defaults to None.
        """
        for observer in self._observers:
            observer.update(self, event, data)
