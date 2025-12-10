"""
Achievement System for Atmospheric Harvester

Tracks player accomplishments across multiple categories with progress and rewards.
"""

from enum import Enum
from typing import Callable, Dict, List, Optional
from dataclasses import dataclass


class AchievementCategory(Enum):
    """Achievement categories."""
    EXPLORER = "explorer"
    ENGINEER = "engineer"
    FARMER = "farmer"
    WEATHER_MASTER = "weather_master"
    EFFICIENCY = "efficiency"
    COLLECTOR = "collector"


class AchievementTier(Enum):
    """Achievement difficulty tiers."""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"


@dataclass
class AchievementReward:
    """Rewards for unlocking an achievement."""
    energy: float = 0.0
    water: float = 0.0
    biomass: float = 0.0
    title: str = ""  # Unlockable player title


class Achievement:
    """Represents a single achievement."""
    
    def __init__(
        self,
        uid: str,
        name: str,
        description: str,
        category: AchievementCategory,
        tier: AchievementTier,
        reward: AchievementReward,
        check_condition: Callable,
        target: float = 1.0,  # Target value for progress tracking
        hidden: bool = False  # Hidden until unlocked
    ):
        self.uid = uid
        self.name = name
        self.description = description
        self.category = category
        self.tier = tier
        self.reward = reward
        self.check_condition = check_condition
        self.target = target
        self.hidden = hidden
        
        # State
        self.unlocked = False
        self.progress = 0.0
        self.unlock_timestamp = None
    
    def update(self, game_state) -> bool:
        """Update progress and check if achievement should unlock."""
        if self.unlocked:
            return False
        
        # Get current progress from condition
        current = self.check_condition(game_state)
        self.progress = min(current / self.target, 1.0) if self.target > 0 else 0.0
        
        # Check if unlocked
        if self.progress >= 1.0:
            self.unlocked = True
            import time
            self.unlock_timestamp = time.time()
            return True
        
        return False


class AchievementManager:
    """Manages all achievements and tracks player progress."""
    
    def __init__(self):
        self.achievements: Dict[str, Achievement] = {}
        self._create_achievements()
    
    def _create_achievements(self):
        """Define all achievements in the game."""
        
        # ================== EXPLORER CATEGORY ==================
        
        self.add_achievement(Achievement(
            uid="explorer_first_steps",
            name="First Steps",
            description="Visit your first location",
            category=AchievementCategory.EXPLORER,
            tier=AchievementTier.BRONZE,
            reward=AchievementReward(energy=25),
            check_condition=lambda gs: getattr(gs, '_locations_visited', 0),
            target=1
        ))
        
        self.add_achievement(Achievement(
            uid="explorer_wanderer",
            name="Wanderer",
            description="Visit 5 different locations",
            category=AchievementCategory.EXPLORER,
            tier=AchievementTier.BRONZE,
            reward=AchievementReward(energy=50),
            check_condition=lambda gs: getattr(gs, '_locations_visited', 0),
            target=5
        ))
        
        self.add_achievement(Achievement(
            uid="explorer_traveler",
            name="World Traveler",
            description="Visit 10 different locations",
            category=AchievementCategory.EXPLORER,
            tier=AchievementTier.SILVER,
            reward=AchievementReward(energy=100, title="Traveler"),
            check_condition=lambda gs: getattr(gs, '_locations_visited', 0),
            target=10
        ))
        
        self.add_achievement(Achievement(
            uid="explorer_globe_trotter",
            name="Globe Trotter",
            description="Visit 25 different locations",
            category=AchievementCategory.EXPLORER,
            tier=AchievementTier.GOLD,
            reward=AchievementReward(energy=250, title="Globe Trotter"),
            check_condition=lambda gs: getattr(gs, '_locations_visited', 0),
            target=25
        ))
        
        self.add_achievement(Achievement(
            uid="explorer_world_tour",
            name="World Tour",
            description="Visit 50 different locations",
            category=AchievementCategory.EXPLORER,
            tier=AchievementTier.PLATINUM,
            reward=AchievementReward(energy=500, water=200, title="Explorer"),
            check_condition=lambda gs: getattr(gs, '_locations_visited', 0),
            target=50
        ))
        
        # ================== ENGINEER CATEGORY ==================
        
        self.add_achievement(Achievement(
            uid="engineer_first_build",
            name="First Build",
            description="Build your first machine",
            category=AchievementCategory.ENGINEER,
            tier=AchievementTier.BRONZE,
            reward=AchievementReward(energy=30),
            check_condition=lambda gs: len(gs.machines),
            target=1
        ))
        
        self.add_achievement(Achievement(
            uid="engineer_constructor",
            name="Constructor",
            description="Build 5 machines",
            category=AchievementCategory.ENGINEER,
            tier=AchievementTier.BRONZE,
            reward=AchievementReward(energy=75),
            check_condition=lambda gs: len(gs.machines),
            target=5
        ))
        
        self.add_achievement(Achievement(
            uid="engineer_industrialist",
            name="Industrialist",
            description="Build 15 machines",
            category=AchievementCategory.ENGINEER,
            tier=AchievementTier.SILVER,
            reward=AchievementReward(energy=150, title="Engineer"),
            check_condition=lambda gs: len(gs.machines),
            target=15
        ))
        
        self.add_achievement(Achievement(
            uid="engineer_tycoon",
            name="Industrial Tycoon",
            description="Build 30 machines",
            category=AchievementCategory.ENGINEER,
            tier=AchievementTier.GOLD,
            reward=AchievementReward(energy=300, water=100),
            check_condition=lambda gs: len(gs.machines),
            target=30
        ))
        
        self.add_achievement(Achievement(
            uid="engineer_megacity",
            name="Megacity Builder",
            description="Build 50 machines",
            category=AchievementCategory.ENGINEER,
            tier=AchievementTier.PLATINUM,
            reward=AchievementReward(energy=600, water=200, biomass=50, title="Master Builder"),
            check_condition=lambda gs: len(gs.machines),
            target=50
        ))
        
        # ================== FARMER CATEGORY ==================
        
        self.add_achievement(Achievement(
            uid="farmer_green_thumb",
            name="Green Thumb",
            description="Harvest your first crop",
            category=AchievementCategory.FARMER,
            tier=AchievementTier.BRONZE,
            reward=AchievementReward(biomass=10),
            check_condition=lambda gs: getattr(gs, '_crops_harvested', 0),
            target=1
        ))
        
        self.add_achievement(Achievement(
            uid="farmer_gardener",
            name="Gardener",
            description="Harvest 10 crops",
            category=AchievementCategory.FARMER,
            tier=AchievementTier.BRONZE,
            reward=AchievementReward(biomass=25, water=20),
            check_condition=lambda gs: getattr(gs, '_crops_harvested', 0),
            target=10
        ))
        
        self.add_achievement(Achievement(
            uid="farmer_agriculturist",
            name="Agriculturist",
            description="Harvest 50 crops",
            category=AchievementCategory.FARMER,
            tier=AchievementTier.SILVER,
            reward=AchievementReward(biomass=75, water=50, title="Farmer"),
            check_condition=lambda gs: getattr(gs, '_crops_harvested', 0),
            target=50
        ))
        
        self.add_achievement(Achievement(
            uid="farmer_master",
            name="Master Farmer",
            description="Harvest 150 crops",
            category=AchievementCategory.FARMER,
            tier=AchievementTier.GOLD,
            reward=AchievementReward(biomass=200, water=100, energy=100),
            check_condition=lambda gs: getattr(gs, '_crops_harvested', 0),
            target=150
        ))
        
        self.add_achievement(Achievement(
            uid="farmer_legend",
            name="Agricultural Legend",
            description="Harvest 500 crops",
            category=AchievementCategory.FARMER,
            tier=AchievementTier.DIAMOND,
            reward=AchievementReward(biomass=500, water=250, energy=250, title="Harvest King"),
            check_condition=lambda gs: getattr(gs, '_crops_harvested', 0),
            target=500
        ))

        self.add_achievement(Achievement(
            uid="farmer_crop_circle",
            name="Crop Circle",
            description="Have one of every crop type growing at once",
            category=AchievementCategory.FARMER,
            tier=AchievementTier.GOLD,
            reward=AchievementReward(biomass=100, energy=100),
            check_condition=lambda gs: len(set([c.type.name for c in gs.crops])) >= 6,
            target=6
        ))

        self.add_achievement(Achievement(
            uid="farmer_sustainable",
            name="Sustainable",
            description="Generate 1000 Biomass from Composting",
            category=AchievementCategory.FARMER,
            tier=AchievementTier.PLATINUM,
            reward=AchievementReward(energy=500, title="Eco-Warrior"),
            check_condition=lambda gs: getattr(gs, '_biomass_composted', 0),
            target=1000
        ))
        
        self.add_achievement(Achievement(
            uid="farmer_master_chef",
            name="Master Chef",
            description="Harvest 1000 total items",
            category=AchievementCategory.FARMER,
            tier=AchievementTier.DIAMOND,
            reward=AchievementReward(biomass=1000, title="Master Chef"),
            check_condition=lambda gs: sum(gs.inventory.values()),
            target=1000
        ))
        
        # ================== WEATHER MASTER CATEGORY ==================
        
        self.add_achievement(Achievement(
            uid="weather_observer",
            name="Weather Observer",
            description="Open the weather overlay",
            category=AchievementCategory.WEATHER_MASTER,
            tier=AchievementTier.BRONZE,
            reward=AchievementReward(energy=20),
            check_condition=lambda gs: 1 if getattr(gs, '_weather_overlay_opened', False) else 0,
            target=1
        ))
        
        self.add_achievement(Achievement(
            uid="weather_storm_chaser",
            name="Storm Chaser",
            description="Experience rain in 3 different locations",
            category=AchievementCategory.WEATHER_MASTER,
            tier=AchievementTier.SILVER,
            reward=AchievementReward(water=100, title="Storm Chaser"),
            check_condition=lambda gs: getattr(gs, '_rainy_locations_visited', 0),
            target=3
        ))
        
        self.add_achievement(Achievement(
            uid="weather_snow_seeker",
            name="Snow Seeker",
            description="Experience snow in 3 different locations",
            category=AchievementCategory.WEATHER_MASTER,
            tier=AchievementTier.SILVER,
            reward=AchievementReward(water=100),
            check_condition=lambda gs: getattr(gs, '_snowy_locations_visited', 0),
            target=3
        ))
        
        self.add_achievement(Achievement(
            uid="weather_sun_worshipper",
            name="Sun Worshipper",
            description="Visit a location with 1000+ W/m² solar irradiance",
            category=AchievementCategory.WEATHER_MASTER,
            tier=AchievementTier.GOLD,
            reward=AchievementReward(energy=200, title="Sun Worshipper"),
            check_condition=lambda gs: 1 if (gs.solar_radiation or 0) >= 1000 else 0,
            target=1
        ))
        
        self.add_achievement(Achievement(
            uid="weather_wind_rider",
            name="Wind Rider",
            description="Experience wind speeds over 20 m/s",
            category=AchievementCategory.WEATHER_MASTER,
            tier=AchievementTier.GOLD,
            reward=AchievementReward(energy=200),
            check_condition=lambda gs: 1 if gs.wind_speed >= 20 else 0,
            target=1
        ))

        self.add_achievement(Achievement(
            uid="weather_storm_survivor",
            name="Storm Survivor",
            description="Experience your first weather event",
            category=AchievementCategory.WEATHER_MASTER,
            tier=AchievementTier.BRONZE,
            reward=AchievementReward(energy=50),
            check_condition=lambda gs: 1 if hasattr(gs, 'event_manager_stats') and gs.event_manager_stats['total_experienced'] >= 1 else 0,
            target=1
        ))

        self.add_achievement(Achievement(
            uid="weather_warrior",
            name="Weather Warrior",
            description="Survive 10 weather events",
            category=AchievementCategory.WEATHER_MASTER,
            tier=AchievementTier.SILVER,
            reward=AchievementReward(energy=200, water=100),
            check_condition=lambda gs: gs.event_manager_stats['total_experienced'] if hasattr(gs, 'event_manager_stats') else 0,
            target=10
        ))

        self.add_achievement(Achievement(
            uid="weather_extreme_conditions",
            name="Extreme Conditions",
            description="Experience an extreme severity event",
            category=AchievementCategory.WEATHER_MASTER,
            tier=AchievementTier.GOLD,
            reward=AchievementReward(energy=500, title="Survivor"),
            check_condition=lambda gs: 1 if hasattr(gs, 'event_manager_stats') and gs.event_manager_stats.get('extreme_experienced', False) else 0,
            target=1
        ))

        self.add_achievement(Achievement(
            uid="weather_aurora_witness",
            name="Aurora Witness",
            description="Witness the rare Aurora event",
            category=AchievementCategory.WEATHER_MASTER,
            tier=AchievementTier.DIAMOND,
            reward=AchievementReward(energy=1000, title="Stargazer"),
            check_condition=lambda gs: 1 if hasattr(gs, 'event_manager_stats') and gs.event_manager_stats.get('aurora_seen', False) else 0,
            target=1
        ))
        
        # ================== EFFICIENCY CATEGORY ==================
        
        self.add_achievement(Achievement(
            uid="efficiency_power_up",
            name="Power Up",
            description="Generate 100 total energy",
            category=AchievementCategory.EFFICIENCY,
            tier=AchievementTier.BRONZE,
            reward=AchievementReward(energy=50),
            check_condition=lambda gs: gs.resources.total_energy_generated,
            target=100
        ))
        
        self.add_achievement(Achievement(
            uid="efficiency_energy_baron",
            name="Energy Baron",
            description="Generate 1,000 total energy",
            category=AchievementCategory.EFFICIENCY,
            tier=AchievementTier.SILVER,
            reward=AchievementReward(energy=200, title="Power Provider"),
            check_condition=lambda gs: gs.resources.total_energy_generated,
            target=1000
        ))
        
        self.add_achievement(Achievement(
            uid="efficiency_power_plant",
            name="Power Plant",
            description="Generate 5,000 total energy",
            category=AchievementCategory.EFFICIENCY,
            tier=AchievementTier.GOLD,
            reward=AchievementReward(energy=500, water=200),
            check_condition=lambda gs: gs.resources.total_energy_generated,
            target=5000
        ))
        
        self.add_achievement(Achievement(
            uid="efficiency_energy_titan",
            name="Energy Titan",
            description="Generate 10,000 total energy",
            category=AchievementCategory.EFFICIENCY,
            tier=AchievementTier.PLATINUM,
            reward=AchievementReward(energy=1000, water=400, biomass=100, title="Energy Titan"),
            check_condition=lambda gs: gs.resources.total_energy_generated,
            target=10000
        ))
        
        self.add_achievement(Achievement(
            uid="efficiency_water_works",
            name="Water Works",
            description="Generate 500 total water",
            category=AchievementCategory.EFFICIENCY,
            tier=AchievementTier.SILVER,
            reward=AchievementReward(water=150),
            check_condition=lambda gs: gs.resources.total_water_generated,
            target=500
        ))
        
        self.add_achievement(Achievement(
            uid="efficiency_aqua_master",
            name="Aqua Master",
            description="Generate 2,000 total water",
            category=AchievementCategory.EFFICIENCY,
            tier=AchievementTier.GOLD,
            reward=AchievementReward(water=400, title="Water Baron"),
            check_condition=lambda gs: gs.resources.total_water_generated,
            target=2000
        ))
        
        # ================== COLLECTOR CATEGORY ==================
        
        self.add_achievement(Achievement(
            uid="collector_hoarder",
            name="Resource Hoarder",
            description="Store 500 energy at once",
            category=AchievementCategory.COLLECTOR,
            tier=AchievementTier.SILVER,
            reward=AchievementReward(energy=100),
            check_condition=lambda gs: gs.resources.energy,
            target=500
        ))
        
        self.add_achievement(Achievement(
            uid="collector_vault",
            name="Energy Vault",
            description="Store 1000 energy at once",
            category=AchievementCategory.COLLECTOR,
            tier=AchievementTier.GOLD,
            reward=AchievementReward(energy=250, title="Vault Keeper"),
            check_condition=lambda gs: gs.resources.energy,
            target=1000
        ))
        
        self.add_achievement(Achievement(
            uid="collector_water_reservoir",
            name="Water Reservoir",
            description="Store 300 water at once",
            category=AchievementCategory.COLLECTOR,
            tier=AchievementTier.SILVER,
            reward=AchievementReward(water=75),
            check_condition=lambda gs: gs.resources.water,
            target=300
        ))
        
        self.add_achievement(Achievement(
            uid="collector_biomass_bank",
            name="Biomass Bank",
            description="Store 80 biomass at once",
            category=AchievementCategory.COLLECTOR,
            tier=AchievementTier.SILVER,
            reward=AchievementReward(biomass=20),
            check_condition=lambda gs: gs.resources.biomass,
            target=80
        ))
        
        # ================== SPECIAL/HIDDEN ACHIEVEMENTS ==================
        
        self.add_achievement(Achievement(
            uid="special_completionist",
            name="Completionist",
            description="Unlock all other achievements",
            category=AchievementCategory.COLLECTOR,
            tier=AchievementTier.DIAMOND,
            reward=AchievementReward(energy=1000, water=500, biomass=250, title="Legend"),
            check_condition=lambda gs: len([a for a in self.achievements.values() 
                                           if a.unlocked and a.uid != "special_completionist"]),
            target=37,  # Total achievements minus this one (38-1)
            hidden=True
        ))
    
    def add_achievement(self, achievement: Achievement):
        """Add an achievement to the manager."""
        self.achievements[achievement.uid] = achievement
    
    def get_achievement(self, uid: str) -> Optional[Achievement]:
        """Get an achievement by UID."""
        return self.achievements.get(uid)
    
    def update(self, game_state):
        """Update all achievements and check for unlocks."""
        newly_unlocked = []
        
        for achievement in self.achievements.values():
            if achievement.update(game_state):
                newly_unlocked.append(achievement)
                print(f"Achievement Unlocked: {achievement.name}!")
                print(f"   {achievement.description}")
                
                # Grant rewards
                if achievement.reward.energy > 0:
                    game_state.resources.add_energy(achievement.reward.energy)
                if achievement.reward.water > 0:
                    game_state.resources.add_water(achievement.reward.water)
                if achievement.reward.biomass > 0:
                    game_state.resources.add_biomass(achievement.reward.biomass)
                if achievement.reward.title:
                    print(f"   Title Unlocked: {achievement.reward.title}")
        
        return newly_unlocked
    
    def get_by_category(self, category: AchievementCategory) -> List[Achievement]:
        """Get all achievements in a category."""
        return [a for a in self.achievements.values() if a.category == category]
    
    def get_unlocked(self) -> List[Achievement]:
        """Get all unlocked achievements."""
        return [a for a in self.achievements.values() if a.unlocked]
    
    def get_locked(self) -> List[Achievement]:
        """Get all locked achievements (excluding hidden)."""
        return [a for a in self.achievements.values() if not a.unlocked and not a.hidden]
    
    def get_in_progress(self) -> List[Achievement]:
        """Get achievements with progress > 0 but not unlocked."""
        return [a for a in self.achievements.values() 
                if not a.unlocked and a.progress > 0 and not a.hidden]
    
    def get_stats(self) -> Dict:
        """Get overall achievement statistics."""
        total = len([a for a in self.achievements.values() if not a.hidden])
        unlocked = len(self.get_unlocked())
        
        return {
            'total': total,
            'unlocked': unlocked,
            'locked': total - unlocked,
            'completion_rate': (unlocked / total * 100) if total > 0 else 0,
            'by_tier': {
                tier: len([a for a in self.achievements.values() 
                          if a.tier == tier and a.unlocked])
                for tier in AchievementTier
            },
            'by_category': {
                cat: len([a for a in self.achievements.values() 
                         if a.category == cat and a.unlocked])
                for cat in AchievementCategory
            }
        }

    def to_dict(self):
        """Serialize achievement state."""
        return {
            uid: {
                "unlocked": a.unlocked,
                "progress": a.progress,
                "unlock_timestamp": a.unlock_timestamp
            }
            for uid, a in self.achievements.items()
            if a.unlocked or a.progress > 0
        }

    def from_dict(self, data):
        """Restore achievement state."""
        for uid, a_data in data.items():
            if uid in self.achievements:
                achievement = self.achievements[uid]
                achievement.unlocked = a_data.get("unlocked", False)
                achievement.progress = a_data.get("progress", 0.0)
                achievement.unlock_timestamp = a_data.get("unlock_timestamp", None)
