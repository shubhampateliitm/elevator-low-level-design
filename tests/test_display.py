import unittest
import sys
import os

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from display import Display
from enums import Direction
from elevator_state import IdleState, MovingUpState

class TestDisplay(unittest.TestCase):
    def setUp(self):
        self.display = Display()

    def test_initial_state(self):
        self.assertEqual(self.display.floor, 0)
        self.assertEqual(self.display.direction, Direction.STOP)
        self.assertIsInstance(self.display.state, IdleState)

    def test_update(self):
        moving_up_state = MovingUpState(None)
        self.display.update(5, Direction.UP, moving_up_state)
        self.assertEqual(self.display.floor, 5)
        self.assertEqual(self.display.direction, Direction.UP)
        self.assertIsInstance(self.display.state, MovingUpState)

if __name__ == '__main__':
    unittest.main()
