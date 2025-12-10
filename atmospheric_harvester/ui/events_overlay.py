"""
Events Overlay UI for displaying active weather events and event history.
"""

import pygame
import time


class EventsOverlay:
    """Displays active weather events and their effects."""
    
    def __init__(self, screen_width, screen_height, game_ref):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.game_ref = game_ref
        
        # Positioning
        self.width = 550
        self.height = screen_height - 100
        self.x = screen_width - self.width - 20
        self.y = 50
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # State
        self.visible = False
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # Flash effect for warnings
        self.flash_alpha = 0
        self.flash_timer = 0
        
        # Fonts
        self.font_title = pygame.font.Font(None, 42)
        self.font_large = pygame.font.Font(None, 28)
        self.font_med = pygame.font.Font(None, 22)
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
    
    def show_warning(self):
        """Trigger flash warning effect."""
        self.flash_alpha = 255
        self.flash_timer = 2.0  # Flash for 2 seconds
    
    def update(self, dt):
        """Update flash effects."""
        if self.flash_timer > 0:
            self.flash_timer -= dt
            self.flash_alpha = int(255 * (self.flash_timer / 2.0))
    
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
        """Render the events overlay."""
        if not self.visible:
            # Still render warning flash even when closed
            if self.flash_alpha > 0:
                flash_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
                pygame.draw.rect(flash_surf, (255, 100, 100, self.flash_alpha // 4), flash_surf.get_rect())
                screen.blit(flash_surf, (0, 0))
            return
        
        # Background
        bg_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        bg_surface.fill((25, 25, 35))
        bg_surface.set_alpha(245)
        screen.blit(bg_surface, (self.x, self.y))
        
        # Border (colored based on most severe active event)
        border_color = (100, 100, 150)
        if self.game_ref.event_manager.active_events:
            max_severity = max([self._get_severity_value(e.severity) 
                              for e in self.game_ref.event_manager.active_events])
            border_color = self._get_severity_color_value(max_severity)
        
        pygame.draw.rect(screen, border_color, self.rect, 3)
        
        # Title
        title = self.font_title.render("Weather Events", True, (255, 255, 255))
        screen.blit(title, (self.x + 20, self.y + 10))
        
        # Frequency multiplier indicator
        freq_mult = self.game_ref.event_manager.frequency_multiplier
        if freq_mult > 1.0:
            freq_text = f"Event Booster: {freq_mult:.1f}x"
            freq_color = (100, 255, 150)
        else:
            freq_text = "Realistic Mode"
            freq_color = (180, 180, 200)
        freq_surf = self.font_tiny.render(freq_text, True, freq_color)
        screen.blit(freq_surf, (self.x + self.width - freq_surf.get_width() - 20, self.y + 15))
        
        # Stats
        stats = self.game_ref.event_manager.get_stats()
        stats_text = f"Active: {stats['active_count']} | Total Experienced: {stats['total_experienced']}"
        stats_surf = self.font_small.render(stats_text, True, (200, 200, 200))
        screen.blit(stats_surf, (self.x + 20, self.y + 55))
        
        # Content area
        content_y = self.y + 85
        content_height = self.height - 95
        
        # Create clip rect for scrolling
        clip_rect = pygame.Rect(self.x, content_y, self.width, content_height)
        screen.set_clip(clip_rect)
        
        y_offset = content_y - self.scroll_offset
        
        # Active Events Section
        if self.game_ref.event_manager.active_events:
            header = self.font_large.render("— ACTIVE EVENTS —", True, (255, 100, 100))
            screen.blit(header, (self.x + 20, y_offset))
            y_offset += 35
            
            for event in self.game_ref.event_manager.active_events:
                y_offset = self._draw_event(screen, event, y_offset, active=True)
                y_offset += 15  # Spacing
        else:
            no_events = self.font_med.render("No active weather events", True, (150, 150, 150))
            screen.blit(no_events, (self.x + self.width // 2 - no_events.get_width() // 2, y_offset))
            y_offset += 40
        
        # Separator
        y_offset += 10
        pygame.draw.line(screen, (80, 80, 100), 
                        (self.x + 20, y_offset), 
                        (self.x + self.width - 20, y_offset), 2)
        y_offset += 20
        
        # Event History Section
        header = self.font_large.render("— EVENT HISTORY —", True, (150, 150, 200))
        screen.blit(header, (self.x + 20, y_offset))
        y_offset += 35
        
        if self.game_ref.event_manager.event_history:
            # Show last 10 events
            for event in reversed(self.game_ref.event_manager.event_history[-10:]):
                y_offset = self._draw_event(screen, event, y_offset, active=False)
                y_offset += 10
        else:
            no_history = self.font_small.render("No events yet", True, (120, 120, 120))
            screen.blit(no_history, (self.x + 30, y_offset))
            y_offset += 30
        
        # Calculate max scroll
        self.max_scroll = max(0, y_offset - content_y - content_height + 20)
        
        # Clear clip
        screen.set_clip(None)
        
        # Scrollbar
        if self.max_scroll > 0:
            scrollbar_height = max(30, (content_height / (y_offset - content_y)) * content_height)
            scrollbar_y = content_y + (self.scroll_offset / self.max_scroll) * (content_height - scrollbar_height)
            pygame.draw.rect(screen, (100, 100, 150), 
                           (self.x + self.width - 10, scrollbar_y, 6, scrollbar_height), border_radius=3)
    
    def _draw_event(self, screen, event, y_offset, active=True):
        """Draw a single event card."""
        card_height = 110 if active else 70
        
        # Severity color
        severity_value = self._get_severity_value(event.severity)
        severity_color = self._get_severity_color(severity_value)
        bg_color = self._get_bg_color(severity_value, active)
        
        # Card background
        card_rect = pygame.Rect(self.x + 15, y_offset, self.width - 30, card_height)
        pygame.draw.rect(screen, bg_color, card_rect, border_radius=5)
        pygame.draw.rect(screen, severity_color, card_rect, 2, border_radius=5)
        
        # Event icon/emoji (using text for simplicity)
        icon = self._get_event_icon(event.event_type)
        icon_surf = self.font_large.render(icon, True, severity_color)
        screen.blit(icon_surf, (self.x + 25, y_offset + 8))
        
        # Event name
        name = event.event_type.value.replace('_', ' ').title()
        name_surf = self.font_med.render(name, True, (255, 255, 255))
        screen.blit(name_surf, (self.x + 65, y_offset + 10))
        
        # Severity badge
        severity_text = event.severity.value.upper()
        severity_badge = self.font_tiny.render(severity_text, True, severity_color)
        screen.blit(severity_badge, (self.x + self.width - severity_badge.get_width() - 30, y_offset + 12))
        
        # Description
        desc_surf = self.font_small.render(event.description[:60] + "...", True, (200, 200, 200))
        screen.blit(desc_surf, (self.x + 25, y_offset + 38))
        
        if active:
            # Time remaining
            time_remaining = event.time_remaining()
            if time_remaining > 3600:
                time_text = f"{time_remaining/3600:.1f}h remaining"
            elif time_remaining > 60:
                time_text = f"{int(time_remaining/60)}m remaining"
            else:
                time_text = f"{int(time_remaining)}s remaining"
            time_surf = self.font_tiny.render(time_text, True, (150, 200, 255))
            screen.blit(time_surf, (self.x + 25, y_offset + 58))
            
            # Modifiers
            modifiers = event.get_modifiers()
            mod_y = y_offset + 75
            mod_x = self.x + 25
            
            for machine_type, multiplier in modifiers.items():
                if multiplier != 1.0:
                    change = (multiplier - 1.0) * 100
                    if change > 0:
                        mod_text = f"▲ {machine_type.title()}: +{change:.0f}%"
                        mod_color = (100, 255, 100)
                    else:
                        mod_text = f"▼ {machine_type.title()}: {change:.0f}%"
                        mod_color = (255, 100, 100)
                    mod_surf = self.font_tiny.render(mod_text, True, mod_color)
                    screen.blit(mod_surf, (mod_x, mod_y))
                    mod_x += mod_surf.get_width() + 15
        
        return y_offset + card_height
    
    def _get_event_icon(self, event_type):
        """Get icon for event type."""
        from game.weather_events import EventType
        icons = {
            EventType.THUNDERSTORM: "⚡",
            EventType.HEATWAVE: "☀",
            EventType.BLIZZARD: "❄",
            EventType.DROUGHT: "🌵",
            EventType.WINDSTORM: "💨",
            EventType.DUST_STORM: "🌪",
            EventType.FOG: "🌫",
            EventType.TORNADO_WARNING: "🌪",
            EventType.HURRICANE: "🌀",
            EventType.COLD_SNAP: "🥶",
            EventType.FLASH_FLOOD: "🌊",
            EventType.AURORA: "✨"
        }
        return icons.get(event_type, "⚠")
    
    def _get_severity_value(self, severity):
        """Convert severity enum to numeric value."""
        from game.weather_events import EventSeverity
        values = {
            EventSeverity.MINOR: 1,
            EventSeverity.MODERATE: 2,
            EventSeverity.SEVERE: 3,
            EventSeverity.EXTREME: 4
        }
        return values.get(severity, 1)
    
    def _get_severity_color(self, severity_value):
        """Get color for severity level."""
        colors = {
            1: (100, 200, 100),  # Green
            2: (255, 220, 100),  # Yellow
            3: (255, 150, 50),   # Orange
            4: (255, 50, 50)     # Red
        }
        return colors.get(severity_value, (150, 150, 150))
    
    def _get_severity_color_value(self, severity_value):
        """Get color for severity value (for border)."""
        return self._get_severity_color(severity_value)
    
    def _get_bg_color(self, severity_value, active):
        """Get background color for event card."""
        if not active:
            return (40, 40, 50)
        
        colors = {
            1: (40, 60, 40),   # Light green tint
            2: (60, 60, 30),   # Yellow tint
            3: (60, 45, 30),   # Orange tint
            4: (70, 30, 30)    # Red tint
        }
        return colors.get(severity_value, (40, 40, 50))
