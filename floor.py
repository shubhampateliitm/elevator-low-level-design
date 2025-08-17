from elevator_panel import HallPanel
from display import Display
from observer import Subject

class Floor:
    def __init__(self, floor_number, top_floor):
        self.floor_number = floor_number
        self.panel = HallPanel(floor_number, top_floor)
        self.display = Display()

    def get_floor_number(self):
        return self.floor_number

    def get_panel(self):
        return self.panel

    def get_display(self):
        return self.display
