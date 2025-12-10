import pygame
import random
import math
from datetime import datetime

class DayNightCycle:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))
        self.surface.set_alpha(255) # Full opacity, we draw the sky
        
    def update(self, game_state):
        # We need to draw the sky gradient based on time.
        # Open-Meteo time is ISO.
        try:
            sunrise_dt = datetime.fromisoformat(game_state.sunrise)
            sunset_dt = datetime.fromisoformat(game_state.sunset)
            now = datetime.now()
            
            now_m = now.hour * 60 + now.minute
            rise_m = sunrise_dt.hour * 60 + sunrise_dt.minute
            set_m = sunset_dt.hour * 60 + sunset_dt.minute
            
            # Normalize time 0-1440
            # Determine phase: Night -> Dawn -> Day -> Dusk -> Night
            
            # Colors (Top, Bottom)
            night_col = ((10, 10, 30), (20, 20, 60))
            dawn_col = ((50, 30, 60), (200, 100, 50))
            day_col = ((100, 200, 255), (200, 230, 255))
            dusk_col = ((50, 20, 60), (200, 100, 50))
            
            current_col = night_col
            
            transition = 60
            
            if now_m < rise_m - transition:
                current_col = night_col
            elif now_m < rise_m:
                t = (now_m - (rise_m - transition)) / transition
                current_col = self._lerp_grad(night_col, dawn_col, t)
            elif now_m < rise_m + transition:
                 t = (now_m - rise_m) / transition
                 current_col = self._lerp_grad(dawn_col, day_col, t)
            elif now_m < set_m - transition:
                current_col = day_col
            elif now_m < set_m:
                t = (now_m - (set_m - transition)) / transition
                current_col = self._lerp_grad(day_col, dusk_col, t)
            elif now_m < set_m + transition:
                t = (now_m - set_m) / transition
                current_col = self._lerp_grad(dusk_col, night_col, t)
            else:
                current_col = night_col
                
            self._draw_gradient(current_col[0], current_col[1])
            
            # Draw Celestial Body
            # Sun/Moon position based on time
            # Arc from Left to Right
            day_len = set_m - rise_m
            if rise_m <= now_m <= set_m:
                # Day (Sun)
                pct = (now_m - rise_m) / day_len
                cx = int(self.width * pct)
                cy = int(self.height * 0.2 + math.sin(pct * math.pi) * -100 + 100) # Arc
                pygame.draw.circle(self.surface, (255, 255, 200), (cx, cy), 40) # Sun
                # Glow
                s = pygame.Surface((100, 100), pygame.SRCALPHA)
                pygame.draw.circle(s, (255, 255, 200, 50), (50, 50), 50)
                self.surface.blit(s, (cx-50, cy-50))
            else:
                # Night (Moon)
                # Map night time to 0-1
                if now_m > set_m:
                    pct = (now_m - set_m) / (1440 - set_m + rise_m)
                else:
                    pct = (now_m + (1440 - set_m)) / (1440 - set_m + rise_m)
                    
                cx = int(self.width * pct)
                cy = int(self.height * 0.2)
                pygame.draw.circle(self.surface, (200, 200, 200), (cx, cy), 30) # Moon
            
        except ValueError:
            self.surface.fill((100, 200, 255)) # Default Day

    def _lerp_grad(self, c1, c2, t):
        top = self._lerp_color(c1[0], c2[0], t)
        bot = self._lerp_color(c1[1], c2[1], t)
        return (top, bot)

    def _lerp_color(self, c1, c2, t):
        return (
            int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t)
        )

    def _draw_gradient(self, top_col, bot_col):
        # Draw simple vertical gradient
        # Optimization: Draw 4px strips? Or just fill?
        # Pygame fill is fast.
        # Let's do 20 steps
        steps = 20
        h_step = self.height // steps
        for i in range(steps):
            t = i / steps
            col = self._lerp_color(top_col, bot_col, t)
            pygame.draw.rect(self.surface, col, (0, i * h_step, self.width, h_step + 1))

    def render(self, screen):
        screen.blit(self.surface, (0,0))

class VectorParticleSystem:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.particles = []
        
    def update(self, dt, game_state):
        # Spawn
        # Rain volume 0-10+
        # If rain_vol is 0, maybe don't spawn, or spawn very few if cloudy?
        # Let's use rain_vol as primary driver.
        
        spawn_count = int(game_state.rain_vol * 2)
        if game_state.weather_code >= 70: # Snow codes
             spawn_count = 5
             
        for _ in range(spawn_count):
            self.particles.append(self._create_particle(game_state))
            
        # Update
        wind_x = game_state.wind_speed * 5 # Scale wind
        
        alive = []
        for p in self.particles:
            p['x'] += (p['vx'] + wind_x) * dt
            p['y'] += p['vy'] * dt
            
            # Wrap x for wind effect? Or just kill?
            # Kill if out of bounds
            if -50 <= p['x'] <= self.width + 50 and 0 <= p['y'] <= self.height:
                alive.append(p)
        self.particles = alive
        
    def _create_particle(self, game_state):
        # Determine type based on temp or weather code
        # Open-Meteo codes: 71, 73, 75 are Snow fall
        is_snow = game_state.weather_code in [71, 73, 75, 77, 85, 86] or game_state.temp_c < 0
        
        # Isometric slant: Rain falls from Top-Left to Bottom-Right
        # So vx should be positive.
        
        return {
            'x': random.randint(-self.width, self.width), # Spawn wider
            'y': -10,
            'vx': random.uniform(10, 20) + (game_state.wind_speed * 2), # Slant + Wind
            'vy': random.uniform(100, 300) if not is_snow else random.uniform(30, 60),
            'color': (200, 200, 255) if not is_snow else (255, 255, 255),
            'is_snow': is_snow
        }

    def render(self, screen):
        for p in self.particles:
            if p['is_snow']:
                pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), 2)
            else:
                # Draw line for rain
                # Length depends on speed
                end_x = p['x'] - (p['vx'] * 0.05) # Trail
                end_y = p['y'] - (p['vy'] * 0.05)
                pygame.draw.line(screen, p['color'], (p['x'], p['y']), (end_x, end_y), 1)

class CloudLayer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.offset_x = 0
        self.generated = False
        
    def generate(self):
        # Simple procedural cloud generation
        # We'll draw a bunch of semi-transparent white circles to simulate clouds
        # This is faster than per-pixel noise in Python
        self.surface.fill((0,0,0,0))
        
        for _ in range(50):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height // 2) # Clouds mostly in top half? No, full screen for top-down view
            y = random.randint(0, self.height)
            r = random.randint(30, 80)
            alpha = random.randint(10, 30)
            
            # Draw blob
            s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 255, 255, alpha), (r, r), r)
            self.surface.blit(s, (x-r, y-r))
            
        self.generated = True
        
    def update(self, dt, game_state):
        if not self.generated:
            self.generate()
            
        # Scroll based on wind
        speed = game_state.wind_speed * 2
        self.offset_x += speed * dt
        if self.offset_x > self.width:
            self.offset_x -= self.width
            
    def render(self, screen):
        # Draw twice for scrolling loop
        screen.blit(self.surface, (self.offset_x - self.width, 0))
        screen.blit(self.surface, (self.offset_x, 0))
