import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from floor import Floor
from elevator_panel import HallPanel
from display import Display

class TestFloor(unittest.TestCase):
    def setUp(self):
        self.floor = Floor(floor_number=3, top_floor=10)

    def test_initial_state(self):
        self.assertEqual(self.floor.get_floor_number(), 3)
        self.assertIsInstance(self.floor.get_panel(), HallPanel)
        self.assertIsInstance(self.floor.get_display(), Display)

if __name__ == '__main__':
    unittest.main()
