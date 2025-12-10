"""
Unified Weather Service

Routes weather requests to the appropriate backend:
- NWS (National Weather Service) for US locations
- Open-Meteo for international locations

Also provides supplemental data (air quality, soil) from Open-Meteo
for US locations since NWS doesn't provide these.
"""

import asyncio
from typing import Optional
from network.nws_client import NWSClient
from network.open_meteo import OpenMeteoClient
from network.gfs_client import GFSClient


class WeatherService:
    """
    Unified weather service that selects the best data source based on location.
    
    For US locations:
    - Primary weather data from NWS (more accurate, real-time)
    - Supplemental air quality and soil data from Open-Meteo
    
    For international locations:
    - All data from Open-Meteo
    """
    
    # Continental US bounding box (approximate)
    US_LAT_MIN = 24.0   # Southern tip of Florida
    US_LAT_MAX = 50.0   # Northern border (lower 48)
    US_LON_MIN = -125.0 # West coast
    US_LON_MAX = -66.0  # East coast
    
    # Alaska bounding box
    ALASKA_LAT_MIN = 51.0
    ALASKA_LAT_MAX = 72.0
    ALASKA_LON_MIN = -180.0
    ALASKA_LON_MAX = -129.0
    
    # Hawaii bounding box
    HAWAII_LAT_MIN = 18.0
    HAWAII_LAT_MAX = 23.0
    HAWAII_LON_MIN = -161.0
    HAWAII_LON_MAX = -154.0
    
    # Puerto Rico bounding box
    PR_LAT_MIN = 17.5
    PR_LAT_MAX = 18.6
    PR_LON_MIN = -68.0
    PR_LON_MAX = -65.0
    
    def __init__(self):
        self.nws = NWSClient()
        self.open_meteo = OpenMeteoClient()
        self.gfs = GFSClient()  # NOAA GFS GRIB2 for supplemental data
        self._last_source = "none"  # Track which source was used
    
    async def start(self):
        """Initialize all weather clients."""
        await self.nws.start()
        await self.open_meteo.start()
        await self.gfs.start()
    
    async def close(self):
        """Close all weather clients."""
        await self.nws.close()
        await self.open_meteo.close()
        await self.gfs.close()
    
    def _is_us_location(self, lat: float, lon: float) -> bool:
        """
        Check if coordinates are within US coverage area.
        
        Includes continental US, Alaska, Hawaii, and Puerto Rico.
        """
        # Continental US
        if (self.US_LAT_MIN <= lat <= self.US_LAT_MAX and 
            self.US_LON_MIN <= lon <= self.US_LON_MAX):
            return True
        
        # Alaska
        if (self.ALASKA_LAT_MIN <= lat <= self.ALASKA_LAT_MAX and 
            self.ALASKA_LON_MIN <= lon <= self.ALASKA_LON_MAX):
            return True
        
        # Hawaii
        if (self.HAWAII_LAT_MIN <= lat <= self.HAWAII_LAT_MAX and 
            self.HAWAII_LON_MIN <= lon <= self.HAWAII_LON_MAX):
            return True
        
        # Puerto Rico
        if (self.PR_LAT_MIN <= lat <= self.PR_LAT_MAX and 
            self.PR_LON_MIN <= lon <= self.PR_LON_MAX):
            return True
        
        return False
    
    async def get_weather(self, lat: float, lon: float) -> Optional[dict]:
        """
        Get weather data for any location.
        
        Automatically routes to NWS for US locations, Open-Meteo for international.
        For US locations, also fetches supplemental data (air quality, soil) from Open-Meteo.
        """
        if self._is_us_location(lat, lon):
            # Try NWS first for US locations
            nws_data = await self.nws.get_weather(lat, lon)
            
            if nws_data:
                self._last_source = "NWS"
                print(f"Weather source: NWS ({nws_data.get('_nws_station', 'Unknown')})")
                
                # Fetch supplemental data from Open-Meteo and GFS
                try:
                    supplemental = await self._get_supplemental_data(lat, lon)
                    if supplemental:
                        # Smart merge: prefer non-zero supplemental values when NWS has zeros
                        nws_data = self._smart_merge(nws_data, supplemental)
                except Exception as e:
                    print(f"Failed to get supplemental data: {e}")
                
                return nws_data
            else:
                # NWS failed, fall back to Open-Meteo
                print("NWS unavailable, falling back to Open-Meteo")
        
        # International location or NWS fallback
        self._last_source = "Open-Meteo"
        print("Weather source: Open-Meteo")
        return await self.open_meteo.get_weather(lat, lon)
    
    async def get_forecast(self, lat: float, lon: float, days: int = 7) -> list:
        """
        Get 7-day forecast for any location.
        
        Uses Open-Meteo forecast API for all locations.
        """
        return await self.open_meteo.get_forecast(lat, lon, days)

    async def get_alerts(self, lat: float, lon: float) -> list:
        """
        Get active weather alerts for a location.
        Only supported for US locations via NWS currently.
        """
        if self._is_us_location(lat, lon):
            return await self.nws.get_alerts(lat, lon)
        return []
    
    async def _get_supplemental_data(self, lat: float, lon: float) -> Optional[dict]:
        """
        Get supplemental data from multiple sources:
        - Open-Meteo: Air quality, UV, solar radiation
        - GFS GRIB2: CAPE, CIN, soil moisture, visibility, gust
        """
        result = {}
        # Fetch from Open-Meteo
        try:
            om_data = await self.open_meteo.get_weather(lat, lon)
            if om_data:
                result.update({
                    # Wind (fallback if NWS returns null)
                    "wind_speed": om_data.get("wind_speed", 0.0),
                    "wind_speed_10m": om_data.get("wind_speed_10m", om_data.get("wind_speed", 0.0)),
                    "wind_speed_80m": om_data.get("wind_speed_80m", 0.0),
                    "wind_speed_120m": om_data.get("wind_speed_120m", 0.0),
                    "wind_dir": om_data.get("wind_dir", 0),
                    "wind_dir_10m": om_data.get("wind_dir_10m", om_data.get("wind_dir", 0)),
                    "wind_gusts": om_data.get("wind_gusts", 0.0),
                    
                    # Air Quality
                    "us_aqi": om_data.get("us_aqi", 0),
                    "pm10": om_data.get("pm10", 0.0),
                    "pm2_5": om_data.get("pm2_5", 0.0),
                    "carbon_monoxide": om_data.get("carbon_monoxide", 0.0),
                    "nitrogen_dioxide": om_data.get("nitrogen_dioxide", 0.0),
                    "sulphur_dioxide": om_data.get("sulphur_dioxide", 0.0),
                    "ozone": om_data.get("ozone", 0.0),
                    "aerosol_optical_depth": om_data.get("aerosol_optical_depth", 0.0),
                    "dust": om_data.get("dust", 0.0),
                    
                    # UV
                    "uv_index": om_data.get("uv_index", 0.0),
                    "uv_index_clear_sky": om_data.get("uv_index_clear_sky", 0.0),
                    
                    # Solar Radiation
                    "shortwave_radiation": om_data.get("shortwave_radiation", 0.0),
                    "direct_radiation": om_data.get("direct_radiation", 0.0),
                    "diffuse_radiation": om_data.get("diffuse_radiation", 0.0),
                    "direct_normal_irradiance": om_data.get("direct_normal_irradiance", 0.0),
                    "global_tilted_irradiance": om_data.get("global_tilted_irradiance", 0.0),
                    "terrestrial_radiation": om_data.get("terrestrial_radiation", 0.0),
                    
                    # Precipitation (NWS observations often lack this)
                    "precip_probability": om_data.get("precip_probability", 0.0),
                    "precipitation": om_data.get("precipitation", 0.0),
                    "rain": om_data.get("rain", 0.0),
                    "snowfall": om_data.get("snowfall", 0.0),
                    "snow_depth": om_data.get("snow_depth", 0.0),
                    "showers": om_data.get("showers", 0.0),
                    
                    # Advanced
                    "freezing_level": om_data.get("freezing_level", 0.0),
                    "et0": om_data.get("et0", 0.0),
                    "evapotranspiration": om_data.get("evapotranspiration", 0.0),
                    
                    # Daily
                    "sunrise": om_data.get("sunrise", ""),
                    "sunset": om_data.get("sunset", ""),
                    "daylight_duration": om_data.get("daylight_duration", 0.0),
                    "daily_sunshine_duration": om_data.get("daily_sunshine_duration", 0.0),
                    "daily_precip_sum": om_data.get("daily_precip_sum", 0.0),
                    "daily_rain_sum": om_data.get("daily_rain_sum", 0.0),
                    "daily_snow_sum": om_data.get("daily_snow_sum", 0.0),
                    "daily_uv_max": om_data.get("daily_uv_max", 0.0),
                    "daily_wind_max": om_data.get("daily_wind_max", 0.0),
                    "daily_wind_gusts_max": om_data.get("daily_wind_gusts_max", 0.0),
                    "daily_et0_sum": om_data.get("daily_et0_sum", 0.0),
                })
        except Exception as e:
            print(f"Open-Meteo supplemental error: {e}")
        
        # Fetch from GFS GRIB2 (CAPE, soil moisture, visibility)
        try:
            gfs_data = await self.gfs.get_supplemental_data(lat, lon)
            if gfs_data:
                # GFS data takes priority for these fields (more accurate model data)
                result.update({
                    "cape": gfs_data.get("gfs_cape", result.get("cape", 0.0)),
                    "cin": gfs_data.get("gfs_cin", 0.0),
                    "soil_moisture": gfs_data.get("gfs_soil_moisture", result.get("soil_moisture", 0.0)),
                    "gfs_visibility": gfs_data.get("gfs_visibility", 0.0),
                    "gfs_gust": gfs_data.get("gfs_gust", 0.0),
                    "gfs_snow_depth": gfs_data.get("gfs_snow_depth", 0.0),
                    "gfs_precip_rate": gfs_data.get("gfs_precip_rate", 0.0),
                })
        except Exception as e:
            print(f"GFS supplemental error: {e}")
        
        return result if result else None
    
    def _smart_merge(self, base: dict, supplemental: dict) -> dict:
        """
        Smart merge that prefers non-zero supplemental values for keys where base has 0.
        
        This handles the case where NWS returns null/0 for wind, but Open-Meteo
        or GFS has valid data.
        """
        # Keys where we should prefer non-zero supplemental values
        prefer_nonzero_keys = {
            "wind_speed", "wind_speed_10m", "wind_speed_80m", "wind_speed_120m",
            "wind_dir", "wind_dir_10m", "wind_gusts",
            "shortwave_radiation", "direct_radiation", "diffuse_radiation",
            "direct_normal_irradiance", "global_tilted_irradiance", "terrestrial_radiation",
            "uv_index", "uv_index_clear_sky",
            "cape", "cin", "et0", "evapotranspiration",
            "soil_moisture", "soil_temp",
            "visibility", "snow_depth",
            "us_aqi", "pm2_5", "pm10", "ozone",
            "sunrise", "sunset", "daylight_duration",
            # Precipitation
            "precip_probability", "precipitation", "rain", "snowfall", "showers",
            "daily_precip_sum", "daily_rain_sum", "daily_snow_sum",
        }
        
        result = base.copy()
        
        for key, value in supplemental.items():
            if key in result:
                # If base value is 0/empty and supplemental has data, use supplemental
                base_val = result[key]
                if key in prefer_nonzero_keys:
                    if (base_val == 0 or base_val == 0.0 or base_val == "") and value:
                        result[key] = value
                    # Also prefer supplemental if it's non-zero and has more precision
                    elif value and value != 0 and value != 0.0:
                        result[key] = value
                else:
                    # For other keys, supplemental overwrites
                    result[key] = value
            else:
                # Key doesn't exist in base, add it
                result[key] = value
        
        return result
    
    @property
    def last_source(self) -> str:
        """Return the name of the last weather source used."""
        return self._last_source


# Test script
async def main():
    service = WeatherService()
    await service.start()
    
    # Test US location (South Saint Paul, MN)
    print("=" * 50)
    print("Testing US location: South Saint Paul, MN")
    print("=" * 50)
    data = await service.get_weather(44.89, -93.02)
    if data:
        print(f"Temperature: {data['temp']:.1f}°C ({data['temp'] * 9/5 + 32:.1f}°F)")
        print(f"Humidity: {data['humidity']:.1f}%")
        print(f"AQI: {data.get('us_aqi', 'N/A')}")
        print(f"UV Index: {data.get('uv_index', 'N/A')}")
        print(f"Source: {service.last_source}")
    
    print()
    
    # Test international location (London, UK)
    print("=" * 50)
    print("Testing international: London, UK")
    print("=" * 50)
    data = await service.get_weather(51.5074, -0.1278)
    if data:
        print(f"Temperature: {data['temp']:.1f}°C ({data['temp'] * 9/5 + 32:.1f}°F)")
        print(f"Humidity: {data['humidity']:.1f}%")
        print(f"Source: {service.last_source}")
    
    await service.close()


if __name__ == "__main__":
    asyncio.run(main())
