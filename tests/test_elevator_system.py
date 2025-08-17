import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from elevator_system import ElevatorSystem
from enums import Direction
from elevator_state import MovingUpState, MovingDownState
from dispatching_strategy import ClosestCarStrategy

class TestElevatorSystem(unittest.TestCase):
    def setUp(self):
        # Reset the Singleton instance before each test
        ElevatorSystem._instance = None
        self.system = ElevatorSystem.get_instance(num_floors=10, num_cars=1, dispatching_strategy=ClosestCarStrategy())

    def test_singleton(self):
        system2 = ElevatorSystem.get_instance(num_floors=20, num_cars=5, dispatching_strategy=ClosestCarStrategy())
        self.assertIs(self.system, system2)
        self.assertEqual(self.system.num_floors, 10)
        self.assertEqual(self.system.num_cars, 1)

    def test_call_elevator(self):
        self.system.call_elevator(5, Direction.UP)
        self.assertEqual(self.system.up_requests, [5])
        self.system.call_elevator(3, Direction.DOWN)
        self.assertEqual(self.system.down_requests, [3])

    def test_dispatcher_idle_car(self):
        self.system.call_elevator(5, Direction.UP)
        self.system.dispatcher()
        car = self.system.get_cars()[0]
        self.assertEqual(car.up_requests, [5])
        # Simulate car moving and fulfilling the request
        car.current_floor = 5 # Manually set car to destination
        car._open_door_at_current_floor() # Open door
        car.notify("request_fulfilled", {"floor": 5}) # Notify system
        self.assertEqual(self.system.up_requests, [])

    def test_dispatcher_moving_car(self):
        car = self.system.get_cars()[0]
        car.state = MovingUpState(car)
        car.direction = Direction.UP
        car.current_floor = 2
        self.system.call_elevator(5, Direction.UP)
        self.system.dispatcher()
        self.assertEqual(car.up_requests, [5])
        # Simulate car moving and fulfilling the request
        car.current_floor = 5 # Manually set car to destination
        car._open_door_at_current_floor() # Open door
        car.notify("request_fulfilled", {"floor": 5}) # Notify system
        self.assertEqual(self.system.up_requests, [])

    def test_dispatcher_no_car_available(self):
        car = self.system.get_cars()[0]
        car.state = MovingDownState(car)
        car.direction = Direction.DOWN
        car.current_floor = 8
        self.system.call_elevator(5, Direction.UP)
        self.system.dispatcher()
        self.assertEqual(car.up_requests, [])
        self.assertEqual(self.system.up_requests, [5])

if __name__ == '__main__':
    unittest.main()
