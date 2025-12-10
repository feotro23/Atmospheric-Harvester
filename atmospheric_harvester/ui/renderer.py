import pygame
import os
from ui.theme import Theme
from ui.ui_manager import UIManager, WeatherOverlay, Button
from ui.build_overlay import BuildOverlay
from ui.missions_overlay import MissionsOverlay
from ui.achievements_overlay import AchievementsOverlay
from ui.events_overlay import EventsOverlay
from ui.farming_overlay import FarmingOverlay
from ui.settings_overlay import SettingsOverlay
from ui.upgrades_overlay import UpgradesOverlay
from ui.building_stats_overlay import BuildingStatsOverlay
from network.geocoding import GeocodingClient

class Renderer:
    def __init__(self, width, height):
        self.screen_width = width
        self.screen_height = height
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Atmospheric Harvester")
        
        self.font_large = Theme.get_font(40)
        self.font_med = Theme.get_font(24)
        self.font_small = Theme.get_font(16)
        
        self.ui_manager = UIManager()
        self.game_ref = None
        self.weather_overlay = None
        self.missions_overlay = None
        self.achievements_overlay = None
        self.events_overlay = None
        self.farming_overlay = None
        self.upgrades_overlay = None
        self.building_stats_overlay = None # New
        self.geocoding_client = GeocodingClient()
        
        self.assets = {}
        self.load_assets()

    def load_assets(self):
        # Use absolute path relative to this file to ensure assets load from anywhere
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        asset_dir = os.path.join(base_dir, "assets")
        try:
            # Weather Icons
            self.assets['sun'] = pygame.image.load(os.path.join(asset_dir, "icon_sun_1763665162472.png")).convert_alpha()
            self.assets['cloud'] = pygame.image.load(os.path.join(asset_dir, "icon_cloud_1763665181339.png")).convert_alpha()
            self.assets['rain'] = pygame.image.load(os.path.join(asset_dir, "icon_rain_1763665194781.png")).convert_alpha()
            self.assets['snow'] = pygame.image.load(os.path.join(asset_dir, "icon_snow_1763665208670.png")).convert_alpha()
            self.assets['lightning'] = pygame.image.load(os.path.join(asset_dir, "icon_lightning_1763665222895.png")).convert_alpha()
            
            # Scale icons
            for key in ['sun', 'cloud', 'rain', 'snow', 'lightning']:
                self.assets[key] = pygame.transform.scale(self.assets[key], (64, 64))
                
        except (pygame.error, FileNotFoundError) as e:
            print(f"Failed to load UI assets: {e}")

    def set_sound_manager(self, sm):
        self.ui_manager.sound_manager = sm

    def init_ui(self):
        """Initialize all UI elements and overlays."""
        # Right sidebar buttons
        btn_w = 200
        btn_h = 50
        start_x = self.width - btn_w - 20
        start_y = self.height - 260
        

        
        # Initialize Overlays
        # Weather Overlay
        self.weather_overlay = WeatherOverlay(self.width, self.height, self.game_ref, 
                                              self.game_ref.travel_manager, 
                                              self.geocoding_client, 
                                              self.game_ref.weather_client)
                                              
        # Build Overlay
        def close_build():
            pass # No specific action needed on close
        self.build_overlay = BuildOverlay(self.width, self.height, self.game_ref, close_build)
        
        # New: Building Stats Overlay
        self.building_stats_overlay = BuildingStatsOverlay(self.width, self.height, self.game_ref.state, self.world_renderer.assets)
        
        # Settings Overlay
        self.settings_overlay = SettingsOverlay(self.width, self.height, self.game_ref.settings_manager)
        
        # Missions Overlay
        self.missions_overlay = MissionsOverlay(self.width, self.height, self.game_ref)
        
        # Achievements Overlay
        self.achievements_overlay = AchievementsOverlay(self.width, self.height, self.game_ref)
        
        # Events Overlay
        self.events_overlay = EventsOverlay(self.width, self.height, self.game_ref)
        
        # Farming Overlay
        f_w = 800
        f_h = 600
        f_x = (self.width - f_w) // 2
        f_y = (self.height - f_h) // 2
        self.farming_overlay = FarmingOverlay(self.game_ref, f_x, f_y, f_w, f_h)
        
        # Upgrades Overlay
        u_w = 800
        u_h = 600
        u_x = (self.width - u_w) // 2
        u_y = (self.height - u_h) // 2
        self.upgrades_overlay = UpgradesOverlay(self.game_ref.state, self.game_ref.upgrade_manager, u_x, u_y, u_w, u_h)
        

        
        # Main UI Buttons (Bottom Bar)
        self._init_main_buttons()

    def _init_main_buttons(self):
        btn_w = 100
        btn_h = 40
        spacing = 10
        start_x = 20
        start_y = self.height - btn_h - 20
        
        # Build (B)
        def toggle_build():
            if self.build_overlay.visible: self.build_overlay.close()
            else: self.build_overlay.open()
        
        btn_build = Button(start_x, start_y, btn_w, btn_h, "Build (B)", toggle_build)
        self.ui_manager.add_element(btn_build)
        start_x += btn_w + spacing
        
        # Farming (F)
        def toggle_farming():
            if self.farming_overlay.visible: self.farming_overlay.visible = False
            else: self.farming_overlay.visible = True
            
        btn_farm = Button(start_x, start_y, btn_w, btn_h, "Farm (F)", toggle_farming)
        self.ui_manager.add_element(btn_farm)
        start_x += btn_w + spacing
        
        # Missions (M)
        def toggle_missions():
            self.missions_overlay.toggle()
            
        btn_miss = Button(start_x, start_y, btn_w, btn_h, "Missions (M)", toggle_missions)
        self.ui_manager.add_element(btn_miss)
        start_x += btn_w + spacing
        
        # Events (E)
        def toggle_events():
            self.events_overlay.toggle()
            
        btn_events = Button(start_x, start_y, btn_w, btn_h, "Events (E)", toggle_events)
        self.ui_manager.add_element(btn_events)
        start_x += btn_w + spacing

        # Upgrades (U)
        def toggle_upgrades():
            if self.upgrades_overlay.visible: self.upgrades_overlay.visible = False
            else: self.upgrades_overlay.visible = True
            
        btn_upgrades = Button(start_x, start_y, btn_w, btn_h, "Upgrades (U)", toggle_upgrades)
        self.ui_manager.add_element(btn_upgrades)
        start_x += btn_w + spacing


        
        # Edit (X)
        def toggle_edit():
            self.game_ref.edit_mode = not self.game_ref.edit_mode
            if self.game_ref.edit_mode:
                # print("Edit Mode ON")
                # Cancel other modes
                self.game_ref.build_selection = None
                self.game_ref.plant_selection = None
            else:
                # print("Edit Mode OFF")
                self.game_ref.cancel_move()
                
        btn_edit = Button(start_x, start_y, btn_w, btn_h, "Edit (X)", toggle_edit)
        self.ui_manager.add_element(btn_edit)

    def render(self, state, dt):
        """Render the main game UI."""
        # 1. Widgets
        self._draw_weather_widget(state, 20, 20)
        self._draw_resources_widget(state, self.width - 420, 20)
        
        # 2. UI Manager (Buttons)
        self.ui_manager.render(self.screen)
        
        # 3. Overlays (Order matters for z-index)
        if self.weather_overlay and self.weather_overlay.visible:
            self.weather_overlay.render(self.screen)
            
        if self.build_overlay and self.build_overlay.visible:
            self.build_overlay.render(self.screen)
            
        if self.farming_overlay and self.farming_overlay.visible:
            self.farming_overlay.render(self.screen)
            
        if self.missions_overlay and self.missions_overlay.visible:
            self.missions_overlay.render(self.screen)
            
        if self.achievements_overlay and self.achievements_overlay.visible:
            self.achievements_overlay.render(self.screen)
            
        if self.events_overlay and self.events_overlay.visible:
            self.events_overlay.render(self.screen)

        if self.upgrades_overlay and self.upgrades_overlay.visible:
            self.upgrades_overlay.render(self.screen)

        if self.building_stats_overlay and self.building_stats_overlay.visible:
            self.building_stats_overlay.render(self.screen)
            
        if self.settings_overlay and self.settings_overlay.visible:
            self.settings_overlay.render(self.screen)
            
        pygame.display.flip()

    def _draw_weather_widget(self, state, x, y):
        """Draw the weather widget with current conditions."""
        w = 320
        h = 180
        
        # Glass background
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(s, (0, 0, 0, 150), (0, 0, w, h), border_radius=15)
        self.screen.blit(s, (x, y))
        
        # Store rect for clicking
        self.weather_widget_rect = pygame.Rect(x, y, w, h)
        
        # Icon
        icon = self.assets.get('sun') # Default
        if state.weather_code >= 95: icon = self.assets.get('lightning')
        elif state.weather_code >= 70: icon = self.assets.get('snow')
        elif state.rain_vol > 0: icon = self.assets.get('rain')
        elif state.clouds > 50: icon = self.assets.get('cloud')
        
        if icon:
            self.screen.blit(icon, (x + 10, y + 10))
            
        # Temperature (use settings for unit)
        temp_display = self.game_ref.settings_manager.get_measurement_display(state.temp_c, "temp")
        temp_surf = self.font_large.render(temp_display, True, (255, 255, 255))
        self.screen.blit(temp_surf, (x + 90, y + 15))
        
        # Settings Button (Gear Icon)
        settings_btn_x = x + w - 35
        settings_btn_y = y + 10
        pygame.draw.circle(self.screen, (100, 100, 100), (settings_btn_x + 12, settings_btn_y + 12), 12)
        pygame.draw.circle(self.screen, (200, 200, 200), (settings_btn_x + 12, settings_btn_y + 12), 12, 2)
        # Simple gear text
        gear_text = self.font_small.render("⚙", True, (255, 255, 255))
        self.screen.blit(gear_text, (settings_btn_x + 5, settings_btn_y + 5))
        
        # Store button rect for clicking
        if not hasattr(self, 'settings_button_rect'):
            self.settings_button_rect = pygame.Rect(settings_btn_x, settings_btn_y, 24, 24)
        else:
            self.settings_button_rect.x = settings_btn_x
            self.settings_button_rect.y = settings_btn_y
        
        # Condition text
        cond_text = "Sunny"
        if state.weather_code >= 95: cond_text = "Thunderstorm"
        elif state.weather_code >= 70: cond_text = "Snowing"
        elif state.rain_vol > 0: cond_text = "Raining"
        elif state.clouds > 50: cond_text = "Cloudy"
        
        cond_surf = self.font_small.render(cond_text, True, (200, 200, 200))
        self.screen.blit(cond_surf, (x + 90, y + 50))
        
        # Location
        loc_surf = self.font_small.render(state.location_name, True, (150, 150, 150))
        self.screen.blit(loc_surf, (x + 10, y + 85))
        
        # Detailed Stats
        stats_y = y + 110
        
        # Wind Speed
        wind_val = self.game_ref.settings_manager.get_measurement_display(state.wind_speed, "speed")
        wind_text = f"🌬 Wind: {wind_val}"
        wind_color = (100, 200, 255) if state.wind_speed > 5 else (150, 150, 150)
        wind_surf = self.font_small.render(wind_text, True, wind_color)
        self.screen.blit(wind_surf, (x + 10, stats_y))
        
        # Humidity
        humidity_text = f"💧 Humidity: {state.humidity:.0f}%"
        humidity_color = (100, 150, 255) if state.humidity > 70 else (150, 150, 150)
        humidity_surf = self.font_small.render(humidity_text, True, humidity_color)
        self.screen.blit(humidity_surf, (x + 10, stats_y + 20))
        
        # Clouds
        clouds_text = f"☁ Clouds: {state.clouds:.0f}%"
        clouds_surf = self.font_small.render(clouds_text, True, (150, 150, 150))
        self.screen.blit(clouds_surf, (x + 10, stats_y + 40))

    def _draw_resources_widget(self, state, x, y):
        """Draw the resources widget showing energy, water, and biomass."""
        w = 400
        h = 220
        
        # Glass background
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(s, (0, 0, 0, 180), (0, 0, w, h), border_radius=15)
        self.screen.blit(s, (x, y))
        
        # Title
        title = self.font_med.render("Base Resources", True, (255, 255, 255))
        self.screen.blit(title, (x + 10, y + 10))
        
        # Credits
        credits_text = f"Credits: {state.resources.credits}"
        credits_surf = self.font_med.render(credits_text, True, (255, 215, 0)) # Gold color
        # Right align
        self.screen.blit(credits_surf, (x + w - credits_surf.get_width() - 15, y + 10))
        
        # Helper to draw bars
        def draw_bar(label, current, max_val, color, y_pos):
            bar_w = w - 20
            bar_h = 25
            
            # Label
            lbl_surf = self.font_small.render(label, True, (200, 200, 200))
            self.screen.blit(lbl_surf, (x + 15, y_pos - 20))
            
            # Background
            pygame.draw.rect(self.screen, (50, 50, 50), (x + 10, y_pos, bar_w, bar_h), border_radius=5)
            
            # Fill
            pct = min(current / max_val, 1.0) if max_val > 0 else 0
            pygame.draw.rect(self.screen, color, (x + 10, y_pos, bar_w * pct, bar_h), border_radius=5)
            
            # Text
            val_text = f"{int(current)} / {int(max_val)}"
            val_surf = self.font_small.render(val_text, True, (255, 255, 255))
            # Right align text
            self.screen.blit(val_surf, (x + bar_w - val_surf.get_width() - 5, y_pos + 5))

        # Energy
        draw_bar("Energy (Joules)", state.resources.energy, state.resources.energy_capacity, Theme.ACCENT_SOLAR, y + 60)
        
        # Water
        draw_bar("Water (Liters)", state.resources.water, state.resources.water_capacity, Theme.ACCENT_HYDRO, y + 110)
        
        # Biomass
        draw_bar("Biomass", state.resources.biomass, state.resources.biomass_capacity, (100, 200, 100), y + 160)
