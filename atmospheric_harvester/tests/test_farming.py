import unittest
from game.core import Game
from game.farming import Crop, CORN
from game.machines import SPRINKLER_TYPE

class TestFarming(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        self.game.state.resources.water = 1000 # Plenty of water
        
    def test_sprinkler_increases_moisture(self):
        # Plant Corn at 5,5 (needs 0.5 moisture)
        crop = Crop(CORN, 5, 5)
        self.game.state.crops = [crop]
        
        # Set low humidity
        self.game.state.humidity = 10 # 0.1 moisture
        
        # Update without sprinkler
        self.game.update(1.0)
        # Moisture passed to crop should be 0.1
        # Corn needs 0.5, so health should drop
        self.assertTrue(crop.health < 100.0)
        
        # Reset health
        crop.health = 100.0
        
        # Build Sprinkler at 5,6 (dist 1)
        self.game.state.resources.energy = 100
        self.game.state.resources.biomass = 100
        self.game.build_machine("Sprinkler", 5, 6)
        
        # Update
        self.game.update(1.0)
        
        # Moisture should be 0.1 + 0.5 = 0.6 > 0.5
        # Health should NOT drop (or drop less if other factors apply, but here only water stress)
        # Actually, update checks temp too. Default temp is 20?
        # CORN optimal min is 20. So temp is fine.
        self.assertEqual(crop.health, 100.0)

if __name__ == '__main__':
    unittest.main()
