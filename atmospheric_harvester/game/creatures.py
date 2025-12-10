import random

class CreatureType:
    def __init__(self, name, description, condition, bonus_type=None, bonus_desc=""):
        self.name = name
        self.description = description
        self.condition = condition # Function(game_state) -> bool
        self.bonus_type = bonus_type
        self.bonus_desc = bonus_desc

class Creature:
    def __init__(self, c_type, x=0, y=0):
        self.type = c_type
        self.caught_at = 0 # Timestamp
        self.x = x
        self.y = y
        self.timer = 60.0 # Lifetime in seconds
        self.move_timer = 0.0
        
    def update(self, dt):
        self.timer -= dt
        
        # Wandering logic
        self.move_timer -= dt
        if self.move_timer <= 0:
            self.move_timer = random.uniform(2.0, 5.0)
            
            # Random move
            dx = random.choice([-1, 0, 1])
            dy = random.choice([-1, 0, 1])
            
            new_x = self.x + dx
            new_y = self.y + dy
            
            # Simple bounds check
            if 0 <= new_x < 10 and 0 <= new_y < 10:
                self.x = new_x
                self.y = new_y

    def to_dict(self):
        return {
            "name": self.type.name,
            "x": self.x,
            "y": self.y,
            "timer": self.timer
        }


ALL_CREATURES = [
    CreatureType("Petrichor Slime", "Spawns in high moisture.", 
                 lambda s: getattr(s, 'soil_moisture', 0) > 0.4,
                 "water_eff", "Increases Water Collection by 10%"),
    CreatureType("Fulgarite Golem", "Spawns during thunderstorms.", 
                 lambda s: 95 <= getattr(s, 'weather_code', 0) <= 99,
                 "passive_energy", "Generates 1.0 Energy/s passively"),
    CreatureType("Thermal Kite", "Spawns in high winds and heat.", 
                 lambda s: getattr(s, 'temp_c', 0) > 25 and getattr(s, 'wind_speed', 0) > 20,
                 "wind_eff", "Increases Wind Efficiency by 10%"),
    CreatureType("Nebula Moth", "Spawns at night with clouds.", 
                 lambda s: not getattr(s, 'is_day', True) and getattr(s, 'weather_code', 0) > 2,
                 "solar_eff", "Increases Solar Efficiency by 10% (Moonlight)"),
    CreatureType("Frost Wisp", "Spawns in freezing temps.", 
                 lambda s: getattr(s, 'temp_c', 0) < 0,
                 "chill_eff", "Increases Chill Hours accumulation by 20%")
]

class Bestiary:
    def __init__(self):
        self.creatures = ALL_CREATURES
        
    def check_spawns(self, game_state):
        spawned = []
        for c in self.creatures:
            if c.condition(game_state):
                # Chance to spawn
                if random.random() < 0.01: # 1% chance per tick if condition met
                    spawned.append(Creature(c))
        return spawned
