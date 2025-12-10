import unittest
from game.core import Game
from game.machines import BATTERY_TYPE, TANK_TYPE

class TestStorage(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        # Give some resources to build
        self.game.state.resources.energy = 1000
        self.game.state.resources.biomass = 100
        
    def test_battery_increases_capacity(self):
        initial_cap = self.game.state.resources.energy_capacity
        
        # Build Battery
        success, msg = self.game.build_machine("Battery", 0, 0)
        self.assertTrue(success, msg)
        
        new_cap = self.game.state.resources.energy_capacity
        self.assertEqual(new_cap, initial_cap + 500)
        
    def test_water_tank_increases_capacity(self):
        initial_cap = self.game.state.resources.water_capacity
        
        # Build Water Tank
        success, msg = self.game.build_machine("Water Tank", 0, 1)
        self.assertTrue(success, msg)
        
        new_cap = self.game.state.resources.water_capacity
        self.assertEqual(new_cap, initial_cap + 250)
        
    def test_cannot_build_without_resources(self):
        self.game.state.resources.energy = 0
        success, msg = self.game.build_machine("Battery", 1, 1)
        self.assertFalse(success)
        self.assertEqual(msg, "Not enough Energy")

if __name__ == '__main__':
    unittest.main()
