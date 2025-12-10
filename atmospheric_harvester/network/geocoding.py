import aiohttp
import asyncio

class GeocodingClient:
    BASE_URL = "https://geocoding-api.open-meteo.com/v1/search"

    def __init__(self):
        self.session = None

    async def start(self):
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def search_city(self, city_name, count=10):
        """
        Search for cities by name using Open-Meteo Geocoding API.
        
        Args:
            city_name: Name of the city to search for (minimum 3 characters)
            count: Number of results to return (max 100)
            
        Returns:
            List of dictionaries with city information:
            {
                'name': 'Paris',
                'country': 'France',
                'lat': 48.8566,
                'lon': 2.3522,
                'admin1': 'Île-de-France'  # State/region if available
            }
        """
        if not city_name or len(city_name) < 3:
            return []
        
        if not self.session:
            await self.start()

        params = {
            "name": city_name,
            "count": min(count, 100),
            "language": "en",
            "format": "json"
        }

        try:
            async with self.session.get(self.BASE_URL, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_results(data)
                else:
                    print(f"Geocoding Error: {response.status}")
                    return []
        except Exception as e:
            print(f"Geocoding Network Error: {e}")
            return []

    def _parse_results(self, data):
        """Parse geocoding API response into clean city data."""
        results = data.get("results", [])
        cities = []
        
        for result in results:
            city = {
                'name': result.get('name', ''),
                'country': result.get('country', ''),
                'lat': result.get('latitude', 0.0),
                'lon': result.get('longitude', 0.0),
                'admin1': result.get('admin1', '')  # State/region
            }
            
            # Create display name with country
            display_name = city['name']
            if city['admin1'] and city['admin1'] != city['name']:
                display_name += f", {city['admin1']}"
            if city['country']:
                display_name += f", {city['country']}"
            
            city['display_name'] = display_name
            cities.append(city)
        
        return cities


# Test script
async def main():
    client = GeocodingClient()
    
    # Test searches
    print("Searching for 'Paris'...")
    results = await client.search_city("Paris", count=5)
    for city in results:
        print(f"  {city['display_name']} ({city['lat']:.2f}, {city['lon']:.2f})")
    
    print("\nSearching for 'Tokyo'...")
    results = await client.search_city("Tokyo", count=5)
    for city in results:
        print(f"  {city['display_name']} ({city['lat']:.2f}, {city['lon']:.2f})")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
