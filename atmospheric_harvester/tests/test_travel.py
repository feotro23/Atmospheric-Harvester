import unittest
from game.state import GameState
from game.travel import TravelManager, Location

class TestTravel(unittest.TestCase):
    def setUp(self):
        self.state = GameState()
        self.travel_manager = TravelManager()
        
    def test_travel_cost(self):
        # Give enough energy
        self.state.resources.add_energy(1000)
        
        start_loc = Location("Start", 0, 0)
        target_loc = Location("Target", 1, 1) # Some distance away
        
        # Mock state location
        self.state.lat = 0
        self.state.lon = 0
        
        # Calculate expected cost
        cost = self.travel_manager.calculate_cost(0, 0, target_loc)
        
        # Try travel
        success = self.travel_manager.travel(self.state, target_loc)
        
        self.assertTrue(success)
        self.assertAlmostEqual(self.state.resources.energy, 1000 - cost)
        self.assertEqual(self.state.lat, 1)
        self.assertEqual(self.state.lon, 1)
        
    def test_insufficient_energy(self):
        self.state.resources.energy = 0
        target_loc = Location("Target", 1, 1)
        
        success = self.travel_manager.travel(self.state, target_loc)
        
        self.assertFalse(success)
        self.assertEqual(self.state.resources.energy, 0)

if __name__ == '__main__':
    unittest.main()
