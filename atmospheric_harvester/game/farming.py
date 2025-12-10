class CropType:
    def __init__(self, name, description, icon_name, base_gdd, optimal_temp_min, optimal_temp_max, chill_hours_req=0, water_need=0.2, yield_amount=1, yield_resource="biomass", wind_tolerance=50.0, base_value=1):
        self.name = name
        self.description = description
        self.icon_name = icon_name
        self.base_gdd = base_gdd # Total GDD needed to harvest
        self.optimal_temp_min = optimal_temp_min
        self.optimal_temp_max = optimal_temp_max
        self.chill_hours_req = chill_hours_req # Hours < 5C needed
        self.water_need = water_need # Minimum soil moisture required
        self.yield_amount = yield_amount
        self.yield_resource = yield_resource # "biomass" or specific item name if inventory exists
        self.wind_tolerance = wind_tolerance # Max wind speed (km/h) before damage
        self.base_value = base_value # Credit value per unit

class Crop:
    def __init__(self, type: CropType, x=0, y=0):
        self.type = type
        self.x = x
        self.y = y
        self.stage = 0 # 0 to 3 (Mature)
        self.progress = 0.0 # 0 to 100 per stage
        self.health = 100.0
        self.accumulated_heat = 0.0 # ATU
        self.chill_hours_accumulated = 0.0
        self.water_stress = 0.0

    @property
    def gdd_accumulated(self):
        return self.accumulated_heat

    @property
    def state(self):
        if self.health <= 0: return "Dead"
        if self.stage >= 3: return "Ready"
        if self.type.chill_hours_req > 0 and self.chill_hours_accumulated < self.type.chill_hours_req:
            return "Dormant"
        return "Growing"
        
    def update(self, dt, temp, soil_moisture, et0=0.0, uv_index=0.0, snow_depth=0.0, wind_speed=0.0):
        # Weather Data passed directly
        
        # 0. Chill Hours (Vernalization)
        if self.type.chill_hours_req > 0 and self.chill_hours_accumulated < self.type.chill_hours_req:
            if temp < 5.0:
                self.chill_hours_accumulated += dt / 3600.0 
            return # Don't grow if dormant
            
        # 1. Snow Cover Dormancy
        if snow_depth > 0.1:
            if "Winter" in self.type.name or "Potato" in self.type.name:
                return # Dormant but safe
            else:
                self.health -= 0.1 * dt
                return

        # 2. Thermal Growth (ATU)
        if temp >= self.type.optimal_temp_min and temp <= self.type.optimal_temp_max:
            growth_rate = (temp - self.type.optimal_temp_min) * dt
            # Bonus for perfect temp (middle of range)
            mid_temp = (self.type.optimal_temp_min + self.type.optimal_temp_max) / 2
            if abs(temp - mid_temp) < 5:
                growth_rate *= 1.2
            self.accumulated_heat += growth_rate
        
        # Frost Damage (New)
        if temp < 0:
            if "Winter" not in self.type.name and "Potato" not in self.type.name:
                # Severe damage for non-hardy crops
                self.health -= 5.0 * dt 
            
        # 3. UV Damage
        if uv_index > 8.0 and "Cactus" not in self.type.name:
            self.health -= 0.05 * dt * (uv_index - 8.0)
            
        # 4. Water Stress
        # Too little water
        if soil_moisture < self.type.water_need:
             self.water_stress += dt
             self.health -= 0.1 * dt
        # Too much water (Drowning) - except Rice
        elif soil_moisture > 0.9 and "Rice" not in self.type.name:
             self.health -= 0.05 * dt
        else:
             self.water_stress = max(0, self.water_stress - dt)
             # Heal slowly if conditions good
             if self.health < 100:
                 self.health += 0.05 * dt
                 
        # 5. Wind Damage (New)
        if wind_speed > self.type.wind_tolerance:
            damage_factor = (wind_speed - self.type.wind_tolerance) * 0.1
            self.health -= damage_factor * dt
             
        # Progress based on heat
        if self.accumulated_heat >= self.type.base_gdd:
             self.stage = 3 # Mature
        elif self.accumulated_heat >= self.type.base_gdd * 0.66:
             self.stage = 2
        elif self.accumulated_heat >= self.type.base_gdd * 0.33:
             self.stage = 1

# Definitions
WHEAT = CropType(
    name="Winter Wheat", 
    description="Hardy grain that survives cold winters.",
    icon_name="wheat",
    base_gdd=100, 
    optimal_temp_min=15, 
    optimal_temp_max=25, 
    chill_hours_req=10, 
    water_need=0.3,
    yield_amount=5,
    yield_resource="wheat",
    wind_tolerance=60.0,
    base_value=2
)

CORN = CropType(
    name="Corn", 
    description="High-yield crop needing warmth and water.",
    icon_name="corn",
    base_gdd=150, 
    optimal_temp_min=20, 
    optimal_temp_max=30, 
    chill_hours_req=0, 
    water_need=0.5,
    yield_amount=8,
    yield_resource="corn",
    wind_tolerance=40.0, # Vulnerable to wind
    base_value=3
)

POTATO = CropType(
    name="Potato", 
    description="Resilient tuber, grows in poor conditions.",
    icon_name="potato",
    base_gdd=120, 
    optimal_temp_min=10, 
    optimal_temp_max=25, 
    chill_hours_req=0, 
    water_need=0.2,
    yield_amount=6,
    yield_resource="potato",
    wind_tolerance=80.0, # Underground, very safe
    base_value=2
)

RICE = CropType(
    name="Rice", 
    description="Thrives in very wet soil.",
    icon_name="rice",
    base_gdd=180, 
    optimal_temp_min=22, 
    optimal_temp_max=35, 
    chill_hours_req=0, 
    water_need=0.7,
    yield_amount=10,
    yield_resource="rice",
    wind_tolerance=50.0,
    base_value=4
)

CACTUS = CropType(
    name="Cactus", 
    description="Desert plant, needs very little water.",
    icon_name="cactus",
    base_gdd=200, 
    optimal_temp_min=25, 
    optimal_temp_max=45, 
    chill_hours_req=0, 
    water_need=0.0,
    yield_amount=3,
    yield_resource="cactus_fruit",
    wind_tolerance=100.0, # Very tough
    base_value=5
)

SUNFLOWER = CropType(
    name="Sunflower", 
    description="Oil-rich flower that loves the sun.",
    icon_name="sunflower",
    base_gdd=140, 
    optimal_temp_min=18, 
    optimal_temp_max=32, 
    chill_hours_req=0, 
    water_need=0.4,
    yield_amount=4,
    yield_resource="sunflower_seeds",
    wind_tolerance=35.0, # Very vulnerable to wind
    base_value=6
)

ALL_CROPS = [WHEAT, CORN, POTATO, RICE, CACTUS, SUNFLOWER]
