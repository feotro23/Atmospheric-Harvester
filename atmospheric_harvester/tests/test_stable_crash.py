import unittest
import pygame
import sys
import os

# Fix path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.core import Game
from game.machines import create_machine
from game.creatures import Creature, ALL_CREATURES
from ui.building_stats_overlay import BuildingStatsOverlay

from ui.theme import Theme

class TestStableCrash(unittest.TestCase):
    def setUp(self):
        pygame.init()
        Theme._fonts = {} # Clear cache
        self.screen = pygame.display.set_mode((800, 600))
        self.game = Game()
        self.overlay = BuildingStatsOverlay(800, 600, self.game.state, {}) # Empty assets
        # self.overlay.state = self.game.state # No longer needed manually
        
    def tearDown(self):
        pygame.quit()
        
    def test_render_stable_with_creatures(self):
        # 1. Add Stable
        stable = create_machine("Creature Stable", 5, 5)
        
        # 2. Add Captured Creatures
        # Get a type from ALL_CREATURES
        c_type = ALL_CREATURES[0] 
        c = Creature(c_type)
        self.game.state.collected_creatures.append(c)
        
        # 3. Open Overlay
        self.overlay.open(stable)
        
        # 4. Render
        try:
            self.overlay.render(self.screen)
        except Exception as e:
            self.fail(f"Render crashed with valid creature: {e}")
            
    def test_render_stable_corrupted_creature(self):
        # Simulate a creature with missing type info if possible
        # Or a type missing bonus fields (though my code handles getattr default)
        
        # What if c.type is None?
        # State loader prevents this, but let's test defensive coding
        class MockCreature:
            def __init__(self):
                self.type = None
        
        self.game.state.collected_creatures.append(MockCreature())
        
        self.overlay.open(create_machine("Creature Stable", 5, 5))
        
        try:
            self.overlay.render(self.screen)
        except Exception as e:
            self.fail(f"Should not crash even with corrupted creature: {e}")

if __name__ == "__main__":
    unittest.main()
