import unittest
import pygame
import sys
import os

# Fix path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.core import Game
from game.state import GameState
from game.upgrades import UpgradeManager
from ui.upgrades_overlay import UpgradesOverlay

class MockGame:
    def __init__(self):
        self.state = GameState()
        self.upgrade_manager = UpgradeManager()

class TestUpgradesCrash(unittest.TestCase):
    def setUp(self):
        pygame.init()
        # Need a display for font rendering
        self.screen = pygame.display.set_mode((800, 600))
        self.game = MockGame()
        self.overlay = UpgradesOverlay(self.game.state, self.game.upgrade_manager, 100, 100, 600, 400)
        self.overlay.visible = True
        
    def tearDown(self):
        pygame.quit()
        
    def test_render(self):
        # Try to render
        try:
            self.overlay.render(self.screen)
        except Exception as e:
            self.fail(f"Render crashed: {e}")
            
    def test_click(self):
        # Fake event
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (150, 150), "button": 1})
        try:
            self.overlay.handle_event(event)
        except Exception as e:
            self.fail(f"Handle event crashed: {e}")

if __name__ == "__main__":
    unittest.main()
