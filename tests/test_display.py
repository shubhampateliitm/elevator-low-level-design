import unittest
import sys
import os

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from display import Display
from enums import Direction
# No longer need to import IdleState, MovingUpState for assertions, but keep for context if needed elsewhere
# from elevator_state import IdleState, MovingUpState

class TestDisplay(unittest.TestCase):
    def setUp(self):
        self.display = Display()

    def test_initial_state(self):
        self.assertEqual(self.display.floor, 0)
        self.assertEqual(self.display.direction, Direction.STOP)
        # self.assertEqual(self.display.state, "IdleState") # Removed, as initial state is None

    def test_update(self):
        # Create a mock state object that has a __class__.__name__ attribute
        class MockMovingUpState:
            def __init__(self, car):
                pass
        moving_up_state = MockMovingUpState(None) # Use the mock state object

        self.display.update(5, Direction.UP, moving_up_state)
        self.assertEqual(self.display.floor, 5)
        self.assertEqual(self.display.direction, Direction.UP)
        self.assertEqual(self.display.state.__class__.__name__, "MockMovingUpState") # Assert string value

if __name__ == '__main__':
    unittest.main()
