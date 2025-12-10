import unittest
from game.core import Game

class TestBuildMode(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        
    def test_build_selection_default(self):
        self.assertIsNone(self.game.build_selection)
        
    def test_set_build_selection(self):
        self.game.build_selection = "Wind Turbine"
        self.assertEqual(self.game.build_selection, "Wind Turbine")
        
    def test_build_machine_clears_selection_if_implemented(self):
        # In current implementation, we decided NOT to clear selection (allow multiple placement)
        # So we test that it persists
        self.game.build_selection = "Wind Turbine"
        # Give resources
        self.game.state.resources.energy = 1000
        self.game.state.resources.biomass = 100
        
        self.game.build_machine("Wind Turbine", 0, 0)
        self.assertEqual(self.game.build_selection, "Wind Turbine")

if __name__ == '__main__':
    unittest.main()
