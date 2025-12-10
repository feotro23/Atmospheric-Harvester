import pygame
from .theme import Theme
from .ui_manager import UIElement, Button

class SettingsOverlay(UIElement):
    def __init__(self, screen_width, screen_height, settings_manager):
        # Center overlay
        w = 500
        h = 400
        x = (screen_width - w) // 2
        y = (screen_height - h) // 2
        super().__init__(x, y, w, h)
        
        self.settings_manager = settings_manager
        self.visible = False
        
        self.font_title = Theme.get_font(32)
        self.font_med = Theme.get_font(20)
        self.font_small = Theme.get_font(16)
        
        # Close button
        self.close_button = Button(self.rect.right - 40, self.rect.y + 10, 30, 30, "X", self.close)
        
        # System Toggle
        self.system_button = Button(
            self.rect.x + 150, self.rect.y + 100, 200, 50, 
            "Toggle System", self.toggle_system
        )
        
        # Volume buttons
        self.vol_down_button = Button(
            self.rect.x + 150, self.rect.y + 200, 60, 50,
            "-", self.decrease_volume
        )
        
        self.vol_up_button = Button(
            self.rect.x + 290, self.rect.y + 200, 60, 50,
            "+", self.increase_volume
        )
        
    def toggle_system(self):
        self.settings_manager.toggle_system()
        # Button text updates in render loop based on state or we can set it here
        # But render loop is safer if state changes elsewhere
        pass
            
    def decrease_volume(self):
        new_vol = self.settings_manager.volume - 0.1
        self.settings_manager.set_volume(new_vol)
        
    def increase_volume(self):
        new_vol = self.settings_manager.volume + 0.1
        self.settings_manager.set_volume(new_vol)
        
    def open(self):
        self.visible = True
        
    def close(self):
        self.visible = False
        
    def handle_event(self, event):
        if not self.visible:
            return False
            
        if self.close_button.handle_event(event):
            return True
            
        if self.system_button.handle_event(event):
            return True
            
        if self.vol_down_button.handle_event(event):
            return True
            
        if self.vol_up_button.handle_event(event):
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
        pygame.draw.rect(screen, (30, 35, 45), self.rect, border_radius=15)
        pygame.draw.rect(screen, (100, 100, 120), self.rect, 2, border_radius=15)
        
        # Title
        title = self.font_title.render("Settings", True, (255, 255, 255))
        screen.blit(title, (self.rect.x + 30, self.rect.y + 20))
        
        # Close button
        self.close_button.render(screen)
        
        # System Section
        sys_label = self.font_med.render("Measurement System:", True, (200, 200, 200))
        screen.blit(sys_label, (self.rect.x + 30, self.rect.y + 80))
        
        current_sys = self.font_small.render(f"Current: {self.settings_manager.system}", True, (150, 200, 255))
        screen.blit(current_sys, (self.rect.x + 30, self.rect.y + 110))
        
        # Update button text
        target_sys = "Imperial" if self.settings_manager.system == "Metric" else "Metric"
        self.system_button.text = f"Switch to {target_sys}"
        self.system_button.render(screen)
        
        # Volume Section
        vol_label = self.font_med.render("Volume:", True, (200, 200, 200))
        screen.blit(vol_label, (self.rect.x + 30, self.rect.y + 180))
        
        vol_display = self.font_small.render(f"{int(self.settings_manager.volume * 100)}%", True, (150, 200, 255))
        screen.blit(vol_display, (self.rect.x + 220, self.rect.y + 210))
        
        self.vol_down_button.render(screen)
        self.vol_up_button.render(screen)
        
        # Volume bar
        bar_x = self.rect.x + 150
        bar_y = self.rect.y + 270
        bar_w = 200
        bar_h = 20
        
        # Background
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h), border_radius=10)
        
        # Fill
        fill_w = int(bar_w * self.settings_manager.volume)
        pygame.draw.rect(screen, (100, 200, 100), (bar_x, bar_y, fill_w, bar_h), border_radius=10)
