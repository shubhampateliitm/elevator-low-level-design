
from abc import ABC, abstractmethod
import time
from enums import Direction, DoorState

class ElevatorState(ABC):
    def __init__(self, car):
        self.car = car

    def _handle_current_floor_request(self):
        self.car._open_door_at_current_floor()
        self.car.notify("request_fulfilled", {"floor": self.car.current_floor})

    @abstractmethod
    def move(self):
        pass

    @abstractmethod
    def register_request(self, floor):
        pass

class IdleState(ElevatorState):
    def move(self):
        if self.car.up_requests:
            self.car.direction = Direction.UP
            self.car.state = MovingUpState(self.car)
        elif self.car.down_requests:
            self.car.direction = Direction.DOWN
            self.car.state = MovingDownState(self.car)

    def register_request(self, floor):
        if floor > self.car.current_floor:
            self.car.up_requests.append(floor)
            self.car.up_requests.sort()
        elif floor < self.car.current_floor:
            self.car.down_requests.append(floor)
            self.car.down_requests.sort(reverse=True)
        else:
            self._handle_current_floor_request()

class MovingUpState(ElevatorState):
    def move(self):
        if not self.car.up_requests:
            self.car.state = IdleState(self.car)
            self.car.direction = Direction.STOP
            return

        destination = self.car.up_requests[0]
        if self.car.current_floor < destination:
            self.car.current_floor += 1
        
        if self.car.current_floor == destination:
            self.car.up_requests.pop(0)
            self.car._open_door_at_current_floor()
            self.car.notify("request_fulfilled", {"floor": self.car.current_floor})
            if not self.car.up_requests:
                if self.car.down_requests:
                    self.car.direction = Direction.DOWN
                    self.car.state = MovingDownState(self.car)
                else:
                    self.car.state = IdleState(self.car)
                    self.car.direction = Direction.STOP

    def register_request(self, floor):
        if floor == self.car.current_floor:
            self._handle_current_floor_request()
        elif floor > self.car.current_floor:
            if floor not in self.car.up_requests:
                self.car.up_requests.append(floor)
                self.car.up_requests.sort()
        # Ignore requests for floors below the current floor while moving up

class MovingDownState(ElevatorState):
    def move(self):
        if not self.car.down_requests:
            self.car.state = IdleState(self.car)
            self.car.direction = Direction.STOP
            return

        destination = self.car.down_requests[0]
        if self.car.current_floor > destination:
            self.car.current_floor -= 1

        if self.car.current_floor == destination:
            self.car.down_requests.pop(0)
            self.car._open_door_at_current_floor()
            self.car.notify("request_fulfilled", {"floor": self.car.current_floor})
            if not self.car.down_requests:
                if self.car.up_requests:
                    self.car.direction = Direction.UP
                    self.car.state = MovingUpState(self.car)
                else:
                    self.car.state = IdleState(self.car)
                    self.car.direction = Direction.STOP

    def register_request(self, floor):
        if floor == self.car.current_floor:
            self._handle_current_floor_request()
        elif floor < self.car.current_floor:
            if floor not in self.car.down_requests:
                self.car.down_requests.append(floor)
                self.car.down_requests.sort(reverse=True)
        # Ignore requests for floors above the current floor while moving down

class MaintenanceState(ElevatorState):
    def move(self):
        # Do nothing in maintenance mode
        pass

    def register_request(self, floor):
        # Do not accept requests in maintenance mode
        pass
