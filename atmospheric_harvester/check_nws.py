"""Check what NWS is actually returning."""
import asyncio
from network.nws_client import NWSClient

async def check_nws():
    c = NWSClient()
    await c.start()
    
    # South Saint Paul, MN
    d = await c.get_weather(44.89, -93.02)
    
    if d:
        print("NWS Core Data:")
        print(f"  temp: {d.get('temp')}")
        print(f"  humidity: {d.get('humidity')}")
        print(f"  pressure: {d.get('pressure')}")
        print(f"  dewpoint: {d.get('dewpoint')}")
        print(f"  wind_speed: {d.get('wind_speed')}")
        print(f"  visibility: {d.get('visibility')}")
        print(f"  _nws_station: {d.get('_nws_station')}")
        print(f"  _nws_text: {d.get('_nws_text')}")
    else:
        print("NWS returned None!")
    
    await c.close()

if __name__ == "__main__":
    asyncio.run(check_nws())
