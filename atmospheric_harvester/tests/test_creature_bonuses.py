import unittest
import sys
import os

# Fix path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.core import Game
from game.creatures import Creature, ALL_CREATURES
from game.machines import create_machine

class TestCreatureBonuses(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        self.game.state.resources.energy = 0
        self.game.state.weather_code = 0 # Init default to avoid EventManager crash
        # Clear achievements to avoid rewards
        self.game.achievement_manager.achievements = {}
        
    def test_bonus_application(self):
        # 1. Setup Wind Turbine
        turbine = create_machine("Wind Turbine", 0, 0)
        self.game.state.machines.append(turbine)
        
        # 2. Add Thermal Kite (Wind Bonus)
        kite_type = next(c for c in ALL_CREATURES if c.name == "Thermal Kite")
        kite = Creature(kite_type)
        self.game.state.collected_creatures.append(kite)
        
        # 3. Simulate Update
        dt = 1.0
        # Mock weather for turbine
        self.game.state.wind_speed = 10.0 
        self.game.state.weather_data = {'wind_speed': 10.0}
        
        # Initial Gen check (requires running update logic)
        # We need to call game.update to trigger machine.update and bonus application
        # But core.update loops machines.
        
        # Let's manually run the loop logic for testing precise math
        # machine.current_rate is set by machine.update()
        turbine.update(dt, self.game.state, self.game.state.weather_data)
        base_rate = turbine.current_rate
        
        # Now run core logic that applies bonus
        # We can't easily isolate the loop in core.update without refactoring or copy-paste logic
        # So let's run self.game.update(dt) and check resources
        
        initial_energy = self.game.state.resources.energy
        self.game.state.gen_kinetic = 0
        
        self.game.update(dt)
        
        # Expected:
        # Base Gen = base_rate * dt
        # Bonus = 10%
        # Total added = base_rate * 1.10 * dt
        
        # But wait, game.update resets gen_kinetic.
        # Check gen_kinetic value
        
        print(f"Base Rate: {base_rate}")
        print(f"Gen Kinetic: {self.game.state.gen_kinetic}")
        
        # Verify it's > base_rate (approx 10% more)
        self.assertAlmostEqual(self.game.state.gen_kinetic, base_rate * 1.10, delta=0.1)

    def test_passive_bonus(self):
        # Golem gives 1.0 Energy/s
        golem_type = next(c for c in ALL_CREATURES if c.name == "Fulgarite Golem")
        golem = Creature(golem_type)
        self.game.state.collected_creatures.append(golem)
        
        initial_energy = self.game.state.resources.energy
        self.game.update(1.0)
        
        # Should have gained 1.0 energy (assuming no other machines running/consuming)
        # No machines in this test
        self.assertEqual(self.game.state.resources.energy, initial_energy + 1.0)

if __name__ == "__main__":
    unittest.main()
