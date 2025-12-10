"""Debug script to see all weather data being returned."""
import asyncio
from network.weather_service import WeatherService

async def debug_weather():
    service = WeatherService()
    await service.start()
    
    # South Saint Paul, MN
    data = await service.get_weather(44.89, -93.02)
    
    print("=" * 70)
    print("ALL WEATHER DATA KEYS AND VALUES")
    print("=" * 70)
    
    if data:
        # Group by prefix
        groups = {}
        for key in sorted(data.keys()):
            if key.startswith("_"):
                group = "Internal"
            elif key.startswith("gfs_"):
                group = "GFS"
            elif key.startswith("daily_"):
                group = "Daily"
            elif key.startswith("soil"):
                group = "Soil"
            elif key.startswith("wind"):
                group = "Wind"
            elif key.startswith("cloud"):
                group = "Cloud"
            else:
                group = "Core"
            
            if group not in groups:
                groups[group] = []
            groups[group].append((key, data[key]))
        
        for group in ["Core", "Wind", "Cloud", "Soil", "GFS", "Daily", "Internal"]:
            if group in groups:
                print(f"\n--- {group} ---")
                for key, value in groups[group]:
                    if isinstance(value, float):
                        print(f"  {key}: {value:.4f}")
                    else:
                        print(f"  {key}: {value}")
        
        print(f"\n\nTotal keys: {len(data)}")
    else:
        print("No data returned!")
    
    await service.close()

if __name__ == "__main__":
    asyncio.run(debug_weather())
