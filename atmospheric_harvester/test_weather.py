import asyncio
import aiohttp

async def test():
    async with aiohttp.ClientSession() as session:
        # South Saint Paul, MN coordinates
        params = {
            'latitude': 44.89,
            'longitude': -93.02,
            'current_weather': 'true',
            'timezone': 'auto'
        }
        response = await session.get('https://api.open-meteo.com/v1/forecast', params=params)
        data = await response.json()
        print('Current Weather from Open-Meteo:')
        print(data.get('current_weather'))
        print(f"\nTimezone: {data.get('timezone')}")

asyncio.run(test())
