"""
Particle System
Visual effects for player actions and environmental feedback
"""

import pygame


class Particle(pygame.sprite.Sprite):
    """
    Particle effect for visual feedback
    Used for landing, dashing, wall slides, etc.
    """
    def __init__(self, x, y, velocity_x, velocity_y, color, lifetime=30, size=3, particle_type='dust'):
        super().__init__()
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.color = color
        self.size = size
        self.particle_type = particle_type
        
        self.image = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.draw_particle()
        
    def draw_particle(self):
        """Draw particle based on type"""
        self.image.fill((0, 0, 0, 0))
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        
        if self.particle_type == 'dust':
            # Dust cloud particle
            pygame.draw.circle(self.image, (*self.color[:3], alpha), (self.size, self.size), self.size)
        elif self.particle_type == 'spark':
            # Sharp spark particle
            points = [
                (self.size, 0),
                (self.size + self.size//2, self.size),
                (self.size, self.size * 2),
                (self.size - self.size//2, self.size)
            ]
            pygame.draw.polygon(self.image, (*self.color[:3], alpha), points)
        elif self.particle_type == 'trail':
            # Dash trail particle
            pygame.draw.ellipse(self.image, (*self.color[:3], alpha), 
                              (0, self.size//2, self.size * 2, self.size))
        
    def update(self):
        """Update particle position and lifetime"""
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        
        # Apply gravity to dust
        if self.particle_type == 'dust':
            self.velocity_y += 0.15
        
        # Fade out
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
        else:
            self.draw_particle()


class DamageNumber(pygame.sprite.Sprite):
    """Floating damage number that appears on hit"""
    
    def __init__(self, x, y, damage, is_crit=False):
        super().__init__()
        self.damage = damage
        self.is_crit = is_crit
        self.lifetime = 60
        self.age = 0
        
        # Font
        font_size = 24 if is_crit else 18
        self.font = pygame.font.Font(None, font_size)
        
        # Position
        self.x = x
        self.y = y
        self.velocity_y = -2
        
        # Color based on crit
        self.color = (255, 200, 50) if is_crit else (255, 255, 255)
        
        # Create text surface
        self.update_image()
    
    def update_image(self):
        """Update the damage number display"""
        text = str(int(self.damage))
        if self.is_crit:
            text = f"{text}!"
        
        # Fade out over time
        alpha = int(255 * (1 - self.age / self.lifetime))
        
        self.image = self.font.render(text, True, self.color)
        self.image.set_alpha(alpha)
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))
    
    def update(self):
        """Update damage number position and lifetime"""
        self.age += 1
        self.y += self.velocity_y
        self.velocity_y *= 0.95  # Slow down
        
        if self.age >= self.lifetime:
            self.kill()
        else:
            self.update_image()
