"""
Platform System
Detailed platforms with Hollow Knight-inspired aesthetic
"""

import pygame
import random
from src.core.constants import (
    STONE_DARK, STONE_MID, STONE_LIGHT,
    MOSS_GREEN, MOSS_LIGHT
)


class Platform(pygame.sprite.Sprite):
    """
    Detailed platform with Hollow Knight aesthetic
    Stone platforms with moss, cracks, and depth
    """
    def __init__(self, x, y, width, height, platform_type='stone'):
        super().__init__()
        self.width = width
        self.height = height
        self.platform_type = platform_type
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.draw_detailed_platform()
    
    def draw_detailed_platform(self):
        """Draw platform with enhanced detail and depth"""
        if self.platform_type == 'stone':
            # Base foundation (darkest layer)
            pygame.draw.rect(self.image, STONE_DARK, (0, 0, self.width, self.height))
            
            # Stone stratification layers
            layer1_h = max(3, self.height // 5)
            layer2_h = max(5, self.height // 3)
            layer3_h = max(4, self.height // 4)
            
            pygame.draw.rect(self.image, STONE_LIGHT, (0, 0, self.width, layer1_h))
            pygame.draw.rect(self.image, STONE_MID, (0, layer1_h, self.width, layer2_h))
            if layer1_h + layer2_h + layer3_h <= self.height:
                pygame.draw.rect(self.image, (38, 42, 58), (0, layer1_h + layer2_h, self.width, layer3_h))
            
            # Detailed moss growth on top
            if self.width > 30:
                moss_segments = max(3, self.width // 35)
                for i in range(moss_segments):
                    moss_x = (self.width // moss_segments) * i - 2
                    moss_w = (self.width // moss_segments) + 8
                    # Layered moss for depth
                    pygame.draw.ellipse(self.image, MOSS_GREEN, (moss_x, -2, moss_w, 8))
                    pygame.draw.ellipse(self.image, MOSS_LIGHT, (moss_x + 2, 0, moss_w - 4, 5))
                    pygame.draw.ellipse(self.image, (100, 140, 110), (moss_x + 4, 1, moss_w - 8, 3))
                    # Small moss clumps
                    if i % 2 == 0 and moss_w > 15:
                        pygame.draw.circle(self.image, MOSS_GREEN, (moss_x + moss_w//2, 2), 3)
            
            # Intricate crack patterns
            if self.width > 40 and self.height > 10:
                random.seed(self.rect.x + self.rect.y)
                
                # Major horizontal cracks
                num_h_cracks = max(1, self.height // 25)
                for i in range(num_h_cracks):
                    crack_y = 8 + i * (self.height // num_h_cracks)
                    crack_start = random.randint(2, 10)
                    crack_end = self.width - random.randint(2, 10)
                    pygame.draw.line(self.image, STONE_DARK, (crack_start, crack_y), (crack_end, crack_y), 1)
                    # Crack depth shadow
                    if crack_y + 1 < self.height:
                        pygame.draw.line(self.image, (20, 22, 32), (crack_start, crack_y + 1), (crack_end, crack_y + 1), 1)
                
                # Vertical stress cracks
                if self.width > 80:
                    num_v_cracks = self.width // 90
                    for i in range(num_v_cracks):
                        crack_x = 30 + i * 90 + random.randint(-10, 10)
                        crack_top = random.randint(4, 8)
                        crack_bottom = self.height - random.randint(2, 6)
                        pygame.draw.line(self.image, STONE_DARK, (crack_x, crack_top), (crack_x, crack_bottom), 1)
                        # Branching mini-crack
                        branch_y = crack_top + (crack_bottom - crack_top) // 2
                        branch_len = random.randint(5, 12)
                        if crack_x + branch_len < self.width:
                            pygame.draw.line(self.image, STONE_DARK, (crack_x, branch_y), 
                                           (crack_x + branch_len, branch_y + random.randint(-3, 3)), 1)
                
                # Rock texture spots (weathering)
                num_spots = self.width // 40
                for i in range(num_spots):
                    spot_x = random.randint(5, self.width - 10)
                    spot_y = random.randint(max(6, self.height // 4), self.height - 4)
                    spot_size = random.randint(2, 5)
                    pygame.draw.circle(self.image, (35, 38, 52), (spot_x, spot_y), spot_size)
                    if spot_size > 1:
                        pygame.draw.circle(self.image, (42, 46, 60), (spot_x - 1, spot_y - 1), spot_size - 1)
            
            # Enhanced edge definition
            pygame.draw.line(self.image, STONE_LIGHT, (0, 0), (self.width, 0), 3)  # Top highlight
            pygame.draw.line(self.image, (85, 95, 115), (0, 1), (self.width, 1), 1)  # Sub-highlight
            if self.height >= 2:
                pygame.draw.line(self.image, STONE_DARK, (0, self.height - 2), (self.width, self.height - 2), 2)
            pygame.draw.line(self.image, (20, 22, 32), (0, self.height - 1), (self.width, self.height - 1), 1)
            
            # Side edges for 3D effect
            if self.height > 15:
                pygame.draw.line(self.image, (48, 52, 68), (0, 2), (0, self.height - 3), 1)
                pygame.draw.line(self.image, STONE_DARK, (self.width - 1, 2), (self.width - 1, self.height - 3), 1)
            
        elif self.platform_type == 'wall':
            # Vertical wall style
            pygame.draw.rect(self.image, STONE_MID, (0, 0, self.width, self.height))
            
            # Side highlights
            pygame.draw.rect(self.image, STONE_LIGHT, (0, 0, 3, self.height))
            pygame.draw.rect(self.image, STONE_DARK, (self.width - 3, 0, 3, self.height))
            
            # Horizontal detail lines
            for i in range(self.height // 40):
                y = i * 40 + 10
                pygame.draw.line(self.image, STONE_DARK, (0, y), (self.width, y), 1)
