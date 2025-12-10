import pygame

class Theme:
    # Colors
    BACKGROUND = (10, 15, 20)
    PANEL_BG = (20, 25, 35)
    PANEL_ALPHA = 200 # 0-255
    TEXT_MAIN = (220, 220, 220)
    TEXT_DIM = (150, 150, 150)
    
    ACCENT_KINETIC = (100, 200, 255)
    ACCENT_SOLAR = (255, 200, 50)
    ACCENT_HYDRO = (50, 255, 150)
    
    WARNING = (255, 80, 80)
    
    # Fonts
    _fonts = {}

    @classmethod
    def get_font(cls, size=20):
        if size not in cls._fonts:
            cls._fonts[size] = pygame.font.SysFont("Arial", size) # Fallback
        return cls._fonts[size]
