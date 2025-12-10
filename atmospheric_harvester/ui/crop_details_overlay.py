import pygame
from .theme import Theme
from .ui_manager import UIElement, Button

class CropDetailsOverlay(UIElement):
    def __init__(self, screen_width, screen_height, game_ref, assets=None):
        # Center overlay
        w = 500
        h = 450
        x = (screen_width - w) // 2
        y = (screen_height - h) // 2
        super().__init__(x, y, w, h)
        
        self.game_ref = game_ref
        self.assets = assets or {}
        self.visible = False
        self.target_crop = None
        
        self.font_title = Theme.get_font(24)
        self.font_text = Theme.get_font(18)
        self.font_small = Theme.get_font(16)
        
        # Close button
        self.close_button = Button(self.rect.right - 35, self.rect.y + 10, 25, 25, "X", self.close)
        
        # Harvest Button (Dynamic)
        self.harvest_button = Button(self.rect.centerx - 60, self.rect.bottom - 60, 120, 40, "Harvest", self.harvest)
        self.harvest_button.visible = False # Hidden by default

        # Remove Button (For dead crops)
        self.remove_button = Button(self.rect.centerx - 60, self.rect.bottom - 60, 120, 40, "Remove", self.remove_plant)
        self.remove_button.visible = False
        
    def open(self, crop):
        self.target_crop = crop
        self.visible = True
        self.update_buttons()
        
    def close(self):
        self.visible = False
        self.target_crop = None
        
    def harvest(self):
        if self.target_crop and self.target_crop.stage >= 3:
            success = self.game_ref.harvest_crop(self.target_crop)
            if success:
                self.close()

    def remove_plant(self):
        if self.target_crop and self.target_crop.state == "Dead":
            success = self.game_ref.remove_crop(self.target_crop)
            if success:
                self.close()
            
    def update_buttons(self):
        if self.target_crop:
            self.harvest_button.visible = False
            self.remove_button.visible = False
            
            if self.target_crop.state == "Dead":
                 self.remove_button.visible = True
                 self.remove_button.bg_color = (150, 50, 50) # Red
            elif self.target_crop.stage >= 3:
                self.harvest_button.visible = True
                self.harvest_button.text = "Harvest!"
                self.harvest_button.bg_color = (50, 150, 50)
                
    def handle_event(self, event):
        if not self.visible:
            return False
            
        if self.close_button.handle_event(event):
            return True
            
        if self.harvest_button.visible and self.harvest_button.handle_event(event):
            return True

        if self.remove_button.visible and self.remove_button.handle_event(event):
            return True
            
        # Consume clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
                
        return False
        
    def render(self, screen):
        if not self.visible or not self.target_crop:
            return
            
        # Panel
        pygame.draw.rect(screen, (35, 45, 35), self.rect, border_radius=15)
        pygame.draw.rect(screen, (100, 150, 100), self.rect, 2, border_radius=15)
        
        # Title
        name = self.target_crop.type.name
        title = self.font_title.render(name, True, (255, 255, 255))
        screen.blit(title, (self.rect.centerx - title.get_width() // 2, self.rect.y + 20))
        
        # Icon/Visual if available
        # TODO: Render icon here
        
        # Status
        status = self.target_crop.state
        status_color = (100, 255, 100)
        if status == "Dead": status_color = (255, 50, 50)
        elif status == "Dormant": status_color = (150, 150, 200)
        
        status_surf = self.font_text.render(f"Status: {status}", True, status_color)
        screen.blit(status_surf, (self.rect.x + 30, self.rect.y + 70))
        
        # Health
        health_text = f"Health: {int(self.target_crop.health)}%"
        h_color = (100, 255, 100) if self.target_crop.health > 80 else (255, 200, 50)
        if self.target_crop.health < 40: h_color = (255, 50, 50)
        
        health_surf = self.font_text.render(health_text, True, h_color)
        screen.blit(health_surf, (self.rect.x + 30, self.rect.y + 100))
        
        # Current Conditions (Left Column)
        y_off_left = self.rect.y + 150
        screen.blit(self.font_text.render("Current Status:", True, (200, 200, 255)), (self.rect.x + 30, y_off_left))
        y_off_left += 30
        
        # Current Temp
        c_temp = self.target_crop.current_temp
        c_temp_val = self.game_ref.settings_manager.get_measurement_display(c_temp, "temp")
        c_temp_str = f"Temp: {c_temp_val}"
        screen.blit(self.font_small.render(c_temp_str, True, (255, 255, 255)), (self.rect.x + 30, y_off_left))
        y_off_left += 25
        
        # Current Moisture
        c_moist = self.target_crop.current_moisture * 100
        c_moist_str = f"Moisture: {c_moist:.0f}%"
        screen.blit(self.font_small.render(c_moist_str, True, (255, 255, 255)), (self.rect.x + 30, y_off_left))
        
        # Optimal Conditions Section
        # Move to right side
        left_col_x = self.rect.x + 30
        right_col_x = self.rect.centerx + 10
        
        y_off = self.rect.y + 70 # Align top with Status/Health
        
        screen.blit(self.font_text.render("Optimal Conditions:", True, (255, 255, 150)), (right_col_x, y_off))
        y_off += 30
        
        type_data = self.target_crop.type
        
        # Temp
        min_t_str = self.game_ref.settings_manager.get_measurement_display(type_data.optimal_temp_min, "temp")
        max_t_str = self.game_ref.settings_manager.get_measurement_display(type_data.optimal_temp_max, "temp")
        temp_range = f"Temp: {min_t_str} - {max_t_str}"
        t_color = (200, 200, 200)
        # Check against LOCAL crop temp, not global
        curr_temp = self.target_crop.current_temp
        if curr_temp < type_data.optimal_temp_min or curr_temp > type_data.optimal_temp_max:
             t_color = (255, 100, 100) # Warning color
             
        screen.blit(self.font_small.render(temp_range, True, t_color), (right_col_x + 10, y_off))
        y_off += 25
        
        # Water
        water_req = f"Water Need: > {int(type_data.water_need * 100)}% Soil Moisture"
        # Check against LOCAL crop moisture
        curr_moisture = self.target_crop.current_moisture
        w_req_color = (200, 200, 200)
        if curr_moisture < type_data.water_need:
             w_req_color = (255, 100, 100)
        
        screen.blit(self.font_small.render(water_req, True, w_req_color), (right_col_x + 10, y_off))
        y_off += 25
        
        # Wind Tolerance
        wind_tol = f"Wind Tolerance: < {type_data.wind_tolerance} km/h"
        curr_wind = self.game_ref.state.wind_speed
        w_color = (200, 200, 200)
        if curr_wind > type_data.wind_tolerance:
            w_color = (255, 100, 100)
            
        screen.blit(self.font_small.render(wind_tol, True, w_color), (right_col_x + 10, y_off))
        y_off += 25

        # Chill Hours (Vernalization) - New Section
        if type_data.chill_hours_req > 0:
            chill_accum = self.target_crop.chill_hours_accumulated
            chill_req = type_data.chill_hours_req
            if chill_accum < chill_req:
                v_color = (100, 255, 255) # Cyan for cold requirement
                # Check if currently accumulating (Temp < 5°C)
                if self.target_crop.current_temp >= 5.0:
                    v_color = (255, 100, 100) # Warning: Too warm to chill!
                
                # Format threshold using settings
                thresh_str = self.game_ref.settings_manager.get_measurement_display(5.0, "temp")
                chill_text = f"Vernalization: {chill_accum:.1f} / {chill_req} Hours (< {thresh_str})"
                screen.blit(self.font_small.render(chill_text, True, v_color), (right_col_x + 10, y_off))
                y_off += 25
        
        # GDD / Progress
        # Ensure we are below both columns
        y_off = max(y_off, y_off_left) + 20
        
        pct = min(1.0, self.target_crop.accumulated_heat / type_data.base_gdd)
        # Draw bar
        bar_w = 300
        bar_h = 20
        pygame.draw.rect(screen, (50, 50, 50), (self.rect.x + 40, y_off, bar_w, bar_h))
        pygame.draw.rect(screen, (100, 200, 100), (self.rect.x + 40, y_off, int(bar_w * pct), bar_h))
        pygame.draw.rect(screen, (150, 150, 150), (self.rect.x + 40, y_off, bar_w, bar_h), 1)
        
        prog_text = f"Growth: {int(pct * 100)}%"
        p_surf = self.font_small.render(prog_text, True, (255, 255, 255))
        screen.blit(p_surf, (self.rect.x + 40 + bar_w // 2 - p_surf.get_width() // 2, y_off + 2))
        
        # Render Buttons
        self.close_button.rect.x = self.rect.right - 35
        self.close_button.rect.y = self.rect.y + 10
        self.close_button.render(screen)
        
        if self.harvest_button.visible:
             self.harvest_button.rect.centerx = self.rect.centerx
             self.harvest_button.rect.bottom = self.rect.bottom - 30
             self.harvest_button.render(screen)
             
        if self.remove_button.visible:
             self.remove_button.rect.centerx = self.rect.centerx
             self.remove_button.rect.bottom = self.rect.bottom - 30
             self.remove_button.render(screen)
