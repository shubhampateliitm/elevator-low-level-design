from enums import Direction
from elevator_state import IdleState

class Display:
    def __init__(self):
        self.floor = 0
        self.direction = Direction.STOP
        self.state = IdleState(None)  # Initial state, car reference can be updated later

    def update(self, floor, direction, state):
        self.floor = floor
        self.direction = direction
        self.state = state

    def show_elevator_display(self, car_id):
        print(f"Elevator {car_id} Display: Floor - {self.floor}, Direction - {self.direction.name}, State - {self.state.__class__.__name__}")
