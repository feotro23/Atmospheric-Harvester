import aiohttp
import asyncio
import json
from datetime import datetime

class OpenMeteoClient:
    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

    def __init__(self):
        self.session = None

    async def start(self):
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def get_weather(self, lat, lon):
        if not self.session:
            await self.start()

        # Weather Forecast Params
        weather_params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": "true",
            "hourly": (
                "temperature_2m,relativehumidity_2m,dewpoint_2m,apparent_temperature,"
                "precipitation_probability,precipitation,rain,showers,snowfall,snow_depth,"
                "weathercode,pressure_msl,surface_pressure,cloudcover,cloudcover_low,cloudcover_mid,cloudcover_high,"
                "visibility,evapotranspiration,et0_fao_evapotranspiration,vapor_pressure_deficit,"
                "windspeed_10m,windspeed_80m,windspeed_120m,winddirection_10m,windgusts_10m,"
                "shortwave_radiation,direct_radiation,diffuse_radiation,direct_normal_irradiance,"
                "global_tilted_irradiance,terrestrial_radiation,shortwave_radiation_instant,"
                "diffuse_radiation_instant,direct_normal_irradiance_instant,global_tilted_irradiance_instant,"
                "terrestrial_radiation_instant,"
                "soil_temperature_0cm,soil_temperature_6cm,soil_temperature_18cm,soil_temperature_54cm,"
                "soil_moisture_0_1cm,soil_moisture_1_3cm,soil_moisture_3_9cm,soil_moisture_9_27cm,soil_moisture_27_81cm,"
                "uv_index,uv_index_clear_sky,is_day,cape,freezinglevel_height,sunshine_duration"
            ),
            "daily": "sunrise,sunset,daylight_duration,sunshine_duration,uv_index_max,uv_index_clear_sky_max,precipitation_sum,rain_sum,showers_sum,snowfall_sum,precipitation_hours,precipitation_probability_max,windspeed_10m_max,windgusts_10m_max,winddirection_10m_dominant,shortwave_radiation_sum,et0_fao_evapotranspiration",
            "timezone": "auto",
            "windspeed_unit": "ms"
        }

        # Air Quality Params
        aqi_params = {
            "latitude": lat,
            "longitude": lon,
            "current": "us_aqi",
            "hourly": "us_aqi,pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,aerosol_optical_depth,dust,uv_index",
            "timezone": "auto"
        }

        try:
            # Fetch both concurrently
            weather_task = self.session.get(self.BASE_URL, params=weather_params)
            aqi_task = self.session.get(self.AIR_QUALITY_URL, params=aqi_params)

            responses = await asyncio.gather(weather_task, aqi_task, return_exceptions=True)
            
            weather_resp = responses[0]
            aqi_resp = responses[1]

            weather_data = {}
            aqi_data = {}

            # Process Weather Response
            if not isinstance(weather_resp, Exception) and weather_resp.status == 200:
                weather_data = await weather_resp.json()
            else:
                print(f"Weather API Error: {weather_resp}")

            # Process AQI Response
            if not isinstance(aqi_resp, Exception) and aqi_resp.status == 200:
                aqi_data = await aqi_resp.json()
            else:
                print(f"AQI API Error: {aqi_resp}")

            if weather_data:
                return self._parse_data(weather_data, aqi_data)
            return None

        except Exception as e:
            print(f"Network Error: {e}")
            return None

    def _parse_data(self, data, aqi_data=None):
        # Parse raw JSON into a comprehensive dictionary for the game
        current = data.get("current_weather", {})
        hourly = data.get("hourly", {})
        daily = data.get("daily", {})
        
        # AQI Data
        aqi_current = aqi_data.get("current", {}) if aqi_data else {}
        aqi_hourly = aqi_data.get("hourly", {}) if aqi_data else {}

        # Get current hour index from the API's current time (respects location timezone)
        # The API returns time in format "2025-12-08T00:45" 
        current_time_str = current.get("time", "")
        now_hour = 0
        if current_time_str:
            try:
                # Parse the ISO format time from the API
                current_dt = datetime.fromisoformat(current_time_str)
                now_hour = current_dt.hour
            except (ValueError, TypeError):
                # Fallback to local time if parsing fails
                now_hour = datetime.now().hour
        else:
            now_hour = datetime.now().hour
        
        def get_hourly(key, default=0.0, source=hourly):
            """Helper to safely get hourly data for current hour."""
            if key in source and len(source[key]) > now_hour:
                value = source[key][now_hour]
                return value if value is not None else default
            return default
        
        def get_daily(key, index=0, default=""):
            """Helper to safely get daily data."""
            if key in daily and len(daily[key]) > index:
                return daily[key][index]
            return default

        return {
            # Current Weather (from current_weather endpoint)
            "temp": current.get("temperature", 0.0),
            "wind_speed": current.get("windspeed", 0.0),
            "wind_dir": current.get("winddirection", 0),
            "weather_code": current.get("weathercode", 0),
            "is_day": current.get("is_day", 1) == 1,
            
            # Temperature & Humidity
            "temp_2m": get_hourly("temperature_2m", 0.0),
            "apparent_temp": get_hourly("apparent_temperature", 0.0),
            "dewpoint": get_hourly("dewpoint_2m", 0.0),
            "humidity": get_hourly("relativehumidity_2m", 0.0),
            
            # Precipitation
            "precip_probability": get_hourly("precipitation_probability", 0.0),
            "precipitation": get_hourly("precipitation", 0.0),
            "rain": get_hourly("rain", 0.0),
            "showers": get_hourly("showers", 0.0),
            "snowfall": get_hourly("snowfall", 0.0),
            "snow_depth": get_hourly("snow_depth", 0.0),
            
            # Atmospheric
            "pressure": get_hourly("pressure_msl", 0.0),
            "surface_pressure": get_hourly("surface_pressure", 0.0),
            "cloud_cover": get_hourly("cloudcover", 0.0),
            "cloud_cover_low": get_hourly("cloudcover_low", 0.0),
            "cloud_cover_mid": get_hourly("cloudcover_mid", 0.0),
            "cloud_cover_high": get_hourly("cloudcover_high", 0.0),
            "visibility": get_hourly("visibility", 0.0),
            "vapor_pressure_deficit": get_hourly("vapor_pressure_deficit", 0.0),
            
            # Wind
            "wind_speed_10m": get_hourly("windspeed_10m", 0.0),
            "wind_speed_80m": get_hourly("windspeed_80m", 0.0),
            "wind_speed_120m": get_hourly("windspeed_120m", 0.0),
            "wind_dir_10m": get_hourly("winddirection_10m", 0),
            "wind_gusts": get_hourly("windgusts_10m", 0.0),
            
            # Solar Radiation
            "shortwave_radiation": get_hourly("shortwave_radiation", 0.0),
            "direct_radiation": get_hourly("direct_radiation", 0.0),
            "diffuse_radiation": get_hourly("diffuse_radiation", 0.0),
            "direct_normal_irradiance": get_hourly("direct_normal_irradiance", 0.0),
            "global_tilted_irradiance": get_hourly("global_tilted_irradiance", 0.0),
            "terrestrial_radiation": get_hourly("terrestrial_radiation", 0.0),
            
            # Soil
            "soil_temp_0cm": get_hourly("soil_temperature_0cm", 0.0),
            "soil_temp_6cm": get_hourly("soil_temperature_6cm", 0.0),
            "soil_temp_18cm": get_hourly("soil_temperature_18cm", 0.0),
            "soil_temp_54cm": get_hourly("soil_temperature_54cm", 0.0),
            "soil_moisture_0_1cm": get_hourly("soil_moisture_0_1cm", 0.0),
            "soil_moisture_1_3cm": get_hourly("soil_moisture_1_3cm", 0.0),
            "soil_moisture_3_9cm": get_hourly("soil_moisture_3_9cm", 0.0),
            "soil_moisture_9_27cm": get_hourly("soil_moisture_9_27cm", 0.0),
            "soil_moisture_27_81cm": get_hourly("soil_moisture_27_81cm", 0.0),
            
            # Advanced
            "uv_index": get_hourly("uv_index", 0.0),
            "uv_index_clear_sky": get_hourly("uv_index_clear_sky", 0.0),
            "cape": get_hourly("cape", 0.0),
            "freezing_level": get_hourly("freezinglevel_height", 0.0),
            "et0": get_hourly("et0_fao_evapotranspiration", 0.0),
            "evapotranspiration": get_hourly("evapotranspiration", 0.0),
            "sunshine_duration": get_hourly("sunshine_duration", 0.0),
            
            # Air Quality
            "us_aqi": aqi_current.get("us_aqi", 0),
            "pm10": get_hourly("pm10", 0.0, source=aqi_hourly),
            "pm2_5": get_hourly("pm2_5", 0.0, source=aqi_hourly),
            "carbon_monoxide": get_hourly("carbon_monoxide", 0.0, source=aqi_hourly),
            "nitrogen_dioxide": get_hourly("nitrogen_dioxide", 0.0, source=aqi_hourly),
            "sulphur_dioxide": get_hourly("sulphur_dioxide", 0.0, source=aqi_hourly),
            "ozone": get_hourly("ozone", 0.0, source=aqi_hourly),
            "aerosol_optical_depth": get_hourly("aerosol_optical_depth", 0.0, source=aqi_hourly),
            "dust": get_hourly("dust", 0.0, source=aqi_hourly),
            
            # Daily Data
            "sunrise": get_daily("sunrise"),
            "sunset": get_daily("sunset"),
            "daylight_duration": get_daily("daylight_duration", 0, 0.0),
            "daily_sunshine_duration": get_daily("sunshine_duration", 0, 0.0),
            "daily_precip_sum": get_daily("precipitation_sum", 0, 0.0),
            "daily_rain_sum": get_daily("rain_sum", 0, 0.0),
            "daily_snow_sum": get_daily("snowfall_sum", 0, 0.0),
            "daily_uv_max": get_daily("uv_index_max", 0, 0.0),
            "daily_wind_max": get_daily("windspeed_10m_max", 0, 0.0),
            "daily_wind_gusts_max": get_daily("windgusts_10m_max", 0, 0.0),
            "daily_et0_sum": get_daily("et0_fao_evapotranspiration", 0, 0.0),
            
            # Legacy compatibility
            "soil_moisture": get_hourly("soil_moisture_0_1cm", 0.0),
            "soil_temp": get_hourly("soil_temperature_6cm", 0.0),
        }
    
    async def get_forecast(self, lat: float, lon: float, days: int = 7) -> list:
        """
        Get 7-day forecast with daily high/low temperatures and conditions.
        
        Returns a list of daily forecast dicts.
        """
        if not self.session:
            await self.start()
        
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": (
                "weathercode,temperature_2m_max,temperature_2m_min,"
                "apparent_temperature_max,apparent_temperature_min,"
                "precipitation_sum,rain_sum,snowfall_sum,"
                "precipitation_probability_max,"
                "windspeed_10m_max,windgusts_10m_max,winddirection_10m_dominant,"
                "uv_index_max,sunrise,sunset"
            ),
            "timezone": "auto",
            "forecast_days": days,
            "windspeed_unit": "ms"
        }
        
        try:
            async with self.session.get(self.BASE_URL, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_forecast(data)
                else:
                    print(f"Forecast API Error: {response.status}")
                    return []
        except Exception as e:
            print(f"Forecast API Error: {e}")
            return []
    
    def _parse_forecast(self, data: dict) -> list:
        """Parse forecast response into a list of daily forecasts."""
        daily = data.get("daily", {})
        times = daily.get("time", [])
        
        forecasts = []
        for i, date_str in enumerate(times):
            forecasts.append({
                "date": date_str,
                "weather_code": daily.get("weathercode", [])[i] if i < len(daily.get("weathercode", [])) else 0,
                "temp_max": daily.get("temperature_2m_max", [])[i] if i < len(daily.get("temperature_2m_max", [])) else 0,
                "temp_min": daily.get("temperature_2m_min", [])[i] if i < len(daily.get("temperature_2m_min", [])) else 0,
                "feels_max": daily.get("apparent_temperature_max", [])[i] if i < len(daily.get("apparent_temperature_max", [])) else 0,
                "feels_min": daily.get("apparent_temperature_min", [])[i] if i < len(daily.get("apparent_temperature_min", [])) else 0,
                "precip_sum": daily.get("precipitation_sum", [])[i] if i < len(daily.get("precipitation_sum", [])) else 0,
                "precip_prob": daily.get("precipitation_probability_max", [])[i] if i < len(daily.get("precipitation_probability_max", [])) else 0,
                "rain_sum": daily.get("rain_sum", [])[i] if i < len(daily.get("rain_sum", [])) else 0,
                "snow_sum": daily.get("snowfall_sum", [])[i] if i < len(daily.get("snowfall_sum", [])) else 0,
                "wind_max": daily.get("windspeed_10m_max", [])[i] if i < len(daily.get("windspeed_10m_max", [])) else 0,
                "gust_max": daily.get("windgusts_10m_max", [])[i] if i < len(daily.get("windgusts_10m_max", [])) else 0,
                "wind_dir": daily.get("winddirection_10m_dominant", [])[i] if i < len(daily.get("winddirection_10m_dominant", [])) else 0,
                "uv_max": daily.get("uv_index_max", [])[i] if i < len(daily.get("uv_index_max", [])) else 0,
                "sunrise": daily.get("sunrise", [])[i] if i < len(daily.get("sunrise", [])) else "",
                "sunset": daily.get("sunset", [])[i] if i < len(daily.get("sunset", [])) else "",
            })
        
        return forecasts

# Test script
async def main():
    client = OpenMeteoClient()
    data = await client.get_weather(52.52, 13.41) # Berlin
    print(json.dumps(data, indent=2))
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
