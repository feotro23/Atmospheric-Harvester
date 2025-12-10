import math

class Location:
    def __init__(self, name, lat, lon):
        self.name = name
        self.lat = lat
        self.lon = lon

class TravelManager:
    def __init__(self):
        self.locations = [
            # North America
            Location("New York, USA", 40.7128, -74.0060),
            Location("Los Angeles, USA", 34.0522, -118.2437),
            Location("Chicago, USA", 41.8781, -87.6298),
            Location("Houston, USA", 29.7604, -95.3698),
            Location("Miami, USA", 25.7617, -80.1918),
            Location("Toronto, Canada", 43.6532, -79.3832),
            Location("Vancouver, Canada", 49.2827, -123.1207),
            Location("Mexico City, Mexico", 19.4326, -99.1332),
            
            # South America
            Location("São Paulo, Brazil", -23.5505, -46.6333),
            Location("Rio de Janeiro, Brazil", -22.9068, -43.1729),
            Location("Buenos Aires, Argentina", -34.6037, -58.3816),
            Location("Lima, Peru", -12.0464, -77.0428),
            Location("Bogotá, Colombia", 4.7110, -74.0721),
            Location("Santiago, Chile", -33.4489, -70.6693),
            
            # Europe
            Location("London, UK", 51.5074, -0.1278),
            Location("Paris, France", 48.8566, 2.3522),
            Location("Berlin, Germany", 52.5200, 13.4050),
            Location("Madrid, Spain", 40.4168, -3.7038),
            Location("Rome, Italy", 41.9028, 12.4964),
            Location("Amsterdam, Netherlands", 52.3676, 4.9041),
            Location("Brussels, Belgium", 50.8503, 4.3517),
            Location("Vienna, Austria", 48.2082, 16.3738),
            Location("Stockholm, Sweden", 59.3293, 18.0686),
            Location("Copenhagen, Denmark", 55.6761, 12.5683),
            Location("Oslo, Norway", 59.9139, 10.7522),
            Location("Helsinki, Finland", 60.1699, 24.9384),
            Location("Warsaw, Poland", 52.2297, 21.0122),
            Location("Prague, Czech Republic", 50.0755, 14.4378),
            Location("Budapest, Hungary", 47.4979, 19.0402),
            Location("Athens, Greece", 37.9838, 23.7275),
            Location("Lisbon, Portugal", 38.7223, -9.1393),
            Location("Dublin, Ireland", 53.3498, -6.2603),
            Location("Reykjavik, Iceland", 64.1466, -21.9426),
            Location("Moscow, Russia", 55.7558, 37.6173),
            
            # Asia
            Location("Tokyo, Japan", 35.6762, 139.6503),
            Location("Beijing, China", 39.9042, 116.4074),
            Location("Shanghai, China", 31.2304, 121.4737),
            Location("Hong Kong", 22.3193, 114.1694),
            Location("Seoul, South Korea", 37.5665, 126.9780),
            Location("Bangkok, Thailand", 13.7563, 100.5018),
            Location("Singapore", 1.3521, 103.8198),
            Location("Kuala Lumpur, Malaysia", 3.1390, 101.6869),
            Location("Jakarta, Indonesia", -6.2088, 106.8456),
            Location("Manila, Philippines", 14.5995, 120.9842),
            Location("Hanoi, Vietnam", 21.0285, 105.8542),
            Location("Mumbai, India", 19.0760, 72.8777),
            Location("New Delhi, India", 28.6139, 77.2090),
            Location("Bangalore, India", 12.9716, 77.5946),
            Location("Dubai, UAE", 25.2048, 55.2708),
            Location("Istanbul, Turkey", 41.0082, 28.9784),
            Location("Tel Aviv, Israel", 32.0853, 34.7818),
            
            # Africa
            Location("Cairo, Egypt", 30.0444, 31.2357),
            Location("Lagos, Nigeria", 6.5244, 3.3792),
            Location("Johannesburg, South Africa", -26.2041, 28.0473),
            Location("Cape Town, South Africa", -33.9249, 18.4241),
            Location("Nairobi, Kenya", -1.2921, 36.8219),
            Location("Casablanca, Morocco", 33.5731, -7.5898),
            
            # Oceania
            Location("Sydney, Australia", -33.8688, 151.2093),
            Location("Melbourne, Australia", -37.8136, 144.9631),
            Location("Brisbane, Australia", -27.4698, 153.0251),
            Location("Perth, Australia", -31.9505, 115.8605),
            Location("Auckland, New Zealand", -36.8485, 174.7633),
            Location("Wellington, New Zealand", -41.2865, 174.7762),
        ]
        self.base_cost_per_km = 0.1

    def get_distance(self, loc1, loc2):
        # Haversine formula
        R = 6371 # Earth radius in km
        dlat = math.radians(loc2.lat - loc1.lat)
        dlon = math.radians(loc2.lon - loc1.lon)
        a = math.sin(dlat/2) * math.sin(dlat/2) + \
            math.cos(math.radians(loc1.lat)) * math.cos(math.radians(loc2.lat)) * \
            math.sin(dlon/2) * math.sin(dlon/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c

    def calculate_cost(self, current_lat, current_lon, target_loc):
        current = Location("Current", current_lat, current_lon)
        dist = self.get_distance(current, target_loc)
        return dist * self.base_cost_per_km

    def can_travel(self, game_state, target_loc):
        cost = self.calculate_cost(game_state.lat, game_state.lon, target_loc)
        return game_state.resources.energy >= cost

    def travel(self, game_state, target_loc):
        cost = self.calculate_cost(game_state.lat, game_state.lon, target_loc)
        if game_state.resources.consume_energy(cost):
            # Track for missions (if this is a new location)
            if hasattr(game_state, '_locations_visited'):
                game_state._locations_visited += 1
            
            game_state.lat = target_loc.lat
            game_state.lon = target_loc.lon
            game_state.location_name = target_loc.name
            # Reset weather data until next fetch
            game_state.weather_data = None 
            return True
        return False
