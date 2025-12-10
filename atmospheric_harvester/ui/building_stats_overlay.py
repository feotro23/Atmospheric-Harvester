import pygame
from .theme import Theme
from .ui_manager import UIElement, Button

class BuildingStatsOverlay(UIElement):
    def __init__(self, screen_width, screen_height, game_ref, assets=None):
        # Center overlay - Increased size
        w = 600
        h = 500
        x = (screen_width - w) // 2
        y = (screen_height - h) // 2
        super().__init__(x, y, w, h)
        
        self.game_ref = game_ref
        self.state = game_ref.state
        self.assets = assets or {}
        self.visible = False
        self.target_machine = None
        
        self.font_title = Theme.get_font(24)
        self.font_text = Theme.get_font(18)
        
        # Close button
        self.close_button = Button(self.rect.right - 35, self.rect.y + 10, 25, 25, "X", self.close)
        
        # Toggle button (placeholder position, updated in open)
        self.toggle_button = Button(self.rect.centerx - 50, self.rect.bottom - 50, 100, 30, "Toggle", self.toggle_target)
        
    def open(self, machine):
        self.target_machine = machine
        self.visible = True
        self.update_buttons()
        
    def close(self):
        self.visible = False
        self.target_machine = None
        
    def toggle_target(self):
        if self.target_machine:
            self.target_machine.active = not self.target_machine.active
            self.update_buttons()
            
    def update_buttons(self):
        if self.target_machine:
            text = "Turn OFF" if self.target_machine.active else "Turn ON"
            self.toggle_button.text = text
            self.toggle_button.bg_color = (150, 50, 50) if self.target_machine.active else (50, 150, 50)
            
    def handle_event(self, event):
        if not self.visible:
            return False
            
        if self.close_button.handle_event(event):
            return True
            
        if self.toggle_button.handle_event(event):
            return True
            
        # Consume clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
                
        return False
        
    def render(self, screen):
        if not self.visible or not self.target_machine:
            return
            
        # Panel
        pygame.draw.rect(screen, (30, 35, 45), self.rect, border_radius=15)
        pygame.draw.rect(screen, (100, 100, 120), self.rect, 2, border_radius=15)
        
        # Title
        name = self.target_machine.type.name
        title = self.font_title.render(name, True, (255, 255, 255))
        screen.blit(title, (self.rect.centerx - title.get_width() // 2, self.rect.y + 20))
        
        # Status
        status_text = "Status: " + ("Running" if self.target_machine.active else "Stopped")
        status_color = (100, 255, 100) if self.target_machine.active else (255, 100, 100)
        status_surf = self.font_text.render(status_text, True, status_color)
        screen.blit(status_surf, (self.rect.x + 30, self.rect.y + 70))
        
        # Stats
        # Depending on machine type, show relevant stat
        # We need to access the machine's current_rate if available
        rate = getattr(self.target_machine, 'current_rate', 0)
        
        info_lines = []
        if name == "Wind Turbine":
            info_lines.append(f"Production: {rate:.1f} J/s")
        elif name == "Solar Panel":
            info_lines.append(f"Production: {rate:.1f} J/s")
        elif name == "Rain Collector":
            info_lines.append(f"Collection: {rate:.1f} L/s")
        elif name == "Creature Stable":
            info_lines.append("Allows capturing creatures.")
            
            # Display Collected Creatures (Grouped)
            if hasattr(self.state, 'collected_creatures') and self.state.collected_creatures:
                # Group by type
                counts = {}
                types = {}
                for c in self.state.collected_creatures:
                    if not c.type: continue
                    t_name = c.type.name
                    if t_name not in counts:
                        counts[t_name] = 0
                        types[t_name] = c.type
                    counts[t_name] += 1
                
                # Render Grid
                y_off = 130
                x_off = 30
                col_width = 250
                
                screen.blit(self.font_text.render(f"Total Collected: {len(self.state.collected_creatures)}", True, (255, 200, 50)), (self.rect.x + 30, self.rect.y + 110))
                
                for t_name, count in counts.items():
                    c_type = types[t_name]
                    # Icon
                    if t_name in self.assets:
                        icon = self.assets[t_name]
                        # Scale down if too big
                        iw, ih = icon.get_size()
                        scale = 32 / max(iw, ih)
                        if scale < 1:
                            icon = pygame.transform.scale(icon, (int(iw*scale), int(ih*scale)))
                        screen.blit(icon, (self.rect.x + x_off, self.rect.y + y_off))
                    else:
                        pygame.draw.circle(screen, (100, 200, 255), (self.rect.x + x_off + 16, self.rect.y + y_off + 16), 10)
                        
                    # Text
                    text = f"{t_name} x{count}"
                    bonus = getattr(c_type, 'bonus_desc', "")
                    
                    surf = self.font_text.render(text, True, (100, 200, 255))
                    screen.blit(surf, (self.rect.x + x_off + 40, self.rect.y + y_off + 5))
                    
                    if bonus:
                        # Wrap bonus text if needed or just show small
                        b_surf = pygame.font.Font(None, 16).render(bonus, True, (180, 180, 180))
                        screen.blit(b_surf, (self.rect.x + x_off + 40, self.rect.y + y_off + 25))
                        
                        # Cumulative Bonus Display
                        total_str = ""
                        if c_type.bonus_type == "water_eff":
                            total_str = f"Total: +{10 * count}% Water Col."
                        elif c_type.bonus_type == "passive_energy":
                            total_str = f"Total: +{1.0 * count:.1f} Energy/s"
                        elif c_type.bonus_type == "wind_eff":
                            total_str = f"Total: +{10 * count}% Wind Eff."
                        elif c_type.bonus_type == "solar_eff":
                            total_str = f"Total: +{10 * count}% Solar Eff."
                        elif c_type.bonus_type == "chill_eff":
                            total_str = f"Total: +{20 * count}% Chill Accum."
                            
                        if total_str:
                            t_surf = pygame.font.Font(None, 16).render(total_str, True, (255, 255, 100)) # Yellow for total
                            screen.blit(t_surf, (self.rect.x + x_off + 40, self.rect.y + y_off + 38))
                        
                    y_off += 50
                    if y_off > self.rect.height - 60:
                        y_off = 130
                        x_off += col_width
                        
                # prevent info_lines below from overwriting
                info_lines = [] 

            else:
                 info_lines.append("")
                 info_lines.append("No creatures collected yet.")
                 
        elif name == "Sprinkler":
            info_lines.append("Consumes 1.0 L/s when active.")
            info_lines.append("Effect Range: 2 Tiles")
            info_lines.append("Water Output: +50% Moisture")
        elif name == "Heater":
            info_lines.append("Consumes 10.0 J/s when active.")
            heat_val = self.game_ref.settings_manager.get_measurement_display(10.0, "temp_delta")
            info_lines.append(f"Heat Output: +{heat_val}")
            info_lines.append("Effect Range: 2 Tiles")
            
        y_off = 110
        for line in info_lines:
            color = (200, 200, 200)
            if line.startswith("-"): color = (100, 200, 255) 
            elif line.startswith("Collected"): color = (255, 200, 50)
            
            surf = self.font_text.render(line, True, color)
            screen.blit(surf, (self.rect.x + 30, self.rect.y + y_off))
            y_off += 25
            
        # Render Buttons
        self.close_button.rect.x = self.rect.right - 35 # Update position dynamic if resized
        self.close_button.rect.y = self.rect.y + 10
        self.close_button.render(screen)
        
        self.toggle_button.rect.centerx = self.rect.centerx
        self.toggle_button.rect.bottom = self.rect.bottom - 20
        self.toggle_button.render(screen)
