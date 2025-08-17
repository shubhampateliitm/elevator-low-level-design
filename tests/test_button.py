import unittest
import sys
import os

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from button import DoorButton, HallButton, ElevatorButton, EmergencyButton
from enums import Direction

class TestButton(unittest.TestCase):
    def test_door_button(self):
        button = DoorButton()
        self.assertFalse(button.is_pressed())
        button.press_down()
        self.assertTrue(button.is_pressed())
        button.reset()
        self.assertFalse(button.is_pressed())

    def test_hall_button(self):
        button = HallButton(Direction.UP)
        self.assertFalse(button.is_pressed())
        button.press_down()
        self.assertTrue(button.is_pressed())
        button.reset()
        self.assertFalse(button.is_pressed())
        self.assertEqual(button.get_direction(), Direction.UP)

    def test_elevator_button(self):
        button = ElevatorButton(5)
        self.assertFalse(button.is_pressed())
        button.press_down()
        self.assertTrue(button.is_pressed())
        button.reset()
        self.assertFalse(button.is_pressed())
        self.assertEqual(button.get_destination_floor(), 5)

    def test_emergency_button(self):
        button = EmergencyButton()
        self.assertFalse(button.is_pressed())
        button.press_down()
        self.assertTrue(button.is_pressed())
        button.reset()
        self.assertFalse(button.is_pressed())

if __name__ == '__main__':
    unittest.main()
