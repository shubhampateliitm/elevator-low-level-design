from abc import ABC, abstractmethod

from enums import Direction


class Button(ABC):
    def __init__(self):
        self.pressed = False

    def press_down(self):
        pass

    def reset(self):
        pass

    @abstractmethod
    def is_pressed(self):
        pass


class DoorButton(Button):
    def is_pressed(self):
        return self.pressed
    

class HallButton(Button):

    def __init__(self, direction:Direction):
        self.direction = direction
        super().__init__()

    def is_pressed(self):
        return False
    
    def get_direction(self):
        return self.direction
    

class ElevatorButton(Button):
    def __init__(self, floor:int):
        super().__init__()
        self.destination_floor = floor

    def get_destination_floor(self):
        return self.destination_floor
    
    def is_pressed(self):
        return False
    

class EmergencyButton(Button):
    def is_pressed(self):
        return False
    
    def set_pressed(self, val):
        pass

    def get_pressed(self):
        return False
    
