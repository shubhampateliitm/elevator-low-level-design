from abc import ABC, abstractmethod
from enums import Direction

class DispatchingStrategy(ABC):
    """Abstract base class for elevator dispatching strategies."""
    @abstractmethod
    def find_best_car(self, cars: list, floor: int, direction: Direction) -> object | None:
        """Finds the best elevator car to serve a given request.

        Args:
            cars (list): A list of available ElevatorCar objects.
            floor (int): The floor number of the request.
            direction (Direction): The direction of the request (UP or DOWN).

        Returns:
            object | None: The best ElevatorCar object to serve the request, or None if no suitable car is found.
        """
        pass

class ClosestCarStrategy(DispatchingStrategy):
    """A dispatching strategy that assigns the closest suitable elevator car to a request."""
    def find_best_car(self, cars: list, floor: int, direction: Direction) -> object | None:
        """Finds the closest suitable elevator car to serve a given request.

        Args:
            cars (list): A list of available ElevatorCar objects.
            floor (int): The floor number of the request.
            direction (Direction): The direction of the request (UP or DOWN).

        Returns:
            object | None: The closest suitable ElevatorCar object, or None if no suitable car is found.
        """
        best_car = None
        min_distance = float('inf')

        for car in cars:
            is_suitable, distance = self._evaluate_car_suitability(car, floor, direction)

            if is_suitable and distance < min_distance:
                min_distance = distance
                best_car = car
        return best_car

    def _evaluate_car_suitability(self, car: object, requested_floor: int, requested_direction: Direction) -> tuple[bool, float]:
        """Evaluates if a car is suitable for a request and calculates its distance/cost.

        Args:
            car (object): The ElevatorCar object to evaluate.
            requested_floor (int): The floor number of the request.
            requested_direction (Direction): The direction of the request.

        Returns:
            tuple[bool, float]: A tuple containing (is_suitable, distance).
                                is_suitable is True if the car can serve the request, False otherwise.
                                distance is the calculated cost/distance, or float('inf') if not suitable.
        """
        car_current_floor = car.get_current_floor()
        car_direction = car.get_direction()
        
        if car.is_idle():
            return True, abs(car_current_floor - requested_floor) + 0.1 # Small penalty for idle cars
        
        if car_direction == requested_direction:
            if requested_direction == Direction.UP:
                if car_current_floor <= requested_floor:
                    # Check if request is on the way or already in requests
                    if requested_floor in car.get_up_requests() or \
                       (not car.get_up_requests() and car_current_floor <= requested_floor) or \
                       (car.get_up_requests() and requested_floor <= max(car.get_up_requests())):
                        return True, abs(car_current_floor - requested_floor)
            elif requested_direction == Direction.DOWN:
                if car_current_floor >= requested_floor:
                    # Check if request is on the way or already in requests
                    if requested_floor in car.get_down_requests() or \
                       (not car.get_down_requests() and car_current_floor >= requested_floor) or \
                       (car.get_down_requests() and requested_floor >= min(car.get_down_requests())):
                        return True, abs(car_current_floor - requested_floor)
        
        return False, float('inf') # Not suitable

