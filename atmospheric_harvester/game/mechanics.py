import math

class Mechanics:
    @staticmethod
    def calculate_kinetic_energy(wind_speed, num_turbines, efficiency=1.0, cut_in=0.1):
        """
        E_k = N * Eff * max(0, V - V_cutin)^1.5
        """
        effective_wind = max(0, wind_speed - cut_in)
        # Reduced multiplier from implicit 1.0 to 0.5 to balance high wind speeds
        return num_turbines * efficiency * (effective_wind ** 1.5) * 0.5

    @staticmethod
    def calculate_hydro_energy(rain_volume, humidity, num_collectors, storm_multiplier=1.0):
        """
        E_h = (N * H) + (R * Mult)
        Note: rain_volume is usually mm/h. We might want to scale it.
        Humidity is %.
        """
        # Passive humidity collection (very small)
        passive = num_collectors * (humidity / 100.0) * 0.2 # Increased passive slightly
        
        # Active rain collection
        # Rain volume can be high, so we scale it down a bit to match other sources
        active = rain_volume * storm_multiplier * 2.0 
        
        return passive + active

    @staticmethod
    def calculate_solar_energy(temp_c, clouds_percent, is_day, num_panels, radiation=0.0):
        """
        Calculate solar energy production.
        
        Args:
            temp_c (float): Ambient temperature in Celsius.
            clouds_percent (float): Cloud cover percentage (0-100).
            is_day (bool): Whether it is day time.
            num_panels (int): Number of solar panels.
            radiation (float): Shortwave radiation (W/m^2). If 0, falls back to cloud model.
            
        Returns:
            float: Energy produced in Watts (or game units).
        """
        if not is_day:
            return 0.0
            
        # Base panel efficiency (e.g., 20% efficient, 1.6m^2 panel -> ~320W peak)
        # Let's assume 1 game unit = 1 Watt for simplicity, or scale it.
        # If radiation is available (W/m^2), use it directly.
        if radiation > 0:
            # E = Area * Radiation * Efficiency * Performance_Ratio
            # Area per panel = 1.6 m^2
            # Efficiency = 0.20
            # PR = 0.75 (losses)
            # Temp Coeff = -0.5% per degree over 25C
            
            # Scaling down raw watts to game units (e.g. / 10)
            base_output = (radiation * 1.6 * 0.20 * 0.75) / 10.0
            
            # Temperature correction
            # Efficiency drops as temp rises above 25C
            temp_diff = temp_c - 25
            temp_factor = 1.0 - (temp_diff * 0.005)
            
            return max(0.0, num_panels * base_output * temp_factor)
        
        # Fallback model if no radiation data
        cloud_factor = 1.0 - (clouds_percent / 100.0)
        # Simple estimation: Peak sun = 1000 W/m^2
        estimated_rad = 1000.0 * cloud_factor
        
        # Same formula as above
        base_output = (estimated_rad * 1.6 * 0.20 * 0.75) / 10.0
        temp_diff = temp_c - 25
        temp_factor = 1.0 - (temp_diff * 0.005)
        
        return max(0.0, num_panels * base_output * temp_factor)

    @staticmethod
    def calculate_harvest_efficiency(visibility):
        """
        Calculate harvest efficiency multiplier based on visibility.
        
        Args:
            visibility (float): Visibility in meters.
            
        Returns:
            float: Efficiency multiplier (0.0 to 1.0).
        """
        # Max efficiency at > 10km visibility
        if visibility >= 10000:
            return 1.0
            
        # Linear drop off below 10km
        # At 0 visibility, efficiency is 0.2 (can still do some work close up)
        return 0.2 + (0.8 * (visibility / 10000.0))
