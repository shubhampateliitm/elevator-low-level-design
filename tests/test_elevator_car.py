import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from elevator_car import ElevatorCar
from enums import Direction, DoorState
from elevator_state import IdleState, MovingUpState, MovingDownState, MaintenanceState
from time_provider import MockTimeProvider
from unittest.mock import Mock

class TestElevatorCar(unittest.TestCase):
    def setUp(self):
        self.time_provider = MockTimeProvider()
        self.mock_door = Mock()
        # Configure mock_door to behave like a real door
        self.mock_door.is_open.return_value = False
        self.mock_door.get_state.return_value = DoorState.CLOSED

        # Side effect for open/close methods to change the state
        def open_door_side_effect():
            self.mock_door.is_open.return_value = True
            self.mock_door.get_state.return_value = DoorState.OPEN
        def close_door_side_effect():
            self.mock_door.is_open.return_value = False
            self.mock_door.get_state.return_value = DoorState.CLOSED
        
        self.mock_door.open.side_effect = open_door_side_effect
        self.mock_door.close.side_effect = close_door_side_effect

        self.mock_panel = Mock()
        self.mock_display = Mock()
        
        # Mock DatabaseManager
        self.mock_db_manager = Mock()
        self.mock_db_manager.load_car_state.return_value = None # Simulate no prior state
        self.mock_db_manager.load_car_requests.return_value = [] # Simulate no prior requests
        self.mock_db_manager.save_car_state.return_value = None # Mock save operations
        self.mock_db_manager.save_car_requests.return_value = None # Mock save operations
        self.mock_db_manager.clear_all_data.return_value = None # Add this line
        self.mock_db_manager.clear_all_data() # Add this line

        self.elevator_car = ElevatorCar(
            car_id=1,
            num_floors=10,
            door_open_duration=2,
            time_provider=self.time_provider,
            door=self.mock_door,
            panel=self.mock_panel,
            display=self.mock_display,
            database_manager=self.mock_db_manager # Pass the mock DB manager
        )

    def test_initial_state(self):
        self.assertEqual(self.elevator_car.get_id(), 1)
        self.assertEqual(self.elevator_car.get_current_floor(), 0)
        self.assertIsInstance(self.elevator_car.get_state(), IdleState)
        self.assertEqual(self.elevator_car.direction, Direction.STOP)
        self.assertFalse(self.elevator_car.door.is_open())
        self.assertEqual(len(self.elevator_car.up_requests), 0)
        self.assertEqual(len(self.elevator_car.down_requests), 0)

    def test_register_request_up(self):
        self.elevator_car.register_request(5)
        self.assertEqual(self.elevator_car.up_requests, [5])

    def test_register_request_down(self):
        self.elevator_car.current_floor = 5
        self.elevator_car.register_request(2)
        self.assertEqual(self.elevator_car.down_requests, [2])

    def test_move_up(self):
        self.elevator_car.register_request(3)
        self.elevator_car.move() # Transition to MovingUpState
        self.elevator_car.move() # Move one floor
        self.assertIsInstance(self.elevator_car.get_state(), MovingUpState)
        self.assertEqual(self.elevator_car.get_current_floor(), 1)
        self.assertEqual(self.elevator_car.direction, Direction.UP)

    def test_move_down(self):
        self.elevator_car.current_floor = 5
        self.elevator_car.register_request(2)
        self.elevator_car.move() # Transition to MovingDownState
        self.elevator_car.move() # Move one floor
        self.assertIsInstance(self.elevator_car.get_state(), MovingDownState)
        self.assertEqual(self.elevator_car.get_current_floor(), 4)
        self.assertEqual(self.elevator_car.direction, Direction.DOWN)

    def test_reach_destination_up(self):
        self.elevator_car.register_request(1)
        self.elevator_car.move() # Transition to MovingUpState
        self.elevator_car.move() # Move to floor 1, door opens
        self.assertEqual(self.elevator_car.get_current_floor(), 1)
        self.assertTrue(self.elevator_car.door.is_open())
        self.time_provider.advance_time(self.elevator_car.door_open_duration + 0.1) # Advance time to close door
        self.elevator_car.move() # Close the door, transition to IdleState
        self.assertIsInstance(self.elevator_car.get_state(), IdleState)
        self.assertEqual(self.elevator_car.direction, Direction.STOP)
        self.assertEqual(len(self.elevator_car.up_requests), 0)

    def test_reach_destination_down(self):
        self.elevator_car.current_floor = 5
        self.elevator_car.register_request(4)
        self.elevator_car.move() # Transition to MovingDownState
        self.elevator_car.move() # Move to floor 4, door opens
        self.assertEqual(self.elevator_car.get_current_floor(), 4)
        self.assertTrue(self.elevator_car.door.is_open())
        self.time_provider.advance_time(self.elevator_car.door_open_duration + 0.1) # Advance time to close door
        self.elevator_car.move() # Close the door, transition to IdleState
        self.assertIsInstance(self.elevator_car.get_state(), IdleState)
        self.assertEqual(self.elevator_car.direction, Direction.STOP)
        self.assertEqual(len(self.elevator_car.down_requests), 0)


    def test_maintenance_mode(self):
        self.elevator_car.enter_maintenance()
        self.assertIsInstance(self.elevator_car.get_state(), MaintenanceState)
        self.elevator_car.exit_maintenance()
        self.assertIsInstance(self.elevator_car.get_state(), IdleState)

    def test_no_move_in_maintenance(self):
        self.elevator_car.enter_maintenance()
        self.elevator_car.register_request(5)
        self.elevator_car.move()
        self.assertEqual(self.elevator_car.get_current_floor(), 0)
        self.assertEqual(len(self.elevator_car.up_requests), 0)

    def test_pickup_in_passing(self):
        self.elevator_car.register_request(5)
        self.elevator_car.move() # Transition to MovingUpState
        self.elevator_car.move() # current floor 1
        self.elevator_car.register_request(3)
        self.assertEqual(self.elevator_car.up_requests, [3, 5])
        self.elevator_car.move() # current floor 2
        self.elevator_car.move() # current floor 3, door opens
        self.assertEqual(self.elevator_car.get_current_floor(), 3)
        self.assertTrue(self.elevator_car.door.is_open())
        self.time_provider.advance_time(self.elevator_car.door_open_duration + 0.1) # Advance time to close door
        self.elevator_car.move() # Close the door, continue moving
        self.assertEqual(self.elevator_car.up_requests, [5])

    def test_request_current_floor_while_moving_up(self):
        self.elevator_car.register_request(5) # Request to go to floor 5
        self.elevator_car.move() # Car transitions to MovingUpState, current_floor = 0, direction = UP
        self.elevator_car.move() # current_floor = 1
        self.elevator_car.move() # current_floor = 2

        # Now, register a request for the current floor (floor 2)
        self.elevator_car.register_request(2)

        # Assert that the door opens at floor 2
        self.assertEqual(self.elevator_car.get_current_floor(), 2)
        self.assertTrue(self.elevator_car.door.is_open())

        # Simulate door closing by advancing time
        self.time_provider.advance_time(2.1) # Advance time past door_open_duration
        self.elevator_car.move() # This call will now close the door and continue movement

        # After door closes, it should continue towards floor 5
        # Let's simulate enough moves to reach floor 5
        self.elevator_car.move() # Door closes, continues moving
        self.elevator_car.move() # current_floor = 3
        self.elevator_car.move() # current_floor = 4
        self.elevator_car.move() # current_floor = 5, door opens
        
        self.assertEqual(self.elevator_car.get_current_floor(), 5)
        self.assertTrue(self.elevator_car.door.is_open())
        self.assertEqual(len(self.elevator_car.up_requests), 0) # All up requests should be fulfilled
        self.assertIsInstance(self.elevator_car.get_state(), IdleState) # Should be idle after fulfilling all requests

if __name__ == '__main__':
    unittest.main()

if __name__ == '__main__':
    unittest.main()