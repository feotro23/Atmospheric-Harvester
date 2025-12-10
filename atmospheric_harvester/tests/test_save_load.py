import unittest
import os
import sys
import json

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.core import Game
from game.creatures import Creature, ALL_CREATURES

class TestSaveLoad(unittest.TestCase):
    def setUp(self):
        self.filename = "test_save.json"
        if os.path.exists(self.filename):
            os.remove(self.filename)
            
    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)
            
    def test_save_load(self):
        # 1. Setup initial state
        game1 = Game()
        game1.state.resources.energy = 500
        game1.settings_manager.toggle_system() # Metric -> Imperial
        
        # Add a creature
        c_type = ALL_CREATURES[0]
        c = Creature(c_type)
        c.x = 5
        c.y = 5
        game1.state.active_spawns.append(c)
        
        # 2. Save
        success, msg = game1.save_game(self.filename)
        self.assertTrue(success, f"Save failed: {msg}")
        
        # 3. Load into new instance
        game2 = Game()
        success, msg = game2.load_game(self.filename)
        self.assertTrue(success, f"Load failed: {msg}")
        
        # 4. Verify
        self.assertEqual(game2.state.resources.energy, 500)
        self.assertEqual(game2.settings_manager.system, "Imperial")
        self.assertEqual(len(game2.state.active_spawns), 1)
        self.assertEqual(game2.state.active_spawns[0].x, 5)
        self.assertEqual(game2.state.active_spawns[0].type.name, c_type.name)
        
if __name__ == "__main__":
    unittest.main()
