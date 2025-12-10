"""
GFS (Global Forecast System) GRIB2 Client

Fetches supplemental weather data directly from NOAA's GFS model via NOMADS.
Uses cfgrib/xarray to parse GRIB2 binary data.

Data includes variables not available through NWS/Open-Meteo APIs:
- CAPE/CIN (storm prediction)
- Soil moisture and temperature
- Visibility
- Snow depth
- Gust speed
"""

import asyncio
import aiohttp
import io
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, Dict, Tuple
import tempfile


class GFSClient:
    """
    Async client for fetching GFS GRIB2 data from NOMADS.
    
    Uses the GRIB Filter to request small subsets of data for specific
    variables, levels, and geographic regions.
    """
    
    NOMADS_BASE = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl"
    
    # GFS cycles run at 00, 06, 12, 18 UTC
    # Data is typically available ~4 hours after cycle time
    CYCLE_DELAY_HOURS = 4
    
    # Variables to fetch (name: (GRIB var name, level))
    VARIABLES = {
        "CAPE": ("CAPE", "surface"),
        "CIN": ("CIN", "surface"),
        "SOILW": ("SOILW", "0-0.1_m_below_ground"),
        "TSOIL": ("TSOIL", "0-0.1_m_below_ground"),
        "VIS": ("VIS", "surface"),
        "SNOD": ("SNOD", "surface"),
        "GUST": ("GUST", "surface"),
        "PRATE": ("PRATE", "surface"),
    }
    
    def __init__(self, cache_dir: Optional[str] = None):
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Default cache directory
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            # Use temp directory for cache
            self.cache_dir = Path(tempfile.gettempdir()) / "gfs_cache"
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._cache_metadata: Dict[str, dict] = {}
        self._load_cache_metadata()
    
    async def start(self):
        """Initialize the HTTP session."""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    def _load_cache_metadata(self):
        """Load cache metadata from disk."""
        metadata_file = self.cache_dir / "metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, "r") as f:
                    self._cache_metadata = json.load(f)
            except Exception as e:
                print(f"GFS: Failed to load cache metadata: {e}")
                self._cache_metadata = {}
    
    def _save_cache_metadata(self):
        """Save cache metadata to disk."""
        metadata_file = self.cache_dir / "metadata.json"
        try:
            with open(metadata_file, "w") as f:
                json.dump(self._cache_metadata, f)
        except Exception as e:
            print(f"GFS: Failed to save cache metadata: {e}")
    
    def _get_latest_cycle(self) -> Tuple[str, str, int]:
        """
        Calculate the latest available GFS cycle.
        
        GFS runs at 00, 06, 12, 18 UTC with ~4 hour processing delay.
        
        Returns:
            (date_str, cycle_str, forecast_hour)
            e.g., ("20251208", "00", 6)
        """
        now = datetime.now(timezone.utc)
        
        # Subtract delay to account for processing time
        available_time = now - timedelta(hours=self.CYCLE_DELAY_HOURS)
        
        # Find the most recent cycle (00, 06, 12, 18)
        cycle_hour = (available_time.hour // 6) * 6
        cycle_time = available_time.replace(
            hour=cycle_hour, minute=0, second=0, microsecond=0
        )
        
        # Calculate forecast hour (difference between now and cycle time)
        forecast_delta = now - cycle_time
        forecast_hour = int(forecast_delta.total_seconds() // 3600)
        
        # Clamp to valid range (f000-f120 for hourly data)
        forecast_hour = max(0, min(120, forecast_hour))
        
        date_str = cycle_time.strftime("%Y%m%d")
        cycle_str = f"{cycle_hour:02d}"
        
        return date_str, cycle_str, forecast_hour
    
    def _build_filter_url(
        self, 
        lat: float, 
        lon: float, 
        date_str: str, 
        cycle_str: str, 
        forecast_hour: int
    ) -> str:
        """
        Build a GRIB Filter URL to download a subset of GFS data.
        
        The filter allows requesting specific variables, levels, and
        geographic bounding boxes to minimize download size.
        """
        # Build variable and level flags
        var_flags = []
        level_flags = set()
        
        for var_name, (grib_var, level) in self.VARIABLES.items():
            var_flags.append(f"var_{grib_var}=on")
            level_flags.add(f"lev_{level}=on")
        
        # Geographic bounding box (1 degree around the point)
        # Handle longitude wrapping
        left_lon = lon - 1
        right_lon = lon + 1
        if left_lon < -180:
            left_lon += 360
        if right_lon > 180:
            right_lon -= 360
        
        bottom_lat = max(-90, lat - 1)
        top_lat = min(90, lat + 1)
        
        # Build URL
        params = [
            f"file=gfs.t{cycle_str}z.pgrb2.0p25.f{forecast_hour:03d}",
            *var_flags,
            *level_flags,
            "subregion=",
            f"leftlon={left_lon:.2f}",
            f"rightlon={right_lon:.2f}",
            f"toplat={top_lat:.2f}",
            f"bottomlat={bottom_lat:.2f}",
            f"dir=%2Fgfs.{date_str}%2F{cycle_str}%2Fatmos"
        ]
        
        return f"{self.NOMADS_BASE}?{'&'.join(params)}"
    
    def _get_cache_key(self, lat: float, lon: float, date_str: str, cycle_str: str) -> str:
        """Generate a cache key for the given location and cycle."""
        return f"{date_str}_{cycle_str}_{lat:.1f}_{lon:.1f}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid (within same GFS cycle)."""
        if cache_key not in self._cache_metadata:
            return False
        
        cached_time = self._cache_metadata[cache_key].get("timestamp")
        if not cached_time:
            return False
        
        # Cache is valid for 6 hours (one GFS cycle)
        cached_dt = datetime.fromisoformat(cached_time)
        now = datetime.now(timezone.utc)
        
        return (now - cached_dt).total_seconds() < 6 * 3600
    
    def _get_cached_data(self, cache_key: str) -> Optional[dict]:
        """Load cached data from disk."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"GFS: Failed to load cache: {e}")
        return None
    
    def _save_to_cache(self, cache_key: str, data: dict):
        """Save data to cache."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, "w") as f:
                json.dump(data, f)
            
            self._cache_metadata[cache_key] = {
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            self._save_cache_metadata()
        except Exception as e:
            print(f"GFS: Failed to save cache: {e}")
    
    async def fetch_grib(self, url: str) -> Optional[bytes]:
        """Download GRIB2 data from NOMADS."""
        if not self.session:
            await self.start()
        
        try:
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    content_type = response.headers.get("content-type", "")
                    if "octet-stream" in content_type or "grib" in content_type:
                        return await response.read()
                    else:
                        # Might be an error page
                        text = await response.text()
                        if "ERROR" in text.upper() or "NOT FOUND" in text.upper():
                            print(f"GFS: Server error: {text[:200]}")
                            return None
                        return await response.read()
                else:
                    print(f"GFS: HTTP error {response.status}")
                    return None
        except asyncio.TimeoutError:
            print("GFS: Request timeout")
            return None
        except Exception as e:
            print(f"GFS: Network error: {e}")
            return None
    
    def parse_grib(self, grib_bytes: bytes, lat: float, lon: float) -> Optional[dict]:
        """
        Parse GRIB2 data using cfgrib and extract values at the given point.
        
        Returns a dict with game-ready variable values.
        """
        try:
            import xarray as xr
            import cfgrib
            
            # Write bytes to temp file (cfgrib needs a file path)
            with tempfile.NamedTemporaryFile(suffix=".grib2", delete=False) as f:
                f.write(grib_bytes)
                temp_path = f.name
            
            try:
                # Open with xarray/cfgrib
                # cfgrib may create multiple datasets for different level types
                datasets = cfgrib.open_datasets(temp_path)
                
                result = {}
                
                for ds in datasets:
                    # Find the grid point closest to our location
                    # GFS uses 0-360 longitude, convert if needed
                    query_lon = lon if lon >= 0 else lon + 360
                    
                    # Select nearest point
                    try:
                        point = ds.sel(
                            latitude=lat, 
                            longitude=query_lon, 
                            method="nearest"
                        )
                    except KeyError:
                        # Try alternate coordinate names
                        try:
                            point = ds.sel(
                                lat=lat,
                                lon=query_lon,
                                method="nearest"
                            )
                        except KeyError:
                            continue
                    
                    # Extract variables
                    for var_name in point.data_vars:
                        try:
                            value = float(point[var_name].values)
                            result[var_name.lower()] = value
                        except (ValueError, TypeError):
                            pass
                    
                    ds.close()
                
                return result if result else None
                
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_path)
                except:
                    pass
                    
        except ImportError as e:
            print(f"GFS: Missing dependency: {e}")
            return None
        except Exception as e:
            print(f"GFS: Parse error: {e}")
            return None
    
    def _to_game_format(self, raw_data: dict) -> dict:
        """
        Convert raw GFS variable names to game format.
        
        Also performs unit conversions where needed.
        """
        # Map GFS variable names to game field names
        mapping = {
            "cape": "gfs_cape",      # J/kg
            "cin": "gfs_cin",        # J/kg
            "soilw": "gfs_soil_moisture",  # fraction 0-1
            "tsoil": "gfs_soil_temp",      # K -> C
            "vis": "gfs_visibility",       # m
            "snod": "gfs_snow_depth",      # m
            "gust": "gfs_gust",            # m/s
            "prate": "gfs_precip_rate",    # kg/m²/s
        }
        
        result = {}
        
        for gfs_key, game_key in mapping.items():
            if gfs_key in raw_data:
                value = raw_data[gfs_key]
                
                # Unit conversions
                if gfs_key == "tsoil":
                    # Kelvin to Celsius
                    value = value - 273.15
                elif gfs_key == "prate":
                    # kg/m²/s to mm/hr
                    value = value * 3600
                
                result[game_key] = value
        
        return result
    
    async def get_supplemental_data(self, lat: float, lon: float) -> Optional[dict]:
        """
        Main entry point: fetch GFS supplemental data for a location.
        
        Uses caching to avoid repeated downloads within the same GFS cycle.
        
        Returns:
            Dict with game-ready weather variables, or None if unavailable.
        """
        # Calculate current cycle
        date_str, cycle_str, forecast_hour = self._get_latest_cycle()
        cache_key = self._get_cache_key(lat, lon, date_str, cycle_str)
        
        # Check cache
        if self._is_cache_valid(cache_key):
            cached = self._get_cached_data(cache_key)
            if cached:
                print(f"GFS: Using cached data ({cache_key})")
                return cached
        
        # Build URL and fetch
        url = self._build_filter_url(lat, lon, date_str, cycle_str, forecast_hour)
        print(f"GFS: Fetching {date_str}/{cycle_str} f{forecast_hour:03d} for ({lat:.2f}, {lon:.2f})")
        
        grib_bytes = await self.fetch_grib(url)
        if not grib_bytes:
            # Try previous cycle as fallback
            prev_cycle_hour = (int(cycle_str) - 6) % 24
            if prev_cycle_hour > int(cycle_str):
                # Rolled back to previous day
                prev_date = (datetime.strptime(date_str, "%Y%m%d") - timedelta(days=1))
                date_str = prev_date.strftime("%Y%m%d")
            cycle_str = f"{prev_cycle_hour:02d}"
            
            url = self._build_filter_url(lat, lon, date_str, cycle_str, forecast_hour + 6)
            print(f"GFS: Trying fallback cycle {date_str}/{cycle_str}")
            grib_bytes = await self.fetch_grib(url)
        
        if not grib_bytes:
            print("GFS: No data available")
            return None
        
        print(f"GFS: Downloaded {len(grib_bytes)} bytes")
        
        # Parse GRIB
        raw_data = self.parse_grib(grib_bytes, lat, lon)
        if not raw_data:
            return None
        
        # Convert to game format
        game_data = self._to_game_format(raw_data)
        
        # Cache the result
        self._save_to_cache(cache_key, game_data)
        
        print(f"GFS: Parsed {len(game_data)} variables")
        return game_data


# Test script
async def main():
    client = GFSClient()
    await client.start()
    
    # Test with South Saint Paul, MN
    print("=" * 60)
    print("Testing GFS GRIB2 Client for South Saint Paul, MN")
    print("=" * 60)
    
    data = await client.get_supplemental_data(44.89, -93.02)
    
    if data:
        print("\nParsed GFS Data:")
        for key, value in sorted(data.items()):
            print(f"  {key}: {value:.4f}")
    else:
        print("Failed to get GFS data")
    
    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
