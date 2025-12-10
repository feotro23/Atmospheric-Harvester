"""
Weather Events System - Dynamic weather events that affect gameplay.

This module defines weather event types, severity levels, and event detection logic.
Events can occur based on realistic weather conditions or with a gameplay multiplier.
"""

import time
from enum import Enum
from typing import List, Dict, Optional
from dataclasses import dataclass


class EventSeverity(Enum):
    """Severity levels for weather events."""
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"
    EXTREME = "extreme"


class EventType(Enum):
    """Types of weather events that can occur."""
    THUNDERSTORM = "thunderstorm"
    HEATWAVE = "heatwave"
    BLIZZARD = "blizzard"
    DROUGHT = "drought"
    WINDSTORM = "windstorm"
    DUST_STORM = "dust_storm"
    FOG = "fog"
    TORNADO_WARNING = "tornado_warning"
    HURRICANE = "hurricane"
    COLD_SNAP = "cold_snap"
    FLASH_FLOOD = "flash_flood"
    AURORA = "aurora"  # Rare bonus event


@dataclass
class WeatherEvent:
    """Represents an active weather event."""
    
    uid: str
    event_type: EventType
    severity: EventSeverity
    start_time: float
    duration: float  # In seconds
    description: str
    warning_issued: bool = False
    
    # Machine efficiency modifiers: machine_type -> multiplier
    # e.g., {"wind": 1.5, "solar": 0.7, "hydro": 1.2}
    wind_modifier: float = 1.0
    solar_modifier: float = 1.0
    hydro_modifier: float = 1.0
    
    def is_active(self) -> bool:
        """Check if event is still active."""
        elapsed = time.time() - self.start_time
        return elapsed < self.duration
    
    def time_remaining(self) -> float:
        """Get remaining time in seconds."""
        elapsed = time.time() - self.start_time
        return max(0, self.duration - elapsed)
    
    def get_modifiers(self) -> Dict[str, float]:
        """Get all machine modifiers as a dictionary."""
        return {
            "wind": self.wind_modifier,
            "solar": self.solar_modifier,
            "hydro": self.hydro_modifier
        }


class WeatherEventManager:
    """Manages weather event detection, lifecycle, and effects."""
    
    def __init__(self):
        self.active_events: List[WeatherEvent] = []
        self.event_history: List[WeatherEvent] = []
        self.max_history = 20
        
        # Tracking for time-based events
        self.last_rain_time = time.time()
        self.heatwave_start_time = 0.0
        self.cold_start_time = 0.0
        
        # Event frequency booster (tech upgrade)
        self.frequency_multiplier = 1.0  # 1.0 = realistic, 1.5+ = gameplay-focused
        
    def set_frequency_multiplier(self, multiplier: float):
        """Set the event frequency multiplier (tech upgrade)."""
        self.frequency_multiplier = max(1.0, min(3.0, multiplier))
    
    def check_for_events(self, game_state) -> List[WeatherEvent]:
        """Check weather conditions and detect new events."""
        new_events = []
        current_time = time.time()
        
        if game_state.rain_vol > 0:
            self.last_rain_time = current_time
            
        # 0. Check for NOAA Alerts
        # Map alert event names to game events
        if getattr(game_state, 'alerts', None):
            for alert in game_state.alerts:
                event_name = alert.get('event', '').lower()
                desc = alert.get('description', '')
                
                # Check mapping
                detected_type = None
                severity = EventSeverity.SEVERE # Default for alerts
                
                if "thunderstorm" in event_name:
                    detected_type = EventType.THUNDERSTORM
                    if "severe" in event_name: severity = EventSeverity.SEVERE
                elif "tornado" in event_name:
                    detected_type = EventType.TORNADO_WARNING
                    severity = EventSeverity.EXTREME
                elif "hurricane" in event_name:
                    detected_type = EventType.HURRICANE
                    severity = EventSeverity.EXTREME
                elif "flood" in event_name:
                    detected_type = EventType.FLASH_FLOOD
                elif "heat" in event_name:
                    detected_type = EventType.HEATWAVE
                elif "freeze" in event_name or "cold" in event_name:
                    detected_type = EventType.COLD_SNAP
                elif "winter" in event_name:
                    # Winter Weather Advisory / Winter Storm Warning
                    if "storm" in event_name or "warning" in event_name:
                         detected_type = EventType.BLIZZARD
                    else:
                         detected_type = EventType.COLD_SNAP
                         severity = EventSeverity.MINOR
                elif "blizzard" in event_name or ("snow" in event_name and "warning" in event_name):
                    detected_type = EventType.BLIZZARD
                elif "wind" in event_name and "warning" in event_name:
                    detected_type = EventType.WINDSTORM
                elif "dust" in event_name:
                    detected_type = EventType.DUST_STORM
                    
                if detected_type and not self._has_active_event(detected_type):
                    # Create event
                    # We use a custom create method or just call the specific ones
                    # Let's map to existing create methods
                    new_event = None
                    if detected_type == EventType.THUNDERSTORM: new_event = self._create_thunderstorm(severity)
                    elif detected_type == EventType.TORNADO_WARNING: new_event = self._create_tornado_warning(severity)
                    elif detected_type == EventType.HURRICANE: new_event = self._create_hurricane(severity)
                    elif detected_type == EventType.FLASH_FLOOD: new_event = self._create_flash_flood(severity)
                    elif detected_type == EventType.HEATWAVE: new_event = self._create_heatwave(severity)
                    elif detected_type == EventType.COLD_SNAP: new_event = self._create_cold_snap(severity)
                    elif detected_type == EventType.BLIZZARD: new_event = self._create_blizzard(severity)
                    elif detected_type == EventType.WINDSTORM: new_event = self._create_windstorm(severity)
                    elif detected_type == EventType.DUST_STORM: new_event = self._create_dust_storm(severity)
                    
                    if new_event:
                        # Override description with actual alert info (truncated)
                        new_event.description = f"NOAA Alert: {alert.get('event')}"
                        new_event.warning_issued = True
                        # Extend duration for real alerts? Let's stick to defaults for now or maybe 1 hour minimum
                        new_event.duration = max(new_event.duration, 3600)
                        
                        new_events.append(new_event)
        
        # Check each event type
        # Apply frequency multiplier to thresholds for gameplay mode
        freq_adj = 1.0 / self.frequency_multiplier  # Lower thresholds = more frequent events
        
        # 1. THUNDERSTORM
        if not self._has_active_event(EventType.THUNDERSTORM):
            if game_state.weather_code >= 95 or getattr(game_state, 'cape', 0) > (1500 * freq_adj):
                severity = self._determine_thunderstorm_severity(game_state)
                event = self._create_thunderstorm(severity)
                new_events.append(event)
        
        # 2. HEATWAVE
        if not self._has_active_event(EventType.HEATWAVE):
            if game_state.temp_c > (35 * freq_adj):
                # Track duration
                if self.heatwave_start_time == 0:
                    self.heatwave_start_time = current_time
                elif current_time - self.heatwave_start_time > (7200 * freq_adj):  # 2 hours
                    severity = self._determine_heatwave_severity(game_state)
                    event = self._create_heatwave(severity)
                    new_events.append(event)
                    self.heatwave_start_time = 0
            else:
                self.heatwave_start_time = 0
        
        # 3. BLIZZARD
        if not self._has_active_event(EventType.BLIZZARD):
            is_heavy_snow = game_state.weather_code in [73, 75, 77, 85, 86]
            if is_heavy_snow and game_state.wind_speed > (15 * freq_adj):
                severity = self._determine_blizzard_severity(game_state)
                event = self._create_blizzard(severity)
                new_events.append(event)
        
        # 4. WINDSTORM
        if not self._has_active_event(EventType.WINDSTORM):
            if game_state.wind_speed > (25 * freq_adj):
                severity = self._determine_windstorm_severity(game_state)
                event = self._create_windstorm(severity)
                new_events.append(event)
        
        # 5. DROUGHT (requires 24+ hours without rain)
        if not self._has_active_event(EventType.DROUGHT):
            hours_since_rain = (current_time - self.last_rain_time) / 3600
            if hours_since_rain > (24 * freq_adj) and game_state.rain_vol == 0:
                severity = EventSeverity.MODERATE
                if hours_since_rain > (72 * freq_adj):
                    severity = EventSeverity.SEVERE
                event = self._create_drought(severity)
                new_events.append(event)
        
        # 6. DUST STORM
        if not self._has_active_event(EventType.DUST_STORM):
            low_visibility = getattr(game_state, 'visibility', 10000) < (2000 * freq_adj)
            high_wind = game_state.wind_speed > (15 * freq_adj)
            if low_visibility and high_wind and game_state.rain_vol == 0:
                severity = EventSeverity.MODERATE
                event = self._create_dust_storm(severity)
                new_events.append(event)
        
        # 7. FOG
        if not self._has_active_event(EventType.FOG):
            low_visibility = getattr(game_state, 'visibility', 10000) < (1000 * freq_adj)
            high_humidity = game_state.humidity > (90 * freq_adj)
            if low_visibility and high_humidity:
                severity = EventSeverity.MINOR
                event = self._create_fog(severity)
                new_events.append(event)
        
        # 8. TORNADO WARNING (very rare)
        if not self._has_active_event(EventType.TORNADO_WARNING):
            extreme_cape = getattr(game_state, 'cape', 0) > (3000 * freq_adj)
            if extreme_cape and game_state.weather_code >= 95:
                # Very rare, only with multiplier or extreme conditions
                if self.frequency_multiplier > 1.2 or extreme_cape > 5000:
                    severity = EventSeverity.EXTREME
                    event = self._create_tornado_warning(severity)
                    new_events.append(event)
        
        # 9. HURRICANE (coastal + extreme conditions)
        if not self._has_active_event(EventType.HURRICANE):
            extreme_wind = game_state.wind_speed > (33 * freq_adj)  # Hurricane force
            extreme_rain = game_state.rain_vol > (50 * freq_adj)
            if extreme_wind and extreme_rain:
                severity = EventSeverity.EXTREME
                event = self._create_hurricane(severity)
                new_events.append(event)
        
        # 10. COLD SNAP
        if not self._has_active_event(EventType.COLD_SNAP):
            if game_state.temp_c < (-10 * freq_adj):
                if self.cold_start_time == 0:
                    self.cold_start_time = current_time
                elif current_time - self.cold_start_time > (3600 * freq_adj):  # 1 hour
                    severity = self._determine_cold_snap_severity(game_state)
                    event = self._create_cold_snap(severity)
                    new_events.append(event)
                    self.cold_start_time = 0
            else:
                self.cold_start_time = 0
        
        # 11. FLASH FLOOD
        if not self._has_active_event(EventType.FLASH_FLOOD):
            extreme_rain = game_state.rain_vol > (100 * freq_adj)  # 100mm/h+
            if extreme_rain:
                severity = EventSeverity.SEVERE
                event = self._create_flash_flood(severity)
                new_events.append(event)
        
        # 12. AURORA (rare bonus, high latitude + night + low solar activity)
        if not self._has_active_event(EventType.AURORA):
            high_latitude = abs(game_state.lat) > (60 * freq_adj)
            is_night = not game_state.is_day
            if high_latitude and is_night:
                # Very rare without multiplier
                import random
                chance = 0.001 * self.frequency_multiplier
                if random.random() < chance:
                    severity = EventSeverity.MINOR
                    event = self._create_aurora(severity)
                    new_events.append(event)
        
        return new_events
    
    def update(self, game_state, dt):
        """Update active events and check for new ones."""
        # Remove expired events
        expired = []
        for event in self.active_events:
            if not event.is_active():
                expired.append(event)
                self.event_history.append(event)
        
        for event in expired:
            self.active_events.remove(event)
        
        # Trim history
        if len(self.event_history) > self.max_history:
            self.event_history = self.event_history[-self.max_history:]
        
        # Check for new events
        new_events = self.check_for_events(game_state)
        if new_events:
            for event in new_events:
                self.active_events.append(event)
                # print(f"Weather Event: {event.event_type.value.title()} ({event.severity.value})")
                # print(f"  {event.description}")
    
    def get_active_modifiers(self) -> Dict[str, float]:
        """Get combined modifiers from all active events."""
        if not self.active_events:
            return {"wind": 1.0, "solar": 1.0, "hydro": 1.0}
        
        # Multiply all modifiers together
        wind_mod = 1.0
        solar_mod = 1.0
        hydro_mod = 1.0
        
        for event in self.active_events:
            wind_mod *= event.wind_modifier
            solar_mod *= event.solar_modifier
            hydro_mod *= event.hydro_modifier
        
        return {
            "wind": wind_mod,
            "solar": solar_mod,
            "hydro": hydro_mod
        }
    
    def _has_active_event(self, event_type: EventType) -> bool:
        """Check if an event of this type is already active."""
        return any(e.event_type == event_type for e in self.active_events)
    
    def get_event_by_type(self, event_type: EventType) -> Optional[WeatherEvent]:
        """Get active event by type."""
        for event in self.active_events:
            if event.event_type == event_type:
                return event
        return None
    
    # Event creation methods
    
    def _determine_thunderstorm_severity(self, state) -> EventSeverity:
        cape = getattr(state, 'cape', 0)
        if cape > 4000 or state.weather_code >= 99:
            return EventSeverity.EXTREME
        elif cape > 2500 or state.weather_code >= 97:
            return EventSeverity.SEVERE
        elif cape > 1500:
            return EventSeverity.MODERATE
        return EventSeverity.MINOR
    
    def _create_thunderstorm(self, severity: EventSeverity) -> WeatherEvent:
        modifiers = {
            EventSeverity.MINOR: (1.2, 0.8, 1.3),
            EventSeverity.MODERATE: (1.3, 0.7, 1.5),
            EventSeverity.SEVERE: (1.4, 0.5, 1.8),
            EventSeverity.EXTREME: (1.5, 0.3, 2.0)
        }
        wind_mod, solar_mod, hydro_mod = modifiers[severity]
        
        durations = {
            EventSeverity.MINOR: 1800,    # 30 min
            EventSeverity.MODERATE: 3600,  # 1 hour
            EventSeverity.SEVERE: 5400,    # 1.5 hours
            EventSeverity.EXTREME: 7200    # 2 hours
        }
        
        return WeatherEvent(
            uid=f"thunderstorm_{int(time.time())}",
            event_type=EventType.THUNDERSTORM,
            severity=severity,
            start_time=time.time(),
            duration=durations[severity],
            description=f"Thunderstorm activity detected! Lightning, heavy rain, and strong winds.",
            wind_modifier=wind_mod,
            solar_modifier=solar_mod,
            hydro_modifier=hydro_mod
        )
    
    def _determine_heatwave_severity(self, state) -> EventSeverity:
        temp = state.temp_c
        if temp > 45:
            return EventSeverity.EXTREME
        elif temp > 40:
            return EventSeverity.SEVERE
        elif temp > 37:
            return EventSeverity.MODERATE
        return EventSeverity.MINOR
    
    def _create_heatwave(self, severity: EventSeverity) -> WeatherEvent:
        modifiers = {
            EventSeverity.MINOR: (0.9, 1.2, 0.8),
            EventSeverity.MODERATE: (0.8, 1.4, 0.7),
            EventSeverity.SEVERE: (0.7, 1.6, 0.6),
            EventSeverity.EXTREME: (0.6, 1.8, 0.5)
        }
        wind_mod, solar_mod, hydro_mod = modifiers[severity]
        
        return WeatherEvent(
            uid=f"heatwave_{int(time.time())}",
            event_type=EventType.HEATWAVE,
            severity=severity,
            start_time=time.time(),
            duration=14400,  # 4 hours
            description=f"Extreme heat warning! Solar panels boosted but overall efficiency reduced.",
            wind_modifier=wind_mod,
            solar_modifier=solar_mod,
            hydro_modifier=hydro_mod
        )
    
    def _determine_blizzard_severity(self, state) -> EventSeverity:
        wind = state.wind_speed
        if wind > 30:
            return EventSeverity.EXTREME
        elif wind > 25:
            return EventSeverity.SEVERE
        elif wind > 20:
            return EventSeverity.MODERATE
        return EventSeverity.MINOR
    
    def _create_blizzard(self, severity: EventSeverity) -> WeatherEvent:
        modifiers = {
            EventSeverity.MINOR: (0.8, 0.5, 1.1),
            EventSeverity.MODERATE: (0.7, 0.4, 1.2),
            EventSeverity.SEVERE: (0.5, 0.2, 1.3),
            EventSeverity.EXTREME: (0.3, 0.1, 1.5)
        }
        wind_mod, solar_mod, hydro_mod = modifiers[severity]
        
        return WeatherEvent(
            uid=f"blizzard_{int(time.time())}",
            event_type=EventType.BLIZZARD,
            severity=severity,
            start_time=time.time(),
            duration=10800,  # 3 hours
            description=f"Blizzard conditions! Heavy snow and wind reducing visibility.",
            wind_modifier=wind_mod,
            solar_modifier=solar_mod,
            hydro_modifier=hydro_mod
        )
    
    def _determine_windstorm_severity(self, state) -> EventSeverity:
        wind = state.wind_speed
        if wind > 40:
            return EventSeverity.EXTREME
        elif wind > 35:
            return EventSeverity.SEVERE
        elif wind > 30:
            return EventSeverity.MODERATE
        return EventSeverity.MINOR
    
    def _create_windstorm(self, severity: EventSeverity) -> WeatherEvent:
        modifiers = {
            EventSeverity.MINOR: (1.4, 0.9, 1.0),
            EventSeverity.MODERATE: (1.6, 0.8, 1.0),
            EventSeverity.SEVERE: (1.8, 0.7, 1.0),
            EventSeverity.EXTREME: (2.0, 0.6, 1.0)
        }
        wind_mod, solar_mod, hydro_mod = modifiers[severity]
        
        return WeatherEvent(
            uid=f"windstorm_{int(time.time())}",
            event_type=EventType.WINDSTORM,
            severity=severity,
            start_time=time.time(),
            duration=5400,  # 1.5 hours
            description=f"High winds detected! Turbines boosted but solar panels affected.",
            wind_modifier=wind_mod,
            solar_modifier=solar_mod,
            hydro_modifier=hydro_mod
        )
    
    def _create_drought(self, severity: EventSeverity) -> WeatherEvent:
        modifiers = {
            EventSeverity.MODERATE: (1.0, 1.1, 0.3),
            EventSeverity.SEVERE: (1.0, 1.2, 0.1),
        }
        wind_mod, solar_mod, hydro_mod = modifiers.get(severity, (1.0, 1.0, 0.5))
        
        return WeatherEvent(
            uid=f"drought_{int(time.time())}",
            event_type=EventType.DROUGHT,
            severity=severity,
            start_time=time.time(),
            duration=86400,  # 24 hours
            description=f"Drought conditions! No rainfall, hydro collectors severely impacted.",
            wind_modifier=wind_mod,
            solar_modifier=solar_mod,
            hydro_modifier=hydro_mod
        )
    
    def _create_dust_storm(self, severity: EventSeverity) -> WeatherEvent:
        return WeatherEvent(
            uid=f"dust_storm_{int(time.time())}",
            event_type=EventType.DUST_STORM,
            severity=severity,
            start_time=time.time(),
            duration=7200,  # 2 hours
            description=f"Dust storm reducing visibility! Solar panels heavily affected.",
            wind_modifier=1.2,
            solar_modifier=0.4,
            hydro_modifier=0.8
        )
    
    def _create_fog(self, severity: EventSeverity) -> WeatherEvent:
        return WeatherEvent(
            uid=f"fog_{int(time.time())}",
            event_type=EventType.FOG,
            severity=severity,
            start_time=time.time(),
            duration=5400,  # 1.5 hours
            description=f"Dense fog! Low visibility reducing solar efficiency.",
            wind_modifier=0.8,
            solar_modifier=0.6,
            hydro_modifier=1.1
        )
    
    def _create_tornado_warning(self, severity: EventSeverity) -> WeatherEvent:
        return WeatherEvent(
            uid=f"tornado_{int(time.time())}",
            event_type=EventType.TORNADO_WARNING,
            severity=severity,
            start_time=time.time(),
            duration=1800,  # 30 min
            description=f"TORNADO WARNING! All machines offline for safety!",
            wind_modifier=0.0,
            solar_modifier=0.0,
            hydro_modifier=0.0
        )
    
    def _create_hurricane(self, severity: EventSeverity) -> WeatherEvent:
        return WeatherEvent(
            uid=f"hurricane_{int(time.time())}",
            event_type=EventType.HURRICANE,
            severity=severity,
            start_time=time.time(),
            duration=21600,  # 6 hours
            description=f"HURRICANE! Extreme wind and rain! Massive hydro boost but high risk!",
            wind_modifier=0.5,
            solar_modifier=0.2,
            hydro_modifier=2.5
        )
    
    def _determine_cold_snap_severity(self, state) -> EventSeverity:
        temp = state.temp_c
        if temp < -30:
            return EventSeverity.EXTREME
        elif temp < -20:
            return EventSeverity.SEVERE
        elif temp < -15:
            return EventSeverity.MODERATE
        return EventSeverity.MINOR
    
    def _create_cold_snap(self, severity: EventSeverity) -> WeatherEvent:
        modifiers = {
            EventSeverity.MINOR: (0.9, 0.8, 0.9),
            EventSeverity.MODERATE: (0.8, 0.7, 0.8),
            EventSeverity.SEVERE: (0.7, 0.6, 0.7),
            EventSeverity.EXTREME: (0.5, 0.4, 0.6)
        }
        wind_mod, solar_mod, hydro_mod = modifiers[severity]
        
        return WeatherEvent(
            uid=f"cold_snap_{int(time.time())}",
            event_type=EventType.COLD_SNAP,
            severity=severity,
            start_time=time.time(),
            duration=14400,  # 4 hours
            description=f"Extreme cold! All systems impacted by freezing temperatures.",
            wind_modifier=wind_mod,
            solar_modifier=solar_mod,
            hydro_modifier=hydro_mod
        )
    
    def _create_flash_flood(self, severity: EventSeverity) -> WeatherEvent:
        return WeatherEvent(
            uid=f"flash_flood_{int(time.time())}",
            event_type=EventType.FLASH_FLOOD,
            severity=severity,
            start_time=time.time(),
            duration=3600,  # 1 hour
            description=f"FLASH FLOOD! Extreme rainfall! Massive water collection!",
            wind_modifier=0.7,
            solar_modifier=0.3,
            hydro_modifier=3.0
        )
    
    def _create_aurora(self, severity: EventSeverity) -> WeatherEvent:
        return WeatherEvent(
            uid=f"aurora_{int(time.time())}",
            event_type=EventType.AURORA,
            severity=severity,
            start_time=time.time(),
            duration=10800,  # 3 hours
            description=f"Aurora Borealis! Rare atmospheric phenomenon boosting energy production!",
            wind_modifier=1.2,
            solar_modifier=1.5,
            hydro_modifier=1.1
        )
    
    def get_stats(self) -> Dict:
        """Get statistics about events."""
        # Check for specific achievements in history
        extreme_experienced = any(e.severity == EventSeverity.EXTREME for e in self.event_history)
        aurora_seen = any(e.event_type == EventType.AURORA for e in self.event_history)
        
        return {
            "active_count": len(self.active_events),
            "total_experienced": len(self.event_history),
            "frequency_multiplier": self.frequency_multiplier,
            "extreme_experienced": extreme_experienced,
            "aurora_seen": aurora_seen
        }
