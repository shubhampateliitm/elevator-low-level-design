import unittest
import sys
import os

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from door import Door
from enums import DoorState

class TestDoor(unittest.TestCase):
    def setUp(self):
        self.door = Door()

    def test_initial_state(self):
        self.assertEqual(self.door.get_state(), DoorState.CLOSED)
        self.assertFalse(self.door.is_open())

    def test_open_door(self):
        self.door.open()
        self.assertEqual(self.door.get_state(), DoorState.OPEN)
        self.assertTrue(self.door.is_open())

    def test_close_door(self):
        self.door.open()
        self.door.close()
        self.assertEqual(self.door.get_state(), DoorState.CLOSED)
        self.assertFalse(self.door.is_open())

if __name__ == '__main__':
    unittest.main()
