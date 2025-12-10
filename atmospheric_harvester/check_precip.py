"""Check what precipitation data Open-Meteo provides."""
import asyncio
from network.open_meteo import OpenMeteoClient

async def check_precip():
    c = OpenMeteoClient()
    await c.start()
    
    d = await c.get_weather(44.89, -93.02)
    
    print("Precipitation data from Open-Meteo:")
    print(f"  precip_probability: {d.get('precip_probability', 'N/A')}")
    print(f"  precipitation: {d.get('precipitation', 'N/A')}")
    print(f"  rain: {d.get('rain', 'N/A')}")
    print(f"  snowfall: {d.get('snowfall', 'N/A')}")
    print(f"  snow_depth: {d.get('snow_depth', 'N/A')}")
    print(f"  showers: {d.get('showers', 'N/A')}")
    print(f"  daily_precip_sum: {d.get('daily_precip_sum', 'N/A')}")
    print(f"  daily_rain_sum: {d.get('daily_rain_sum', 'N/A')}")
    print(f"  daily_snow_sum: {d.get('daily_snow_sum', 'N/A')}")
    
    await c.close()

if __name__ == "__main__":
    asyncio.run(check_precip())
