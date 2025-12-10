"""Check raw NWS API response."""
import asyncio
import aiohttp

async def check_raw_nws():
    url = "https://api.weather.gov/stations/KSGS/observations/latest"
    headers = {
        "User-Agent": "AtmosphericHarvester/1.0",
        "Accept": "application/geo+json"
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                props = data.get("properties", {})
                
                print("Raw NWS API Response for KSGS:")
                print(f"  temperature: {props.get('temperature')}")
                print(f"  relativeHumidity: {props.get('relativeHumidity')}")
                print(f"  barometricPressure: {props.get('barometricPressure')}")
                print(f"  dewpoint: {props.get('dewpoint')}")
                print(f"  windSpeed: {props.get('windSpeed')}")
                print(f"  windDirection: {props.get('windDirection')}")
                print(f"  visibility: {props.get('visibility')}")
                print(f"  textDescription: {props.get('textDescription')}")
                print(f"  timestamp: {props.get('timestamp')}")
            else:
                print(f"Error: {response.status}")

if __name__ == "__main__":
    asyncio.run(check_raw_nws())
