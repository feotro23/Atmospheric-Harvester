import unittest
import os
import sys

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.core import Game
from game.creatures import Creature, ALL_CREATURES
from game.machines import create_machine, STABLE_TYPE

class TestCreatureStable(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        self.game.state.resources.energy = 500
        self.game.state.resources.biomass = 500
        
    def test_capture_logic(self):
        # 1. Spawn a creature
        c_type = ALL_CREATURES[0]
        c = Creature(c_type, x=2, y=2)
        self.game.state.active_spawns.append(c)
        
        # 2. Try to interact WITHOUT stable
        self.game.interact(2, 2)
        
        # Assert NOT captured
        self.assertIn(c, self.game.state.active_spawns)
        self.assertEqual(len(self.game.state.collected_creatures), 0)
        
        # 3. Build Stable
        # Create directly to skip cost checks for unit test simplicity, or use build_machine
        # Let's use build_machine to verify cost/placement too if we wanted, but direct is easier for logic test
        stable = create_machine("Creature Stable", 0, 0)
        stable.active = False # Verify it works even if "off" (passive building)
        self.game.state.machines.append(stable)
        
        # 4. Try to interact WITH stable
        self.game.interact(2, 2)
        
        # Assert Captured
        self.assertNotIn(c, self.game.state.active_spawns)
        self.assertIn(c, self.game.state.collected_creatures)
        
if __name__ == "__main__":
    unittest.main()
