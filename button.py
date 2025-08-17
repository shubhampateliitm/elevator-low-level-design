from abc import ABC, abstractmethod
from enums import Direction

class Button(ABC):
    def __init__(self):
        self.pressed = False

    def press_down(self):
        self.pressed = True

    def reset(self):
        self.pressed = False

    @abstractmethod
    def is_pressed(self):
        pass

class DoorButton(Button):
    def is_pressed(self):
        return self.pressed

class HallButton(Button):
    def __init__(self, direction: Direction):
        super().__init__()
        self.direction = direction

    def is_pressed(self):
        return self.pressed

    def get_direction(self):
        return self.direction

class ElevatorButton(Button):
    def __init__(self, floor: int):
        super().__init__()
        self.destination_floor = floor

    def get_destination_floor(self):
        return self.destination_floor

    def is_pressed(self):
        return self.pressed

class EmergencyButton(Button):
    def is_pressed(self):
        return self.pressed