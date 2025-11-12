"""
Collectibles System
Coins, essence orbs, and other collectible items
"""

import pygame
from src.core.constants import GLOW_CYAN, GLOW_BLUE, WHITE


class Coin(pygame.sprite.Sprite):
    """
    Collectible essence/soul orb (Hollow Knight inspired)
    Glowing ethereal collectible
    """
    def __init__(self, x, y):
        super().__init__()
        self.base_y = y
        self.float_offset = 0
        self.pulse_offset = 0
        self.create_orb()
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        
    def create_orb(self):
        """Create a glowing ethereal orb"""
        self.image = pygame.Surface((28, 28), pygame.SRCALPHA)
        
        # Outer glow (largest, most transparent)
        pygame.draw.circle(self.image, (*GLOW_CYAN[:3], 30), (14, 14), 13)
        
        # Middle glow
        pygame.draw.circle(self.image, (*GLOW_CYAN[:3], 80), (14, 14), 9)
        
        # Inner bright core
        pygame.draw.circle(self.image, (*GLOW_BLUE[:3], 150), (14, 14), 6)
        
        # Bright center
        pygame.draw.circle(self.image, (200, 240, 255), (14, 14), 3)
        
        # Sparkle effect
        pygame.draw.circle(self.image, WHITE, (16, 12), 1)
        
    def update(self):
        """Floating and pulsing animation"""
        self.float_offset += 0.08
        self.pulse_offset += 0.15
        
        # Float up and down
        float_y = self.base_y + pygame.math.Vector2(0, 1).rotate(self.float_offset * 10).y * 8
        self.rect.centery = float_y
        
        # Pulsing glow effect (recreate image with different alpha)
        pulse = abs(pygame.math.Vector2(1, 0).rotate(self.pulse_offset * 10).x)
        alpha_mult = 0.7 + pulse * 0.3
        
        self.image = pygame.Surface((28, 28), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (*GLOW_CYAN[:3], int(30 * alpha_mult)), (14, 14), 13)
        pygame.draw.circle(self.image, (*GLOW_CYAN[:3], int(80 * alpha_mult)), (14, 14), 9)
        pygame.draw.circle(self.image, (*GLOW_BLUE[:3], int(150 * alpha_mult)), (14, 14), 6)
        pygame.draw.circle(self.image, (200, 240, 255), (14, 14), 3)
        pygame.draw.circle(self.image, WHITE, (16, 12), 1)
