from enums import Direction, DoorState
from door import Door
from elevator_panel import ElevatorPanel
from display import Display
from elevator_state import IdleState, MaintenanceState
import time
from time_provider import TimeProvider
from observer import Subject

class ElevatorCar(Subject):
    def __init__(self, car_id, num_floors, door_open_duration=2, time_provider=None, door=None, panel=None, display=None):
        self.car_id = car_id
        self.num_floors = num_floors
        self.current_floor = 0
        self.direction = Direction.STOP
        self.door = door if door else Door() # Injected or default
        self.panel = panel if panel else ElevatorPanel(num_floors) # Injected or default
        self.display = display if display else Display() # Injected or default
        self.up_requests = []
        self.down_requests = []
        self.state = IdleState(self)
        self.door_open_time = 0 # To track when the door was opened
        self.door_open_duration = door_open_duration # Configurable door open duration
        self.time_provider = time_provider if time_provider else TimeProvider()
        self._observers = [] # List of observers

    def _open_door_at_current_floor(self):
        """Opens the door and records the time."""
        self.door.open()
        self.door_open_time = self.time_provider.get_time()

    def get_id(self):
        return self.car_id

    def get_current_floor(self):
        return self.current_floor

    def get_state(self):
        return self.state

    def is_idle(self):
        return isinstance(self.state, IdleState)

    def register_request(self, floor):
        self.state.register_request(floor)

    def move(self):
        # If door is open and enough time has passed, close it
        if self.door.get_state() == DoorState.OPEN and (self.time_provider.get_time() - self.door_open_time) > self.door_open_duration: # Use configurable duration
            self.door.close()
            self.door_open_time = 0 # Reset

        # If door is closed, proceed with state-based movement
        if self.door.get_state() == DoorState.CLOSED:
            self.state.move()
        
        # Update display after potential state/floor/direction change
        self.display.update(self.current_floor, self.direction, self.state)

    def show_display(self):
        self.display.show_elevator_display(self.car_id)

    def enter_maintenance(self):
        self.state = MaintenanceState(self)

    def exit_maintenance(self):
        self.state = IdleState(self)

    def attach(self, observer) -> None:
        self._observers.append(observer)

    def detach(self, observer) -> None:
        self._observers.remove(observer)

    def notify(self, event: str, data: dict = None) -> None:
        for observer in self._observers:
            observer.update(self, event, data)
