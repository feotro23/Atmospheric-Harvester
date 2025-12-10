import pygame
from ui.theme import Theme
from ui.ui_manager import Button

class HarvesterOverlay:
    def __init__(self, screen_width, screen_height, game):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.game = game
        self.visible = False
        
        # Dimensions
        self.width = 500
        self.height = 400
        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        self.font_title = Theme.get_font(32)
        self.font_header = Theme.get_font(24)
        self.font_text = Theme.get_font(18)
        
        # Close Button
        self.btn_close = Button(self.x + self.width - 40, self.y + 10, 30, 30, "X", self.close)

    def close(self):
        self.visible = False

    def open(self):
        self.visible = True

    def render(self, screen):
        if not self.visible:
            return

        # Semi-transparent background (Glassmorphism)
        s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (20, 25, 40, 230), (0, 0, self.width, self.height), border_radius=15)
        # Border
        pygame.draw.rect(s, (100, 100, 120), (0, 0, self.width, self.height), 2, border_radius=15)
        
        screen.blit(s, (self.x, self.y))
        
        # Title
        title_surf = self.font_title.render("Harvester Status", True, (255, 255, 255))
        screen.blit(title_surf, (self.x + 20, self.y + 20))
        
        # Render Close Button
        self.btn_close.rect.x = self.x + self.width - 40
        self.btn_close.rect.y = self.y + 10
        self.btn_close.render(screen)
        
        # --- Stats Calculation ---
        total_energy_gen = 0.0
        wind_gen = 0.0
        wind_bonus_upgrades = 0.0
        
        solar_gen = 0.0
        solar_bonus_upgrades = 0.0
        
        passive_energy = 0.0
        
        total_water_gen = 0.0
        rain_gen = 0.0
        rain_bonus_upgrades = 0.0
        
        passive_water = 0.0
        
        # Get Multipliers
        upgrade_mgr = self.game.upgrade_manager
        state = self.game.state
        
        t_mult = upgrade_mgr.get_multiplier(state, "turbine_eff")
        s_mult = upgrade_mgr.get_multiplier(state, "solar_eff")
        r_mult = upgrade_mgr.get_multiplier(state, "hydro_eff")
        
        for m in state.machines:
            if not m.active: continue
            
            rate = m.current_rate
            
            if m.type.name == "Wind Turbine":
                # Base Rate + Event Modifier is in m.current_rate?
                # Wait, machines.py sets current_rate = mechanics output.
                # Mechanics uses wind speed. It does NOT include event modifier?
                # core.py lines 69-91 applies event modifier AND upgrade modifier externally.
                # machines.py logic: current_rate = base.
                # We need to fetch event modifier too if we want "Base" to reflect current conditions?
                # Actually, "Wind Turbines" usually implies base output from wind.
                # If we want to be precise:
                # Base = m.current_rate
                # Upgrade Bonus = m.current_rate * (t_mult - 1.0)
                # But notice core.py applies event modifier to base too?
                # core.py: modifier = event_modifiers.get("wind", 1.0)
                # total_mult = modifier * upgrade_mult
                # total added = base * total_mult.
                # So if we want to split it:
                # Base Display = base * modifier ? (Actual output if no upgrades)
                # Upgrade Bonus = base * modifier * (t_mult - 1.0) ? 
                # Or Upgrade Bonus = (base * total_mult) - (base * modifier)
                # Let's check core.py again.
                # total_mult = modifier * upgrade_mult.
                # So yes, the upgrade EFFECTIVELY multiplies the event-modified base.
                
                # Let's get event modifiers
                event_mods = self.game.event_manager.get_active_modifiers()
                w_mod = event_mods.get("wind", 1.0)
                s_mod = event_mods.get("solar", 1.0)
                h_mod = event_mods.get("hydro", 1.0)
                
                if m.type.name == "Wind Turbine":
                    real_base = rate * w_mod
                    wind_gen += real_base
                    wind_bonus_upgrades += real_base * (t_mult - 1.0)
                    total_energy_gen += real_base * t_mult
                    
            elif m.type.name == "Solar Panel":
                event_mods = self.game.event_manager.get_active_modifiers()
                s_mod = event_mods.get("solar", 1.0)
                
                real_base = rate * s_mod
                solar_gen += real_base
                solar_bonus_upgrades += real_base * (s_mult - 1.0)
                total_energy_gen += real_base * s_mult
                
            elif m.type.name == "Rain Collector":
                event_mods = self.game.event_manager.get_active_modifiers()
                h_mod = event_mods.get("hydro", 1.0)
                
                real_base = rate * h_mod
                rain_gen += real_base
                rain_bonus_upgrades += real_base * (r_mult - 1.0)
                total_water_gen += real_base * r_mult
                
        # Passive Creatures
        for c in state.collected_creatures:
            if hasattr(c.type, 'bonus_type'):
                if c.type.bonus_type == "passive_energy":
                    passive_energy += 1.0 # Hardcoded 1.0/s from core.py logic
                    
        total_energy_gen += passive_energy
        
        # --- Layout ---
        col1_x = self.x + 30
        col2_x = self.x + 260
        curr_y = self.y + 80
        
        # Energy Section
        screen.blit(self.font_header.render("Energy Generation", True, Theme.ACCENT_SOLAR), (col1_x, curr_y))
        curr_y += 30
        
        self._draw_row(screen, "Wind Turbines:", f"+{wind_gen:.1f}/s", col1_x, curr_y)
        curr_y += 20
        self._draw_row(screen, "Solar Panels:", f"+{solar_gen:.1f}/s", col1_x, curr_y)
        curr_y += 20
        self._draw_row(screen, "Passive (Creatures):", f"+{passive_energy:.1f}/s", col1_x, curr_y)
        curr_y += 20
        # Upgrade Bonus Total
        total_energy_upgrades = wind_bonus_upgrades + solar_bonus_upgrades
        self._draw_row(screen, "Passive (Upgrades):", f"+{total_energy_upgrades:.1f}/s", col1_x, curr_y)
        curr_y += 30
        
        # Total Energy
        total_surf = self.font_header.render(f"Total: {total_energy_gen:.1f} J/s", True, (255, 255, 255))
        screen.blit(total_surf, (col1_x, curr_y))
        
        curr_y = self.y + 80
        
        # Water Section
        screen.blit(self.font_header.render("Water Collection", True, Theme.ACCENT_HYDRO), (col2_x, curr_y))
        curr_y += 30
        
        self._draw_row(screen, "Rain Collectors:", f"+{rain_gen:.1f}/s", col2_x, curr_y)
        curr_y += 20
        self._draw_row(screen, "Passive:", f"+{passive_water:.1f}/s", col2_x, curr_y)
        curr_y += 20
        self._draw_row(screen, "Passive (Upgrades):", f"+{rain_bonus_upgrades:.1f}/s", col2_x, curr_y)
        curr_y += 50 # Spacer
        
        # Total Water
        total_w_surf = self.font_header.render(f"Total: {total_water_gen:.1f} L/s", True, (255, 255, 255))
        screen.blit(total_w_surf, (col2_x, curr_y))

    def _draw_row(self, screen, label, value, x, y):
        lbl = self.font_text.render(label, True, (180, 180, 180))
        val = self.font_text.render(value, True, (220, 220, 220))
        screen.blit(lbl, (x, y))
        screen.blit(val, (x + 160, y))

    def handle_event(self, event):
        if not self.visible:
            return False
            
        if self.btn_close.handle_event(event):
            return True
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.rect.collidepoint(event.pos):
                self.close() # Click outside closes
                return True
                
        return False
