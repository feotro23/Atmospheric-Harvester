from game.resources import ResourceManager
from game.farming import Crop, ALL_CROPS

class GameState:
    def __init__(self):
        # Resources
        self.resources = ResourceManager()
        
        # Machines
        self.machines = []
        
        # Location
        self.lat = 40.7128
        self.lon = -74.0060
        self.location_name = "New York"
        
        # Weather Data (Raw)
        self.weather_data = {
            "temp": 20.0,
            "wind_speed": 5.0,
            "wind_dir": 0,
            "weather_code": 0,
            "is_day": True,
            "rain": 0.0,
            "humidity": 50.0,
            "cloud_cover": 0.0,
            "shortwave_radiation": 0.0
        }
        
        self.alerts = [] # List of alert dicts
        
        # Derived Weather Stats
        self.wind_speed = 0.0
        self.temp_c = 0.0
        self.humidity = 0.0
        self.clouds = 0.0
        self.is_day = True
        self.rain_vol = 0.0
        
        # Generation Rates (per second)
        self.gen_kinetic = 0.0
        self.gen_solar = 0.0
        self.gen_hydro = 0.0
        
        # Farming
        self.crops = []
        self.inventory = {} # Item name -> count
        self.seeds = {
            "Winter Wheat": 5,
            "Corn": 5,
            "Potato": 5,
            "Rice": 5,
            "Cactus": 5,
            "Sunflower": 5
        } # Crop name -> count
        self.selected_seed_index = 0
        
        # Creatures
        self.collected_creatures = []
        self.active_spawns = [] # Creatures currently visible but not caught
        
        # Upgrades
        self.upgrades = {} # uid -> level
        
        # History
        self.energy_history = [] # List of (timestamp, energy_rate)
        self.history_timer = 0.0
        
        # World
        self.world_map = []
        
        # Advanced Weather Metrics
        self.solar_radiation = 0.0 # Shortwave (GHI)
        self.direct_radiation = 0.0
        self.diffuse_radiation = 0.0
        
        self.cloud_cover_low = 0.0
        self.cloud_cover_mid = 0.0
        self.cloud_cover_high = 0.0
        
        self.visibility = 0.0
        self.cape = 0.0 # Storm potential
        self.et0 = 0.0 # Evapotranspiration
        self.snow_depth = 0.0
        self.uv_index = 0.0
        
        self.aqi = 0 # US AQI
        self.pm2_5 = 0.0
        self.ozone = 0.0
        
        self.sunrise = ""
        self.sunset = ""
        

        
    def update_weather(self, data):
        if not data:
            return
            
        self.weather_data = data
        
        # Core Data
        self.temp_c = data.get("temp", 0.0)
        self.wind_speed = data.get("wind_speed", 0.0)
        self.wind_dir = data.get("wind_dir", 0)
        self.weather_code = data.get("weather_code", 0)
        self.is_day = data.get("is_day", True)
        
        self.soil_moisture = data.get("soil_moisture", 0.0)
        self.soil_temp = data.get("soil_temp", 0.0)
        
        self.sunrise = data.get("sunrise", "")
        self.sunset = data.get("sunset", "")
        
        # Advanced Metrics
        self.solar_radiation = data.get("solar_radiation", 0.0)
        self.direct_radiation = data.get("direct_radiation", 0.0)
        self.diffuse_radiation = data.get("diffuse_radiation", 0.0)
        
        self.cloud_cover_low = data.get("cloud_cover_low", 0.0)
        self.cloud_cover_mid = data.get("cloud_cover_mid", 0.0)
        self.cloud_cover_high = data.get("cloud_cover_high", 0.0)
        
        self.visibility = data.get("visibility", 0.0)
        self.cape = data.get("cape", 0.0)
        self.et0 = data.get("et0", 0.0)
        self.snow_depth = data.get("snow_depth", 0.0)
        self.uv_index = data.get("uv_index", 0.0)
        
        self.aqi = data.get("aqi", 0)
        self.pm2_5 = data.get("pm2_5", 0.0)
        self.ozone = data.get("ozone", 0.0)
        
        # Derived
        self.humidity = data.get("humidity", 0.0)
        self.clouds = data.get("cloud_cover", data.get("clouds", 0.0))  # API uses cloud_cover
        self.rain_vol = data.get("rain", 0.0)

    def to_dict(self):
        return {
            "resources": {
                "energy": self.resources.energy,
                "water": self.resources.water,
                "biomass": self.resources.biomass,
                "credits": self.resources.credits,
                "energy_capacity": self.resources.energy_capacity,
                "water_capacity": self.resources.water_capacity,
                "biomass_capacity": self.resources.biomass_capacity,
                "total_energy": self.resources.total_energy_generated,
                "total_water": self.resources.total_water_generated,
                "total_biomass": self.resources.total_biomass_generated,
                "total_credits": self.resources.total_credits_earned
            },
            "machines": [m.to_dict() for m in self.machines],
            "crops": [
                {
                    "type": c.type.name,
                    "x": c.x,
                    "y": c.y,
                    "health": c.health,
                    "stage": c.stage,
                    "water_stress": c.water_stress,
                    "accumulated_heat": c.accumulated_heat,
                    "chill_hours": c.chill_hours_accumulated
                }
                for c in self.crops
            ],
            "inventory": self.inventory,
            "seeds": self.seeds,
            "upgrades": self.upgrades,
            "location": {
                "lat": self.lat,
                "lon": self.lon,
                "name": self.location_name
            },
            "stats": {
                "rainy_locs": getattr(self, '_rainy_locations_visited', 0),
                "snowy_locs": getattr(self, '_snowy_locations_visited', 0),
                "biomass_composted": getattr(self, '_biomass_composted', 0),
                "locs_visited": getattr(self, '_locations_visited', 0)
            },
            "creatures": {
                "collected": [c.to_dict() for c in self.collected_creatures],
                "active": [c.to_dict() for c in self.active_spawns]
            }
        }

    def from_dict(self, data):
        # Resources
        res_data = data.get("resources", {})
        self.resources.energy = res_data.get("energy", 100.0)
        self.resources.water = res_data.get("water", 50.0)
        self.resources.biomass = res_data.get("biomass", 10.0)
        self.resources.credits = res_data.get("credits", 0)
        self.resources.energy_capacity = res_data.get("energy_capacity", 1000.0)
        self.resources.water_capacity = res_data.get("water_capacity", 500.0)
        self.resources.biomass_capacity = res_data.get("biomass_capacity", 100.0)
        self.resources.total_energy_generated = res_data.get("total_energy", 0.0)
        self.resources.total_water_generated = res_data.get("total_water", 0.0)
        self.resources.total_biomass_generated = res_data.get("total_biomass", 0.0)
        self.resources.total_credits_earned = res_data.get("total_credits", 0)
        
        # Machines
        # Machines
        self.machines = []
        from game.machines import create_machine
        for m_data in data.get("machines", []):
            m = create_machine(m_data["type"], m_data["x"], m_data["y"])
            if m:
                m.active = m_data.get("active", True)
                self.machines.append(m)
        
        # Crops
        self.crops = []
        crop_map = {c.name: c for c in ALL_CROPS}
        for c_data in data.get("crops", []):
            c_type_name = c_data.get("type")
            if c_type_name in crop_map:
                crop = Crop(crop_map[c_type_name], c_data.get("x", 0), c_data.get("y", 0))
                crop.health = c_data.get("health", 100.0)
                crop.stage = c_data.get("stage", 0)
                crop.water_stress = c_data.get("water_stress", 0.0)
                crop.accumulated_heat = c_data.get("accumulated_heat", 0.0)
                crop.chill_hours_accumulated = c_data.get("chill_hours", 0.0)
                self.crops.append(crop)
                
        # Inventory & Seeds
        self.inventory = data.get("inventory", {})
        self.seeds = data.get("seeds", self.seeds)
        self.upgrades = data.get("upgrades", {})
        
        # Location
        loc_data = data.get("location", {})
        self.lat = loc_data.get("lat", 40.7128)
        self.lon = loc_data.get("lon", -74.0060)
        self.location_name = loc_data.get("name", "New York")
        
        # Stats
        stats = data.get("stats", {})
        self._rainy_locations_visited = stats.get("rainy_locs", 0)
        self._snowy_locations_visited = stats.get("snowy_locs", 0)
        self._biomass_composted = stats.get("biomass_composted", 0)
        self._locations_visited = stats.get("locs_visited", 0)
        
        # Creatures
        creatures_data = data.get("creatures", {})
        self.collected_creatures = []
        # Import here to avoid circular dependency if possible, or assume already imported
        from game.creatures import Creature, ALL_CREATURES
        # Helper to find creature type by name
        def get_creature_type(name):
             return next((c for c in ALL_CREATURES if c.name == name), None)

        for c_data in creatures_data.get("collected", []):
            c_type = get_creature_type(c_data.get("name"))
            if c_type:
                # Reconstruct wrapper if needed, or just store type? 
                # collected_creatures usually stores Creature objects or instances?
                # Looking at state.py init: self.collected_creatures = []
                # Assuming complete objects
                inst = Creature(c_type)
                # Restore other props if any
                self.collected_creatures.append(inst)
                
        self.active_spawns = []
        for c_data in creatures_data.get("active", []):
            c_type = get_creature_type(c_data.get("name"))
            if c_type:
                inst = Creature(c_type)
                inst.x = c_data.get("x", 0)
                inst.y = c_data.get("y", 0)
                inst.timer = c_data.get("timer", 0)
                self.active_spawns.append(inst)

