"""
Decorative Elements
Environmental decorations like glowing crystals, grass, roots, etc.
"""

import pygame
from src.core.constants import GLOW_CYAN, GLOW_BLUE, WHITE, MOSS_LIGHT, MOSS_GREEN


class DecorativeElement(pygame.sprite.Sprite):
    """
    Environmental decoration (glowing crystals, roots, etc.)
    """
    def __init__(self, x, y, element_type='crystal'):
        super().__init__()
        self.element_type = element_type
        self.animation_offset = 0
        self.create_element()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
    def create_element(self):
        """Create decorative element"""
        if self.element_type == 'crystal':
            self.image = pygame.Surface((20, 30), pygame.SRCALPHA)
            # Crystal shape
            crystal_points = [(10, 0), (16, 10), (14, 28), (6, 28), (4, 10)]
            pygame.draw.polygon(self.image, GLOW_CYAN, crystal_points)
            pygame.draw.polygon(self.image, GLOW_BLUE, [(10, 2), (14, 10), (12, 25), (8, 25), (6, 10)])
            # Bright core
            pygame.draw.line(self.image, WHITE, (10, 5), (10, 20), 2)
            
        elif self.element_type == 'grass':
            self.image = pygame.Surface((8, 16), pygame.SRCALPHA)
            # Simple grass blade
            pygame.draw.line(self.image, MOSS_LIGHT, (4, 16), (3, 8), 2)
            pygame.draw.line(self.image, MOSS_LIGHT, (3, 8), (4, 0), 2)
            pygame.draw.line(self.image, MOSS_GREEN, (4, 16), (4, 6), 1)
            
    def update(self):
        """Subtle animation for crystals"""
        if self.element_type == 'crystal':
            self.animation_offset += 0.05
            # Pulsing glow (we could redraw, but for performance just leave static)
