class Display:

    def __init__(self):
        self.floor = 0
        self.load = 0
        self.direction = None
        self.state = None
        self.maintenance = False
        self.overloaded = False

    def update(self, f, direction, load, state, overloaded, maintenance):
        pass

    def show_elevator_display(self, car_id):
        pass