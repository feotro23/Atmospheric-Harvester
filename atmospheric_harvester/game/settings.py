class SettingsManager:
    def __init__(self):
        # Default settings
        self.system = "Metric"  # "Metric" or "Imperial"
        self.volume = 0.5  # 0.0 to 1.0
        
    def toggle_system(self):
        """Toggle between Metric and Imperial systems."""
        self.system = "Imperial" if self.system == "Metric" else "Metric"
        
    def set_volume(self, volume):
        """Set volume level (0.0 to 1.0)."""
        self.volume = max(0.0, min(1.0, volume))
        
    def get_measurement_display(self, value, type):
        """
        Convert value to display string based on system and type.
        Types: 'temp' (C), 'speed' (m/s), 'distance' (km), 'length_m' (m), 'length_cm' (cm), 'length_mm' (mm)
        """
        if self.system == "Imperial":
            if type == "temp": # C -> F
                val = (value * 9/5) + 32
                return f"{val:.1f}°F"
            elif type == "speed": # m/s -> mph
                val = value * 2.23694
                return f"{val:.1f} mph"
            elif type == "speed_kmh": # km/h -> mph
                val = value * 0.621371
                return f"{val:.1f} mph"
            elif type == "distance": # km -> miles
                val = value * 0.621371
                return f"{val:.1f} mi"
            elif type == "length_m": # m -> ft
                val = value * 3.28084
                return f"{val:.1f} ft"
            elif type == "length_cm": # cm -> in
                val = value * 0.393701
                return f"{val:.1f} in"
            elif type == "length_mm": # mm -> in
                val = value * 0.0393701
                return f"{val:.2f} in"
                
        # Metric Defaults
        if type == "temp": return f"{value:.1f}°C"
        elif type == "speed": return f"{value:.1f} m/s"
        elif type == "speed_kmh": return f"{value:.1f} km/h"
        elif type == "distance": return f"{value:.1f} km"
        elif type == "length_m": return f"{value:.1f} m"
        elif type == "length_cm": return f"{value:.1f} cm"
        elif type == "length_mm": return f"{value:.1f} mm"
        
        return str(value)

    def to_dict(self):
        return {
            "system": self.system,
            "volume": self.volume
        }
        
    def from_dict(self, data):
        self.system = data.get("system", "Metric")
        self.volume = data.get("volume", 0.5)
