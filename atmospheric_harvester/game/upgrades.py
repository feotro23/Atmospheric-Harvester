class Upgrade:
    def __init__(self, uid, name, description, base_cost, cost_multiplier=1.5):
        self.uid = uid
        self.name = name
        self.description = description
        self.base_cost = base_cost
        self.cost_multiplier = cost_multiplier
        
    def get_cost(self, current_level):
        return int(self.base_cost * (self.cost_multiplier ** current_level))

class UpgradeManager:
    def __init__(self):
        self.upgrades = {
            "turbine_eff": Upgrade("turbine_eff", "Aerodynamic Blades", "Increases Kinetic Efficiency by 20%", 100),
            "solar_eff": Upgrade("solar_eff", "Solar Tracking", "Increases Solar Efficiency by 15%", 150),
            "hydro_eff": Upgrade("hydro_eff", "Plant Clouds", "Increases Hydro Efficiency by 25%", 120),
            "battery_cap": Upgrade("battery_cap", "Lithium Arrays", "Increases Max Energy by 500", 200),
        }
        
    def get_upgrade(self, uid):
        return self.upgrades.get(uid)
        
    def buy_upgrade(self, game_state, uid):
        upgrade = self.upgrades.get(uid)
        if not upgrade:
            return False
            
        current_level = game_state.upgrades.get(uid, 0)
        cost = upgrade.get_cost(current_level)
        
        if game_state.resources.consume_energy(cost):
            game_state.upgrades[uid] = current_level + 1
            self._apply_upgrade_effect(game_state, uid)
            return True
        return False

    def _apply_upgrade_effect(self, game_state, uid):
        # Immediate effects (like capacity)
        if uid == "battery_cap":
            game_state.resources.modify_capacity("energy", 500)
            
    def get_multiplier(self, game_state, uid):
        level = game_state.upgrades.get(uid, 0)
        if uid == "turbine_eff":
            return 1.0 + (0.20 * level)
        elif uid == "solar_eff":
            return 1.0 + (0.15 * level)
        elif uid == "hydro_eff":
            return 1.0 + (0.25 * level)
        return 1.0
