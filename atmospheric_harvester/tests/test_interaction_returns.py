import unittest
import os
import sys

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.core import Game
from game.machines import create_machine
from game.creatures import Creature, ALL_CREATURES
from game.farming import Crop, ALL_CROPS

class TestInteractionReturn(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        self.game.state.resources.energy = 500
        self.game.state.resources.biomass = 500
        
    def test_machine_interact(self):
        # Build machine
        m = create_machine("Wind Turbine", 5, 5)
        self.game.state.machines.append(m)
        
        # Interact
        action, payload = self.game.interact(5, 5)
        
        # Verify return - should be machine_click, and machine should NOT have toggled yet (UI does it)
        self.assertEqual(action, "machine_click")
        self.assertEqual(payload, m)
        self.assertTrue(m.active) # Still active
        
    def test_crop_harvest(self):
        # Plant crop
        c_type = ALL_CROPS[0]
        c = Crop(c_type, 2, 2)
        c.stage = 3 # Ready
        self.game.state.crops.append(c)
        
        # Interact
        action, payload = self.game.interact(2, 2)
        
        self.assertEqual(action, "harvest")
        self.assertEqual(payload, c)
        
    def test_none_interact(self):
        action, payload = self.game.interact(0,0)
        self.assertIsNone(action)
        self.assertIsNone(payload)

if __name__ == "__main__":
    unittest.main()
