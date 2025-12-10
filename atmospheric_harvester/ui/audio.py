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
            
            # Resolve assets dir relative to this file
            # ui/audio.py -> ../assets/sfx
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.sfx_dir = os.path.join(base_dir, "assets", "sfx")
            
            # Check if sfx dir exists
            if not os.path.exists(self.sfx_dir):
                print(f"Warning: {self.sfx_dir} directory not found. Audio disabled.")
                return

            self._load_sounds()
        except Exception as e:
            print(f"Audio init failed: {e}")

    def _load_sounds(self):
        # SFX
        self._load_sound("click", os.path.join(self.sfx_dir, "click.wav"))
        self._load_sound("upgrade", os.path.join(self.sfx_dir, "upgrade.wav"))
        
        # Loops
        self._load_sound("wind", os.path.join(self.sfx_dir, "wind_loop.wav"))
        self._load_sound("rain", os.path.join(self.sfx_dir, "rain_loop.wav"))
        self._load_sound("music", os.path.join(self.sfx_dir, "Paradise_Found.mp3"))

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

        # Start music loop on Channel 2
        if "music" in self.sounds:
            self.channels["music"] = self.sounds["music"].play(loops=-1)
            self.channels["music"].set_volume(0)

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
            
        # Music Volume
        # Constant background, lower volume (30%)
        if "music" in self.channels and self.channels["music"]:
            self.channels["music"].set_volume(0.3 * master_vol)
