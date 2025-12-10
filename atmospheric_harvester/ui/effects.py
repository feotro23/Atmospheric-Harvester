import pygame
import random
from .theme import Theme

class Particle:
    def __init__(self, x, y, p_type):
        self.x = x
        self.y = y
        self.p_type = p_type  # 'rain', 'snow', 'cloud'
        
        if p_type == 'rain':
            self.vy = random.uniform(10, 20)
            self.vx = 0 # Will be modified by wind
            self.color = (150, 150, 255)
            self.size = 2
            self.length = random.uniform(5, 10)
        elif p_type == 'snow':
            self.vy = random.uniform(1, 3)
            self.vx = random.uniform(-1, 1)
            self.color = (220, 220, 220)
            self.size = random.uniform(2, 4)
            self.length = self.size
        
    def update(self, dt, wind_speed):
        # Wind effect: 1 m/s = 1 pixel/s drift? Let's scale it.
        # Wind speed 50 m/s is huge. Let's say max wind adds 10 px/frame -> 600 px/s.
        # So wind_factor = 10.
        wind_vx = wind_speed * 5.0
        
        self.x += (self.vx + wind_vx) * dt
        self.y += self.vy * 60 * dt # Scale vy to be pixels per second roughly
        
class ParticleSystem:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.particles = []
        self.max_particles = 500
        
    def update(self, dt, game_state):
        # Spawn new particles based on weather
        # Rain
        if game_state.rain_vol > 0:
            # rain_vol is mm/h. 
            # >0.5 is light, >4 is heavy.
            spawn_rate = int(game_state.rain_vol * 5)
            self._spawn('rain', spawn_rate)
            
        # Snow (if temp < 0 and clouds/precip condition met)
        # Simplified: if temp < 0 and rain_vol > 0, treat as snow
        if game_state.temp_c < 0 and game_state.rain_vol > 0:
            spawn_rate = int(game_state.rain_vol * 5)
            self._spawn('snow', spawn_rate)
            
        # Always spawn a few "dust/air" particles if windy? Maybe later.
        
        # Update existing
        wind = game_state.wind_speed
        # Direction? We only have speed in state.wind_speed. 
        # We have wind_deg in raw data but let's just assume wind blows right for now or use simple logic.
        # Let's use a fixed direction for visual simplicity or random drift if speed is low.
        
        for p in self.particles:
            p.update(dt, wind)
            
        # Remove out of bounds
        self.particles = [p for p in self.particles if self._is_in_bounds(p)]
        
    def _spawn(self, p_type, count):
        if len(self.particles) >= self.max_particles:
            return
            
        for _ in range(count):
            # Spawn at top, random x
            # Also spawn slightly off-screen left if wind is blowing right
            x = random.randint(-100, self.width)
            y = -20
            self.particles.append(Particle(x, y, p_type))
            
    def _is_in_bounds(self, p):
        return -200 < p.x < self.width + 200 and p.y < self.height + 20

    def render(self, screen):
        for p in self.particles:
            if p.p_type == 'rain':
                end_x = p.x # Rain falls straight-ish relative to wind
                end_y = p.y + p.length
                # Slant based on wind?
                # simple line
                pygame.draw.line(screen, p.color, (p.x, p.y), (p.x, end_y), 1)
            elif p.p_type == 'snow':
                pygame.draw.circle(screen, p.color, (p.x, p.y), p.size)
