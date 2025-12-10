"""
Achievements Overlay UI for displaying achievement progress and unlocks.
"""

import pygame


class AchievementsOverlay:
    """Displays achievements, progress, and rewards."""
    
    def __init__(self, screen_width, screen_height, game_ref):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.game_ref = game_ref
        
        # Positioning
        self.width = 500
        self.height = screen_height - 100
        self.x = screen_width - self.width - 20
        self.y = 50
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # State
        self.visible = False
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # Current filter
        self.filter_category = None  # None = show all
        
        # Fonts
        self.font_title = pygame.font.Font(None, 42)
        self.font_med = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        self.font_tiny = pygame.font.Font(None, 14)
    
    def toggle(self):
        """Toggle visibility."""
        self.visible = not self.visible
        if self.visible:
            self.scroll_offset = 0
    
    def close(self):
        """Close overlay."""
        self.visible = False
    
    def handle_event(self, event):
        """Handle UI events."""
        if not self.visible:
            return False
        
        # ESC to close
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.close()
            return True
        
        # Scroll with mouse wheel
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if event.button == 4:  # Scroll up
                    self.scroll_offset = max(0, self.scroll_offset - 30)
                    return True
                elif event.button == 5:  # Scroll down
                    self.scroll_offset = min(self.max_scroll, self.scroll_offset + 30)
                    return True
        
        return False
    
    def render(self, screen):
        """Render the achievements overlay."""
        if not self.visible:
            return
        
        # Background
        bg_surface = pygame.Surface((self.width, self.height))
        bg_surface.fill((20, 20, 30))
        bg_surface.set_alpha(240)
        screen.blit(bg_surface, (self.x, self.y))
        
        # Border
        pygame.draw.rect(screen, (100, 100, 150), self.rect, 2)
        
        # Title
        title = self.font_title.render("🏆 Achievements", True, (255, 215, 0))
        screen.blit(title, (self.x + 20, self.y + 10))
        
        # Stats Summary
        stats = self.game_ref.achievement_manager.get_stats()
        stats_text = f"{stats['unlocked']}/{stats['total']} Unlocked ({stats['completion_rate']:.1f}%)"
        stats_surface = self.font_small.render(stats_text, True, (200, 200, 200))
        screen.blit(stats_surface, (self.x + 20, self.y + 50))
        
        # Scrollable content area
        content_y = self.y + 80
        content_height = self.height - 90
        
        # Create clip rect for scrolling
        clip_rect = pygame.Rect(self.x, content_y, self.width, content_height)
        screen.set_clip(clip_rect)
        
        y_offset = content_y - self.scroll_offset
        
        # Group achievements by category
        from game.achievements import AchievementCategory
        
        for category in AchievementCategory:
            achievements = self.game_ref.achievement_manager.get_by_category(category)
            if not achievements:
                continue
            
            # Category Header
            category_color = self._get_category_color(category)
            category_name = category.value.replace('_', ' ').title()
            header = self.font_med.render(f"— {category_name} —", True, category_color)
            screen.blit(header, (self.x + 20, y_offset))
            y_offset += 30
            
            # Draw achievements in this category
            for achievement in achievements:
                if achievement.hidden and not achievement.unlocked:
                    continue  # Skip hidden achievements
                
                y_offset = self._draw_achievement(screen, achievement, y_offset)
                y_offset += 10  # Spacing between achievements
        
        # Calculate max scroll
        self.max_scroll = max(0, y_offset - content_y - content_height + 20)
        
        # Clear clip
        screen.set_clip(None)
        
        # Scrollbar indicator
        if self.max_scroll > 0:
            scrollbar_height = max(30, (content_height / (y_offset - content_y)) * content_height)
            scrollbar_y = content_y + (self.scroll_offset / self.max_scroll) * (content_height - scrollbar_height)
            pygame.draw.rect(screen, (100, 100, 150), 
                           (self.x + self.width - 10, scrollbar_y, 6, scrollbar_height), border_radius=3)
    
    def _draw_achievement(self, screen, achievement, y_offset):
        """Draw a single achievement card."""
        card_height = 90
        
        # Background color based on status
        if achievement.unlocked:
            bg_color = (40, 70, 40)  # Green tint
            border_color = (100, 200, 100)
        elif achievement.progress > 0:
            bg_color = (60, 60, 40)  # Yellow tint
            border_color = (200, 200, 100)
        else:
            bg_color = (40, 40, 50)  # Neutral
            border_color = (80, 80, 100)
        
        # Card background
        card_rect = pygame.Rect(self.x + 15, y_offset, self.width - 30, card_height)
        pygame.draw.rect(screen, bg_color, card_rect, border_radius=5)
        pygame.draw.rect(screen, border_color, card_rect, 2, border_radius=5)
        
        # Tier badge
        tier_color = self._get_tier_color(achievement.tier)
        tier_name = achievement.tier.value.upper()
        tier_surface = self.font_tiny.render(tier_name, True, tier_color)
        screen.blit(tier_surface, (self.x + 25, y_offset + 8))
        
        # Achievement name
        name_color = (255, 255, 255) if achievement.unlocked else (180, 180, 180)
        name = self.font_med.render(achievement.name, True, name_color)
        screen.blit(name, (self.x + 25, y_offset + 25))
        
        # Description
        desc = self.font_small.render(achievement.description, True, (150, 150, 150))
        screen.blit(desc, (self.x + 25, y_offset + 48))
        
        # Progress bar (if not unlocked)
        if not achievement.unlocked and achievement.progress > 0:
            bar_x = self.x + 25
            bar_y = y_offset + 68
            bar_width = self.width - 60
            bar_height = 12
            
            # Background
            pygame.draw.rect(screen, (50, 50, 60), (bar_x, bar_y, bar_width, bar_height), border_radius=6)
            
            # Progress fill
            fill_width = int(bar_width * achievement.progress)
            if fill_width > 0:
                pygame.draw.rect(screen, (100, 200, 100), (bar_x, bar_y, fill_width, bar_height), border_radius=6)
            
            # Progress text
            progress_text = f"{achievement.progress * 100:.0f}%"
            progress_surface = self.font_tiny.render(progress_text, True, (255, 255, 255))
            screen.blit(progress_surface, (bar_x + bar_width + 10, bar_y))
        
        # Unlocked checkmark
        if achievement.unlocked:
            checkmark = self.font_med.render("✓", True, (100, 255, 100))
            screen.blit(checkmark, (self.x + self.width - 50, y_offset + 30))
        
        # Reward preview (on right side)
        reward_y = y_offset + 68
        reward_x = self.x + self.width - 200
        if achievement.reward.energy > 0:
            reward_text = f"+{achievement.reward.energy} ⚡"
            color = (255, 200, 50) if achievement.unlocked else (150, 150, 100)
            reward_surf = self.font_tiny.render(reward_text, True, color)
            screen.blit(reward_surf, (reward_x, reward_y))
            reward_x += 70
        if achievement.reward.water > 0:
            reward_text = f"+{achievement.reward.water} 💧"
            color = (100, 200, 255) if achievement.unlocked else (100, 100, 150)
            reward_surf = self.font_tiny.render(reward_text, True, color)
            screen.blit(reward_surf, (reward_x, reward_y))
            reward_x += 70
        if achievement.reward.biomass > 0:
            reward_text = f"+{achievement.reward.biomass} 🌿"
            color = (100, 255, 100) if achievement.unlocked else (100, 150, 100)
            reward_surf = self.font_tiny.render(reward_text, True, color)
            screen.blit(reward_surf, (reward_x, reward_y))
        
        return y_offset + card_height
    
    def _get_category_color(self, category):
        """Get color for achievement category."""
        from game.achievements import AchievementCategory
        colors = {
            AchievementCategory.EXPLORER: (100, 200, 255),
            AchievementCategory.ENGINEER: (255, 150, 50),
            AchievementCategory.FARMER: (100, 255, 100),
            AchievementCategory.WEATHER_MASTER: (200, 200, 255),
            AchievementCategory.EFFICIENCY: (255, 200, 50),
            AchievementCategory.COLLECTOR: (200, 150, 255),
        }
        return colors.get(category, (200, 200, 200))
    
    def _get_tier_color(self, tier):
        """Get color for achievement tier."""
        from game.achievements import AchievementTier
        colors = {
            AchievementTier.BRONZE: (205, 127, 50),
            AchievementTier.SILVER: (192, 192, 192),
            AchievementTier.GOLD: (255, 215, 0),
            AchievementTier.PLATINUM: (229, 228, 226),
            AchievementTier.DIAMOND: (185, 242, 255),
        }
        return colors.get(tier, (150, 150, 150))
