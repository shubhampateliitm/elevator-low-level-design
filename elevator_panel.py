from button import ElevatorButton, DoorButton, EmergencyButton, HallButton
from enums import Direction


class ElevatorPanel:

    def __init__(self, num_floors):
        self.floor_buttons = [ElevatorButton(i) for i in range(num_floors)]
        self.open_button = DoorButton()
        self.close_button = DoorButton()
        self.emergency_button = EmergencyButton()

    def get_floor_buttons(self):
        return self.floor_buttons

    def get_open_button(self):
        return self.open_button

    def get_close_button(self):
        return self.close_button

    def get_emergency_button(self):
        return self.emergency_button

    def press_floor_button(self, floor_number):
        self.floor_buttons[floor_number].press_down()

    def press_open_button(self):
        self.open_button.press_down()

    def press_close_button(self):
        self.close_button.press_down()

    def press_emergency_button(self):
        self.emergency_button.press_down()


class HallPanel:
    def __init__(self, floor_number, top_floor):
        self.floor_number = floor_number
        self.up = None
        self.down = None
        if floor_number < top_floor:
            self.up = HallButton(Direction.UP)
        if floor_number > 0:
            self.down = HallButton(Direction.DOWN)

    def get_up_button(self):
        return self.up

    def get_down_button(self):
        return self.down

    def press_up_button(self):
        if self.up:
            self.up.press_down()

    def press_down_button(self):
        if self.down:
            self.down.press_down()

    def __repr__(self):
        return f"HallPanel(floor={self.floor_number})"
