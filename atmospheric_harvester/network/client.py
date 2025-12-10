import aiohttp
import asyncio
import time
import config
from .weather_mock import MockWeatherService

class WeatherClient:
    def __init__(self):
        self.mock_service = MockWeatherService() if config.USE_MOCK_DATA else None
        self.base_url = "https://api.openweathermap.org/data/3.0/onecall"
        self.session = None

    async def start(self):
        if not config.USE_MOCK_DATA:
            self.session = aiohttp.ClientSession()

    async def close(self):
        if self.session:
            await self.session.close()

    async def get_weather(self, lat, lon):
        if config.USE_MOCK_DATA:
            return await self.mock_service.get_weather(lat, lon)
        
        if not self.session:
            await self.start()

        params = {
            "lat": lat,
            "lon": lon,
            "appid": config.OPENWEATHER_API_KEY,
            "units": "metric",
            "exclude": "minutely,hourly,daily,alerts"
        }

        try:
            async with self.session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Error fetching weather: {response.status}")
                    return None
        except Exception as e:
            print(f"Network error: {e}")
            return None
