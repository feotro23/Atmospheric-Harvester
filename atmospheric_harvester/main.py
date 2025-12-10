import asyncio
import pygame
import sys
import time
from config import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, DEFAULT_LAT, DEFAULT_LON, POLL_INTERVAL

AUTO_SAVE_INTERVAL = 60 # Seconds
from game.core import Game
from network.weather_service import WeatherService
from ui.renderer import Renderer
from ui.world_renderer import WorldRenderer
from ui.visuals import DayNightCycle, VectorParticleSystem, CloudLayer
from world.terrain import TerrainGenerator
from ui.audio import SoundManager

class AsyncGameLoop:
    def __init__(self):
        pygame.init()
        self.game = Game() # Init game first
        
        # Initialize weather service before UI setup (needed for overlay)
        self.weather_service = WeatherService()
        self.game.weather_client = self.weather_service  # For overlay compatibility
        
        self.renderer = Renderer(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.renderer.game_ref = self.game # Link
        
        # World Gen
        self.terrain_gen = TerrainGenerator(width=10, height=10, seed=12345)
        self.game.state.world_map = self.terrain_gen.generate(scale=0.1)
        self.world_renderer = WorldRenderer(self.renderer.screen, tile_size=64)
        
        # Pass world renderer to UI renderer
        self.renderer.world_renderer = self.world_renderer
        self.renderer.init_ui() # Setup UI elements (including weather overlay)
        
        # Visuals
        self.day_night = DayNightCycle(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.particles = VectorParticleSystem(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.clouds = CloudLayer(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        self.sound_manager = SoundManager()
        self.sound_manager.settings_manager = self.game.settings_manager # Link settings
        self.renderer.set_sound_manager(self.sound_manager)
        self.sound_manager.start_loops()
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.last_weather_poll = 0
        self.last_auto_save = time.time()
        
        # Load Game
        success, msg = self.game.load_game()
        print(f"Startup Load: {msg}")

    async def run(self):
        await self.weather_service.start()
        await self.renderer.geocoding_client.start()
        
        # Initial fetch
        await self.fetch_weather()

        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds
            
            self.handle_events()
            self.update(dt)
            self.render(dt)
            
            # Check for weather update
            if time.time() - self.last_weather_poll > POLL_INTERVAL:
                await self.fetch_weather()
                
            # Auto-Save
            if time.time() - self.last_auto_save > AUTO_SAVE_INTERVAL:
                self.last_auto_save = time.time()
                success, msg = self.game.save_game()
                if success:
                    print(f"[Auto-Save] {msg}")
            
            # Check for pending city search
            if self.renderer.weather_overlay and self.renderer.weather_overlay.search_pending:
                self.renderer.weather_overlay.search_pending = False
                await self.renderer.weather_overlay.search_cities(self.renderer.weather_overlay.search_input.text)
            
            # Check for pending preview weather fetch
            if self.renderer.weather_overlay and self.renderer.weather_overlay.preview_pending:
                self.renderer.weather_overlay.preview_pending = False
                await self.renderer.weather_overlay.fetch_preview_weather()
                # Update travel button after weather fetch
                self.renderer.weather_overlay._update_travel_button()
            
            # Check for pending forecast fetch
            if self.renderer.weather_overlay and self.renderer.weather_overlay.forecast_pending:
                self.renderer.weather_overlay.forecast_pending = False
                state = self.game.state
                forecast = await self.weather_service.get_forecast(state.lat, state.lon)
                self.renderer.weather_overlay.forecast_data = forecast
            
            # Update overlay
            if self.renderer.weather_overlay:
                self.renderer.weather_overlay.update(dt)
            
            # Yield to event loop
            await asyncio.sleep(0)

        # Save on exit
        self.game.save_game()
        print("Game saved on exit.")
        
        await self.weather_service.close()
        await self.renderer.geocoding_client.close()
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            # Settings Overlay Priority
            if hasattr(self.renderer, 'settings_overlay') and self.renderer.settings_overlay.handle_event(event):
                continue
            
            # Build Overlay Priority
            if hasattr(self.renderer, 'build_overlay') and self.renderer.build_overlay.handle_event(event):
                continue
            
            # Missions Overlay Priority
            if hasattr(self.renderer, 'missions_overlay') and self.renderer.missions_overlay.handle_event(event):
                continue
            
            # Achievements Overlay Priority
            if hasattr(self.renderer, 'achievements_overlay') and self.renderer.achievements_overlay.handle_event(event):
                continue
            
            # Events Overlay Priority
            if hasattr(self.renderer, 'events_overlay') and self.renderer.events_overlay.handle_event(event):
                continue

            # Farming Overlay Priority
            if hasattr(self.renderer, 'farming_overlay') and self.renderer.farming_overlay.handle_event(event):
                continue

            # Upgrades Overlay Priority
            if hasattr(self.renderer, 'upgrades_overlay') and self.renderer.upgrades_overlay.handle_event(event):
                continue

            # Building Stats Overlay Priority
            if hasattr(self.renderer, 'building_stats_overlay') and self.renderer.building_stats_overlay.handle_event(event):
                continue

            # Weather overlay gets priority
            if self.renderer.weather_overlay and self.renderer.weather_overlay.handle_event(event):
                # Track that weather overlay was opened for missions
                if not self.game.state._weather_overlay_opened:
                    self.game.state._weather_overlay_opened = True
                # If city was selected via overlay, trigger weather fetch
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Schedule immediate weather update
                    self.last_weather_poll = 0
                continue
            
            # UI Manager (For other buttons like Plant, Harvest, etc.)
            if self.renderer.ui_manager.handle_event(event):
                continue
            
            # Settings button click
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if hasattr(self.renderer, 'settings_button_rect'):
                    if self.renderer.settings_button_rect.collidepoint(event.pos):
                        self.renderer.settings_overlay.open()
                        continue
                
                # Weather Widget click (Open Weather Overlay)
                if hasattr(self.renderer, 'weather_widget_rect'):
                    if self.renderer.weather_widget_rect.collidepoint(event.pos):
                        self.renderer.weather_overlay.visible = True
                        self.game.state._weather_overlay_opened = True
                        continue
            
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                # Camera Scrolling
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.world_renderer.camera.scroll_x += 20
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.world_renderer.camera.scroll_x -= 20
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.world_renderer.camera.scroll_y += 20
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.world_renderer.camera.scroll_y -= 20
                    
                # Missions key (M)
                elif event.key == pygame.K_m:
                    if hasattr(self.renderer, 'missions_overlay'):
                        self.renderer.missions_overlay.toggle()
                # Achievements key (A)
                elif event.key == pygame.K_a:
                    if hasattr(self.renderer, 'achievements_overlay'):
                        self.renderer.achievements_overlay.toggle()
                # Events key (E)
                elif event.key == pygame.K_e:
                    if hasattr(self.renderer, 'events_overlay'):
                        self.renderer.events_overlay.toggle()
                # Farming key (F)
                elif event.key == pygame.K_f:
                        if not self.game.state._weather_overlay_opened:
                            self.game.state._weather_overlay_opened = True
                # Edit key (X)
                elif event.key == pygame.K_x:
                    self.game.edit_mode = not self.game.edit_mode
                    if self.game.edit_mode:
                        # print("Edit Mode ON")
                        self.game.build_selection = None
                        self.game.plant_selection = None
                    else:
                        # print("Edit Mode OFF")
                        self.game.cancel_move()
                # Travel keys 1-6
                elif pygame.K_1 <= event.key <= pygame.K_6:
                    idx = event.key - pygame.K_1
                    self.try_travel(idx)
                # Save (F5)
                elif event.key == pygame.K_F5:
                    success, msg = self.game.save_game()
                    if msg: print(msg)
                # Load (F9)
                elif event.key == pygame.K_F9:
                    success, msg = self.game.load_game()
                    if msg: print(msg)
                    if success:
                        # Force weather update
                        self.last_weather_poll = 0
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    mx, my = pygame.mouse.get_pos()
                    # Convert to grid
                    gx, gy = self.world_renderer.camera.screen_to_iso(mx, my)
                    # Round to nearest integer
                    gx = int(round(gx / self.world_renderer.tile_size))
                    gy = int(round(gy / self.world_renderer.tile_size))
                    
                    if self.game.build_selection:
                        # Try to build
                        success, msg = self.game.build_machine(self.game.build_selection, gx, gy)
                        if msg: print(msg)
                        if success:
                            # Optional: Deselect after build? Or keep selected for multiple placement?
                            # Let's keep selected for now (Shift-click style is better but simple is fine)
                            pass
                    elif self.game.plant_selection:
                        # Try to plant
                        success, msg = self.game.plant_crop(self.game.plant_selection, gx, gy)
                        if msg: print(msg)
                        if success:
                            # Check if we have more seeds
                            if self.game.state.seeds.get(self.game.plant_selection, 0) <= 0:
                                self.game.plant_selection = None
                                # print("Out of seeds.")
                    elif self.game.edit_mode:
                        if self.game.moving_object:
                            # Try to place
                            success, msg = self.game.place_moving_object(gx, gy)
                            if msg: print(msg)
                        else:
                            # Try to pick up
                            success, msg = self.game.start_move(gx, gy)
                            if msg: print(msg)
                    else:
                        action, payload = self.game.interact(gx, gy)
                        if action == "machine_click":
                            # Open stats overlay
                            if self.renderer.building_stats_overlay:
                                self.renderer.building_stats_overlay.open(payload)
                        elif action == "harvest":
                            # Already handled logic in core, maybe play sound?
                            pass
                        elif action == "creature_capture":
                            # Handled in core
                            pass
                        
                elif event.button == 3: # Right click
                    if self.game.build_selection:
                        # print("Cancelled build mode.")
                        self.game.build_selection = None
                    elif self.game.plant_selection:
                        # print("Cancelled planting mode.")
                        self.game.plant_selection = None
                    elif self.game.edit_mode:
                        if self.game.moving_object:
                            self.game.cancel_move()
                            pass # print("Cancelled move")
                        else:
                            self.game.edit_mode = False
                            # print("Edit Mode OFF")

    def try_travel(self, idx):
        locations = self.game.travel_manager.locations
        if 0 <= idx < len(locations):
            target = locations[idx]
            if self.game.travel_manager.travel(self.game.state, target):
                # print(f"Traveled to {target.name}")
                # Force immediate weather update
                self.last_weather_poll = 0 # Will trigger update next loop
            else:
                print("Not enough energy to travel!")

    async def fetch_weather(self):
        # Use the current game state location - WeatherService routes to NWS or Open-Meteo
        data = await self.weather_service.get_weather(self.game.state.lat, self.game.state.lon)
        if data:
            # Update weather data
            self.game.state.update_weather(data)
            
            # Fetch alerts
            alerts = await self.weather_service.get_alerts(self.game.state.lat, self.game.state.lon)
            self.game.state.alerts = alerts
            if alerts:
                print(f"Active Alerts: {[a['event'] for a in alerts]}")
            
            # Track weather conditions for achievements
            if self.game.state.rain_vol > 0:  # Raining
                if not hasattr(self.game.state, '_current_location_rainy_counted'):
                    self.game.state._rainy_locations_visited += 1
                    self.game.state._current_location_rainy_counted = True
            if self.game.state.snow_depth > 0:  # Snowing
                if not hasattr(self.game.state, '_current_location_snowy_counted'):
                    self.game.state._snowy_locations_visited += 1
                    self.game.state._current_location_snowy_counted = True
            
            self.last_weather_poll = time.time()

    def update(self, dt):
        self.game.update(dt)
        self.day_night.update(self.game.state)
        self.particles.update(dt, self.game.state)
        self.clouds.update(dt, self.game.state)
        self.sound_manager.update(self.game.state)

    def render(self, dt):
        # 1. Sky (Background)
        self.day_night.render(self.renderer.screen)
        
        # 2. World
        self.world_renderer.render(self.game.state.world_map)
        self.world_renderer.render_objects(self.game.state) # Don't forget objects!
        
        # Preview
        if self.game.build_selection:
            # Get mouse pos and convert to grid
            mx, my = pygame.mouse.get_pos()
            gx, gy = self.world_renderer.camera.screen_to_iso(mx, my)
            gx = int(round(gx / self.world_renderer.tile_size))
            gy = int(round(gy / self.world_renderer.tile_size))
            
            # Check validity
            valid = True
            if not (0 <= gx < 10 and 0 <= gy < 10): valid = False
            
            # Check occupation (simple check against list)
            for m in self.game.state.machines:
                if m.x == gx and m.y == gy: valid = False
            for c in self.game.state.crops:
                if c.x == gx and c.y == gy: valid = False
                
            self.world_renderer.render_preview(gx, gy, self.game.build_selection, valid)
        elif self.game.plant_selection:
            mx, my = pygame.mouse.get_pos()
            gx, gy = self.world_renderer.camera.screen_to_iso(mx, my)
            gx = int(round(gx / self.world_renderer.tile_size))
            gy = int(round(gy / self.world_renderer.tile_size))
            
            # Check validity (simple check)
            valid = True
            if not (0 <= gx < 10 and 0 <= gy < 10): valid = False
            # Check occupation (could duplicate logic or add helper)
            
            self.world_renderer.render_preview(gx, gy, self.game.plant_selection, valid)
            
        elif self.game.edit_mode and self.game.moving_object:
            mx, my = pygame.mouse.get_pos()
            gx, gy = self.world_renderer.camera.screen_to_iso(mx, my)
            gx = int(round(gx / self.world_renderer.tile_size))
            gy = int(round(gy / self.world_renderer.tile_size))
            
            # Check validity
            valid = True
            if not (0 <= gx < 10 and 0 <= gy < 10): valid = False
            
            self.world_renderer.render_moving_preview(gx, gy, self.game.moving_object[0], valid)
        
        # 3. Visuals
        self.particles.render(self.renderer.screen)
        self.clouds.render(self.renderer.screen)
        
        # 4. UI Overlay
        self.renderer.render(self.game.state, dt)

async def main():
    loop = AsyncGameLoop()
    await loop.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
