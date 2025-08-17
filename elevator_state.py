
from abc import ABC, abstractmethod
from typing import List, Tuple, Any
from enums import Direction, DoorState
from commands import Command

class ElevatorState(ABC):
    """Abstract base class for all states of an elevator car (State pattern)."""
    def __init__(self, car: object) -> None:
        """Initializes an ElevatorState instance.

        Args:
            car (object): The ElevatorCar instance this state belongs to.
        """
        self.car = car

    @abstractmethod
    def move(self) -> List[Tuple[Command, Any]]:
        """Abstract method to define the movement behavior for the current state.
        Returns a list of commands for the ElevatorCar to execute.
        """
        pass

    @abstractmethod
    def register_request(self, floor: int) -> List[Tuple[Command, Any]]:
        """Abstract method to define how a new request is handled in the current state.
        Returns a list of commands for the ElevatorCar to execute.

        Args:
            floor (int): The floor number of the new request.
        """
        pass

class IdleState(ElevatorState):
    """Represents the idle state of an elevator car."""
    def move(self) -> List[Tuple[Command, Any]]:
        """Determines the next movement based on pending requests when idle."""
        commands = []
        if self.car.get_up_requests():
            commands.append((Command.SET_DIRECTION, Direction.UP))
            commands.append((Command.SET_STATE, MovingUpState(self.car)))
        elif self.car.get_down_requests():
            commands.append((Command.SET_DIRECTION, Direction.DOWN))
            commands.append((Command.SET_STATE, MovingDownState(self.car)))
        return commands

    def register_request(self, floor: int) -> List[Tuple[Command, Any]]:
        """Registers a new request when the elevator is idle.

        Args:
            floor (int): The floor number of the new request.
        """
        commands = []
        current_floor = self.car.get_current_floor()
        if floor > current_floor:
            commands.append((Command.ADD_UP_REQUEST, floor))
        elif floor < current_floor:
            commands.append((Command.ADD_DOWN_REQUEST, floor))
        else:
            commands.append((Command.OPEN_DOOR_AND_NOTIFY,))
        return commands

class MovingUpState(ElevatorState):
    """Represents the state of an elevator car moving upwards."""
    def move(self) -> List[Tuple[Command, Any]]:
        """Moves the elevator car one floor up, handling stops at requested floors."""
        commands = []
        up_requests = self.car.get_up_requests()
        current_floor = self.car.get_current_floor()

        if not up_requests:
            commands.append((Command.SET_STATE, IdleState(self.car)))
            commands.append((Command.SET_DIRECTION, Direction.STOP))
            return commands

        destination = up_requests[0]
        if current_floor < destination:
            commands.append((Command.INCREMENT_FLOOR,))
        
        if current_floor + 1 == destination: # Check if next floor is destination
            commands.append((Command.REMOVE_UP_REQUEST, destination))
            commands.append((Command.OPEN_DOOR_AND_NOTIFY,))
            if len(up_requests) == 1: # Check if this is the last up request
                if self.car.get_down_requests():
                    commands.append((Command.SET_DIRECTION, Direction.DOWN))
                    commands.append((Command.SET_STATE, MovingDownState(self.car)))
                else:
                    commands.append((Command.SET_STATE, IdleState(self.car)))
                    commands.append((Command.SET_DIRECTION, Direction.STOP))
        return commands

    def register_request(self, floor: int) -> List[Tuple[Command, Any]]:
        """Registers a new request when the elevator is moving upwards.

        Args:
            floor (int): The floor number of the new request.
        """
        commands = []
        current_floor = self.car.get_current_floor()
        if floor == current_floor:
            commands.append((Command.OPEN_DOOR_AND_NOTIFY,))
        elif floor > current_floor:
            commands.append((Command.ADD_UP_REQUEST, floor))
        # Ignore requests for floors below the current floor while moving up
        return commands

class MovingDownState(ElevatorState):
    """Represents the state of an elevator car moving downwards."""
    def move(self) -> List[Tuple[Command, Any]]:
        """Moves the elevator car one floor down, handling stops at requested floors."""
        commands = []
        down_requests = self.car.get_down_requests()
        current_floor = self.car.get_current_floor()

        if not down_requests:
            commands.append((Command.SET_STATE, IdleState(self.car)))
            commands.append((Command.SET_DIRECTION, Direction.STOP))
            return commands

        destination = down_requests[0]
        if current_floor > destination:
            commands.append((Command.DECREMENT_FLOOR,))

        if current_floor - 1 == destination: # Check if next floor is destination
            commands.append((Command.REMOVE_DOWN_REQUEST, destination))
            commands.append((Command.OPEN_DOOR_AND_NOTIFY,))
            if len(down_requests) == 1: # Check if this is the last down request
                if self.car.get_up_requests():
                    commands.append((Command.SET_DIRECTION, Direction.UP))
                    commands.append((Command.SET_STATE, MovingUpState(self.car)))
                else:
                    commands.append((Command.SET_STATE, IdleState(self.car)))
                    commands.append((Command.SET_DIRECTION, Direction.STOP))
        return commands

    def register_request(self, floor: int) -> List[Tuple[Command, Any]]:
        """Registers a new request when the elevator is moving downwards.

        Args:
            floor (int): The floor number of the new request.
        """
        commands = []
        current_floor = self.car.get_current_floor()
        if floor == current_floor:
            commands.append((Command.OPEN_DOOR_AND_NOTIFY,))
        elif floor < current_floor:
            commands.append((Command.ADD_DOWN_REQUEST, floor))
        # Ignore requests for floors above the current floor while moving down
        return commands

class MaintenanceState(ElevatorState):
    """Represents the maintenance state of an elevator car."""
    def move(self) -> List[Tuple[Command, Any]]:
        """In maintenance mode, the elevator does not move."""
        return [] # Do nothing in maintenance mode

    def register_request(self, floor: int) -> List[Tuple[Command, Any]]:
        """In maintenance mode, the elevator does not accept new requests.

        Args:
            floor (int): The floor number of the new request.
        """
        return [] # Do not accept requests in maintenance mode
