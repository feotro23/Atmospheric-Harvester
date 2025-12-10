from game.mechanics import Mechanics

class MachineType:
    def __init__(self, name, cost_energy=0, cost_biomass=0, description=""):
        self.name = name
        self.cost_energy = cost_energy
        self.cost_biomass = cost_biomass
        self.description = description

class Machine:
    def __init__(self, machine_type, x, y):
        self.type = machine_type
        self.x = x
        self.y = y
        self.active = True
        self.current_rate = 0.0
        
    def update(self, dt, state, weather_data):
        pass

    def to_dict(self):
        return {
            "type": self.type.name,
            "x": self.x,
            "y": self.y,
            "active": self.active
        }

    def on_place(self, state):
        pass

    def on_remove(self, state):
        pass

class WindTurbine(Machine):
    def __init__(self, machine_type, x, y):
        super().__init__(machine_type, x, y)
        import random
        self.animation_offset = random.random() * 100

    def update(self, dt, state, weather_data):
        if not self.active: return
        
        # Generate Energy
        wind_speed = weather_data.get('wind_speed', 0)
        energy_prod = Mechanics.calculate_kinetic_energy(wind_speed, num_turbines=1)
        
        # Scale by dt (Mechanics returns Watts/Instantaneous, we want Joules/Energy over time)
        self.current_rate = energy_prod
        state.resources.add_energy(energy_prod * dt)

class RainCollector(Machine):
    def update(self, dt, state, weather_data):
        if not self.active: return
        
        rain = weather_data.get('rain', 0)
        humidity = weather_data.get('humidity', 0)
        
        water_prod = Mechanics.calculate_hydro_energy(rain, humidity, num_collectors=1)
        self.current_rate = water_prod
        state.resources.add_water(water_prod * dt)

class SolarPanel(Machine):
    def update(self, dt, state, weather_data):
        if not self.active: return
        
        temp = weather_data.get('temp', 20)
        clouds = weather_data.get('cloud_cover', 0)
        is_day = weather_data.get('is_day', True)
        rad = weather_data.get('shortwave_radiation', 0)
        
        energy_prod = Mechanics.calculate_solar_energy(temp, clouds, is_day, num_panels=1, radiation=rad)
        self.current_rate = energy_prod
        state.resources.add_energy(energy_prod * dt)

class Heater(Machine):
    def update(self, dt, state, weather_data):
        if not self.active: return
        
        # Consumes Energy to heat area (Logic to be added to farming/world later)
        consumption = 10.0 * dt # 10 Watts
        if state.resources.consume_energy(consumption):
            # Effect: Raise local temp (placeholder)
            pass
        else:
            self.active = False # Turn off if no power

class Battery(Machine):
    def on_place(self, state):
        state.resources.modify_capacity("energy", 500)

    def on_remove(self, state):
        state.resources.modify_capacity("energy", -500)

class WaterTank(Machine):
    def on_place(self, state):
        state.resources.modify_capacity("water", 250)

    def on_remove(self, state):
        state.resources.modify_capacity("water", -250)

class Sprinkler(Machine):
    def update(self, dt, state, weather_data):
        if not self.active: return
        
        # Consumes Water to irrigate
        consumption = 1.0 * dt # 1 Liter per second
        if state.resources.consume_water(consumption):
            # Effect is applied in Game.update (checking distance to crops)
            pass
        else:
            # No water, inactive for this frame (but don't set self.active=False permanently, just fail to irrigate)
            # Actually, we need a way to signal it's working.
            # Let's just consume. If fail, it doesn't work.
            # Let's just consume. If fail, it doesn't work.
            pass

class CreatureStable(Machine):
    def on_place(self, state):
        pass # Maybe increase max creature capacity later?

# Definitions
TURBINE_TYPE = MachineType("Wind Turbine", cost_energy=50, cost_biomass=10, description="Generates energy from wind.")
COLLECTOR_TYPE = MachineType("Rain Collector", cost_energy=20, cost_biomass=5, description="Collects water from rain/humidity.")
PANEL_TYPE = MachineType("Solar Panel", cost_energy=100, cost_biomass=20, description="Generates energy from sun.")
HEATER_TYPE = MachineType("Heater", cost_energy=50, cost_biomass=0, description="Consumes energy to warm crops.")
BATTERY_TYPE = MachineType("Battery", cost_energy=100, cost_biomass=10, description="Stores 500 Energy.")
TANK_TYPE = MachineType("Water Tank", cost_energy=50, cost_biomass=20, description="Stores 250 Water.")
SPRINKLER_TYPE = MachineType("Sprinkler", cost_energy=10, cost_biomass=5, description="Irrigates nearby crops.")
STABLE_TYPE = MachineType("Creature Stable", cost_energy=75, cost_biomass=40, description="Allows capturing creatures.")

def create_machine(name, x, y):
    if name == "Wind Turbine": return WindTurbine(TURBINE_TYPE, x, y)
    if name == "Rain Collector": return RainCollector(COLLECTOR_TYPE, x, y)
    if name == "Solar Panel": return SolarPanel(PANEL_TYPE, x, y)
    if name == "Heater": return Heater(HEATER_TYPE, x, y)
    if name == "Battery": return Battery(BATTERY_TYPE, x, y)
    if name == "Water Tank": return WaterTank(TANK_TYPE, x, y)
    if name == "Sprinkler": return Sprinkler(SPRINKLER_TYPE, x, y)
    if name == "Creature Stable": return CreatureStable(STABLE_TYPE, x, y)
    return None
