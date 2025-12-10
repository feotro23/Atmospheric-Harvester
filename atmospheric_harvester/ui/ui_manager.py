import pygame
from .theme import Theme

class UIElement:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.visible = True
        
    def handle_event(self, event):
        pass
        
    def render(self, screen):
        pass

class Button(UIElement):
    def __init__(self, x, y, w, h, text, callback, tooltip=None):
        super().__init__(x, y, w, h)
        self.text = text
        self.callback = callback
        self.tooltip = tooltip
        self.hovered = False
        self.font = Theme.get_font(16)
        
    def handle_event(self, event):
        if not self.visible:
            return False
            
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.hovered:
                if self.callback:
                    self.callback()
                return True
        return False
        
    def render(self, screen):
        if not self.visible:
            return
            
        # Procedural Glossy Look
        # Base color
        base_color = (50, 100, 200) # Blue-ish
        if "Harvest" in self.text: base_color = (200, 150, 0) # Gold
        elif "Plant" in self.text: base_color = (50, 150, 50) # Green
        
        if self.hovered:
            # Brighten
            base_color = (min(255, base_color[0] + 30), min(255, base_color[1] + 30), min(255, base_color[2] + 30))
            
        # Draw Gradient Background
        # Top half lighter, bottom half darker
        top_col = (min(255, base_color[0] + 20), min(255, base_color[1] + 20), min(255, base_color[2] + 20))
        bot_col = (max(0, base_color[0] - 20), max(0, base_color[1] - 20), max(0, base_color[2] - 20))
        
        # Draw rect with gradient (simulated by 2 rects for speed)
        half_h = self.rect.height // 2
        pygame.draw.rect(screen, top_col, (self.rect.x, self.rect.y, self.rect.width, half_h), border_top_left_radius=10, border_top_right_radius=10)
        pygame.draw.rect(screen, bot_col, (self.rect.x, self.rect.y + half_h, self.rect.width, self.rect.height - half_h), border_bottom_left_radius=10, border_bottom_right_radius=10)
        
        # Border
        pygame.draw.rect(screen, (200, 200, 200) if self.hovered else (50, 50, 50), self.rect, 2, border_radius=10)
        
        # Gloss Highlight (Top curve)
        # pygame.draw.ellipse(screen, (255, 255, 255, 50), (self.rect.x + 5, self.rect.y + 2, self.rect.width - 10, self.rect.height // 2))
        # Pygame drawing doesn't support alpha directly on screen unless surface.
        # Let's draw a white line at top
        pygame.draw.line(screen, (255, 255, 255), (self.rect.x + 10, self.rect.y + 5), (self.rect.right - 10, self.rect.y + 5), 1)
        
        # Text Shadow
        text_surf_s = self.font.render(self.text, True, (0, 0, 0))
        text_rect_s = text_surf_s.get_rect(center=(self.rect.centerx + 1, self.rect.centery + 1))
        screen.blit(text_surf_s, text_rect_s)
        
        # Text
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

class TextInput(UIElement):
    def __init__(self, x, y, w, h, placeholder="Type here...", max_length=50):
        super().__init__(x, y, w, h)
        self.text = ""
        self.placeholder = placeholder
        self.max_length = max_length
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        self.font = Theme.get_font(18)
        
    def handle_event(self, event):
        if not self.visible:
            return False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Check if clicked inside
                self.active = self.rect.collidepoint(event.pos)
                return self.active
        
        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                return True
            elif event.key == pygame.K_RETURN:
                # Enter key - could trigger search
                return True
            elif event.key == pygame.K_ESCAPE:
                self.active = False
                return True
            elif len(self.text) < self.max_length:
                # Add character
                if event.unicode.isprintable():
                    self.text += event.unicode
                    return True
        
        return False
    
    def update(self, dt):
        """Update cursor blink animation."""
        self.cursor_timer += dt
        if self.cursor_timer > 0.5:
            self.cursor_timer = 0
            self.cursor_visible = not self.cursor_visible
    
    def render(self, screen):
        if not self.visible:
            return
        
        # Background
        bg_color = (40, 45, 55) if self.active else (30, 35, 40)
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=8)
        
        # Border
        border_color = (100, 150, 255) if self.active else (70, 70, 70)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=8)
        
        # Text or placeholder
        if self.text:
            text_surf = self.font.render(self.text, True, (255, 255, 255))
        else:
            text_surf = self.font.render(self.placeholder, True, (120, 120, 120))
        
        text_rect = text_surf.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
        
        # Clip text if too long
        if text_rect.right > self.rect.right - 10:
            # Create a subsurface to clip
            clip_rect = pygame.Rect(self.rect.x + 10, self.rect.y, self.rect.width - 20, self.rect.height)
            screen.set_clip(clip_rect)
            screen.blit(text_surf, text_rect)
            screen.set_clip(None)
        else:
            screen.blit(text_surf, text_rect)
        
        # Cursor
        if self.active and self.cursor_visible and self.text:
            cursor_x = min(text_rect.right + 2, self.rect.right - 10)
            cursor_y1 = self.rect.centery - 10
            cursor_y2 = self.rect.centery + 10
            pygame.draw.line(screen, (255, 255, 255), (cursor_x, cursor_y1), (cursor_x, cursor_y2), 2)


class UIManager:
    def __init__(self, sound_manager=None):
        self.elements = []
        self.sound_manager = sound_manager
        
    def add_element(self, element):
        self.elements.append(element)
        
    def clear(self):
        self.elements = []
        
    def handle_event(self, event):
        for el in self.elements:
            if el.handle_event(event):
                # If event handled (clicked), play sound
                if self.sound_manager:
                    self.sound_manager.play_sfx("click")
            
    def render(self, screen):
        tooltip_to_draw = None
        
        for el in self.elements:
            el.render(screen)
            if isinstance(el, Button) and el.hovered and el.tooltip:
                tooltip_to_draw = (el.tooltip, pygame.mouse.get_pos())
                
        if tooltip_to_draw:
            self._draw_tooltip(screen, tooltip_to_draw[0], tooltip_to_draw[1])

    def _draw_tooltip(self, screen, text, pos):
        font = Theme.get_font(16)
        lines = text.split('\n')
        
        # Calculate size
        max_w = 0
        h = 0
        surfs = []
        for line in lines:
            s = font.render(line, True, Theme.TEXT_MAIN)
            max_w = max(max_w, s.get_width())
            h += s.get_height() + 2
            surfs.append(s)
            
        w = max_w + 10
        h += 10
        
        x, y = pos
        x += 15 # Offset
        y += 15
        
        # Clamp to screen
        if x + w > screen.get_width(): x -= w + 20
        if y + h > screen.get_height(): y -= h + 20
        
        # Draw bg
        pygame.draw.rect(screen, (10, 10, 15), (x, y, w, h))
        pygame.draw.rect(screen, Theme.TEXT_DIM, (x, y, w, h), 1)
        
        # Draw text
        curr_y = y + 5
        for s in surfs:
            screen.blit(s, (x + 5, curr_y))
            curr_y += s.get_height() + 2

class WeatherOverlay(UIElement):
    def __init__(self, screen_width, screen_height, game_ref, travel_manager, geocoding_client, weather_client):
        # Center overlay
        w = 900 # Wider for 2 columns
        h = 700  # Taller to fit all data
        x = (screen_width - w) // 2
        y = (screen_height - h) // 2
        super().__init__(x, y, w, h)
        
        self.game_ref = game_ref
        self.travel_manager = travel_manager
        self.geocoding_client = geocoding_client
        self.weather_client = weather_client
        self.visible = False
        
        self.font_title = Theme.get_font(32)
        self.font_med = Theme.get_font(20)
        self.font_small = Theme.get_font(16)
        
        # Preview state
        self.preview_location = None  # {'name': str, 'lat': float, 'lon': float}
        self.preview_weather_data = None
        self.preview_pending = False
        
        # Search input - positioned dynamically in render
        self.search_input = TextInput(0, 0, self.rect.width - 60, 40, placeholder="Search for a city...")
        
        # City result buttons
        self.city_buttons = []
        self.search_results = []
        self.search_pending = False
        self.last_search_text = ""
        
        # Travel button (created dynamically when needed)
        self.travel_button = None
        
        # Forecast state
        self.show_forecast = False
        self.forecast_data = []
        self.forecast_pending = False
        
        # 7-Day Forecast button (top area)
        forecast_btn_x = self.rect.x + 620
        forecast_btn_y = self.rect.y + 50
        self.forecast_button = Button(
            forecast_btn_x, forecast_btn_y, 140, 35,
            "7-Day Forecast",
            self._toggle_forecast
        )
        
        # Back button (shown when viewing forecast)
        self.back_button = Button(
            self.rect.x + 620, self.rect.y + 50, 140, 35,
            "← Back",
            self._toggle_forecast
        )
        
        # Close button
        close_x = self.rect.right - 40
        close_y = self.rect.top + 10
        self.close_button = Button(close_x, close_y, 30, 30, "X", self.close)
    
    def _toggle_forecast(self):
        """Toggle between current weather and 7-day forecast view."""
        self.show_forecast = not self.show_forecast
        if self.show_forecast and not self.forecast_data:
            self.forecast_pending = True  # Flag to fetch forecast
    
    async def search_cities(self, query):
        """Perform city search using geocoding API."""
        if not query or len(query) < 3:
            self.search_results = []
            self._create_city_buttons()
            return
        
        results = await self.geocoding_client.search_city(query, count=10)
        self.search_results = results
        self._create_city_buttons()
    
    def select_city_from_search(self, city_data):
        """Select a city from search results to preview."""
        self.preview_location = {
            'name': city_data['display_name'],
            'lat': city_data['lat'],
            'lon': city_data['lon']
        }
        
        # Clear search
        self.search_input.text = ""
        self.search_results = []
        self.city_buttons = []
        
        # Flag for async weather fetch
        self.preview_pending = True
        print(f"Previewing weather for {city_data['display_name']}")

    def _create_city_buttons(self):
        """Create buttons from search results."""
        self.city_buttons = []
        
        if not self.search_results:
            return
        
        # City buttons are created with absolute positions
        # They will be positioned below search box in render
        
        # Grid layout for cities
        btn_w = self.rect.width - 60
        btn_h = 35
        
        for city in self.search_results:
            # Create a callback that captures the current city data
            def make_callback(c):
                return lambda: self.select_city_from_search(c)
            
            # Position will be set in render, but we need initial rects
            # Just set them to 0,0 for now, render will update
            btn = Button(
                0, 0, btn_w, btn_h,
                f"{city['display_name']} ({city['country']})",
                make_callback(city)
            )
            self.city_buttons.append(btn)
    
    async def fetch_preview_weather(self):
        """Fetch weather data for preview location."""
        if not self.preview_location:
            return
        
        weather_data = await self.weather_client.get_weather(
            self.preview_location['lat'],
            self.preview_location['lon']
        )
        
        if weather_data:
            self.preview_weather_data = weather_data
            print(f"Preview weather fetched for {self.preview_location['name']}")
    
    def travel_to_preview(self):
        """Travel to the currently previewed location."""
        if not self.preview_location:
            return
        
        from game.travel import Location
        location = Location(
            self.preview_location['name'],
            self.preview_location['lat'],
            self.preview_location['lon']
        )
        
        if self.travel_manager.travel(self.game_ref.state, location):
            print(f"Traveled to {location.name}")
            # Clear preview since we're now at this location
            self.preview_location = None
            self.preview_weather_data = None
            self._update_travel_button()
        else:
            print(f"Not enough energy to travel to {location.name}")
    
    def _update_travel_button(self):
        """Create or remove travel button based on preview state."""
        current_loc = self.game_ref.state.location_name
        preview_name = self.preview_location['name'] if self.preview_location else None
        
        # Show button only if previewing a different location
        if preview_name and preview_name != current_loc:
            if not self.travel_button:
                btn_x = self.rect.x + 350  # Moved to right side
                btn_y = self.rect.y + 80   # Moved to top, below location
                btn_w = 220
                btn_h = 35
                
                # Calculate travel cost
                from game.travel import Location
                temp_loc = Location(preview_name, self.preview_location['lat'], self.preview_location['lon'])
                cost = self.travel_manager.calculate_cost(
                    self.game_ref.state.lat,
                    self.game_ref.state.lon,
                    temp_loc
                )
                
                self.travel_button = Button(
                    btn_x, btn_y, btn_w, btn_h,
                    f"Travel Here ({cost:.0f} kWh)",
                    self.travel_to_preview
                )
        else:
            self.travel_button = None

    
    def select_city(self, location):
        # Travel to selected city
        if self.travel_manager.travel(self.game_ref.state, location):
            print(f"Traveled to {location.name}")
        else:
            print(f"Not enough energy to travel to {location.name}")
    
    def close(self):
        self.visible = False
    
    def toggle(self):
        self.visible = not self.visible
    
    def handle_event(self, event):
        if not self.visible:
            return False
        
        # Travel button first (if exists)
        if self.travel_button and self.travel_button.handle_event(event):
            return True
        
        # Forecast/Back button
        if self.show_forecast:
            if self.back_button.handle_event(event):
                return True
        else:
            if self.forecast_button.handle_event(event):
                return True
        
        # Search input (only if not showing forecast)
        if not self.show_forecast:
            if self.search_input.handle_event(event):
                # Check if text changed (trigger search)
                if self.search_input.text != self.last_search_text:
                    self.last_search_text = self.search_input.text
                    self.search_pending = True  # Flag for async search
                return True
        
        # Close button
        if self.close_button.handle_event(event):
            return True
        
        # City buttons
        for btn in self.city_buttons:
            if btn.handle_event(event):
                # Update travel button after city selection
                self._update_travel_button()
                return True
        
        # ESC to close
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            # If search is active, deactivate it first
            if self.search_input.active:
                self.search_input.active = False
                return True
            else:
                self.close()
                return True
        
        # Intercept all clicks on overlay area
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        
        return False
    
    def update(self, dt):
        """Update text input cursor animation."""
        self.search_input.update(dt)
    
    def render(self, screen):
        if not self.visible:
            return
        
        # Semi-transparent background overlay
        overlay_bg = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        pygame.draw.rect(overlay_bg, (0, 0, 0, 180), overlay_bg.get_rect())
        screen.blit(overlay_bg, (0, 0))
        
        # Main panel
        panel_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (20, 25, 35, 250), (0, 0, self.rect.width, self.rect.height), border_radius=20)
        pygame.draw.rect(panel_surf, (100, 150, 200), (0, 0, self.rect.width, self.rect.height), 3, border_radius=20)
        screen.blit(panel_surf, (self.rect.x, self.rect.y))
        
        # Title
        title = self.font_title.render("Comprehensive Weather Data", True, (255, 255, 255))
        title_rect = title.get_rect(centerx=self.rect.centerx, y=self.rect.y + 15)
        screen.blit(title, title_rect)
        
        # Get weather data - use preview if available, otherwise current
        state = self.game_ref.state
        if self.preview_weather_data:
            wd = self.preview_weather_data
            location_name = self.preview_location['name']
            is_preview = True
        else:
            wd = state.weather_data if state.weather_data else {}
            location_name = state.location_name
            is_preview = False
        
        # Location at the very top
        top_y = self.rect.y + 55
        if is_preview:
            self._draw_text(screen, f"📍 {location_name} (Preview)", self.rect.x + 25, top_y, (255, 200, 100), self.font_med)
        else:
            self._draw_text(screen, f"📍 {location_name}", self.rect.x + 25, top_y, (200, 220, 255), self.font_med)
        
        # Time below location
        import datetime
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        self._draw_text(screen, f"🕐 {current_time}", self.rect.x + 25, top_y + 25, (180, 180, 180))
        
        # Render forecast button or back button
        if self.show_forecast:
            self.back_button.rect.x = self.rect.x + 620
            self.back_button.rect.y = self.rect.y + 50
            self.back_button.render(screen)
            # Render forecast view
            self._render_forecast(screen)
            # Close button
            self.close_button.rect.x = self.rect.right - 40
            self.close_button.render(screen)
            return
        else:
            self.forecast_button.rect.x = self.rect.x + 620
            self.forecast_button.rect.y = self.rect.y + 50
            self.forecast_button.render(screen)
        
        # Weather content area starts lower to make room for location/travel button
        # TWO COLUMN LAYOUT
        col1_x = self.rect.x + 25
        col2_x = self.rect.x + 450 # Second column starts halfway
        content_y = self.rect.y + 110
        line_height = 18
        
        # --- COLUMN 1 ---
        y = content_y
        
        # CURRENT CONDITIONS
        sm = self.game_ref.settings_manager
        
        self._draw_category(screen, "CURRENT CONDITIONS", col1_x, y)
        y += 22
        self._draw_data(screen, "Temperature", sm.get_measurement_display(wd.get('temp', 0), "temp"), col1_x, y, (255, 150, 150))
        y += line_height
        self._draw_data(screen, "Feels Like", sm.get_measurement_display(wd.get('apparent_temp', 0), "temp"), col1_x, y)
        y += line_height
        self._draw_data(screen, "Condition", self._get_condition_text(state.weather_code), col1_x, y, (255, 255, 100))
        y += line_height + 10
        
        # ATMOSPHERIC
        self._draw_category(screen, "ATMOSPHERIC", col1_x, y)
        y += 22
        self._draw_data(screen, "Humidity", f"{wd.get('humidity', 0):.0f}%", col1_x, y)
        y += line_height
        self._draw_data(screen, "Dewpoint", sm.get_measurement_display(wd.get('dewpoint', 0), "temp"), col1_x, y)
        y += line_height
        self._draw_data(screen, "Pressure", f"{wd.get('pressure', 0):.0f} hPa", col1_x, y)
        y += line_height
        self._draw_data(screen, "Visibility", sm.get_measurement_display(wd.get('visibility', 0)/1000, "distance"), col1_x, y)
        y += line_height
        self._draw_data(screen, "Cloud Cover", f"{wd.get('cloud_cover', 0):.0f}%", col1_x, y)
        y += line_height
        # Detailed clouds
        self._draw_data(screen, "  Low/Mid/High", f"{wd.get('cloud_cover_low', 0):.0f}/{wd.get('cloud_cover_mid', 0):.0f}/{wd.get('cloud_cover_high', 0):.0f}%", col1_x, y, (150, 150, 150))
        y += line_height + 10
        
        # PRECIPITATION
        self._draw_category(screen, "PRECIPITATION", col1_x, y)
        y += 22
        self._draw_data(screen, "Probability", f"{wd.get('precip_probability', 0):.0f}%", col1_x, y, (150, 200, 255))
        y += line_height
        
        rain_val = sm.get_measurement_display(wd.get('rain', 0), "length_mm")
        snow_val = sm.get_measurement_display(wd.get('snowfall', 0), "length_cm") # Snowfall usually cm
        self._draw_data(screen, "Rain/Snow", f"{rain_val} / {snow_val}", col1_x, y)
        y += line_height
        
        snow_depth_val = sm.get_measurement_display(wd.get('snow_depth', 0), "length_m") # Depth usually m
        self._draw_data(screen, "Snow Depth", snow_depth_val, col1_x, y)
        y += line_height
        
        daily_precip = sm.get_measurement_display(wd.get('daily_precip_sum', 0), "length_mm")
        self._draw_data(screen, "Daily Total", daily_precip, col1_x, y)
        y += line_height + 10

        # WIND
        self._draw_category(screen, "WIND", col1_x, y)
        y += 22
        
        wind_spd = sm.get_measurement_display(wd.get('wind_speed_10m', wd.get('wind_speed', 0)), "speed")
        self._draw_data(screen, "Speed (10m)", wind_spd, col1_x, y, (150, 255, 200))
        y += line_height
        
        gusts = sm.get_measurement_display(wd.get('wind_gusts', 0), "speed")
        self._draw_data(screen, "Gusts", gusts, col1_x, y)
        y += line_height
        self._draw_data(screen, "Direction", f"{wd.get('wind_dir_10m', wd.get('wind_dir', 0))}°", col1_x, y)
        
        # --- COLUMN 2 ---
        y = content_y
        
        # SOLAR & UV
        self._draw_category(screen, "SOLAR & UV", col2_x, y)
        y += 22
        self._draw_data(screen, "Solar Rad.", f"{wd.get('shortwave_radiation', 0):.0f} W/m²", col2_x, y, (255, 200, 100))
        y += line_height
        self._draw_data(screen, "Direct/Diffuse", f"{wd.get('direct_normal_irradiance', 0):.0f} / {wd.get('diffuse_radiation', 0):.0f}", col2_x, y)
        y += line_height
        self._draw_data(screen, "UV Index", f"{wd.get('uv_index', 0):.1f}", col2_x, y, (200, 100, 255))
        y += line_height
        self._draw_data(screen, "Sunshine", f"{wd.get('sunshine_duration', 0)/3600:.1f} hrs", col2_x, y)
        y += line_height + 10
        
        # ADVANCED
        self._draw_category(screen, "ADVANCED", col2_x, y)
        y += 22
        self._draw_data(screen, "CAPE", f"{wd.get('cape', 0):.0f} J/kg", col2_x, y, (255, 100, 100))
        y += line_height
        
        et0 = sm.get_measurement_display(wd.get('et0', 0), "length_mm")
        self._draw_data(screen, "Evapotrans.", et0, col2_x, y)
        y += line_height
        
        freezing_lvl = sm.get_measurement_display(wd.get('freezing_level', 0), "length_m")
        self._draw_data(screen, "Freezing Lvl", freezing_lvl, col2_x, y)
        y += line_height
        self._draw_data(screen, "Soil Moist.", f"{wd.get('soil_moisture', 0):.2f} m³/m³", col2_x, y)
        y += line_height + 10
        
        # AIR QUALITY
        self._draw_category(screen, "AIR QUALITY", col2_x, y)
        y += 22
        self._draw_data(screen, "US AQI", f"{wd.get('us_aqi', 0)}", col2_x, y, (100, 255, 100))
        y += line_height
        self._draw_data(screen, "PM 2.5", f"{wd.get('pm2_5', 0):.1f} µg/m³", col2_x, y)
        y += line_height
        self._draw_data(screen, "Ozone", f"{wd.get('ozone', 0):.1f} µg/m³", col2_x, y)
        y += line_height + 10
        
        # SEARCH UI (Bottom)
        # City search results appear ABOVE search box
        # Position them at the bottom of the panel
        search_area_y = self.rect.y + self.rect.height - 120
        
        if self.search_results:
            # Calculate height needed for results
            results_h = len(self.search_results) * 43 + 30
            results_start_y = search_area_y - results_h
            
            # Draw background for results so they don't overlap text
            results_bg_rect = pygame.Rect(self.rect.x + 20, results_start_y, self.rect.width - 40, results_h)
            pygame.draw.rect(screen, (20, 25, 35), results_bg_rect)
            pygame.draw.rect(screen, (50, 60, 80), results_bg_rect, 1)
            
            results_label = self.font_small.render(f"{len(self.search_results)} results:", True, (200, 200, 200))
            screen.blit(results_label, (self.rect.x + 30, results_start_y + 5))
            
            # Position and render city buttons
            btn_spacing = 8
            btn_start_y = results_start_y + 25
            for i, btn in enumerate(self.city_buttons):
                btn.rect.x = self.rect.x + 30
                btn.rect.y = btn_start_y + i * (35 + btn_spacing)
                btn.rect.width = self.rect.width - 60 # Update width
                btn.render(screen)
            
        # Search field label and input
        search_label = self.font_med.render("Search for any city:", True, (255, 255, 255))
        screen.blit(search_label, (self.rect.x + 30, search_area_y))
        
        # Update search input position dynamically
        self.search_input.rect.x = self.rect.x + 30
        self.search_input.rect.y = search_area_y + 30
        self.search_input.rect.width = self.rect.width - 60
        
        # Render search input
        self.search_input.render(screen)
        
        # Update travel button position if it exists
        if self.travel_button:
            self.travel_button.rect.x = self.rect.right - 250
            self.travel_button.rect.y = self.rect.y + 60
            self.travel_button.render(screen)
        
        # Render close button
        self.close_button.rect.x = self.rect.right - 40
        self.close_button.render(screen)
    
    def _draw_category(self, screen, title, x, y):
        """Draw a category header."""
        surf = self.font_small.render(title, True, (100, 200, 255))
        screen.blit(surf, (x, y))
    
    def _draw_data(self, screen, label, value, x, y, color=(200, 200, 200)):
        """Draw a data row."""
        label_surf = self.font_small.render(f"{label}:", True, (150, 150, 150))
        value_surf = self.font_small.render(str(value), True, color)
        screen.blit(label_surf, (x + 5, y))
        screen.blit(value_surf, (x + 250, y))
    
    def _draw_text(self, screen, text, x, y, color=(255, 255, 255), font=None):
        """Draw plain text."""
        if font is None:
            font = self.font_small
        surf = font.render(text, True, color)
        screen.blit(surf, (x, y))
    
    def _get_condition_text(self, code):
        """Convert weather code to readable condition."""
        if code == 0: return "Clear"
        elif code <= 3: return "Partly Cloudy" if code < 3 else "Cloudy"
        elif code <= 48: return "Foggy"
        elif code <= 67: return "Drizzle/Rain"
        elif code <= 77: return "Snow"
        elif code <= 82: return "Showers"
        elif code <= 86: return "Snow Showers"
        elif code <= 94: return "Thunderstorm"
        else: return "Severe Storm"
    
    def _render_forecast(self, screen):
        """Render the 7-day forecast view."""
        sm = self.game_ref.settings_manager
        
        # Title
        title = self.font_med.render("7-Day Weather Forecast", True, (100, 200, 255))
        screen.blit(title, (self.rect.x + 30, self.rect.y + 95))
        
        if not self.forecast_data:
            loading = self.font_small.render("Loading forecast...", True, (180, 180, 180))
            screen.blit(loading, (self.rect.x + 30, self.rect.y + 130))
            return
        
        # Calculate card dimensions to fill space
        # Overlay is 900px wide with 30px padding = 840 available
        # 7 cards with 6 gaps between them
        spacing = 6
        available_width = self.rect.width - 60  # 30px padding each side
        card_width = (available_width - (6 * spacing)) // 7  # ~118px each
        card_height = 320  # Taller to fill vertical space
        start_x = self.rect.x + 30
        start_y = self.rect.y + 130
        
        # Parse day names
        import datetime
        
        for i, day in enumerate(self.forecast_data[:7]):
            card_x = start_x + i * (card_width + spacing)
            card_y = start_y
            
            # Card background
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            pygame.draw.rect(screen, (30, 40, 55), card_rect, border_radius=10)
            pygame.draw.rect(screen, (70, 90, 120), card_rect, 2, border_radius=10)
            
            # Parse date
            try:
                date_obj = datetime.datetime.strptime(day['date'], "%Y-%m-%d")
                day_name = date_obj.strftime("%a")  # Mon, Tue, etc.
                date_str = date_obj.strftime("%m/%d")
            except:
                day_name = f"Day {i+1}"
                date_str = ""
            
            # Today highlight
            if i == 0:
                pygame.draw.rect(screen, (60, 100, 160), card_rect, border_radius=10)
                day_name = "Today"
            
            # Day name
            day_surf = self.font_med.render(day_name, True, (255, 255, 255))
            day_rect = day_surf.get_rect(centerx=card_x + card_width // 2, y=card_y + 8)
            screen.blit(day_surf, day_rect)
            
            # Date
            if date_str:
                date_surf = self.font_small.render(date_str, True, (150, 150, 150))
                date_rect = date_surf.get_rect(centerx=card_x + card_width // 2, y=card_y + 30)
                screen.blit(date_surf, date_rect)
            
            
            # Weather condition (text + color indicator)
            weather_code = day.get('weather_code', 0)
            condition_text, condition_color = self._get_weather_condition(weather_code)
            
            # Draw custom weather icon
            indicator_x = card_x + card_width // 2
            indicator_y = card_y + 58
            self._draw_weather_icon(screen, indicator_x, indicator_y, weather_code)
            
            # Condition text
            cond_surf = self.font_small.render(condition_text, True, (220, 220, 220))
            cond_rect = cond_surf.get_rect(centerx=card_x + card_width // 2, y=card_y + 95)
            screen.blit(cond_surf, cond_rect)
            
            # High temp (larger font for emphasis)
            high_c = day.get('temp_max', 0)
            high_str = sm.get_measurement_display(high_c, "temp")
            high_surf = self.font_title.render(high_str, True, (255, 150, 100))
            high_rect = high_surf.get_rect(centerx=card_x + card_width // 2, y=card_y + 125)
            screen.blit(high_surf, high_rect)
            
            # Low temp
            low_c = day.get('temp_min', 0)
            low_str = sm.get_measurement_display(low_c, "temp")
            low_surf = self.font_med.render(low_str, True, (100, 150, 255))
            low_rect = low_surf.get_rect(centerx=card_x + card_width // 2, y=card_y + 170)
            screen.blit(low_surf, low_rect)
            
            # Separator line
            sep_y = card_y + 205
            pygame.draw.line(screen, (60, 70, 90), 
                           (card_x + 10, sep_y), (card_x + card_width - 10, sep_y), 1)
            
            # Precipitation probability
            precip = day.get('precip_prob', 0)
            precip_text = f"Precip: {precip:.0f}%" if precip else "Precip: 0%"
            precip_surf = self.font_small.render(precip_text, True, (100, 200, 255))
            precip_rect = precip_surf.get_rect(centerx=card_x + card_width // 2, y=card_y + 225)
            screen.blit(precip_surf, precip_rect)
            
            # Wind
            wind = day.get('wind_max', 0)
            wind_str = sm.get_measurement_display(wind, "speed")
            wind_surf = self.font_small.render(f"Wind: {wind_str}", True, (150, 200, 150))
            wind_rect = wind_surf.get_rect(centerx=card_x + card_width // 2, y=card_y + 250)
            screen.blit(wind_surf, wind_rect)
            
            # UV Index
            uv = day.get('uv_max', 0)
            uv_color = (255, 200, 100) if uv < 6 else (255, 100, 100)
            uv_surf = self.font_small.render(f"UV: {uv:.1f}", True, uv_color)
            uv_rect = uv_surf.get_rect(centerx=card_x + card_width // 2, y=card_y + 275)
            screen.blit(uv_surf, uv_rect)
    
    def _draw_weather_icon(self, screen, cx, cy, code):
        """Draw vector weather icon centered at (cx, cy)."""
        # Icon configuration
        sun_color = (255, 220, 50)
        cloud_color = (200, 200, 200)
        dark_cloud_color = (150, 150, 160)
        rain_color = (70, 130, 255)
        snow_color = (240, 240, 255)
        bolt_color = (255, 200, 50)
        
        def draw_sun(x, y, r):
            pygame.draw.circle(screen, sun_color, (x, y), r)
            # Rays
            for i in range(8):
                angle = i * (360 / 8)
                import math
                rad = math.radians(angle)
                start_dist = r + 2
                end_dist = r + 6
                start_pos = (x + math.cos(rad) * start_dist, y + math.sin(rad) * start_dist)
                end_pos = (x + math.cos(rad) * end_dist, y + math.sin(rad) * end_dist)
                pygame.draw.line(screen, sun_color, start_pos, end_pos, 2)

        def draw_cloud(x, y, color):
            # Overlapping circles to make a cloud shape
            # Center circle
            pygame.draw.circle(screen, color, (x, y), 10)
            # Left circle
            pygame.draw.circle(screen, color, (x - 8, y + 2), 7)
            # Right circle
            pygame.draw.circle(screen, color, (x + 8, y + 2), 7)
            # Top bubble
            pygame.draw.circle(screen, color, (x - 2, y - 6), 6)

        def draw_rain(x, y):
            start_y = y + 8
            pygame.draw.line(screen, rain_color, (x - 4, start_y), (x - 6, start_y + 8), 2)
            pygame.draw.line(screen, rain_color, (x, start_y), (x - 2, start_y + 8), 2)
            pygame.draw.line(screen, rain_color, (x + 4, start_y), (x + 2, start_y + 8), 2)

        def draw_snow(x, y):
            start_y = y + 8
            pygame.draw.circle(screen, snow_color, (x - 5, start_y + 4), 2)
            pygame.draw.circle(screen, snow_color, (x, start_y + 6), 2)
            pygame.draw.circle(screen, snow_color, (x + 5, start_y + 4), 2)

        def draw_bolt(x, y):
            start_y = y + 5
            points = [
                (x + 2, start_y),
                (x - 4, start_y + 6),
                (x, start_y + 6),
                (x - 2, start_y + 14)
            ]
            pygame.draw.lines(screen, bolt_color, False, points, 2)

        # Draw based on code
        if code == 0:  # Clear
            draw_sun(cx, cy, 10)
        
        elif code <= 2:  # Partly Cloudy
            draw_sun(cx - 6, cy - 6, 8)
            draw_cloud(cx + 4, cy + 4, (240, 240, 240))
            
        elif code == 3:  # Overcast
            draw_cloud(cx, cy, dark_cloud_color)
            
        elif code <= 48:  # Fog
            draw_cloud(cx, cy, (180, 180, 190))
            pygame.draw.line(screen, (180, 180, 190), (cx - 10, cy + 12), (cx + 10, cy + 12), 2)
            
        elif code <= 67:  # Rain
            draw_cloud(cx, cy, dark_cloud_color)
            draw_rain(cx, cy)
            
        elif code <= 77:  # Snow
            draw_cloud(cx, cy, (200, 200, 210))
            draw_snow(cx, cy)
            
        elif code <= 82:  # Showers
            draw_cloud(cx - 4, cy - 2, dark_cloud_color)
            draw_sun(cx + 6, cy - 8, 6)
            draw_rain(cx, cy)
            
        elif code <= 86:  # Snow showers
            draw_cloud(cx, cy, dark_cloud_color)
            draw_snow(cx, cy)
            
        elif code <= 99:  # Thunderstorm
            draw_cloud(cx, cy, (80, 80, 90))
            draw_bolt(cx, cy)
            
        else:
            # Fallback
            pygame.draw.circle(screen, (100, 100, 100), (cx, cy), 10, 1)
    
    def _get_weather_condition(self, code):
        """Return condition text and color for weather code."""
        # Colors: Yellow=sunny, Gray=cloudy, LightBlue=rain, White=snow, Orange=storm
        if code == 0:
            return ("Clear", (255, 220, 100))  # Yellow
        elif code <= 2:
            return ("Partly Cloudy", (200, 200, 150))  # Light yellow-gray
        elif code == 3:
            return ("Cloudy", (150, 150, 160))  # Gray
        elif code <= 48:
            return ("Foggy", (180, 180, 190))  # Light gray
        elif code <= 55:
            return ("Drizzle", (100, 150, 200))  # Light blue
        elif code <= 67:
            return ("Rain", (70, 130, 200))  # Blue
        elif code <= 77:
            return ("Snow", (220, 230, 255))  # White-blue
        elif code <= 82:
            return ("Showers", (80, 140, 220))  # Blue
        elif code <= 86:
            return ("Snow Showers", (200, 210, 240))  # Light blue-white
        elif code <= 94:
            return ("Thunder", (255, 180, 80))  # Orange
        else:
            return ("Storm", (255, 100, 100))  # Red

