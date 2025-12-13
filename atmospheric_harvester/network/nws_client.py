"""
NWS (National Weather Service) API Client

Fetches weather data from the official US government weather service.
Only works for locations within the United States and its territories.

API Documentation: https://www.weather.gov/documentation/services-web-api
"""

import aiohttp
import asyncio
from datetime import datetime
from typing import Optional, Dict, List, Any


class NWSClient:
    """
    Async client for the National Weather Service API.
    
    The NWS API requires a two-step process:
    1. Get grid point metadata from lat/lon → returns forecast URLs and station list URL
    2. Get current observations from the nearest weather station
    """
    
    BASE_URL = "https://api.weather.gov"
    USER_AGENT = "AtmosphericHarvester/1.0 (github.com/atmospheric-harvester)"
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self._gridpoint_cache: Dict[str, dict] = {}  # Cache gridpoint lookups
    
    async def start(self):
        """Initialize the HTTP session."""
        if not self.session:
            headers = {
                "User-Agent": self.USER_AGENT,
                "Accept": "application/geo+json"
            }
            self.session = aiohttp.ClientSession(headers=headers)
    
    async def close(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def get_gridpoint(self, lat: float, lon: float) -> Optional[dict]:
        """
        Get grid point metadata for a location.
        
        Returns URLs for forecast, hourly forecast, and observation stations.
        Results are cached to avoid repeated lookups for the same location.
        """
        if not self.session:
            await self.start()
        
        # Round to 2 decimal places for cache key
        cache_key = f"{lat:.2f},{lon:.2f}"
        if cache_key in self._gridpoint_cache:
            return self._gridpoint_cache[cache_key]
        
        url = f"{self.BASE_URL}/points/{lat},{lon}"
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    properties = data.get("properties", {})
                    result = {
                        "gridId": properties.get("gridId"),
                        "gridX": properties.get("gridX"),
                        "gridY": properties.get("gridY"),
                        "forecast": properties.get("forecast"),
                        "forecastHourly": properties.get("forecastHourly"),
                        "forecastGridData": properties.get("forecastGridData"),
                        "observationStations": properties.get("observationStations"),
                        "timeZone": properties.get("timeZone"),
                        "city": properties.get("relativeLocation", {}).get("properties", {}).get("city", ""),
                        "state": properties.get("relativeLocation", {}).get("properties", {}).get("state", "")
                    }
                    self._gridpoint_cache[cache_key] = result
                    return result
                elif response.status == 404:
                    # Location not in US
                    print(f"NWS: Location {lat}, {lon} not in US coverage area")
                    return None
                else:
                    print(f"NWS Gridpoint Error: {response.status}")
                    return None
        except Exception as e:
            print(f"NWS Network Error (gridpoint): {e}")
            return None
    
    async def get_stations(self, stations_url: str) -> List[str]:
        """
        Get list of observation station IDs near the grid point.
        
        Returns station IDs sorted by distance (nearest first).
        """
        if not self.session:
            await self.start()
        
        try:
            async with self.session.get(stations_url) as response:
                if response.status == 200:
                    data = await response.json()
                    features = data.get("features", [])
                    # Extract station IDs (already sorted by distance)
                    station_ids = []
                    for feature in features[:5]:  # Only keep 5 nearest
                        station_id = feature.get("properties", {}).get("stationIdentifier")
                        if station_id:
                            station_ids.append(station_id)
                    return station_ids
                else:
                    print(f"NWS Stations Error: {response.status}")
                    return []
        except Exception as e:
            print(f"NWS Network Error (stations): {e}")
            return []
    
    async def get_current_observation(self, station_id: str) -> Optional[dict]:
        """
        Get the latest weather observation from a station.
        
        Returns parsed observation data or None if unavailable.
        """
        if not self.session:
            await self.start()
        
        url = f"{self.BASE_URL}/stations/{station_id}/observations/latest"
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_observation(data)
                else:
                    print(f"NWS Observation Error for {station_id}: {response.status}")
                    return None
        except Exception as e:
            print(f"NWS Network Error (observation): {e}")
            return None
    
    def _parse_observation(self, data: dict) -> dict:
        """
        Parse NWS observation response into game-compatible format.
        
        Returns None if the observation has no valid temperature data.
        """
        props = data.get("properties", {})
        
        def get_value(key: str, default: float = 0.0) -> float:
            """Safely extract value from NWS property object."""
            obj = props.get(key, {})
            if isinstance(obj, dict):
                val = obj.get("value")
                return val if val is not None else default
            return default
        
        def has_valid_value(key: str) -> bool:
            """Check if a key has a non-null value."""
            obj = props.get(key, {})
            if isinstance(obj, dict):
                return obj.get("value") is not None
            return False
        
        # Check if this observation has valid temperature data
        if not has_valid_value("temperature"):
            return None  # This observation is invalid, try next station
        
        # Parse cloud cover from cloud layers
        cloud_cover = 0.0
        cloud_layers = props.get("cloudLayers", [])
        if cloud_layers:
            # Map cloud amount codes to percentages
            amount_map = {
                "CLR": 0, "SKC": 0,  # Clear
                "FEW": 18,           # Few (1-2 oktas)
                "SCT": 44,           # Scattered (3-4 oktas)
                "BKN": 75,           # Broken (5-7 oktas)
                "OVC": 100           # Overcast (8 oktas)
            }
            # Use the highest layer amount
            for layer in cloud_layers:
                amount = layer.get("amount", "")
                cloud_cover = max(cloud_cover, amount_map.get(amount, 0))
        
        # Map text description to weather code
        text_desc = props.get("textDescription", "").lower()
        weather_code = self._text_to_weather_code(text_desc)
        
        # Get timestamp
        timestamp = props.get("timestamp", "")
        
        # Temperature is in Celsius
        temp_c = get_value("temperature")
        
        # Wind speed from NWS is in km/h, convert to m/s
        wind_kmh = get_value("windSpeed")
        wind_ms = wind_kmh / 3.6 if wind_kmh else 0.0
        
        # Pressure from NWS is in Pascals, convert to hPa
        pressure_pa = get_value("barometricPressure")
        pressure_hpa = pressure_pa / 100 if pressure_pa else 0.0
        
        # Visibility from NWS is in meters
        visibility_m = get_value("visibility")
        
        return {
            # Core weather data
            "temp": temp_c,
            "wind_speed": wind_ms,
            "wind_dir": get_value("windDirection"),
            "weather_code": weather_code,
            "is_day": self._is_daytime(),  # NWS doesn't provide this directly
            
            # Temperature & Humidity
            "temp_2m": temp_c,
            "temp_2m": temp_c,
            "apparent_temp": self._calculate_feels_like(
                temp_c, 
                get_value("windChill", None), 
                get_value("heatIndex", None), 
                wind_ms, 
                get_value("relativeHumidity")
            ),
            "dewpoint": get_value("dewpoint"),
            "humidity": get_value("relativeHumidity"),
            
            # Precipitation (NWS observations don't always have this)
            "precip_probability": 0.0,  # Not available in observations
            "precipitation": get_value("precipitationLastHour"),
            "rain": get_value("precipitationLastHour"),
            "showers": 0.0,
            "snowfall": 0.0,
            "snow_depth": 0.0,
            
            # Atmospheric
            "pressure": pressure_hpa,
            "surface_pressure": pressure_hpa,
            "cloud_cover": cloud_cover,
            "cloud_cover_low": cloud_cover,
            "cloud_cover_mid": 0.0,
            "cloud_cover_high": 0.0,
            "visibility": visibility_m,
            "vapor_pressure_deficit": 0.0,
            
            # Wind
            "wind_speed_10m": wind_ms,
            "wind_speed_80m": wind_ms,
            "wind_speed_120m": wind_ms,
            "wind_dir_10m": get_value("windDirection"),
            "wind_gusts": get_value("windGust") / 3.6 if get_value("windGust") else 0.0,
            
            # Solar (not available from NWS observations)
            "shortwave_radiation": 0.0,
            "direct_radiation": 0.0,
            "diffuse_radiation": 0.0,
            "direct_normal_irradiance": 0.0,
            "global_tilted_irradiance": 0.0,
            "terrestrial_radiation": 0.0,
            
            # Soil (not available from NWS)
            "soil_temp_0cm": 0.0,
            "soil_temp_6cm": 0.0,
            "soil_temp_18cm": 0.0,
            "soil_temp_54cm": 0.0,
            "soil_moisture_0_1cm": 0.0,
            "soil_moisture_1_3cm": 0.0,
            "soil_moisture_3_9cm": 0.0,
            "soil_moisture_9_27cm": 0.0,
            "soil_moisture_27_81cm": 0.0,
            
            # Advanced
            "uv_index": 0.0,  # Not in NWS observations
            "uv_index_clear_sky": 0.0,
            "cape": 0.0,
            "freezing_level": 0.0,
            "et0": 0.0,
            "evapotranspiration": 0.0,
            "sunshine_duration": 0.0,
            
            # Air Quality (not available from NWS)
            "us_aqi": 0,
            "pm10": 0.0,
            "pm2_5": 0.0,
            "carbon_monoxide": 0.0,
            "nitrogen_dioxide": 0.0,
            "sulphur_dioxide": 0.0,
            "ozone": 0.0,
            "aerosol_optical_depth": 0.0,
            "dust": 0.0,
            
            # Daily Data (would need forecast endpoint)
            "sunrise": "",
            "sunset": "",
            "daylight_duration": 0.0,
            "daily_sunshine_duration": 0.0,
            "daily_precip_sum": 0.0,
            "daily_rain_sum": 0.0,
            "daily_snow_sum": 0.0,
            "daily_uv_max": 0.0,
            "daily_wind_max": 0.0,
            "daily_wind_gusts_max": 0.0,
            "daily_et0_sum": 0.0,
            
            # Legacy compatibility
            "soil_moisture": 0.0,
            "soil_temp": 0.0,
            
            # NWS-specific extras
            "_nws_timestamp": timestamp,
            "_nws_station": props.get("stationId", ""),
            "_nws_text": props.get("textDescription", ""),
        }
    
    def _text_to_weather_code(self, text: str) -> int:
        """
        Convert NWS text description to WMO weather code.
        
        Reference: https://open-meteo.com/en/docs (weather codes)
        """
        text = text.lower()
        
        # Thunderstorms (95-99)
        if "thunder" in text:
            if "heavy" in text:
                return 99
            return 95
        
        # Snow (71-77)
        if "snow" in text or "blizzard" in text:
            if "heavy" in text:
                return 75
            if "light" in text:
                return 71
            return 73
        
        # Freezing rain/drizzle (66-67)
        if "freezing" in text:
            return 67 if "rain" in text else 66
        
        # Rain (61-67, 80-82)
        if "rain" in text or "shower" in text:
            if "heavy" in text:
                return 65
            if "light" in text:
                return 61
            return 63
        
        # Drizzle (51-57)
        if "drizzle" in text:
            return 53
        
        # Fog/Mist (45-48)
        if "fog" in text or "mist" in text:
            return 45
        
        # Overcast (3)
        if "overcast" in text or "cloudy" in text:
            return 3
        
        # Partly cloudy (2)
        if "partly" in text or "mostly sunny" in text:
            return 2
        
        # Few clouds (1)
        if "few" in text or "mostly clear" in text:
            return 1
        
        # Clear (0)
        if "clear" in text or "sunny" in text or "fair" in text:
            return 0
        
        # Default to partly cloudy
        return 2
    
    def _calculate_feels_like(self, temp_c: float, wind_chill: Optional[float], 
                             heat_index: Optional[float], wind_ms: float, humidity: float) -> float:
        """
        Calculate 'Feels Like' temperature.
        
        Logic:
        1. Use NWS provided windChill or heatIndex if available.
        2. If temp <= 10°C (50°F), calculate Wind Chill.
        3. If temp >= 27°C (80°F), calculate Heat Index.
        4. Otherwise return actual temperature.
        """
        # 1. Trust NWS provided values if they trigger
        if wind_chill is not None:
            return wind_chill
        if heat_index is not None:
            return heat_index
            
        # 2. Wind Chill (Valid for T <= 10°C and Wind > 4.8 km/h)
        wind_kmh = wind_ms * 3.6
        if temp_c <= 10.0 and wind_kmh > 4.8:
            # Formula: 13.12 + 0.6215*T - 11.37*V^0.16 + 0.3965*T*V^0.16
            return 13.12 + (0.6215 * temp_c) - (11.37 * (wind_kmh ** 0.16)) + (0.3965 * temp_c * (wind_kmh ** 0.16))
            
        # 3. Heat Index (Valid for T >= 27°C)
        if temp_c >= 27.0:
            # Simple approximation if humidity not provided
            if not humidity:
                return temp_c
                
            # Rothfusz regression (requires T in F)
            T = (temp_c * 9/5) + 32
            RH = humidity
            
            HI = -42.379 + 2.04901523*T + 10.14333127*RH - 0.22475541*T*RH - \
                 6.83783e-3*T*T - 5.481717e-2*RH*RH + 1.22874e-3*T*T*RH + \
                 8.5282e-4*T*RH*RH - 1.99e-6*T*T*RH*RH
                 
            # Adjustments
            if RH < 13 and 80 <= T <= 112:
                adj = ((13-RH)/4)*(((17-abs(T-95.))/17)**0.5)
                HI -= adj
            elif RH > 85 and 80 <= T <= 87:
                adj = ((RH-85)/10) * ((87-T)/5)
                HI += adj
                
            # Convert back to C
            return (HI - 32) * 5/9
            
        # 4. Standard Temp
        return temp_c

    def _is_daytime(self) -> bool:
        """
        Simple daytime check based on current hour.
        
        TODO: Could use sunrise/sunset from forecast endpoint for accuracy.
        """
        hour = datetime.now().hour
        return 6 <= hour < 20
    
    async def get_weather(self, lat: float, lon: float) -> Optional[dict]:
        """
        Get current weather for a US location.
        
        This is the main entry point that handles the multi-step API process:
        1. Get grid point → observation stations URL
        2. Get nearest stations
        3. Get latest observation from first available station
        
        Returns None if location is not in US or if all API calls fail.
        """
        # Step 1: Get grid point
        gridpoint = await self.get_gridpoint(lat, lon)
        if not gridpoint:
            return None
        
        # Step 2: Get stations
        stations_url = gridpoint.get("observationStations")
        if not stations_url:
            print("NWS: No observation stations URL")
            return None
        
        station_ids = await self.get_stations(stations_url)
        if not station_ids:
            print("NWS: No observation stations found")
            return None
        
        # Step 3: Try each station until we get data
        for station_id in station_ids:
            observation = await self.get_current_observation(station_id)
            if observation and observation.get("temp") is not None:
                print(f"NWS: Using station {station_id} for weather data")
                return observation
        
        print("NWS: No valid observations from any station")
        return None

    async def get_alerts(self, lat: float, lon: float) -> List[dict]:
        """
        Get active weather alerts for a location.
        
        Returns a list of alerts containing event name, severity, and description.
        """
        if not self.session:
            await self.start()
            
        url = f"{self.BASE_URL}/alerts/active?point={lat},{lon}"
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    features = data.get("features", [])
                    alerts = []
                    
                    for feature in features:
                        props = feature.get("properties", {})
                        alerts.append({
                            "event": props.get("event", "Unknown Alert"),
                            "severity": props.get("severity", "Unknown"),
                            "description": props.get("description", ""),
                            "headline": props.get("headline", ""),
                            "instruction": props.get("instruction", "")
                        })
                    return alerts
                else:
                    print(f"NWS Alert Error: {response.status}")
                    return []
        except Exception as e:
            print(f"NWS Network Error (alerts): {e}")
            return []


# Test script
async def main():
    client = NWSClient()
    
    # Test with South Saint Paul, MN
    print("Testing NWS API for South Saint Paul, MN...")
    data = await client.get_weather(44.89, -93.02)
    
    if data:
        print(f"\nTemperature: {data['temp']:.1f}°C ({data['temp'] * 9/5 + 32:.1f}°F)")
        print(f"Humidity: {data['humidity']:.1f}%")
        print(f"Wind: {data['wind_speed']:.1f} m/s from {data['wind_dir']}°")
        print(f"Feels Like: {data['apparent_temp']:.1f}°C")
        print(f"Conditions: {data.get('_nws_text', 'Unknown')}")
        print(f"Station: {data.get('_nws_station', 'Unknown')}")
    else:
        print("Failed to get weather data")
    
    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
