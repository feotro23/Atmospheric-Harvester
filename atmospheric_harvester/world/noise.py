import random
import math

class PerlinNoise:
    def __init__(self, seed=None):
        if seed:
            random.seed(seed)
        self.permutation = [i for i in range(256)]
        random.shuffle(self.permutation)
        self.permutation += self.permutation
        
    def _fade(self, t):
        return t * t * t * (t * (t * 6 - 15) + 10)
        
    def _lerp(self, t, a, b):
        return a + t * (b - a)
        
    def _grad(self, hash, x, y, z):
        h = hash & 15
        u = x if h < 8 else y
        v = y if h < 4 else (x if h == 12 or h == 14 else z)
        return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)
        
    def noise(self, x, y, z=0):
        X = int(math.floor(x)) & 255
        Y = int(math.floor(y)) & 255
        Z = int(math.floor(z)) & 255
        
        x -= math.floor(x)
        y -= math.floor(y)
        z -= math.floor(z)
        
        u = self._fade(x)
        v = self._fade(y)
        w = self._fade(z)
        
        A = self.permutation[X] + Y
        AA = self.permutation[A] + Z
        AB = self.permutation[A + 1] + Z
        B = self.permutation[X + 1] + Y
        BA = self.permutation[B] + Z
        BB = self.permutation[B + 1] + Z
        
        return self._lerp(w, self._lerp(v, self._lerp(u, self._grad(self.permutation[AA], x, y, z),
                                                       self._grad(self.permutation[BA], x - 1, y, z)),
                                       self._lerp(u, self._grad(self.permutation[AB], x, y - 1, z),
                                                       self._grad(self.permutation[BB], x - 1, y - 1, z))),
                         self._lerp(v, self._lerp(u, self._grad(self.permutation[AA + 1], x, y, z - 1),
                                                       self._grad(self.permutation[BA + 1], x - 1, y, z - 1)),
                                       self._lerp(u, self._grad(self.permutation[AB + 1], x, y - 1, z - 1),
                                                       self._grad(self.permutation[BB + 1], x - 1, y - 1, z - 1))))
