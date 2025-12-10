import pygame
from .theme import Theme
from .ui_manager import UIElement, Button
from game.machines import TURBINE_TYPE, PANEL_TYPE, COLLECTOR_TYPE, BATTERY_TYPE, TANK_TYPE, SPRINKLER_TYPE, HEATER_TYPE, STABLE_TYPE

class BuildOverlay(UIElement):
    def __init__(self, screen_width, screen_height, game_ref, close_callback):
        # Center overlay
        w = 800
        h = 600
        x = (screen_width - w) // 2
        y = (screen_height - h) // 2
        super().__init__(x, y, w, h)
        
        self.game_ref = game_ref
        self.close_callback = close_callback
        self.visible = False
        
        self.font_title = Theme.get_font(32)
        self.font_med = Theme.get_font(20)
        self.font_small = Theme.get_font(16)
        
        # Close button
        self.close_button = Button(self.rect.right - 40, self.rect.y + 10, 30, 30, "X", self.close)
        
        # Machine List
        self.machines = [
            TURBINE_TYPE, PANEL_TYPE, COLLECTOR_TYPE, 
            BATTERY_TYPE, TANK_TYPE, SPRINKLER_TYPE, HEATER_TYPE, STABLE_TYPE
        ]
        
        self.buttons = []
        self._create_buttons()
        
    def _create_buttons(self):
        # Grid layout
        cols = 3
        start_x = self.rect.x + 30
        start_y = self.rect.y + 80
        w = 230
        h = 140
        gap_x = 20
        gap_y = 20
        
        for i, m_type in enumerate(self.machines):
            row = i // cols
            col = i % cols
            
            x = start_x + col * (w + gap_x)
            y = start_y + row * (h + gap_y)
            
            # We need a custom button or just a region?
            # Let's use a Button for the whole card for simplicity, 
            # or maybe a "Build" button inside a drawn card.
            # Let's draw cards manually in render and put a "Select" button in each.
            
            btn_x = x + 10
            btn_y = y + h - 40
            btn_w = w - 20
            btn_h = 30
            
            def make_cb(name):
                return lambda: self.select_machine(name)
            
            btn = Button(btn_x, btn_y, btn_w, btn_h, "Select", make_cb(m_type.name))
            self.buttons.append(btn)

    def select_machine(self, name):
        self.game_ref.build_selection = name
        print(f"Selected {name}")
        self.close()

    def close(self):
        self.visible = False
        if self.close_callback:
            self.close_callback()

    def open(self):
        self.visible = True

    def handle_event(self, event):
        if not self.visible:
            return False
            
        if self.close_button.handle_event(event):
            return True
            
        for btn in self.buttons:
            if btn.handle_event(event):
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
        title = self.font_title.render("Construction Menu", True, (255, 255, 255))
        screen.blit(title, (self.rect.x + 30, self.rect.y + 20))
        
        # Close
        self.close_button.render(screen)
        
        # Draw Machine Cards
        cols = 3
        start_x = self.rect.x + 30
        start_y = self.rect.y + 80
        w = 230
        h = 140
        gap_x = 20
        gap_y = 20
        
        for i, m_type in enumerate(self.machines):
            row = i // cols
            col = i % cols
            
            x = start_x + col * (w + gap_x)
            y = start_y + row * (h + gap_y)
            
            # Card Bg
            pygame.draw.rect(screen, (50, 55, 65), (x, y, w, h), border_radius=10)
            pygame.draw.rect(screen, (80, 85, 95), (x, y, w, h), 1, border_radius=10)
            
            # Name
            name_surf = self.font_med.render(m_type.name, True, (255, 255, 200))
            screen.blit(name_surf, (x + 10, y + 10))
            
            # Cost
            cost_text = f"Energy: {m_type.cost_energy} | Bio: {m_type.cost_biomass}"
            cost_surf = self.font_small.render(cost_text, True, (200, 200, 200))
            screen.blit(cost_surf, (x + 10, y + 35))
            
            # Description (Wrap?)
            # Simple truncation for now
            desc = m_type.description
            if len(desc) > 30: desc = desc[:27] + "..."
            desc_surf = self.font_small.render(desc, True, (150, 150, 150))
            screen.blit(desc_surf, (x + 10, y + 55))
            
            # Button is rendered by loop below
            
        # Render Buttons
        for btn in self.buttons:
            btn.render(screen)
