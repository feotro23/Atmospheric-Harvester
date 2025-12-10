"""
Missions Overlay UI for Atmospheric Harvester

Displays active missions, available missions, and completion status.
"""

import pygame
from ui.theme import Theme
from game.missions import MissionStatus, MissionTier


class MissionsOverlay:
    """UI overlay showing missions and progression."""
    
    def __init__(self, screen_width, screen_height, game_ref):
        # Right side panel
        self.width = 350
        self.height = screen_height - 40
        self.x = screen_width - self.width - 20
        self.y = 20
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.game_ref = game_ref
        self.visible = False
        
        self.font_title = Theme.get_font(24)
        self.font_med = Theme.get_font(18)
        self.font_small = Theme.get_font(14)
        
        # Scroll state
        self.scroll_offset = 0
        self.max_scroll = 0
        
    def toggle(self):
        """Toggle visibility."""
        self.visible = not self.visible
    
    def handle_event(self, event):
        """Handle input events."""
        if not self.visible:
            return False
        
        # ESC to close
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.visible = False
            return True
        
        # Mouse wheel scrolling
        if event.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.scroll_offset -= event.y * 20
                self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))
                return True
        
        # Click to claim rewards
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                # Check if clicked on a completed mission
                self._handle_claim_click(event.pos)
                return True
        
        return False
    
    def _handle_claim_click(self, pos):
        """Check if user clicked on a Claim button."""
        # Calculate y_offset matching the render method
        y_offset = self.y + 80 - self.scroll_offset
        
        # Account for Active Missions section
        active = self.game_ref.mission_manager.get_active_missions()
        if active:
            y_offset += 30  # Section title height
            y_offset += len(active) * 120  # Active mission cards
        
        # Now at Completed section
        completed = self.game_ref.mission_manager.get_completed_missions()
        if completed:
            y_offset += 30  # Completed section title height
            
            for mission in completed:
                mission_y = y_offset
                
                # Check if clicked on claim button area
                claim_rect = pygame.Rect(self.x + 220, mission_y + 75, 100, 30)
                if claim_rect.collidepoint(pos):
                    self.game_ref.mission_manager.claim_reward(mission.uid, self.game_ref.state)
                    print(f"Claimed: {mission.name}!")
                    break
                
                y_offset += 120  # Move to next mission card
    
    def render(self, screen):
        """Render the missions overlay."""
        if not self.visible:
            return
        
        # Semi-transparent background
        bg_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, (20, 25, 35, 240), (0, 0, self.width, self.height), border_radius=15)
        pygame.draw.rect(bg_surf, (100, 150, 200), (0, 0, self.width, self.height), 3, border_radius=15)
        screen.blit(bg_surf, (self.x, self.y))
        
        # Title
        title = self.font_title.render("Missions", True, (255, 255, 255))
        screen.blit(title, (self.x + 20, self.y + 15))
        
        # Stats
        stats = self.game_ref.mission_manager.get_stats()
        stats_text = f"{stats['claimed']}/{stats['total']} Complete ({stats['completion_rate']:.0f}%)"
        stats_surf = self.font_small.render(stats_text, True, (180, 180, 180))
        screen.blit(stats_surf, (self.x + 20, self.y + 50))
        
        # Close hint
        close_hint = self.font_small.render("Press ESC to close", True, (150, 150, 150))
        screen.blit(close_hint, (self.x + self.width - 140, self.y + 15))
        
        # Create clipping region for scrollable content
        content_rect = pygame.Rect(self.x + 10, self.y + 80, self.width - 20, self.height - 90)
        screen.set_clip(content_rect)
        
        y_offset = self.y + 80 - self.scroll_offset
        
        # Active Missions
        active = self.game_ref.mission_manager.get_active_missions()
        if active:
            section_title = self.font_med.render("Active", True, (100, 255, 100))
            screen.blit(section_title, (self.x + 20, y_offset))
            y_offset += 30
            
            for mission in active:
                y_offset = self._draw_mission_card(screen, mission, y_offset, (50, 100, 200))
        
        # Completed (Unclaimed) Missions
        completed = self.game_ref.mission_manager.get_completed_missions()
        if completed:
            section_title = self.font_med.render("Completed - Click to Claim!", True, (255, 200, 50))
            screen.blit(section_title, (self.x + 20, y_offset))
            y_offset += 30
            
            for mission in completed:
                y_offset = self._draw_mission_card(screen, mission, y_offset, (200, 150, 50), show_claim=True)
        
        # Available Missions
        available = self.game_ref.mission_manager.get_available_missions()
        if available:
            section_title = self.font_med.render("Available", True, (200, 200, 200))
            screen.blit(section_title, (self.x + 20, y_offset))
            y_offset += 30
            
            for mission in available:
                y_offset = self._draw_mission_card(screen, mission, y_offset, (100, 100, 100))
        
        # Calculate max scroll
        self.max_scroll = max(0, y_offset - (self.y + self.height - 100))
        
        # Clear clip
        screen.set_clip(None)
    
    def _draw_mission_card(self, screen, mission, y, border_color, show_claim=False):
        """Draw a single mission card."""
        card_h = 110
        
        # Card background
        card_rect = pygame.Rect(self.x + 15, y, self.width - 30, card_h)
        
        # Skip if outside visible area
        if card_rect.bottom < self.y + 80 or card_rect.top > self.y + self.height:
            return y + card_h + 10
        
        pygame.draw.rect(screen, (30, 35, 45), card_rect, border_radius=8)
        pygame.draw.rect(screen, border_color, card_rect, 2, border_radius=8)
        
        # Tier badge
        tier_color = self._get_tier_color(mission.tier)
        tier_text = mission.tier.value.capitalize()
        tier_surf = self.font_small.render(tier_text, True, tier_color)
        screen.blit(tier_surf, (self.x + 25, y + 10))
        
        # Mission name
        name_surf = self.font_med.render(mission.name, True, (255, 255, 255))
        screen.blit(name_surf, (self.x + 25, y + 30))
        
        # Description (wrapped)
        desc_lines = self._wrap_text(mission.description, self.width - 60)
        desc_y = y + 55
        for line in desc_lines[:2]:  # Limit to 2 lines
            desc_surf = self.font_small.render(line, True, (180, 180, 180))
            screen.blit(desc_surf, (self.x + 25, desc_y))
            desc_y += 18
        
        # Show claim button if completed
        if show_claim:
            claim_rect = pygame.Rect(self.x + 220, y + 75, 100, 30)
            pygame.draw.rect(screen, (50, 150, 50), claim_rect, border_radius=5)
            pygame.draw.rect(screen, (100, 255, 100), claim_rect, 2, border_radius=5)
            claim_text = self.font_small.render("CLAIM", True, (255, 255, 255))
            text_rect = claim_text.get_rect(center=claim_rect.center)
            screen.blit(claim_text, text_rect)
        
        return y + card_h + 10
    
    def _get_tier_color(self, tier):
        """Get color for mission tier."""
        colors = {
            MissionTier.TUTORIAL: (100, 200, 255),
            MissionTier.BASIC: (100, 255, 100),
            MissionTier.INTERMEDIATE: (255, 200, 100),
            MissionTier.ADVANCED: (255, 100, 100),
            MissionTier.MASTER: (200, 100, 255)
        }
        return colors.get(tier, (200, 200, 200))
    
    def _wrap_text(self, text, max_width):
        """Wrap text to fit within max_width pixels."""
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            if self.font_small.size(test_line)[0] < max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines
