import unittest
import sys
import os

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from elevator_panel import ElevatorPanel, HallPanel
from button import ElevatorButton, DoorButton, EmergencyButton, HallButton
from enums import Direction

class TestElevatorPanel(unittest.TestCase):
    def setUp(self):
        self.num_floors = 10
        self.panel = ElevatorPanel(self.num_floors)

    def test_initialization(self):
        self.assertEqual(len(self.panel.floor_buttons), self.num_floors)
        for i, button in enumerate(self.panel.floor_buttons):
            self.assertIsInstance(button, ElevatorButton)
            self.assertEqual(button.get_destination_floor(), i)
            self.assertFalse(button.is_pressed())
        self.assertIsInstance(self.panel.open_button, DoorButton)
        self.assertIsInstance(self.panel.close_button, DoorButton)
        self.assertIsInstance(self.panel.emergency_button, EmergencyButton)

    def test_press_floor_button(self):
        self.panel.press_floor_button(5)
        self.assertTrue(self.panel.floor_buttons[5].is_pressed())
        self.panel.floor_buttons[5].reset() # Reset for next tests

    def test_press_open_button(self):
        self.panel.press_open_button()
        self.assertTrue(self.panel.open_button.is_pressed())
        self.panel.open_button.reset()

    def test_press_close_button(self):
        self.panel.press_close_button()
        self.assertTrue(self.panel.close_button.is_pressed())
        self.panel.close_button.reset()

    def test_press_emergency_button(self):
        self.panel.press_emergency_button()
        self.assertTrue(self.panel.emergency_button.is_pressed())
        self.panel.emergency_button.reset()

class TestHallPanel(unittest.TestCase):
    def test_initialization_middle_floor(self):
        panel = HallPanel(floor_number=5, top_floor=10)
        self.assertEqual(panel.floor_number, 5)
        self.assertIsInstance(panel.get_up_button(), HallButton)
        self.assertIsInstance(panel.get_down_button(), HallButton)
        self.assertEqual(panel.get_up_button().get_direction(), Direction.UP)
        self.assertEqual(panel.get_down_button().get_direction(), Direction.DOWN)

    def test_initialization_top_floor(self):
        # For a system with 10 floors (0-9), floor 9 is the top floor.
        # It should have an UP button (9 < 10) and a DOWN button (9 > 0).
        panel = HallPanel(floor_number=9, top_floor=10)
        self.assertEqual(panel.floor_number, 9)
        self.assertIsInstance(panel.get_up_button(), HallButton)
        self.assertIsInstance(panel.get_down_button(), HallButton)

    def test_initialization_bottom_floor(self):
        # For a system with 10 floors (0-9), floor 0 is the bottom floor.
        # It should have an UP button (0 < 10) but no DOWN button (0 > 0 is false).
        panel = HallPanel(floor_number=0, top_floor=10)
        self.assertEqual(panel.floor_number, 0)
        self.assertIsInstance(panel.get_up_button(), HallButton)
        self.assertIsNone(panel.get_down_button())

    def test_press_up_button(self):
        panel = HallPanel(floor_number=5, top_floor=10)
        self.assertFalse(panel.get_up_button().is_pressed())
        panel.press_up_button()
        self.assertTrue(panel.get_up_button().is_pressed())
        panel.get_up_button().reset()

    def test_press_down_button(self):
        panel = HallPanel(floor_number=5, top_floor=10)
        self.assertFalse(panel.get_down_button().is_pressed())
        panel.press_down_button()
        self.assertTrue(panel.get_down_button().is_pressed())
        panel.get_down_button().reset()

    def test_press_non_existent_button(self):
        # Test pressing the down button on floor 0 (which doesn't exist)
        panel_bottom = HallPanel(floor_number=0, top_floor=10)
        self.assertIsNone(panel_bottom.get_down_button())
        panel_bottom.press_down_button() # This should not raise an error
        # No assertion on button state, as it doesn't exist.

if __name__ == '__main__':
    unittest.main()