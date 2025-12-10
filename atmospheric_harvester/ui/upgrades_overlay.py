import pygame
from .theme import Theme

class UpgradesOverlay:
    def __init__(self, game_state, upgrade_manager, x, y, width, height):
        self.state = game_state
        self.upgrade_manager = upgrade_manager
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
                
            # Check clicks on buy buttons
            # List starts at y=60
            list_y = self.rect.y + 60 - self.scroll_y
            
            for uid, upgrade in self.upgrade_manager.upgrades.items():
                # Item height 80
                item_rect = pygame.Rect(self.rect.x + 10, list_y, self.rect.width - 20, 70)
                
                # Buy Button
                btn_rect = pygame.Rect(item_rect.right - 100, item_rect.centery - 15, 90, 30)
                
                if btn_rect.collidepoint(mx, my):
                    # Attempt buy
                    if self.upgrade_manager.buy_upgrade(self.state, uid):
                        print(f"Bought upgrade {upgrade.name}")
                    else:
                        print("Cannot afford upgrade")
                    return True
                
                list_y += 80
                
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
        title = self.font_title.render("Upgrades", True, Theme.ACCENT_SOLAR)
        screen.blit(title, (self.rect.x + 20, self.rect.y + 15))
        
        # List
        list_y = self.rect.y + 60 - self.scroll_y
        
        # Clip rect for scrolling
        clip_rect = pygame.Rect(self.rect.x, self.rect.y + 50, self.rect.width, self.rect.height - 60)
        screen.set_clip(clip_rect)
        
        for uid, upgrade in self.upgrade_manager.upgrades.items():
            current_level = self.state.upgrades.get(uid, 0)
            cost = upgrade.get_cost(current_level)
            
            # Item Box
            item_rect = pygame.Rect(self.rect.x + 10, list_y, self.rect.width - 20, 70)
            pygame.draw.rect(screen, Theme.PANEL_BG, item_rect, border_radius=5)
            pygame.draw.rect(screen, (60, 60, 80), item_rect, 1, border_radius=5)
            
            # Text
            name_text = self.font_text.render(f"{upgrade.name} (Lvl {current_level})", True, Theme.TEXT_MAIN)
            screen.blit(name_text, (item_rect.x + 10, item_rect.y + 10))
            
            # Current Value Display
            val_str = ""
            if uid in ["turbine_eff", "solar_eff", "hydro_eff"]:
                mult = self.upgrade_manager.get_multiplier(self.state, uid)
                val_str = f"Current: +{int((mult - 1.0) * 100)}%"
            elif uid == "battery_cap":
                val_str = f"Total: +{current_level * 500} Cap"
                
            if val_str:
                val_surf = self.font_small.render(val_str, True, Theme.ACCENT_KINETIC)
                # Position to the right of the name, with some padding
                screen.blit(val_surf, (item_rect.x + 10 + name_text.get_width() + 15, item_rect.y + 12))
            
            desc_text = self.font_small.render(upgrade.description, True, Theme.TEXT_DIM)
            screen.blit(desc_text, (item_rect.x + 10, item_rect.y + 35))
            
            # Buy Button
            can_afford = self.state.resources.energy >= cost # Currently costs Energy
            btn_color = (100, 200, 100) if can_afford else (100, 100, 100)
            
            btn_rect = pygame.Rect(item_rect.right - 100, item_rect.centery - 15, 90, 30)
            pygame.draw.rect(screen, btn_color, btn_rect, border_radius=5)
            
            cost_text = self.font_small.render(f"{cost} Energy", True, (0, 50, 0) if can_afford else (50, 50, 50))
            screen.blit(cost_text, (btn_rect.centerx - cost_text.get_width()//2, btn_rect.centery - cost_text.get_height()//2))
            
            list_y += 80
            
        screen.set_clip(None)
