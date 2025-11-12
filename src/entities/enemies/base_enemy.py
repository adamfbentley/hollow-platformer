"""
Base Enemy Class
Shared functionality for all enemy types
"""

import pygame
import math
import random


class BaseEnemy(pygame.sprite.Sprite):
    """
    Base class for all enemies
    Provides common functionality like health, physics, hitstun, etc.
    """
    def __init__(self, x, y):
        super().__init__()
        self.rect = None  # Will be set by child classes
        
        # HP System
        self.max_health = 100
        self.current_health = self.max_health
        self.level = 1
        self.xp_reward = 10
        
        # Physics
        self.velocity_x = 0
        self.velocity_y = 0
        self.knockback_x = 0
        self.knockback_y = 0
        self.knockback_friction = 0.85
        self.knockback_gravity = 0.4
        self.gravity = 0.8
        self.on_ground = False
        self.is_grounded = False
        
        # Hitstun system
        self.hitstun_frames = 0
        self.hit_flash_timer = 0
        
        # Visual
        self.soul_color = (120, 120, 180)
        self.facing_right = True
        
        # References (set externally)
        self.particle_group = None
    
    def take_damage(self, damage):
        """Take damage from player attack"""
        self.current_health -= damage
        self.hit_flash_timer = 4
        
        if self.current_health <= 0:
            self.die()
    
    def die(self):
        """Handle enemy death with particle effects"""
        if hasattr(self, 'particle_group') and self.particle_group:
            # Import here to avoid circular dependency
            from src.world.particles import Particle
            
            for i in range(15):
                angle = random.uniform(0, 360)
                speed = random.uniform(2, 6)
                vel_x = math.cos(math.radians(angle)) * speed
                vel_y = math.sin(math.radians(angle)) * speed
                
                particle = Particle(
                    self.rect.centerx, self.rect.centery,
                    vel_x, vel_y,
                    self.soul_color,
                    lifetime=35,
                    size=3,
                    particle_type='spark'
                )
                self.particle_group.add(particle)
        
        self.kill()
    
    def apply_knockback(self, knockback_x, knockback_y):
        """Apply knockback force"""
        self.knockback_x = knockback_x
        self.knockback_y = knockback_y
    
    def apply_hitstun(self, frames):
        """Apply hitstun (freeze enemy AI for frames)"""
        self.hitstun_frames = max(self.hitstun_frames, frames)
    
    def apply_physics(self, platforms):
        """Apply physics: knockback, gravity, platform collision"""
        # Apply knockback velocity
        if abs(self.knockback_x) > 0.1 or abs(self.knockback_y) > 0.1:
            self.rect.x += self.knockback_x
            self.rect.y += self.knockback_y
            
            # Apply gravity to knockback
            self.knockback_y += self.knockback_gravity
            
            # Apply friction
            self.knockback_x *= self.knockback_friction
            self.knockback_y *= 0.98
            
            # Stop knockback when very small
            if abs(self.knockback_x) < 0.2:
                self.knockback_x = 0
            if abs(self.knockback_y) < 0.2:
                self.knockback_y = 0
        
        # Apply gravity
        self.velocity_y += self.gravity
        self.velocity_y = min(self.velocity_y, 15)  # Terminal velocity
        
        # Apply velocity
        self.rect.x += int(self.velocity_x)
        self.rect.y += int(self.velocity_y)
        
        # Platform collision
        self.on_ground = False
        self.is_grounded = False
        
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # Landing on top
                if self.velocity_y > 0 and self.rect.bottom > platform.rect.top:
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                    self.is_grounded = True
                
                # Hit ceiling
                elif self.velocity_y < 0 and self.rect.top < platform.rect.bottom:
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0
                
                # Wall collision
                if abs(self.knockback_x) > 2:
                    if self.knockback_x > 0 and self.rect.right > platform.rect.left:
                        self.rect.right = platform.rect.left
                        self.knockback_x *= -0.4  # Bounce
                    elif self.knockback_x < 0 and self.rect.left < platform.rect.right:
                        self.rect.left = platform.rect.right
                        self.knockback_x *= -0.4
    
    def draw_health_bar(self, surface, screen_pos):
        """Draw health bar above enemy"""
        if self.current_health >= self.max_health:
            return  # Don't show bar at full health
        
        bar_width = 60
        bar_height = 6
        bar_x = screen_pos.x + (self.rect.width - bar_width) // 2
        bar_y = screen_pos.y - 12
        
        # Background
        pygame.draw.rect(surface, (40, 20, 20), (bar_x, bar_y, bar_width, bar_height))
        
        # Health bar with color gradient
        health_percent = self.current_health / self.max_health
        health_width = int(bar_width * health_percent)
        
        if health_percent > 0.6:
            health_color = (50, 200, 50)  # Green
        elif health_percent > 0.3:
            health_color = (220, 180, 50)  # Yellow
        else:
            health_color = (220, 50, 50)  # Red
        
        pygame.draw.rect(surface, health_color, (bar_x, bar_y, health_width, bar_height))
        
        # Border
        pygame.draw.rect(surface, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 1)
