import pygame
import os

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.channels = {}
        self.initialized = False
        self.settings_manager = None
        
        try:
            pygame.mixer.init()
            self.initialized = True
            
            # Check if sfx dir exists
            if not os.path.exists("assets/sfx"):
                print("Warning: assets/sfx directory not found. Audio disabled.")
                return

            self._load_sounds()
        except Exception as e:
            print(f"Audio init failed: {e}")

    def _load_sounds(self):
        # SFX
        self._load_sound("click", "assets/sfx/click.wav")
        self._load_sound("upgrade", "assets/sfx/upgrade.wav")
        
        # Loops
        self._load_sound("wind", "assets/sfx/wind_loop.wav")
        self._load_sound("rain", "assets/sfx/rain_loop.wav")

    def _load_sound(self, name, path):
        if os.path.exists(path):
            try:
                self.sounds[name] = pygame.mixer.Sound(path)
            except Exception as e:
                print(f"Failed to load {path}: {e}")
        else:
            print(f"Sound file not found: {path}")

    def play_sfx(self, name):
        if not self.initialized: return
        
        vol = 1.0
        if self.settings_manager:
            vol = self.settings_manager.volume
            
        if name in self.sounds:
            self.sounds[name].set_volume(vol)
            self.sounds[name].play()

    def start_loops(self):
        if not self.initialized: return
        
        # Start wind loop on Channel 0
        if "wind" in self.sounds:
            self.channels["wind"] = self.sounds["wind"].play(loops=-1)
            self.channels["wind"].set_volume(0)
            
        # Start rain loop on Channel 1
        if "rain" in self.sounds:
            self.channels["rain"] = self.sounds["rain"].play(loops=-1)
            self.channels["rain"].set_volume(0)

    def update(self, game_state):
        if not self.initialized: return
        
        master_vol = 1.0
        if self.settings_manager:
            master_vol = self.settings_manager.volume
        
        # Dynamic Wind Volume
        # Wind speed 0-30 m/s -> Volume 0.0 - 1.0
        wind_vol = min(1.0, game_state.wind_speed / 30.0)
        if "wind" in self.channels and self.channels["wind"]:
            self.channels["wind"].set_volume(wind_vol * 0.5 * master_vol) # Cap at 50% * master
            
        # Dynamic Rain Volume
        # Rain vol 0-10 mm -> Volume 0.0 - 1.0
        rain_vol = min(1.0, game_state.rain_vol / 5.0)
        if "rain" in self.channels and self.channels["rain"]:
            self.channels["rain"].set_volume(rain_vol * 0.6 * master_vol)
