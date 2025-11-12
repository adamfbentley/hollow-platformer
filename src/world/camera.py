"""
Camera System
Smooth scrolling camera with zoom support and parallax layers
"""

import pygame
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT


class Camera:
    """
    Smooth scrolling camera that follows the player with zoom support
    """
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0
        self.zoom = 1.0  # Default zoom level
        self.target_zoom = 1.0
        self.min_zoom = 0.5  # Can zoom out to 50%
        self.max_zoom = 2.0  # Can zoom in to 200%
        
    def apply(self, entity):
        """Apply camera offset to entity position"""
        return pygame.Rect(entity.rect.x - self.x, entity.rect.y - self.y, 
                          entity.rect.width, entity.rect.height)
    
    def apply_pos(self, x, y):
        """Apply camera offset to raw position"""
        return (x - self.x, y - self.y)
    
    def adjust_zoom(self, delta):
        """Adjust zoom level"""
        self.target_zoom = max(self.min_zoom, min(self.max_zoom, self.target_zoom + delta))
    
    def update(self, target):
        """Smooth camera following with zoom"""
        # Smooth zoom transition
        zoom_speed = 0.1
        self.zoom += (self.target_zoom - self.zoom) * zoom_speed
        
        # Tighter deadzone for zoomed-in side-scroller feel
        deadzone_x = SCREEN_WIDTH // 10
        deadzone_y = SCREEN_HEIGHT // 8
        
        # Calculate target camera position (zoomed closer, player slightly left of center)
        target_x = target.rect.centerx - SCREEN_WIDTH // 2.5  # Player slightly left
        target_y = target.rect.centery - SCREEN_HEIGHT // 2.2  # Slightly above center
        
        # Camera anticipation based on velocity (helps with fast movement)
        anticipation_factor = 50
        target_x += target.velocity_x * anticipation_factor
        target_y += target.velocity_y * (anticipation_factor * 0.15)
        
        # Much smoother camera movement for cinematic feel
        smoothness = 0.08  # Slower = smoother
        self.x += (target_x - self.x) * smoothness
        self.y += (target_y - self.y) * smoothness
        
        # Keep camera within world bounds
        self.x = max(0, min(self.x, WORLD_WIDTH - SCREEN_WIDTH))
        self.y = max(0, min(self.y, WORLD_HEIGHT - SCREEN_HEIGHT))
        
        self.camera = pygame.Rect(self.x, self.y, self.width, self.height)


class ParallaxLayer:
    """
    Background layer that moves at different speed for depth effect
    """
    def __init__(self, scroll_speed, y_offset=0):
        self.scroll_speed = scroll_speed  # 0.0 to 1.0, lower = further away
        self.y_offset = y_offset
        
    def get_offset(self, camera_x, camera_y):
        """Calculate parallax offset based on camera position"""
        return (camera_x * self.scroll_speed, camera_y * self.scroll_speed + self.y_offset)
