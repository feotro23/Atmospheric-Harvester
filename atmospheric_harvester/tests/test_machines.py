import unittest
from game.state import GameState
from game.machines import create_machine

class TestMachines(unittest.TestCase):
    def setUp(self):
        self.state = GameState()
        
    def test_wind_turbine(self):
        turbine = create_machine("Wind Turbine", 0, 0)
        self.state.machines.append(turbine)
        
        # Mock weather data: High wind
        weather_data = {'wind_speed': 10.0}
        dt = 1.0
        
        turbine.update(dt, self.state, weather_data)
        
        # Check energy produced
        # Kinetic Energy = 1 * 1.0 * (10 - 3)^1.5 = 7^1.5 approx 18.5
        self.assertGreater(self.state.resources.energy, 0)
        print(f"Wind Energy Produced: {self.state.resources.energy}")
        
    def test_solar_panel(self):
        panel = create_machine("Solar Panel", 0, 0)
        self.state.machines.append(panel)
        
        # Mock weather data: Sunny day
        weather_data = {
            'temperature': 25.0,
            'cloud_cover': 0.0,
            'is_day': True,
            'radiation': 1000.0
        }
        dt = 1.0
        
        panel.update(dt, self.state, weather_data)
        
        self.assertGreater(self.state.resources.energy, 0)
        print(f"Solar Energy Produced: {self.state.resources.energy}")
        
    def test_rain_collector(self):
        collector = create_machine("Rain Collector", 0, 0)
        self.state.machines.append(collector)
        
        # Mock weather data: Raining
        weather_data = {
            'rain': 5.0,
            'humidity': 90.0
        }
        dt = 1.0
        
        collector.update(dt, self.state, weather_data)
        
        self.assertGreater(self.state.resources.water, 0)
        print(f"Water Collected: {self.state.resources.water}")

if __name__ == '__main__':
    unittest.main()
