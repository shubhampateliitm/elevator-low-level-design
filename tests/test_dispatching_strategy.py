import unittest
import sys
import os
from unittest.mock import Mock

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dispatching_strategy import ClosestCarStrategy
from enums import Direction
from elevator_state import IdleState, MovingUpState, MovingDownState

class TestClosestCarStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = ClosestCarStrategy()

    def create_mock_car(self, car_id, current_floor, direction, state_instance, up_requests=None, down_requests=None):
        mock_car = Mock()
        mock_car.car_id = car_id
        mock_car.get_current_floor.return_value = current_floor
        mock_car.get_direction.return_value = direction # Use getter
        mock_car.get_state.return_value = state_instance
        mock_car.is_idle.return_value = isinstance(state_instance, IdleState)
        mock_car.get_up_requests.return_value = up_requests if up_requests is not None else [] # Use getter
        mock_car.get_down_requests.return_value = down_requests if down_requests is not None else [] # Use getter
        return mock_car

    def test_find_best_car_no_cars(self):
        best_car = self.strategy.find_best_car([], 5, Direction.UP)
        self.assertIsNone(best_car)

    def test_find_best_car_idle_cars(self):
        car1 = self.create_mock_car(1, 0, Direction.STOP, IdleState(None))
        car2 = self.create_mock_car(2, 10, Direction.STOP, IdleState(None))
        car3 = self.create_mock_car(3, 5, Direction.STOP, IdleState(None)) # Closest

        cars = [car1, car2, car3]
        best_car = self.strategy.find_best_car(cars, 6, Direction.UP)
        self.assertEqual(best_car, car3)

    def test_find_best_car_moving_up_matching_direction(self):
        car1 = self.create_mock_car(1, 0, Direction.UP, MovingUpState(None))
        car2 = self.create_mock_car(2, 3, Direction.UP, MovingUpState(None), up_requests=[5]) # Closest and moving up
        car3 = self.create_mock_car(3, 8, Direction.UP, MovingUpState(None))

        cars = [car1, car2, car3]
        best_car = self.strategy.find_best_car(cars, 5, Direction.UP)
        self.assertEqual(best_car, car2)

    def test_find_best_car_moving_down_matching_direction(self):
        car1 = self.create_mock_car(1, 10, Direction.DOWN, MovingDownState(None))
        car2 = self.create_mock_car(2, 7, Direction.DOWN, MovingDownState(None), down_requests=[5]) # Closest and moving down
        car3 = self.create_mock_car(3, 2, Direction.DOWN, MovingDownState(None))

        cars = [car1, car2, car3]
        best_car = self.strategy.find_best_car(cars, 5, Direction.DOWN)
        self.assertEqual(best_car, car2)

    def test_find_best_car_mixed_cars_idle_preferred(self):
        car1 = self.create_mock_car(1, 0, Direction.UP, MovingUpState(None))
        car2 = self.create_mock_car(2, 5, Direction.STOP, IdleState(None)) # Idle and closest
        car3 = self.create_mock_car(3, 8, Direction.DOWN, MovingDownState(None))

        cars = [car1, car2, car3]
        best_car = self.strategy.find_best_car(cars, 6, Direction.UP)
        self.assertEqual(best_car, car2)

    def test_find_best_car_moving_wrong_direction(self):
        car1 = self.create_mock_car(1, 0, Direction.DOWN, MovingDownState(None)) # Moving wrong way
        car2 = self.create_mock_car(2, 5, Direction.STOP, IdleState(None)) # Idle and closest
        car3 = self.create_mock_car(3, 8, Direction.UP, MovingUpState(None)) # Moving right way, but further

        cars = [car1, car2, car3]
        best_car = self.strategy.find_best_car(cars, 6, Direction.UP)
        self.assertEqual(best_car, car2)

    def test_find_best_car_no_suitable_car(self):
        car1 = self.create_mock_car(1, 0, Direction.DOWN, MovingDownState(None)) # Moving wrong way
        car2 = self.create_mock_car(2, 5, Direction.DOWN, MovingDownState(None)) # Moving wrong way (past floor)
        car3 = self.create_mock_car(3, 8, Direction.UP, MovingUpState(None)) # Moving right way, but past floor

        cars = [car1, car2, car3]
        best_car = self.strategy.find_best_car(cars, 6, Direction.UP)
        self.assertIsNone(best_car)

    def test_find_best_car_multiple_idle_same_distance(self):
        car1 = self.create_mock_car(1, 0, Direction.STOP, IdleState(None))
        car2 = self.create_mock_car(2, 10, Direction.STOP, IdleState(None))
        car3 = self.create_mock_car(3, 1, Direction.STOP, IdleState(None)) # Same distance as car1, but car1 is first

        cars = [car1, car2, car3]
        best_car = self.strategy.find_best_car(cars, 0, Direction.UP)
        self.assertEqual(best_car, car1) # Should pick the first one encountered

    def test_find_best_car_moving_up_past_floor(self):
        car1 = self.create_mock_car(1, 5, Direction.UP, MovingUpState(None))
        cars = [car1]
        best_car = self.strategy.find_best_car(cars, 3, Direction.UP) # Request is below current floor
        self.assertIsNone(best_car)

    def test_find_best_car_moving_down_past_floor(self):
        car1 = self.create_mock_car(1, 5, Direction.DOWN, MovingDownState(None))
        cars = [car1]
        best_car = self.strategy.find_best_car(cars, 7, Direction.DOWN) # Request is above current floor
        self.assertIsNone(best_car)

    def test_find_best_car_moving_up_on_the_way(self):
        # Car at floor 2, moving UP, with requests for 5 and 8
        car1 = self.create_mock_car(1, 2, Direction.UP, MovingUpState(None), up_requests=[5, 8])
        # Request for floor 4, which is on the way
        best_car = self.strategy.find_best_car([car1], 4, Direction.UP)
        self.assertEqual(best_car, car1)

    def test_find_best_car_moving_down_on_the_way(self):
        # Car at floor 8, moving DOWN, with requests for 5 and 2
        car1 = self.create_mock_car(1, 8, Direction.DOWN, MovingDownState(None), down_requests=[5, 2])
        # Request for floor 6, which is on the way
        best_car = self.strategy.find_best_car([car1], 6, Direction.DOWN)
        self.assertEqual(best_car, car1)

    def test_find_best_car_moving_up_past_highest_request(self):
        # Car at floor 2, moving UP, with requests for 5 and 8
        car1 = self.create_mock_car(1, 2, Direction.UP, MovingUpState(None), up_requests=[5, 8])
        # Request for floor 9, which is past its current highest request (8)
        best_car = self.strategy.find_best_car([car1], 9, Direction.UP)
        self.assertIsNone(best_car)

    def test_find_best_car_moving_down_past_lowest_request(self):
        # Car at floor 8, moving DOWN, with requests for 5 and 2
        car1 = self.create_mock_car(1, 8, Direction.DOWN, MovingDownState(None), down_requests=[5, 2])
        # Request for floor 1, which is past its current lowest request (2)
        best_car = self.strategy.find_best_car([car1], 1, Direction.DOWN)
        self.assertIsNone(best_car)

    def test_find_best_car_request_already_in_car_requests_up(self):
        # Car at floor 2, moving UP, with requests for 4 and 8
        car1 = self.create_mock_car(1, 2, Direction.UP, MovingUpState(None), up_requests=[4, 8])
        # Request for floor 4, which is already in its requests
        best_car = self.strategy.find_best_car([car1], 4, Direction.UP)
        self.assertEqual(best_car, car1)

    def test_find_best_car_request_already_in_car_requests_down(self):
        # Car at floor 8, moving DOWN, with requests for 6 and 2
        car1 = self.create_mock_car(1, 8, Direction.DOWN, MovingDownState(None), down_requests=[6, 2])
        # Request for floor 6, which is already in its requests
        best_car = self.strategy.find_best_car([car1], 6, Direction.DOWN)
        self.assertEqual(best_car, car1)

    def test_find_best_car_idle_preferred_over_moving_on_the_way(self):
        # Idle car at floor 3
        car1 = self.create_mock_car(1, 3, Direction.STOP, IdleState(None))
        # Moving car at floor 0, moving UP, with requests for 5 and 8
        car2 = self.create_mock_car(2, 0, Direction.UP, MovingUpState(None), up_requests=[5, 8])
        # Request for floor 4
        cars = [car1, car2]
        best_car = self.strategy.find_best_car(cars, 4, Direction.UP)
        self.assertEqual(best_car, car1) # Idle car is closer

    def test_find_best_car_moving_on_the_way_preferred_over_further_idle(self):
        # Idle car at floor 8
        car1 = self.create_mock_car(1, 8, Direction.STOP, IdleState(None))
        # Moving car at floor 0, moving UP, with requests for 5 and 8
        car2 = self.create_mock_car(2, 0, Direction.UP, MovingUpState(None), up_requests=[5, 8])
        # Request for floor 4
        cars = [car1, car2]
        best_car = self.strategy.find_best_car(cars, 4, Direction.UP)
        self.assertEqual(best_car, car2) # Moving car is closer and on the way

if __name__ == '__main__':
    unittest.main()
