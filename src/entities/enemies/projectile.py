"""
Projectile System
Enemy projectiles (arrows, soul bolts, etc.)
"""

import pygame
import math


class Projectile(pygame.sprite.Sprite):
    """Enemy projectile"""
    
    def __init__(self, x, y, target_x, target_y, damage=10, speed=6, projectile_type='arrow'):
        super().__init__()
        self.damage = damage
        self.projectile_type = projectile_type
        self.lifetime = 180  # 3 seconds at 60fps
        
        # Calculate direction
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            self.velocity_x = (dx / distance) * speed
            self.velocity_y = (dy / distance) * speed
        else:
            self.velocity_x = speed
            self.velocity_y = 0
        
        # Create projectile sprite
        if projectile_type == 'arrow':
            self.image = pygame.Surface((16, 4), pygame.SRCALPHA)
            # Arrow shaft
            pygame.draw.rect(self.image, (80, 60, 40), (0, 1, 12, 2))
            # Arrow head
            pygame.draw.polygon(self.image, (120, 120, 140), [(12, 0), (16, 2), (12, 4)])
            # Feathers
            pygame.draw.line(self.image, (200, 180, 160), (1, 1), (1, 3), 1)
        elif projectile_type == 'soul_bolt':
            self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (150, 100, 200), (6, 6), 6)
            pygame.draw.circle(self.image, (200, 150, 255), (6, 6), 4)
            pygame.draw.circle(self.image, (255, 200, 255), (6, 6), 2)
        
        # Rotate arrow to face direction
        if projectile_type == 'arrow':
            angle = math.degrees(math.atan2(-self.velocity_y, self.velocity_x))
            self.image = pygame.transform.rotate(self.image, angle)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.x = float(x)
        self.y = float(y)
    
    def update(self, platforms=None):
        """Update projectile position"""
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
        
        # Check platform collision
        if platforms:
            for platform in platforms:
                if self.rect.colliderect(platform.rect):
                    self.kill()
                    break
