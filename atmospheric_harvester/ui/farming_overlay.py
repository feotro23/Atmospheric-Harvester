import pygame
from .theme import Theme
from game.farming import ALL_CROPS

class FarmingOverlay:
    def __init__(self, game, x, y, width, height):
        self.game = game
        self.state = game.state
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = False
        self.font_title = pygame.font.SysFont("Arial", 24, bold=True)
        self.font_text = pygame.font.SysFont("Arial", 16)
        self.font_small = pygame.font.SysFont("Arial", 14)
        
        # UI State
        self.selected_tab = "inventory" # inventory, seeds, soil
        self.scroll_y = 0
        
    def handle_event(self, event):
        if not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if not self.rect.collidepoint(mx, my):
                return False
                
            # Local coordinates
            lx = mx - self.rect.x
            ly = my - self.rect.y
            
            # Tab switching
            if ly < 40:
                if lx < self.rect.width / 3:
                    self.selected_tab = "inventory"
                elif lx < 2 * self.rect.width / 3:
                    self.selected_tab = "seeds"
                else:
                    self.selected_tab = "soil"
                return True
                
            # Content interaction
            if self.selected_tab == "seeds":
                # List starts at y=50, items are 40px tall
                list_y = ly - 50 + self.scroll_y
                index = int(list_y // 40)
                if 0 <= index < len(ALL_CROPS):
                    # Check if clicked on Plant button
                    # Button is at right side: x = width - 100, w = 80
                    btn_x = self.rect.width - 100
                    if lx > btn_x and lx < btn_x + 80:
                        # Plant clicked
                        crop = ALL_CROPS[index]
                        if self.state.seeds.get(crop.name, 0) > 0:
                            self.game.plant_selection = crop.name
                            self.visible = False # Close overlay
                            print(f"Selected {crop.name} for planting")
                            return True
                    
                    self.state.selected_seed_index = index
                    return True
            
            elif self.selected_tab == "inventory":
                # Buttons at bottom
                if ly > self.rect.height - 40:
                    btn_width = (self.rect.width - 20) // 2 - 5
                    
                    # Compost (Left)
                    if lx < 10 + btn_width:
                        self._compost_all()
                        return True
                    # Sell (Right)
                    elif lx > 10 + btn_width + 10:
                        self._sell_all()
                        return True

        elif event.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.scroll_y = max(0, self.scroll_y - event.y * 10)
                return True
                
        return False
        
    def _compost_all(self):
        # Convert all inventory to biomass
        total_biomass = 0
        for item, count in self.state.inventory.items():
            # Simple conversion: 1 item = 1 biomass
            total_biomass += count
        
        if total_biomass > 0:
            self.state.resources.add_biomass(total_biomass)
            self.state.inventory.clear()
            
            # Track for achievement
            if not hasattr(self.state, '_biomass_composted'):
                self.state._biomass_composted = 0
            self.state._biomass_composted += total_biomass
            
            print(f"Composted {total_biomass} items into biomass.")

    def _sell_all(self):
        # Use Game logic
        success, msg = self.game.sell_inventory()
        print(msg)

    def render(self, screen):
        if not self.visible:
            return
            
        # Background
        pygame.draw.rect(screen, Theme.BACKGROUND, self.rect)
        pygame.draw.rect(screen, (100, 100, 150), self.rect, 2)
        
        # Tabs
        tab_w = self.rect.width / 3
        tabs = ["Inventory", "Seeds", "Soil"]
        for i, tab in enumerate(tabs):
            color = Theme.ACCENT_KINETIC if self.selected_tab.lower() == tab.lower() else Theme.PANEL_BG
            r = pygame.Rect(self.rect.x + i * tab_w, self.rect.y, tab_w, 40)
            pygame.draw.rect(screen, color, r)
            pygame.draw.rect(screen, (100, 100, 150), r, 1)
            
            text = self.font_text.render(tab, True, Theme.TEXT_MAIN)
            screen.blit(text, (r.centerx - text.get_width()//2, r.centery - text.get_height()//2))
            
        # Content Area
        content_rect = pygame.Rect(self.rect.x + 10, self.rect.y + 50, self.rect.width - 20, self.rect.height - 60)
        
        if self.selected_tab == "inventory":
            self._render_inventory(screen, content_rect)
        elif self.selected_tab == "seeds":
            self._render_seeds(screen, content_rect)
        elif self.selected_tab == "soil":
            self._render_soil(screen, content_rect)
            
    def _render_inventory(self, screen, rect):
        y = rect.y
        if not self.state.inventory:
            text = self.font_text.render("Inventory Empty", True, Theme.TEXT_DIM)
            screen.blit(text, (rect.x, y))
        else:
            for item, count in self.state.inventory.items():
                text = self.font_text.render(f"{item.title()}: {count}", True, Theme.TEXT_MAIN)
                screen.blit(text, (rect.x, y))
                y += 25
                
        # Buttons
        btn_width = rect.width // 2 - 5
        
        # Compost Button
        compost_rect = pygame.Rect(rect.x, self.rect.bottom - 40, btn_width, 30)
        pygame.draw.rect(screen, (100, 200, 100), compost_rect, border_radius=5)
        text = self.font_text.render("Compost (+Bio)", True, (0, 50, 0))
        screen.blit(text, (compost_rect.centerx - text.get_width()//2, compost_rect.centery - text.get_height()//2))
        
        # Sell Button
        sell_rect = pygame.Rect(rect.x + btn_width + 10, self.rect.bottom - 40, btn_width, 30)
        pygame.draw.rect(screen, (200, 200, 100), sell_rect, border_radius=5)
        text = self.font_text.render("Sell (+Cr)", True, (50, 50, 0))
        screen.blit(text, (sell_rect.centerx - text.get_width()//2, sell_rect.centery - text.get_height()//2))

    def _render_seeds(self, screen, rect):
        y = rect.y - self.scroll_y
        for i, crop in enumerate(ALL_CROPS):
            # Highlight selected
            is_selected = (i == self.state.selected_seed_index)
            color = (60, 60, 80) if is_selected else Theme.PANEL_BG
            
            item_rect = pygame.Rect(rect.x, y, rect.width, 35)
            if item_rect.bottom < rect.y or item_rect.top > rect.bottom:
                y += 40
                continue
                
            pygame.draw.rect(screen, color, item_rect, border_radius=5)
            if is_selected:
                pygame.draw.rect(screen, Theme.ACCENT_KINETIC, item_rect, 2, border_radius=5)
            
            # Name and Count
            count = self.state.seeds.get(crop.name, 0)
            name_text = self.font_text.render(f"{crop.name} ({count})", True, Theme.TEXT_MAIN)
            screen.blit(name_text, (rect.x + 10, y + 8))
            
            # Info
            sm = self.game.settings_manager
            min_t = sm.get_measurement_display(crop.optimal_temp_min, "temp")
            max_t = sm.get_measurement_display(crop.optimal_temp_max, "temp")
            
            info = f"Water: {crop.water_need*100:.0f}% | Temp: {min_t}-{max_t}"
            info_text = self.font_small.render(info, True, Theme.TEXT_DIM)
            screen.blit(info_text, (rect.x + 200, y + 10))
            
            # Plant Button
            if count > 0:
                btn_rect = pygame.Rect(rect.right - 90, y + 5, 80, 25)
                pygame.draw.rect(screen, (50, 150, 50), btn_rect, border_radius=5)
                btn_text = self.font_small.render("Plant", True, (200, 255, 200))
                screen.blit(btn_text, (btn_rect.centerx - btn_text.get_width()//2, btn_rect.centery - btn_text.get_height()//2))
            
            y += 40

    def _render_soil(self, screen, rect):
        y = rect.y
        
        # Current Conditions
        sm = self.game.settings_manager
        
        soil_temp_str = sm.get_measurement_display(self.state.soil_temp, "temp")
        air_temp_str = sm.get_measurement_display(self.state.temp_c, "temp")
        snow_depth_str = sm.get_measurement_display(self.state.snow_depth, "length_m")
        wind_speed_str = sm.get_measurement_display(self.state.wind_speed, "speed_kmh") # Note: state.wind_speed is usually m/s, but display said km/h. Let's assume m/s and use speed type.
        # Update: state.wind_speed is now correctly m/s from API.
        wind_speed_str = sm.get_measurement_display(self.state.wind_speed, "speed")
        
        stats = [
            f"Soil Moisture: {self.state.soil_moisture*100:.1f}%",
            f"Soil Temp: {soil_temp_str}",
            f"Air Temp: {air_temp_str}",
            f"UV Index: {self.state.uv_index:.1f}",
            f"Snow Depth: {snow_depth_str}",
            f"Wind Speed: {wind_speed_str}"
        ]
        
        for stat in stats:
            text = self.font_text.render(stat, True, Theme.TEXT_MAIN)
            screen.blit(text, (rect.x, y))
            y += 25
            
        y += 20
        # Suitability Guide
        header = self.font_title.render("Crop Suitability:", True, Theme.ACCENT_KINETIC)
        screen.blit(header, (rect.x, y))
        y += 30
        
        for crop in ALL_CROPS:
            # Check if suitable
            suitable = True
            reasons = []
            
            if self.state.soil_moisture < crop.water_need:
                suitable = False
                reasons.append("Too Dry")
            if not (crop.optimal_temp_min <= self.state.temp_c <= crop.optimal_temp_max):
                suitable = False
                reasons.append("Bad Temp")
            
            # Check wind tolerance
            if hasattr(crop, 'wind_tolerance') and self.state.wind_speed > crop.wind_tolerance:
                 suitable = False
                 reasons.append("Too Windy")
                
            color = (100, 255, 100) if suitable else (255, 100, 100)
            status = "Good" if suitable else f"Poor ({', '.join(reasons)})"
            
            text = self.font_small.render(f"{crop.name}: {status}", True, color)
            screen.blit(text, (rect.x, y))
            y += 20
