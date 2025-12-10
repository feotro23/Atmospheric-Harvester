import unittest
from game.core import Game
from ui.build_overlay import BuildOverlay

# Mock Pygame for headless testing
import sys
from unittest.mock import MagicMock
sys.modules['pygame'] = MagicMock()
import pygame

# Mock font
pygame.font.SysFont.return_value = MagicMock()

class TestBuildOverlay(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        # Mock Theme.get_font to avoid real pygame font init
        with unittest.mock.patch('ui.theme.Theme.get_font') as mock_font:
            mock_font.return_value = MagicMock()
            self.overlay = BuildOverlay(800, 600, self.game, None)
        
    def test_initial_state(self):
        self.assertFalse(self.overlay.visible)
        
    def test_open(self):
        self.overlay.open()
        self.assertTrue(self.overlay.visible)
        
    def test_select_machine(self):
        self.overlay.open()
        self.overlay.select_machine("Solar Panel")
        
        # Should set game selection
        self.assertEqual(self.game.build_selection, "Solar Panel")
        
        # Should close overlay
        self.assertFalse(self.overlay.visible)

if __name__ == '__main__':
    unittest.main()
