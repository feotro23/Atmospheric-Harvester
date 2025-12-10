import pygame
from .theme import Theme

class TravelOverlay:
    def __init__(self, game_state, travel_manager, x, y, width, height):
        self.state = game_state
        self.travel_manager = travel_manager
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = False
        self.font_title = pygame.font.SysFont("Arial", 24, bold=True)
        self.font_text = pygame.font.SysFont("Arial", 16)
        self.font_small = pygame.font.SysFont("Arial", 14)
        
        self.scroll_y = 0
        
    def handle_event(self, event):
        if not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if not self.rect.collidepoint(mx, my):
                return False
                
            # List starts at y=60
            list_y = self.rect.y + 60 - self.scroll_y
            
            for loc in self.travel_manager.locations:
                # Item height 60
                item_rect = pygame.Rect(self.rect.x + 10, list_y, self.rect.width - 20, 50)
                
                # Travel Button
                btn_rect = pygame.Rect(item_rect.right - 100, item_rect.centery - 15, 90, 30)
                
                if btn_rect.collidepoint(mx, my):
                    # Attempt travel
                    if self.travel_manager.travel(self.state, loc):
                        print(f"Traveled to {loc.name}")
                        self.visible = False # Close on travel
                    else:
                        print("Cannot afford travel")
                    return True
                
                list_y += 60
                
        elif event.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.scroll_y = max(0, self.scroll_y - event.y * 10)
                return True
                
        return False

    def render(self, screen):
        if not self.visible:
            return
            
        # Background
        pygame.draw.rect(screen, Theme.BACKGROUND, self.rect)
        pygame.draw.rect(screen, (100, 100, 150), self.rect, 2)
        
        # Header
        title = self.font_title.render("Travel", True, Theme.ACCENT_KINETIC)
        screen.blit(title, (self.rect.x + 20, self.rect.y + 15))
        
        # Current Location
        curr_text = self.font_small.render(f"Current: {self.state.location_name}", True, Theme.TEXT_DIM)
        screen.blit(curr_text, (self.rect.x + 120, self.rect.y + 20))
        
        # List
        list_y = self.rect.y + 60 - self.scroll_y
        
        # Clip rect for scrolling
        clip_rect = pygame.Rect(self.rect.x, self.rect.y + 50, self.rect.width, self.rect.height - 60)
        screen.set_clip(clip_rect)
        
        for loc in self.travel_manager.locations:
            # Calculate cost
            cost = int(self.travel_manager.calculate_cost(self.state.lat, self.state.lon, loc))
            is_current = (loc.name == self.state.location_name)
            
            # Item Box
            item_rect = pygame.Rect(self.rect.x + 10, list_y, self.rect.width - 20, 50)
            bg_color = (40, 40, 60) if is_current else Theme.PANEL_BG
            pygame.draw.rect(screen, bg_color, item_rect, border_radius=5)
            pygame.draw.rect(screen, (60, 60, 80), item_rect, 1, border_radius=5)
            
            # Text
            name_text = self.font_text.render(loc.name, True, Theme.TEXT_MAIN)
            screen.blit(name_text, (item_rect.x + 10, item_rect.y + 15))
            
            if is_current:
                status_text = self.font_small.render("Current Location", True, Theme.ACCENT_SOLAR)
                screen.blit(status_text, (item_rect.right - 150, item_rect.centery - status_text.get_height()//2))
            else:
                # Travel Button
                can_afford = self.state.resources.energy >= cost
                btn_color = (100, 200, 100) if can_afford else (100, 100, 100)
                
                btn_rect = pygame.Rect(item_rect.right - 100, item_rect.centery - 15, 90, 30)
                pygame.draw.rect(screen, btn_color, btn_rect, border_radius=5)
                
                cost_text = self.font_small.render(f"{cost} E", True, (0, 50, 0) if can_afford else (50, 50, 50))
                screen.blit(cost_text, (btn_rect.centerx - cost_text.get_width()//2, btn_rect.centery - cost_text.get_height()//2))
            
            list_y += 60
            
        screen.set_clip(None)
