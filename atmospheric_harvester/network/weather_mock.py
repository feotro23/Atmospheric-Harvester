import random
import time
import asyncio

class MockWeatherService:
    def __init__(self):
        self.last_update = 0
        self.current_weather = self._generate_initial_weather()

    def _generate_initial_weather(self):
        return {
            "lat": 0,
            "lon": 0,
            "timezone": "UTC",
            "timezone_offset": 0,
            "current": {
                "dt": int(time.time()),
                "sunrise": int(time.time()) - 20000,
                "sunset": int(time.time()) + 20000,
                "temp": 20.0,  # Celsius
                "feels_like": 19.0,
                "pressure": 1013,
                "humidity": 50,
                "dew_point": 10.0,
                "uvi": 5.0,
                "clouds": 20,
                "visibility": 10000,
                "wind_speed": 5.0,  # m/s
                "wind_deg": 180,
                "weather": [{"id": 801, "main": "Clouds", "description": "few clouds", "icon": "02d"}]
            }
        }

    async def get_weather(self, lat, lon):
        # Simulate network delay
        await asyncio.sleep(0.5)
        
        # Evolve weather slightly
        self._evolve_weather()
        return self.current_weather

    def _evolve_weather(self):
        # Random walk for values
        current = self.current_weather["current"]
        
        # Temp fluctuation (-0.5 to +0.5)
        current["temp"] += random.uniform(-0.5, 0.5)
        current["temp"] = max(-30, min(50, current["temp"]))
        
        # Wind fluctuation
        current["wind_speed"] += random.uniform(-1.0, 1.0)
        current["wind_speed"] = max(0, min(50, current["wind_speed"]))
        
        # Wind direction
        current["wind_deg"] = (current["wind_deg"] + random.randint(-10, 10)) % 360
        
        # Update timestamp
        current["dt"] = int(time.time())
