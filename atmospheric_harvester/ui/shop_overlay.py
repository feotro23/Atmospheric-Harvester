import pygame
from .theme import Theme
from .ui_manager import UIElement, Button
from game.farming import ALL_CROPS

class ShopOverlay(UIElement):
    def __init__(self, screen_width, screen_height, game_ref):
        # Center overlay
        w = 700
        h = 600
        x = (screen_width - w) // 2
        y = (screen_height - h) // 2
        super().__init__(x, y, w, h)
        
        self.game_ref = game_ref
        self.settings_manager = game_ref.settings_manager
        self.visible = False
        
        self.font_title = Theme.get_font(32)
        self.font_name = Theme.get_font(20)
        self.font_price = Theme.get_font(18)
        self.font_small = Theme.get_font(16)
        
        # Close button
        self.close_button = Button(self.rect.right - 40, self.rect.y + 10, 30, 30, "X", self.close)
        
        # Buy Buttons
        self.buy_buttons = []
        # Layout grid
        cols = 3
        spacing_x = 220
        spacing_y = 200
        start_x = self.rect.x + 30
        start_y = self.rect.y + 80
        
        for i, crop in enumerate(ALL_CROPS):
            c_idx = i % cols
            r_idx = i // cols
            
            bx = start_x + (c_idx * spacing_x)
            by = start_y + (r_idx * spacing_y) + 140 # Position button at bottom of card
            
            btn = Button(bx, by, 180, 40, f"Buy ({crop.seed_cost} Cr)", lambda c=crop: self.buy_seed(c))
            self.buy_buttons.append(btn)
            
    def open(self):
        self.visible = True
        
    def close(self):
        self.visible = False
        
    def buy_seed(self, crop_type):
        cost = crop_type.seed_cost
        if self.game_ref.state.resources.credits >= cost:
            self.game_ref.state.resources.credits -= cost
            self.game_ref.state.seeds[crop_type.name] = self.game_ref.state.seeds.get(crop_type.name, 0) + 1
            # Optional: Play sound
            return True
        return False
        
    def handle_event(self, event):
        if not self.visible:
            return False
            
        if self.close_button.handle_event(event):
            return True
            
        for btn in self.buy_buttons:
            if btn.handle_event(event):
                return True
            
        # ESC to close
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.close()
            return True
            
        # Consume clicks on overlay
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
                
        return False
        
    def render(self, screen):
        if not self.visible:
            return
            
        # Dim background
        overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 200), overlay.get_rect())
        screen.blit(overlay, (0, 0))
        
        # Panel
        pygame.draw.rect(screen, (30, 30, 40), self.rect, border_radius=15)
        pygame.draw.rect(screen, (100, 100, 150), self.rect, 2, border_radius=15)
        
        # Title
        title = self.font_title.render("Seed Shop", True, (255, 255, 255))
        screen.blit(title, (self.rect.x + 30, self.rect.y + 20))
        
        # Credits Display
        credits_text = f"Credits: {int(self.game_ref.state.resources.credits)}"
        c_surf = self.font_name.render(credits_text, True, (255, 215, 0))
        screen.blit(c_surf, (self.rect.right - c_surf.get_width() - 60, self.rect.y + 25))
        
        # Close button
        self.close_button.render(screen)
        
        # Render Crops Grid
        cols = 3
        spacing_x = 220
        spacing_y = 200
        start_x = self.rect.x + 30
        start_y = self.rect.y + 80
        
        for i, crop in enumerate(ALL_CROPS):
            c_idx = i % cols
            r_idx = i // cols
            
            x = start_x + (c_idx * spacing_x)
            y = start_y + (r_idx * spacing_y)
            w = 200
            h = 190
            
            # Card Background
            pygame.draw.rect(screen, (50, 50, 60), (x, y, w, h), border_radius=10)
            pygame.draw.rect(screen, (80, 80, 90), (x, y, w, h), 1, border_radius=10)
            
            # Name
            name_surf = self.font_name.render(crop.name, True, (200, 255, 200))
            screen.blit(name_surf, (x + 10, y + 10))
            
            # Owned Count
            count = self.game_ref.state.seeds.get(crop.name, 0)
            cnt_color = (200, 200, 200)
            if count == 0: cnt_color = (150, 50, 50)
            cnt_surf = self.font_small.render(f"Owned: {count}", True, cnt_color)
            screen.blit(cnt_surf, (x + 10, y + 40))
            
            # GDD Info
            gdd_surf = self.font_small.render(f"GDD: {crop.base_gdd}", True, (150, 150, 150))
            screen.blit(gdd_surf, (x + 10, y + 60))
            
            # Temp Range (using settings)
            min_t = self.settings_manager.get_measurement_display(crop.optimal_temp_min, "temp")
            max_t = self.settings_manager.get_measurement_display(crop.optimal_temp_max, "temp")
            temp_surf = self.font_small.render(f"{min_t} - {max_t}", True, (150, 150, 150))
            screen.blit(temp_surf, (x + 10, y + 80))
            
            # Water Need
            water_surf = self.font_small.render(f"Water: > {int(crop.water_need*100)}%", True, (150, 150, 255))
            screen.blit(water_surf, (x + 10, y + 100))
            
            # Render Buy Button
            btn = self.buy_buttons[i]
            # Update button state based on credits
            can_afford = self.game_ref.state.resources.credits >= crop.seed_cost
            if can_afford:
                btn.bg_color = (50, 150, 50)
                btn.text_color = (255, 255, 255)
            else:
                btn.bg_color = (100, 50, 50)
                btn.text_color = (150, 150, 150)
                
            btn.render(screen)
