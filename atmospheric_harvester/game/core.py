from .state import GameState
from .mechanics import Mechanics
from .farming import Crop, ALL_CROPS
from .creatures import Bestiary, Creature
from .travel import TravelManager
from .upgrades import UpgradeManager
from .settings import SettingsManager
from .machines import create_machine
from .missions import MissionManager
from .achievements import AchievementManager
from .weather_events import WeatherEventManager

class Game:
    def __init__(self):
        self.state = GameState()
        self.mechanics = Mechanics()
        self.bestiary = Bestiary()
        self.travel_manager = TravelManager()
        self.upgrade_manager = UpgradeManager()
        self.settings_manager = SettingsManager()
        self.mission_manager = MissionManager()
        self.achievement_manager = AchievementManager()
        self.event_manager = WeatherEventManager()
        self.build_selection = None
        
        # Mission & Achievement tracking flags
        self.state._crops_harvested = 0
        self.state._locations_visited = 1  # Start at 1 (starting location)
        self.state._weather_overlay_opened = False
        self.state._rainy_locations_visited = 0
        self.state._snowy_locations_visited = 0
        
        self.plant_selection = None # (crop_name, crop_data)
        self.edit_mode = False
        self.moving_object = None # (obj, original_x, original_y)

    def update(self, dt):
        # Reset Generation Rates
        self.state.gen_kinetic = 0.0
        self.state.gen_solar = 0.0
        self.state.gen_hydro = 0.0
        
        # Update weather events
        self.event_manager.update(self.state, dt)
        
        # Update Missions
        self.mission_manager.update(self.state)
        
        # Update Achievements
        self.achievement_manager.update(self.state)
        
        # Get event modifiers
        event_modifiers = self.event_manager.get_active_modifiers()
        
        # Update Machines
        if self.state.weather_data:
            # Prepare weather data
            w_data = self.state.weather_data.copy()
            w_data['rain'] = self.state.rain_vol
            
            for machine in self.state.machines:
                machine.update(dt, self.state, w_data)
                
                # Apply event modifiers to generation
                base_rate = machine.current_rate
                modifier = 1.0
                
                if machine.type.name == "Wind Turbine":
                    modifier = event_modifiers.get("wind", 1.0)
                    upgrade_mult = self.upgrade_manager.get_multiplier(self.state, "turbine_eff")
                    
                    # Apply upgrade to base rate first (permanent boost)
                    # Then apply event modifier
                    # Note: machine.current_rate is what the machine produced this frame (raw)
                    # We should probably scale the output added to resources, but machine.update adds directly?
                    # Wait, machine.update adds to resources directly.
                    # We need to check machine.update implementations.
                    pass
                    
                elif machine.type.name == "Solar Panel":
                    modifier = event_modifiers.get("solar", 1.0)
                    upgrade_mult = self.upgrade_manager.get_multiplier(self.state, "solar_eff")
                    pass
                    
                elif machine.type.name == "Rain Collector":
                    modifier = event_modifiers.get("hydro", 1.0)
                    upgrade_mult = self.upgrade_manager.get_multiplier(self.state, "hydro_eff")
                    pass
                
                # Calculate total multiplier
                total_mult = modifier * upgrade_mult
                
                # Apply Creature Bonuses
                for creature in self.state.collected_creatures:
                    if not hasattr(creature.type, 'bonus_type'): continue # Safety
                    
                    b_type = creature.type.bonus_type
                    if b_type == "water_eff" and machine.type.name == "Rain Collector":
                        total_mult += 0.10
                    elif b_type == "wind_eff" and machine.type.name == "Wind Turbine":
                        total_mult += 0.10
                    elif b_type == "solar_eff" and machine.type.name == "Solar Panel":
                        # Only at night (Moonlight) per description? Or just flat?
                        # Description says "Moonlight", let's check not is_day
                        if not self.state.is_day:
                            total_mult += 0.10
                
                # Update generation stats (visual only)
                if machine.type.name == "Wind Turbine":
                    self.state.gen_kinetic += base_rate * total_mult
                elif machine.type.name == "Solar Panel":
                    self.state.gen_solar += base_rate * total_mult
                elif machine.type.name == "Rain Collector":
                    self.state.gen_hydro += base_rate * total_mult
                
                # Apply additional resources from multipliers (Upgrades + Events + Creatures)
                # machine.update() already added base_rate * dt
                # We need to add: base_rate * (total_mult - 1.0) * dt
                
                if total_mult != 1.0:
                    additional = base_rate * (total_mult - 1.0) * dt
                    
                    if machine.type.name == "Wind Turbine" or machine.type.name == "Solar Panel":
                        if additional > 0:
                            self.state.resources.add_energy(additional)
                        else:
                            # If multiplier < 1 (e.g. bad event), we consume the excess that was added
                            self.state.resources.consume_energy(-additional)
                            
                    elif machine.type.name == "Rain Collector":
                        if additional > 0:
                            self.state.resources.add_water(additional)
                        else:
                            self.state.resources.consume_water(-additional)

        # Passive Bonuses (e.g. Golem)
        passive_energy = 0.0
        for c in self.state.collected_creatures:
             if hasattr(c.type, 'bonus_type') and c.type.bonus_type == "passive_energy":
                 passive_energy += 1.0
        
        if passive_energy > 0:
            self.state.resources.add_energy(passive_energy * dt)
            # Add to a gen stat?
            # self.state.gen_kinetic += passive_energy (Maybe confusing?)
            # Let's leave it as hidden passive or add a new stat later if needed.

        # Total generation per second (for history)
        total_gen = self.state.gen_kinetic + self.state.gen_solar + self.state.gen_hydro
        
        # History Tracking
        self.state.history_timer += dt
        if self.state.history_timer >= 0.5:
            self.state.history_timer = 0
            self.state.energy_history.append(total_gen)
            if len(self.state.energy_history) > 100: # Keep last 50 seconds
                self.state.energy_history.pop(0)
        active_sprinklers = []
        active_heaters = []
        for m in self.state.machines:
            if m.active:
                if m.type.name == "Sprinkler":
                    active_sprinklers.append((m.x, m.y))
                elif m.type.name == "Heater":
                    active_heaters.append((m.x, m.y))

        base_moisture = self.state.humidity / 100.0
        base_temp = self.state.temp_c

        for crop in self.state.crops:
            # Calculate local moisture
            moisture = base_moisture
            
            # Check for nearby sprinklers (Radius 2)
            for sx, sy in active_sprinklers:
                dist = max(abs(crop.x - sx), abs(crop.y - sy))
                if dist <= 2:
                    moisture += 0.5 # Big boost
                    break # Only one sprinkler needed
            
            # Check for nearby heaters (Radius 2)
            local_temp = base_temp
            for hx, hy in active_heaters:
                dist = max(abs(crop.x - hx), abs(crop.y - hy))
                if dist <= 2:
                    local_temp += 10.0 # Heat boost

            # Clamp moisture
            moisture = min(moisture, 1.0)
            
            crop.update(dt, local_temp, moisture, uv_index=self.state.uv_index, snow_depth=self.state.snow_depth, wind_speed=self.state.wind_speed)
            
        # Creature Spawns
        # Remove expired creatures
        self.state.active_spawns = [c for c in self.state.active_spawns if c.timer > 0]
        
        # Update active creatures
        for c in self.state.active_spawns:
            c.update(dt)
            
        # Spawn new ones
        if len(self.state.active_spawns) < 5:
            import random
            spawnable_types = self.bestiary.check_spawns(self.state)
            
            for c in spawnable_types:
                # If we spawned a new creature wrapper from check_spawns, it needs coords
                # Check if this type is already spawned (limit 1 per type for variety? or just limit total?)
                # Let's just limit total for now, but ensure we set coords
                if random.random() < 0.1: # 10% chance to actually add it if condition met
                    # Pick random valid spot
                    attempts = 0
                    while attempts < 10:
                        rx = random.randint(0, 9)
                        ry = random.randint(0, 9)
                        
                        # Check collision with other creatures
                        occupied = False
                        for ac in self.state.active_spawns:
                            if ac.x == rx and ac.y == ry:
                                occupied = True
                                break
                        
                        if not occupied:
                            c.x = rx
                            c.y = ry
                            self.state.active_spawns.append(c)
                            break
                        attempts += 1

    def update_weather(self, weather_data):
        self.state.update_weather(weather_data)

    def sell_inventory(self, item_name=None):
        """
        Sell items from inventory for credits.
        If item_name is None, sell everything.
        """
        total_value = 0
        items_sold = 0
        
        # Find crop types to get values
        crop_values = {c.yield_resource: c.base_value for c in ALL_CROPS}
        
        if item_name:
            if item_name in self.state.inventory:
                count = self.state.inventory[item_name]
                value = crop_values.get(item_name, 1) * count
                total_value += value
                items_sold += count
                del self.state.inventory[item_name]
        else:
            # Sell all
            for item, count in list(self.state.inventory.items()):
                value = crop_values.get(item, 1) * count
                total_value += value
                items_sold += count
            self.state.inventory.clear()
            
        if total_value > 0:
            self.state.resources.add_credits(total_value)
            return True, f"Sold {items_sold} items for {total_value} Credits"
        return False, "Nothing to sell"

    def build_machine(self, name, x, y):
        # Check bounds
        if not (0 <= x < 10 and 0 <= y < 10):
            return False, "Out of bounds"
            
        # Check occupation
        for m in self.state.machines:
            if m.x == x and m.y == y:
                return False, "Space occupied"
        
        # Create instance to check cost
        machine = create_machine(name, x, y)
        if not machine:
            return False, "Invalid machine type"
            
        # Check cost (Balanced)
        # Costs are defined in machines.py, passed via create_machine
        
        # Note: We should rely on the defaults in machines.py unless we specifically want to override here.
        # The lines above were overriding with different values than definitions.
        # Let's trust the MachineType defaults which are assigned when creating the machine.
        # So we don't need to manually set them here unless we want dynamic costs.
        # But to be safe and match the previous logic's intent (which seemed to want to enforce specific costs),
        # I will leave them but commented out or corrected to match defaults if that was the intent.
        # Actually, the previous code had: turbine=100, solar=150, collector=50.
        # machines.py has: turbine=50, solar=100, collector=20.
        # The previous code was making them MORE expensive.
        # I will respect the override but use correct names.
        
        if name == "Wind Turbine": machine.type.cost_energy = 100
        elif name == "Solar Panel": machine.type.cost_energy = 150
        elif name == "Rain Collector": machine.type.cost_energy = 50
        
        if self.state.resources.energy < machine.type.cost_energy:
            return False, f"Not enough Energy (Need {machine.type.cost_energy})"
        if self.state.resources.biomass < machine.type.cost_biomass:
            return False, "Not enough Biomass"
            
        # Deduct cost
        self.state.resources.consume_energy(machine.type.cost_energy)
        self.state.resources.consume_biomass(machine.type.cost_biomass)
        
        # Place
        self.state.machines.append(machine)
        machine.on_place(self.state)
        return True, f"Built {name}"

    def plant_crop(self, crop_name, x, y):
        # Check bounds
        if not (0 <= x < 10 and 0 <= y < 10):
            return False, "Out of bounds"
            
        # Check occupation
        for m in self.state.machines:
            if m.x == x and m.y == y:
                return False, "Space occupied by machine"
        
        for c in self.state.crops:
            if c.x == x and c.y == y:
                return False, "Space occupied by crop"
                
        # Check seeds
        if self.state.seeds.get(crop_name, 0) <= 0:
            return False, "No seeds available"
            
        # Plant
        crop_type = next((c for c in ALL_CROPS if c.name == crop_name), None)
        if crop_type:
            self.state.crops.append(Crop(crop_type, x, y))
            self.state.seeds[crop_name] -= 1
            return True, f"Planted {crop_name}"
        
        return False, "Invalid crop type"

    def start_move(self, x, y):
        # Find object at x, y
        # Check machines
        for m in self.state.machines:
            if m.x == x and m.y == y:
                self.moving_object = (m, m.x, m.y)
                self.state.machines.remove(m)
                return True, f"Moving {m.type.name}"
        
        # Check crops
        for c in self.state.crops:
            if c.x == x and c.y == y:
                self.moving_object = (c, c.x, c.y)
                self.state.crops.remove(c)
                return True, f"Moving {c.type.name}"
                
        return False, "Nothing to move"

    def place_moving_object(self, x, y):
        if not self.moving_object:
            return False, "Not moving anything"
            
        obj, ox, oy = self.moving_object
        
        # Check bounds
        if not (0 <= x < 10 and 0 <= y < 10):
            return False, "Out of bounds"
            
        # Check occupation
        for m in self.state.machines:
            if m.x == x and m.y == y:
                return False, "Space occupied"
        for c in self.state.crops:
            if c.x == x and c.y == y:
                return False, "Space occupied"
                
        # Place
        obj.x = x
        obj.y = y
        
        # Add back to list
        if hasattr(obj, 'type') and hasattr(obj.type, 'yield_resource'): # It's a crop
            self.state.crops.append(obj)
        else: # It's a machine
            self.state.machines.append(obj)
            
        self.moving_object = None
        return True, "Placed object"

    def cancel_move(self):
        if not self.moving_object:
            return
            
        obj, ox, oy = self.moving_object
        obj.x = ox
        obj.y = oy
        
        # Add back
        if hasattr(obj, 'type') and hasattr(obj.type, 'yield_resource'): # It's a crop
            self.state.crops.append(obj)
        else: # It's a machine
            self.state.machines.append(obj)
            
        self.moving_object = None
        return True, "Cancelled move"

    def harvest_crop(self, crop):
        if crop not in self.state.crops: return False
        
        # print(f"Harvested {crop.type.name} at {crop.x},{crop.y}")
        self.state.crops.remove(crop)
        
        # Add to inventory
        item = crop.type.yield_resource
        amount = crop.type.yield_amount
        self.state.inventory[item] = self.state.inventory.get(item, 0) + amount
        
        # Track stats
        self.state._crops_harvested += 1
        
        # Chance to get seeds back
        if item != "cactus_fruit": # Cactus doesn't give seeds easily
            self.state.seeds[crop.type.name] = self.state.seeds.get(crop.type.name, 0) + 1
        
        return True

    def remove_crop(self, crop):
        """Remove a crop (e.g. dead) without harvesting."""
        if crop not in self.state.crops: return False
        self.state.crops.remove(crop)
        return True

    def interact(self, x, y):
        # Check bounds (assuming 10x10 map)
        if not (0 <= x < 10 and 0 <= y < 10):
            return None, None

        # Check for existing crop
        existing_crop = None
        for crop in self.state.crops:
            if crop.x == x and crop.y == y:
                existing_crop = crop
                break
        
        # Check for Harvester (Center Base) - Interactive
        if x == 5 and y == 5:
            # Check if occupied by crop/machine first? 
            # Actually Harvester is drawn there visually by WorldRenderer.
            # We should prioritize it if nothing else is there, or maybe always?
            # Let's assume Harvester is the permanent base structure.
            if not existing_crop and not any(m.x == 5 and m.y == 5 for m in self.state.machines):
                 return "harvester_click", None
        
        if existing_crop:
            # Always return crop_click to open details panel
            return "crop_click", existing_crop

        else:
            # Check for creature capture
            creature_clicked = None
            for c in self.state.active_spawns:
                if c.x == x and c.y == y:
                    creature_clicked = c
                    break
            
            if creature_clicked:
                # Check for Stable
                has_stable = any(m.type.name == "Creature Stable" for m in self.state.machines)
                
                if has_stable:
                    # Capture!
                    self.state.active_spawns.remove(creature_clicked)
                    import time
                    creature_clicked.caught_at = time.time()
                    self.state.collected_creatures.append(creature_clicked)
                    # print(f"Captured {creature_clicked.type.name}!")
                    return "creature_capture", creature_clicked
                else:
                    # print("Build a Creature Stable to capture creatures!")
                    return None, None
            
            # Check for machine interaction
            for m in self.state.machines:
                if m.x == x and m.y == y:
                    # Interact with machine (toggle, etc)
                    # Interact with machine (toggle, etc)
                    # Return machine for UI to handle
                    return "machine_click", m
            
            # print("Nothing to interact with.")
            return None, None

    def save_game(self, filename="savegame.json"):
        """Save game state to file."""
        import json
        
        data = {
            "state": self.state.to_dict(),
            "missions": self.mission_manager.to_dict(),
            "achievements": self.achievement_manager.to_dict(),
            "settings": self.settings_manager.to_dict()
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
            return True, "Game Saved"
        except Exception as e:
            return False, f"Save Failed: {e}"

    def load_game(self, filename="savegame.json"):
        """Load game state from file."""
        import json
        import os
        
        if not os.path.exists(filename):
            return False, "No save file found"
            
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                
            if "state" in data:
                self.state.from_dict(data["state"])
            if "missions" in data:
                self.mission_manager.from_dict(data["missions"])
            if "achievements" in data:
                self.achievement_manager.from_dict(data["achievements"])
            if "settings" in data:
                self.settings_manager.from_dict(data["settings"])
                
            # Force weather update after load to restore derived stats
            # (Weather data is not fully serialized, only current snapshot)
            # Ideally we should trigger a fetch, but state has some data.
            
            return True, "Game Loaded"
        except Exception as e:
            return False, f"Load Failed: {e}"
