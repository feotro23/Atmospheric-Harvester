from .noise import PerlinNoise

class Tile:
    def __init__(self, x, y, biome, height, moisture):
        self.x = x
        self.y = y
        self.biome = biome
        self.height = height
        self.moisture = moisture
        self.color = (0, 0, 0)
        self._set_color()
        
    def _set_color(self):
        if self.biome == "WATER":
            self.color = (50, 100, 200)
        elif self.biome == "SAND":
            self.color = (240, 240, 140)
        elif self.biome == "GRASS":
            self.color = (50, 200, 50)
        elif self.biome == "FOREST":
            self.color = (20, 140, 20)
        elif self.biome == "ROCK":
            self.color = (120, 120, 120)
        elif self.biome == "SNOW":
            self.color = (240, 240, 255)

class TerrainGenerator:
    def __init__(self, width, height, seed=None):
        self.width = width
        self.height = height
        self.noise_gen = PerlinNoise(seed)
        self.moisture_gen = PerlinNoise(seed + 1 if seed else None)
        self.map = []
        
    def generate(self, scale=0.1):
        self.map = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                # Generate Height (-1 to 1)
                h = self.noise_gen.noise(x * scale, y * scale)
                # Generate Moisture (-1 to 1)
                m = self.moisture_gen.noise(x * scale, y * scale)
                
                biome = self._get_biome(h, m)
                row.append(Tile(x, y, biome, h, m))
            self.map.append(row)
        return self.map
        
    def _get_biome(self, h, m):
        if h < -0.2:
            return "WATER"
        elif h < 0.0:
            return "SAND"
        elif h > 0.6:
            if m > 0.2:
                return "SNOW"
            else:
                return "ROCK"
        else:
            if m < -0.3:
                return "SAND"
            elif m < 0.2:
                return "GRASS"
            else:
                return "FOREST"
