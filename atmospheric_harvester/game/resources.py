class ResourceManager:
    """
    Manages game resources (Energy, Water, Biomass, Credits).
    Tracks current amounts, capacities, and lifetime totals.
    """
    def __init__(self):
        # Current Resources
        self.energy = 100.0  # kWh
        self.water = 50.0    # Liters
        self.biomass = 10.0  # kg
        
        # Capacity
        self.energy_capacity = 1000.0
        self.water_capacity = 500.0
        self.biomass_capacity = 100.0
        
        # Lifetime Totals (for missions/achievements)
        self.total_energy_generated = 0.0
        self.total_water_generated = 0.0
        self.total_biomass_generated = 0.0
        
        # Economy
        self.credits = 0
        self.total_credits_earned = 0
        
    def add_energy(self, amount):
        """Add energy, capping at capacity and tracking lifetime total."""
        if amount > 0:
            self.total_energy_generated += amount
        self.energy = min(self.energy + amount, self.energy_capacity)
        
    def consume_energy(self, amount):
        """Consume energy if available. Returns True if successful."""
        if self.energy >= amount:
            self.energy -= amount
            return True
        return False
        
    def add_water(self, amount):
        """Add water, capping at capacity and tracking lifetime total."""
        if amount > 0:
            self.total_water_generated += amount
        self.water = min(self.water + amount, self.water_capacity)
        
    def consume_water(self, amount):
        """Consume water if available. Returns True if successful."""
        if self.water >= amount:
            self.water -= amount
            return True
        return False
        
    def add_biomass(self, amount):
        """Add biomass, capping at capacity and tracking lifetime total."""
        if amount > 0:
            self.total_biomass_generated += amount
        self.biomass = min(self.biomass + amount, self.biomass_capacity)
        
    def consume_biomass(self, amount):
        """Consume biomass if available. Returns True if successful."""
        if self.biomass >= amount:
            self.biomass -= amount
            return True
        return False

    def modify_capacity(self, resource_type, amount):
        """Modify the maximum capacity of a resource."""
        if resource_type == "energy":
            self.energy_capacity += amount
        elif resource_type == "water":
            self.water_capacity += amount
        elif resource_type == "biomass":
            self.biomass_capacity += amount

    def add_credits(self, amount):
        """Add credits and track lifetime total."""
        if amount > 0:
            self.total_credits_earned += amount
            self.credits += amount
            
    def consume_credits(self, amount):
        """Consume credits if available. Returns True if successful."""
        if self.credits >= amount:
            self.credits -= amount
            return True
        return False
