from threading import Lock
from observer import Observer, Subject
from elevator_car import ElevatorCar
from floor import Floor
from enums import Direction
from dispatching_strategy import DispatchingStrategy, ClosestCarStrategy
from door import Door
from elevator_panel import ElevatorPanel
from display import Display
from database_manager import DatabaseManager # Import DatabaseManager
from time_provider import TimeProvider # Import TimeProvider
import logging
from config import NUM_FLOORS, DOOR_OPEN_DURATION # Import configuration values
from elevator_component_factory import ElevatorComponentFactory # Import the new factory
from request_manager import RequestManager # Import the new RequestManager

class ElevatorSystem(Observer):
    """The central control system for managing multiple elevators and handling requests."""
    _instance = None
    _lock = Lock()

    def __init__(self,
                 num_floors: int,
                 num_cars: int,
                 dispatching_strategy: DispatchingStrategy = None,
                 database_manager: DatabaseManager = None,
                 factory: ElevatorComponentFactory = None) -> None:
        """Initializes the ElevatorSystem.

        Args:
            num_floors (int): The total number of floors in the building.
            num_cars (int): The number of elevator cars in the system.
            dispatching_strategy (DispatchingStrategy, optional): The strategy to use for dispatching elevators.
                                                                 Defaults to ClosestCarStrategy.
            database_manager (DatabaseManager, optional): The database manager instance. Defaults to a new DatabaseManager.
        """
        self.database_manager = database_manager if database_manager else DatabaseManager()
        self.factory = factory if factory else ElevatorComponentFactory() # Store the factory
        self.request_manager = RequestManager(self.database_manager) # Initialize RequestManager

        # Try to load system state from DB
        loaded_system_state = self.database_manager.load_system_state()
        if loaded_system_state:
            self.num_floors = loaded_system_state["num_floors"]
            self.num_cars = loaded_system_state["num_cars"]
            logging.info(f"Loaded system state: {self.num_floors} floors, {self.num_cars} cars")
        else:
            self.num_floors = NUM_FLOORS # Use config value
            self.num_cars = num_cars
            self.database_manager.save_system_state(self.num_floors, self.num_cars)
            logging.info(f"Initialized new system state: {self.num_floors} floors, {self.num_cars} cars")

        self.cars = []
        for i in range(self.num_cars):
            car = self._create_elevator_car(i, self.database_manager) # Pass database_manager
            self.cars.append(car)
        self.floors = [Floor(i, self.num_floors) for i in range(self.num_floors)]
        
        # Requests are now managed by RequestManager, so remove loading logic here
        # loaded_system_requests = self.database_manager.load_system_requests()
        # if loaded_system_requests:
        #     self.up_requests = [req[0] for req in loaded_system_requests if req[1] == Direction.UP]
        #     self.down_requests = [req[0] for req in loaded_system_requests if req[1] == Direction.DOWN]
        #     self.up_requests.sort()
        #     self.down_requests.sort(reverse=True)
        #     logging.info(f"Loaded system requests: Up - {self.up_requests}, Down - {self.down_requests}")
        # else:
        #     self.up_requests = []
        #     self.down_requests = []
        #     self.database_manager.save_system_requests([]) # Save empty lists initially

        self.dispatching_strategy = dispatching_strategy if dispatching_strategy else ClosestCarStrategy()
        # Locks are now managed by RequestManager
        # self._up_requests_lock = Lock()
        # self._down_requests_lock = Lock()

        # Attach self as observer to each car
        for car in self.cars:
            car.attach(self)

    def _create_elevator_car(self, car_id: int, database_manager: DatabaseManager) -> ElevatorCar:
        """Helper method to create and initialize an ElevatorCar instance.

        Args:
            car_id (int): The ID of the car to create.
            database_manager (DatabaseManager): The database manager instance.

        Returns:
            ElevatorCar: The newly created ElevatorCar instance.
        """
        car_dependencies = self.factory.create_elevator_car_dependencies(self.num_floors, database_manager)
        car = ElevatorCar(car_id=car_id, num_floors=self.num_floors, **car_dependencies)
        return car

    @classmethod
    def get_instance(cls) -> 'ElevatorSystem':
        """Returns the singleton instance of ElevatorSystem.

        Returns:
            ElevatorSystem: The singleton instance of ElevatorSystem.

        Raises:
            RuntimeError: If the ElevatorSystem has not been initialized yet.
        """
        with cls._lock:
            if cls._instance is None:
                raise RuntimeError("ElevatorSystem has not been initialized. Call ElevatorSystem.initialize() first.")
            return cls._instance

    @classmethod
    def initialize(cls, num_floors: int, num_cars: int, dispatching_strategy: DispatchingStrategy = None, database_manager: DatabaseManager = None, factory: ElevatorComponentFactory = None) -> 'ElevatorSystem':
        """Initializes the singleton instance of ElevatorSystem.

        Args:
            num_floors (int): The total number of floors in the building.
            num_cars (int): The number of elevator cars in the system.
            dispatching_strategy (DispatchingStrategy, optional): The strategy to use for dispatching elevators.
                                                                 Defaults to ClosestCarStrategy.
            database_manager (DatabaseManager, optional): The database manager instance. Defaults to a new DatabaseManager.

        Returns:
            ElevatorSystem: The newly initialized (or existing) singleton instance of ElevatorSystem.

        Raises:
            RuntimeError: If the ElevatorSystem has already been initialized with different parameters.
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = ElevatorSystem(num_floors, num_cars, dispatching_strategy, database_manager, factory)
            # Optional: Add logic to check if parameters are consistent if already initialized
            # For now, we'll assume initialize is called once.
            return cls._instance

    def get_cars(self) -> list[ElevatorCar]:
        """Gets the list of elevator cars managed by the system.

        Returns:
            list[ElevatorCar]: A list of ElevatorCar instances.
        """
        return self.cars

    def call_elevator(self, floor: int, direction: Direction) -> None:
        """Registers a new elevator call request from a floor.

        Args:
            floor (int): The floor number from which the elevator is called.
            direction (Direction): The direction the caller wishes to go (UP or DOWN).
        """
        self.request_manager.add_request(floor, direction)
        # State will be saved by a higher-level orchestrator

    

    def dispatcher(self) -> None:
        """Dispatches elevator cars to handle pending requests based on the dispatching strategy."""
        self._process_requests_for_direction(self.request_manager.get_up_requests(), Direction.UP)
        self._process_requests_for_direction(self.request_manager.get_down_requests(), Direction.DOWN)

    def _process_requests_for_direction(self, requests_list: list[int], direction: Direction) -> None:
        """Processes a list of requests for a specific direction.

        Args:
            requests_list (list[int]): The list of floor requests.
            direction (Direction): The direction of the requests.
        """
        if requests_list:
            requests_to_process = requests_list[:]
            for floor in requests_to_process:
                best_car = self.dispatching_strategy.find_best_car(self.cars, floor, direction)
                if best_car:
                    best_car.register_request(floor)

    def monitoring(self) -> None:
        """Monitors the status of all elevator cars and displays their information."""
        for car in self.cars:
            car.show_display()

    def update(self, subject: Subject, event: str, data: dict = None) -> None:
        """Receives updates from observed elevator cars (e.g., when a request is fulfilled).

        Args:
            subject (Subject): The subject (ElevatorCar) that sent the update.
            event (str): The type of event (e.g., "request_fulfilled").
            data (dict, optional): Additional data related to the event. Defaults to None.
        """
        if event == "request_fulfilled":
            floor = data["floor"]
            # Determine direction based on car's current direction or request type if available
            # For simplicity, assuming the fulfilled request was either an UP or DOWN request
            # This might need refinement based on how requests are tracked in ElevatorCar
            # For now, we'll try to remove from both, and RequestManager will handle if it exists.
            self.request_manager.remove_request(floor, Direction.UP)
            self.request_manager.remove_request(floor, Direction.DOWN)
            # State will be saved by a higher-level orchestrator

    def save_state(self) -> None:
        """Explicitly saves the entire system state to the database."""
        self.database_manager.save_system_state(self.num_floors, self.num_cars)
        self.request_manager.save_requests_to_db()
        for car in self.cars:
            car.save_state() # Delegate saving car state to each car
