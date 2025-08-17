from abc import ABC, abstractmethod
from enums import Direction

class DispatchingStrategy(ABC):
    @abstractmethod
    def find_best_car(self, cars, floor, direction):
        pass

class ClosestCarStrategy(DispatchingStrategy):
    def find_best_car(self, cars, floor, direction):
        best_car = None
        min_distance = float('inf')

        for car in cars:
            car_current_floor = car.get_current_floor()
            car_direction = car.direction

            is_suitable = False
            distance = float('inf')

            if car.is_idle():
                is_suitable = True
                distance = abs(car_current_floor - floor) + 0.1 # Add a small penalty to idle cars
            elif car_direction == direction:
                # A car moving in the correct direction is suitable if:
                # 1. The requested floor is already in its requests.
                # 2. It has existing requests and the requested floor is "on its way" (between current floor and furthest request).
                # 3. It has no existing requests but is moving in the correct direction (implies it's heading to become idle or pick up a new request).
                if direction == Direction.UP:
                    if car_current_floor <= floor: # Car is below or at the requested floor
                        if floor in car.up_requests or \
                           (not car.up_requests and car_current_floor <= floor) or \
                           (car.up_requests and floor <= max(car.up_requests)):
                            is_suitable = True
                            distance = abs(car_current_floor - floor)
                elif direction == Direction.DOWN:
                    if car_current_floor >= floor: # Car is above or at the requested floor
                        if floor in car.down_requests or \
                           (not car.down_requests and car_current_floor >= floor) or \
                           (car.down_requests and floor >= min(car.down_requests)):
                            is_suitable = True
                            distance = abs(car_current_floor - floor)

            if is_suitable and distance < min_distance:
                min_distance = distance
                best_car = car
        return best_car

