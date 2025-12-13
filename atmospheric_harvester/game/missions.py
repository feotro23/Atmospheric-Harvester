"""
Mission System for Atmospheric Harvester

This module implements a quest/objective system to guide player progression
and provide clear goals throughout the game.
"""

from enum import Enum
from typing import Dict, List, Callable, Any


class MissionStatus(Enum):
    """Status of a mission."""
    LOCKED = "locked"          # Not yet available
    AVAILABLE = "available"    # Can be started
    ACTIVE = "active"          # Currently tracking
    COMPLETED = "completed"    # Finished
    CLAIMED = "claimed"        # Rewards collected


class MissionTier(Enum):
    """Difficulty/progression tier of missions."""
    TUTORIAL = "tutorial"
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    MASTER = "master"


class MissionReward:
    """Rewards given upon mission completion."""
    def __init__(self, energy=0, water=0, biomass=0, unlocks=None):
        self.energy = energy
        self.water = water
        self.biomass = biomass
        self.unlocks = unlocks or []  # List of tech/machine names to unlock


class Mission:
    """Represents a single mission/quest."""
    
    def __init__(self, 
                 uid: str,
                 name: str,
                 description: str,
                 tier: MissionTier,
                 reward: MissionReward,
                 check_condition: Callable[[Any], bool],
                 prerequisites: List[str] = None):
        """
        Initialize a mission.
        
        Args:
            uid: Unique identifier
            name: Display name
            description: What the player needs to do
            tier: Difficulty tier
            reward: Rewards for completion
            check_condition: Function that returns True when mission is complete
            prerequisites: List of mission UIDs that must be completed first
        """
        self.uid = uid
        self.name = name
        self.description = description
        self.tier = tier
        self.reward = reward
        self.check_condition = check_condition
        self.prerequisites = prerequisites or []
        self.status = MissionStatus.LOCKED
        self.progress = 0.0  # 0.0 to 1.0 for UI display
        
    def update(self, game_state) -> bool:
        """
        Check if mission is complete.
        
        Returns:
            True if mission was just completed (state transition)
        """
        if self.status != MissionStatus.ACTIVE:
            return False
            
        if self.check_condition(game_state):
            self.status = MissionStatus.COMPLETED
            self.progress = 1.0
            return True
        return False
    
    def can_activate(self, mission_manager) -> bool:
        """Check if this mission can be activated."""
        if self.status != MissionStatus.AVAILABLE:
            return False
        # Check prerequisites
        for prereq_uid in self.prerequisites:
            prereq = mission_manager.get_mission(prereq_uid)
            if prereq and prereq.status != MissionStatus.CLAIMED:
                return False
        return True


class MissionManager:
    """Manages all missions and progression."""
    
    def __init__(self):
        self.missions: Dict[str, Mission] = {}
        self.active_missions: List[Mission] = []
        self.max_active = 5  # Maximum concurrent active missions
        
        # Initialize all missions
        self._create_missions()
        
        # Activate tutorial missions
        self._unlock_initial_missions()
    
    def _create_missions(self):
        """Create all game missions."""
        
        # ===== TUTORIAL MISSIONS =====
        
        self.add_mission(Mission(
            uid="tutorial_welcome",
            name="Welcome to the Harvester",
            description="Open the weather overlay to see current conditions (Press W or click Weather button)",
            tier=MissionTier.TUTORIAL,
            reward=MissionReward(energy=10),
            check_condition=lambda gs: hasattr(gs, '_weather_overlay_opened') and gs._weather_overlay_opened
        ))
        
        self.add_mission(Mission(
            uid="tutorial_first_machine",
            name="Build Your First Machine",
            description="Build any machine to start generating resources",
            tier=MissionTier.TUTORIAL,
            reward=MissionReward(energy=50, biomass=10),
            check_condition=lambda gs: len(gs.machines) >= 1,
            prerequisites=["tutorial_welcome"]
        ))
        
        self.add_mission(Mission(
            uid="tutorial_plant_crop",
            name="Plant Your First Crop",
            description="Click on an empty tile to plant a crop",
            tier=MissionTier.TUTORIAL,
            reward=MissionReward(energy=25, biomass=5),
            check_condition=lambda gs: len(gs.crops) >= 1,
            prerequisites=["tutorial_first_machine"]
        ))
        
        self.add_mission(Mission(
            uid="tutorial_harvest",
            name="Harvest Your First Crop",
            description="Wait for a crop to mature (stage 3) then click it to harvest",
            tier=MissionTier.TUTORIAL,
            reward=MissionReward(biomass=20),
            check_condition=lambda gs: hasattr(gs, '_crops_harvested') and gs._crops_harvested >= 1,
            prerequisites=["tutorial_plant_crop"]
        ))
        
        # ===== BASIC MISSIONS =====
        
        self.add_mission(Mission(
            uid="basic_wind_power",
            name="Harness the Wind",
            description="Build a Wind Turbine",
            tier=MissionTier.BASIC,
            reward=MissionReward(energy=100),
            check_condition=lambda gs: any(m.type.name == "Wind Turbine" for m in gs.machines),
            prerequisites=["tutorial_harvest"]
        ))
        
        self.add_mission(Mission(
            uid="basic_solar_power",
            name="Capture Solar Energy",
            description="Build a Solar Panel",
            tier=MissionTier.BASIC,
            reward=MissionReward(energy=100),
            check_condition=lambda gs: any(m.type.name == "Solar Panel" for m in gs.machines),
            prerequisites=["tutorial_harvest"]
        ))
        
        self.add_mission(Mission(
            uid="basic_water_collection",
            name="Collect Rainwater",
            description="Build a Rain Collector",
            tier=MissionTier.BASIC,
            reward=MissionReward(water=50),
            check_condition=lambda gs: any(m.type.name == "Rain Collector" for m in gs.machines),
            prerequisites=["tutorial_harvest"]
        ))
        
        self.add_mission(Mission(
            uid="basic_energy_milestone",
            name="Power Up",
            description="Generate a total of 500 kWh of energy",
            tier=MissionTier.BASIC,
            reward=MissionReward(biomass=50),
            check_condition=lambda gs: hasattr(gs.resources, 'total_energy_generated') and 
                                      gs.resources.total_energy_generated >= 500,
            prerequisites=["basic_wind_power", "basic_solar_power"]
        ))
        
        self.add_mission(Mission(
            uid="basic_farm_expansion",
            name="Expand Your Farm",
            description="Have 5 crops growing simultaneously",
            tier=MissionTier.BASIC,
            reward=MissionReward(energy=50, biomass=25),
            check_condition=lambda gs: len(gs.crops) >= 5,
            prerequisites=["tutorial_harvest"]
        ))
        
        # ===== INTERMEDIATE MISSIONS =====
        
        self.add_mission(Mission(
            uid="intermediate_travel",
            name="First Expedition",
            description="Travel to a different location",
            tier=MissionTier.INTERMEDIATE,
            reward=MissionReward(energy=200),
            check_condition=lambda gs: hasattr(gs, '_locations_visited') and gs._locations_visited >= 2,
            prerequisites=["basic_energy_milestone"]
        ))
        
        self.add_mission(Mission(
            uid="intermediate_diversify",
            name="Diversify Your Energy",
            description="Have at least one of each: Wind Turbine, Solar Panel, and Rain Collector",
            tier=MissionTier.INTERMEDIATE,
            reward=MissionReward(energy=300, water=100, biomass=50),
            check_condition=lambda gs: (
                any(m.type.name == "Wind Turbine" for m in gs.machines) and
                any(m.type.name == "Solar Panel" for m in gs.machines) and
                any(m.type.name == "Rain Collector" for m in gs.machines)
            ),
            prerequisites=["basic_wind_power", "basic_solar_power", "basic_water_collection"]
        ))
        
        self.add_mission(Mission(
            uid="intermediate_storage",
            name="Build Energy Storage",
            description="Build a Battery to store excess energy",
            tier=MissionTier.INTERMEDIATE,
            reward=MissionReward(energy=150),
            check_condition=lambda gs: any(m.type.name == "Battery" for m in gs.machines),
            prerequisites=["basic_energy_milestone"]
        ))
        
        self.add_mission(Mission(
            uid="intermediate_irrigation",
            name="Automated Irrigation",
            description="Build a Sprinkler to water crops automatically",
            tier=MissionTier.INTERMEDIATE,
            reward=MissionReward(water=100, biomass=30),
            check_condition=lambda gs: any(m.type.name == "Sprinkler" for m in gs.machines),
            prerequisites=["basic_farm_expansion"]
        ))
        
        # ===== ADVANCED MISSIONS =====
        
        self.add_mission(Mission(
            uid="advanced_machine_count",
            name="Industrial Complex",
            description="Build 20 machines total",
            tier=MissionTier.ADVANCED,
            reward=MissionReward(energy=500, water=200, biomass=100),
            check_condition=lambda gs: len(gs.machines) >= 20,
            prerequisites=["intermediate_diversify"]
        ))
        
        self.add_mission(Mission(
            uid="advanced_crop_master",
            name="Master Farmer",
            description="Harvest 50 crops total",
            tier=MissionTier.ADVANCED,
            reward=MissionReward(energy=300, biomass=200),
            check_condition=lambda gs: hasattr(gs, '_crops_harvested') and gs._crops_harvested >= 50,
            prerequisites=["intermediate_irrigation"]
        ))
        
        self.add_mission(Mission(
            uid="advanced_explorer",
            name="World Explorer",
            description="Visit 10 different locations",
            tier=MissionTier.ADVANCED,
            reward=MissionReward(energy=1000),
            check_condition=lambda gs: hasattr(gs, '_locations_visited') and gs._locations_visited >= 10,
            prerequisites=["intermediate_travel"]
        ))
    
        # ===== FARMING MISSIONS =====
        
        self.add_mission(Mission(
            uid="farming_potato_famine",
            name="Potato Famine Prevention",
            description="Harvest 50 Potatoes",
            tier=MissionTier.INTERMEDIATE,
            reward=MissionReward(biomass=100, energy=50),
            check_condition=lambda gs: gs.inventory.get("potato", 0) >= 50,
            prerequisites=["basic_farm_expansion"]
        ))
        
        self.add_mission(Mission(
            uid="farming_oil_baron",
            name="Oil Baron",
            description="Harvest 20 Sunflowers",
            tier=MissionTier.INTERMEDIATE,
            reward=MissionReward(biomass=150),
            check_condition=lambda gs: gs.inventory.get("sunflower_seeds", 0) >= 20,
            prerequisites=["basic_farm_expansion"]
        ))
        
        self.add_mission(Mission(
            uid="farming_desert_bloom",
            name="Desert Bloom",
            description="Harvest 10 Cactus Fruits",
            tier=MissionTier.ADVANCED,
            reward=MissionReward(water=50, biomass=50),
            check_condition=lambda gs: gs.inventory.get("cactus_fruit", 0) >= 10,
            prerequisites=["farming_oil_baron"]
        ))
        
        self.add_mission(Mission(
            uid="farming_rice_paddy",
            name="Rice Paddy",
            description="Harvest 30 Rice",
            tier=MissionTier.ADVANCED,
            reward=MissionReward(water=100, biomass=100),
            check_condition=lambda gs: gs.inventory.get("rice", 0) >= 30,
            prerequisites=["farming_potato_famine"]
        ))

        # ===== WEATHER MISSIONS (New) =====
        
        self.add_mission(Mission(
            uid="weather_freeze",
            name="Deep Freeze",
            description="Experience freezing temperatures (< 0°C)",
            tier=MissionTier.BASIC,
            reward=MissionReward(energy=50),
            check_condition=lambda gs: gs.temp_c < 0.0,
            prerequisites=["tutorial_welcome"]
        ))

        self.add_mission(Mission(
            uid="weather_heat",
            name="Heat Wave",
            description="Experience hot temperatures (> 30°C)",
            tier=MissionTier.BASIC,
            reward=MissionReward(energy=50, water=10),
            check_condition=lambda gs: gs.temp_c > 30.0,
            prerequisites=["tutorial_welcome"]
        ))

        self.add_mission(Mission(
            uid="weather_storm",
            name="Storm Chaser",
            description="Encounter high storm potential (CAPE > 500) or a Thunderstorm",
            tier=MissionTier.INTERMEDIATE,
            reward=MissionReward(energy=100, biomass=20),
            check_condition=lambda gs: gs.cape > 500 or gs.weather_code in [95, 96, 99],
            prerequisites=["weather_freeze"] # Just link one basic one to start chain
        ))

        # ===== CREATURE MISSIONS (New) =====

        self.add_mission(Mission(
            uid="creature_first",
            name="Creature Hunter",
            description="Collect your first creature (click on wandering creatures)",
            tier=MissionTier.BASIC,
            reward=MissionReward(biomass=100),
            check_condition=lambda gs: len(gs.collected_creatures) >= 1,
            prerequisites=["tutorial_welcome"]
        ))

        self.add_mission(Mission(
            uid="creature_zoo",
            name="Zoo Keeper",
            description="Collect 3 distinct types of creatures",
            tier=MissionTier.INTERMEDIATE,
            reward=MissionReward(biomass=200, water=100),
            check_condition=lambda gs: len(set(c.type.name for c in gs.collected_creatures)) >= 3,
            prerequisites=["creature_first"]
        ))

        # ===== RESOURCE MISSIONS (New) =====

        self.add_mission(Mission(
            uid="resource_energy_cap",
            name="Battery Bank",
            description="Store 1000 Energy",
            tier=MissionTier.INTERMEDIATE,
            reward=MissionReward(biomass=200),
            check_condition=lambda gs: gs.resources.energy >= 1000,
            prerequisites=["basic_energy_milestone"]
        ))

        self.add_mission(Mission(
            uid="resource_water_cap",
            name="Water Tank",
            description="Store 500 Water",
            tier=MissionTier.INTERMEDIATE,
            reward=MissionReward(biomass=200),
            check_condition=lambda gs: gs.resources.water >= 500,
            prerequisites=["basic_water_collection"]
        ))

        # ===== TECH MISSIONS (New Round 2) =====

        self.add_mission(Mission(
            uid="upgrade_wind",
            name="Better Blades",
            description="Upgrade Wind Turbine efficiency (Level 1)",
            tier=MissionTier.INTERMEDIATE,
            reward=MissionReward(energy=50),
            check_condition=lambda gs: gs.upgrades.get("turbine_eff", 0) >= 1,
            prerequisites=["basic_wind_power"]
        ))

        self.add_mission(Mission(
            uid="upgrade_solar",
            name="Solar Tech",
            description="Upgrade Solar efficiency (Level 1)",
            tier=MissionTier.INTERMEDIATE,
            reward=MissionReward(energy=50),
            check_condition=lambda gs: gs.upgrades.get("solar_eff", 0) >= 1,
            prerequisites=["basic_solar_power"]
        ))

        self.add_mission(Mission(
            uid="upgrade_max",
            name="Tech Maximizer",
            description="Reach Level 3 on any upgrade",
            tier=MissionTier.ADVANCED,
            reward=MissionReward(energy=500, biomass=100),
            check_condition=lambda gs: any(lvl >= 3 for lvl in gs.upgrades.values()),
            prerequisites=["upgrade_wind"] # Soft requirement
        ))

        # ===== WEATHER EXPERT MISSIONS (New Round 2) =====

        self.add_mission(Mission(
            uid="weather_rain",
            name="Rain Dancer",
            description="Experience Rain conditions",
            tier=MissionTier.BASIC,
            reward=MissionReward(water=100),
            check_condition=lambda gs: gs.rain_vol > 0 or gs.weather_code in [51, 53, 55, 61, 63, 65, 80, 81, 82],
            prerequisites=["basic_water_collection"] 
        ))

        self.add_mission(Mission(
            uid="weather_snow",
            name="Snow Walker",
            description="Experience Snow conditions",
            tier=MissionTier.BASIC,
            reward=MissionReward(water=100),
            check_condition=lambda gs: gs.snow_depth > 0 or (gs.temp_c < 0 and gs.rain_vol > 0) or gs.weather_code in [71, 73, 75, 77, 85, 86],
            prerequisites=["weather_freeze"]
        ))

        # ===== ECONOMY MISSIONS (New Round 2) =====

        self.add_mission(Mission(
            uid="economy_first",
            name="First Sale",
            description="Earn 10 Credits (Sell items)",
            tier=MissionTier.BASIC,
            reward=MissionReward(energy=50), # Credits reward not supported in MissionReward class init directly yet, sticking to resources
            check_condition=lambda gs: gs.resources.total_credits_earned >= 10,
            prerequisites=["tutorial_harvest"]
        ))

        self.add_mission(Mission(
            uid="economy_1000",
            name="Market Maker",
            description="Earn 1000 Credits total",
            tier=MissionTier.ADVANCED,
            reward=MissionReward(biomass=200),
            check_condition=lambda gs: gs.resources.total_credits_earned >= 1000,
            prerequisites=["economy_first"]
        ))

    def add_mission(self, mission: Mission):
        """Add a mission to the manager."""
        self.missions[mission.uid] = mission
    
    def get_mission(self, uid: str) -> Mission:
        """Get a mission by UID."""
        return self.missions.get(uid)
    
    def _unlock_initial_missions(self):
        """Unlock tutorial missions at game start."""
        tutorial = self.get_mission("tutorial_welcome")
        if tutorial:
            tutorial.status = MissionStatus.AVAILABLE
            self.activate_mission(tutorial.uid)
    
    def activate_mission(self, uid: str) -> bool:
        """Activate a mission if possible."""
        mission = self.get_mission(uid)
        if not mission:
            return False
        
        if not mission.can_activate(self):
            return False
        
        if len(self.active_missions) >= self.max_active:
            return False  # Too many active missions
        
        mission.status = MissionStatus.ACTIVE
        self.active_missions.append(mission)
        return True
    
    def update(self, game_state):
        """Update all active missions."""
        completed = []
        
        for mission in self.active_missions:
            if mission.update(game_state):
                completed.append(mission)
                print(f"✓ Mission Completed: {mission.name}")
        
        # Check for newly available missions
        for mission in self.missions.values():
            if mission.status == MissionStatus.LOCKED:
                # Check if prerequisites are met
                can_unlock = True
                for prereq_uid in mission.prerequisites:
                    prereq = self.get_mission(prereq_uid)
                    if prereq and prereq.status != MissionStatus.CLAIMED:
                        can_unlock = False
                        break
                
                if can_unlock:
                    mission.status = MissionStatus.AVAILABLE
        
        # Auto-activate available missions if space allows
        available_missions = [m for m in self.missions.values() if m.status == MissionStatus.AVAILABLE]
        for mission in available_missions:
            if len(self.active_missions) < self.max_active:
                self.activate_mission(mission.uid)
            else:
                break
    
    def claim_reward(self, uid: str, game_state) -> bool:
        """Claim rewards for a completed mission."""
        mission = self.get_mission(uid)
        if not mission or mission.status != MissionStatus.COMPLETED:
            return False
        
        # Grant rewards
        game_state.resources.add_energy(mission.reward.energy)
        game_state.resources.add_water(mission.reward.water)
        game_state.resources.add_biomass(mission.reward.biomass)
        
        # Handle unlocks
        for unlock in mission.reward.unlocks:
            # This will be implemented when tech tree is added
            pass
        
        mission.status = MissionStatus.CLAIMED
        if mission in self.active_missions:
            self.active_missions.remove(mission)
        
        print(f"✓ Claimed rewards: {mission.reward.energy} Energy, {mission.reward.water} Water, {mission.reward.biomass} Biomass")
        return True
    
    def get_active_missions(self) -> List[Mission]:
        """Get list of active missions."""
        return self.active_missions.copy()
    
    def get_available_missions(self) -> List[Mission]:
        """Get list of missions that can be activated."""
        return [m for m in self.missions.values() 
                if m.status == MissionStatus.AVAILABLE]
    
    def get_completed_missions(self) -> List[Mission]:
        """Get list of completed but unclaimed missions."""
        return [m for m in self.missions.values() 
                if m.status == MissionStatus.COMPLETED]
    
    def get_stats(self) -> Dict[str, int]:
        """Get mission completion statistics."""
        total = len(self.missions)
        completed = len([m for m in self.missions.values() 
                        if m.status in [MissionStatus.COMPLETED, MissionStatus.CLAIMED]])
        claimed = len([m for m in self.missions.values() 
                      if m.status == MissionStatus.CLAIMED])
        
        return {
            "total": total,
            "completed": completed,
            "claimed": claimed,
            "completion_rate": (claimed / total * 100) if total > 0 else 0
        }

    def to_dict(self):
        """Serialize mission state."""
        return {
            uid: mission.status.value 
            for uid, mission in self.missions.items()
        }

    def from_dict(self, data):
        """Restore mission state."""
        self.active_missions = []
        for uid, status_val in data.items():
            if uid in self.missions:
                mission = self.missions[uid]
                try:
                    mission.status = MissionStatus(status_val)
                    if mission.status == MissionStatus.ACTIVE:
                        self.active_missions.append(mission)
                except ValueError:
                    print(f"Invalid mission status for {uid}: {status_val}")
