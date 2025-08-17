from threading import Lock
from observer import Observer, Subject
from elevator_car import ElevatorCar
from floor import Floor
from enums import Direction
from dispatching_strategy import DispatchingStrategy, ClosestCarStrategy
from door import Door
from elevator_panel import ElevatorPanel
from display import Display

class ElevatorSystem(Observer):
    _instance = None
    _lock = Lock()

    def __init__(self, num_floors, num_cars, dispatching_strategy: DispatchingStrategy = None):
        self.num_floors = num_floors
        self.num_cars = num_cars
        self.cars = []
        for i in range(num_cars):
            car = self._create_elevator_car(i)
            self.cars.append(car)
        self.floors = [Floor(i, self.num_floors) for i in range(num_floors)]
        self.up_requests = []
        self.down_requests = []
        self.dispatching_strategy = dispatching_strategy if dispatching_strategy else ClosestCarStrategy()
        self._up_requests_lock = Lock() # New lock for up_requests
        self._down_requests_lock = Lock() # New lock for down_requests

        # Attach self as observer to each car
        for car in self.cars:
            car.attach(self)

    def _create_elevator_car(self, car_id):
        door = Door()
        panel = ElevatorPanel(self.num_floors)
        display = Display()
        car = ElevatorCar(car_id, self.num_floors, door=door, panel=panel, display=display)
        return car

    @classmethod
    def get_instance(cls, num_floors, num_cars, dispatching_strategy: DispatchingStrategy = None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = ElevatorSystem(num_floors, num_cars, dispatching_strategy)
            return cls._instance

    def get_cars(self):
        return self.cars

    def call_elevator(self, floor, direction):
        if direction == Direction.UP:
            with self._up_requests_lock: # Acquire lock
                if floor not in self.up_requests:
                    self.up_requests.append(floor)
                    self.up_requests.sort()
        elif direction == Direction.DOWN:
            with self._down_requests_lock: # Acquire lock
                if floor not in self.down_requests:
                    self.down_requests.append(floor)
                    self.down_requests.sort(reverse=True)

    def dispatcher(self):
        self._process_requests_for_direction(self.up_requests, self._up_requests_lock, Direction.UP)
        self._process_requests_for_direction(self.down_requests, self._down_requests_lock, Direction.DOWN)

    def _process_requests_for_direction(self, requests_list, lock, direction):
        with lock:
            if requests_list:
                requests_to_process = requests_list[:]
                for floor in requests_to_process:
                    best_car = self.dispatching_strategy.find_best_car(self.cars, floor, direction)
                    if best_car:
                        best_car.register_request(floor)

    def monitoring(self):
        for car in self.cars:
            car.show_display()

    def update(self, subject: Subject, event: str, data: dict = None) -> None:
        if event == "request_fulfilled":
            floor = data["floor"]
            # Remove the fulfilled request from the system's lists
            with self._up_requests_lock:
                if floor in self.up_requests:
                    self.up_requests.remove(floor)
            with self._down_requests_lock:
                if floor in self.down_requests:
                    self.down_requests.remove(floor)
