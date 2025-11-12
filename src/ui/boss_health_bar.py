"""
Boss Health Bar UI
Large, prominent boss health display at top of screen
Inspired by Hollow Knight and Dark Souls boss UI
"""

import pygame
from typing import Optional


class BossHealthBar:
    """
    Boss health bar UI component
    Shows boss name, health, and phase indicators
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        """
        Initialize boss health bar
        
        Args:
            screen_width: Width of the game screen
            screen_height: Height of the game screen
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Positioning (top-center of screen)
        self.bar_width = 800
        self.bar_height = 40
        self.bar_x = (screen_width - self.bar_width) // 2
        self.bar_y = 60
        
        # Name positioning
        self.name_y = 20
        
        # Fonts
        pygame.font.init()
        self.font_boss_name = pygame.font.Font(None, 56)
        self.font_health = pygame.font.Font(None, 32)
        
        # Colors
        self.COLOR_BACKGROUND = (20, 20, 20, 200)
        self.COLOR_OUTLINE = (255, 215, 0)  # Gold outline
        self.COLOR_HEALTH_HIGH = (200, 50, 50)  # Red
        self.COLOR_HEALTH_MED = (255, 150, 50)  # Orange
        self.COLOR_HEALTH_LOW = (255, 50, 50)  # Bright red
        self.COLOR_HEALTH_LOST = (60, 10, 10)  # Dark red
        self.COLOR_TEXT = (255, 255, 255)
        self.COLOR_PHASE_MARKER = (255, 215, 0)  # Gold
        
        # Animation
        self.slide_in_timer = 0
        self.slide_in_duration = 60  # 1 second
        self.damage_flash_timer = 0
        self.previous_health = 1.0
        
        # Phase markers
        self.phase_thresholds = []  # Will be set from boss
        
        # Active state
        self.is_active = False
        self.boss_name = ""
        self.current_health_percent = 1.0
        
    def activate(self, boss_name: str, phase_thresholds: list):
        """
        Activate the boss health bar
        
        Args:
            boss_name: Name of the boss
            phase_thresholds: List of health percentages where phases change
        """
        self.is_active = True
        self.boss_name = boss_name
        self.phase_thresholds = sorted(phase_thresholds, reverse=True)
        self.slide_in_timer = 0
        self.current_health_percent = 1.0
        self.previous_health = 1.0
    
    def deactivate(self):
        """Deactivate the boss health bar"""
        self.is_active = False
        self.boss_name = ""
        self.phase_thresholds = []
    
    def update(self, boss):
        """
        Update boss health bar
        
        Args:
            boss: Boss object
        """
        if not self.is_active:
            return
        
        # Update slide-in animation
        if self.slide_in_timer < self.slide_in_duration:
            self.slide_in_timer += 1
        
        # Update health
        new_health = boss.get_health_percent()
        
        # Flash effect on damage
        if new_health < self.previous_health:
            self.damage_flash_timer = 15
        
        self.current_health_percent = new_health
        self.previous_health = new_health
        
        # Update flash timer
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= 1
    
    def draw(self, surface: pygame.Surface):
        """
        Draw boss health bar
        
        Args:
            surface: Surface to draw on
        """
        if not self.is_active:
            return
        
        # Slide-in animation
        slide_progress = min(1.0, self.slide_in_timer / self.slide_in_duration)
        slide_offset = int((1.0 - slide_progress) * -100)  # Slide from top
        
        current_bar_y = self.bar_y + slide_offset
        current_name_y = self.name_y + slide_offset
        
        # Draw boss name (large, center-top)
        name_surface = self.font_boss_name.render(self.boss_name, True, self.COLOR_TEXT)
        name_rect = name_surface.get_rect(center=(self.screen_width // 2, current_name_y))
        
        # Name shadow for visibility
        name_shadow = self.font_boss_name.render(self.boss_name, True, (0, 0, 0))
        shadow_rect = name_shadow.get_rect(center=(self.screen_width // 2 + 3, current_name_y + 3))
        surface.blit(name_shadow, shadow_rect)
        surface.blit(name_surface, name_rect)
        
        # Draw health bar background
        bg_rect = pygame.Rect(self.bar_x, current_bar_y, self.bar_width, self.bar_height)
        bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg_surface.fill(self.COLOR_BACKGROUND)
        surface.blit(bg_surface, bg_rect)
        
        # Draw outline (gold, thick)
        pygame.draw.rect(surface, self.COLOR_OUTLINE, bg_rect, 3)
        
        # Draw lost health (dark red background)
        lost_health_rect = pygame.Rect(
            self.bar_x + 3,
            current_bar_y + 3,
            self.bar_width - 6,
            self.bar_height - 6
        )
        pygame.draw.rect(surface, self.COLOR_HEALTH_LOST, lost_health_rect)
        
        # Draw current health (with color gradient based on health level)
        if self.current_health_percent > 0:
            health_width = int((self.bar_width - 6) * self.current_health_percent)
            
            # Color based on health
            if self.current_health_percent > 0.6:
                health_color = self.COLOR_HEALTH_HIGH
            elif self.current_health_percent > 0.3:
                # Interpolate between high and medium
                t = (self.current_health_percent - 0.3) / 0.3
                health_color = self._lerp_color(self.COLOR_HEALTH_MED, self.COLOR_HEALTH_HIGH, t)
            else:
                # Interpolate between low and medium
                t = self.current_health_percent / 0.3
                health_color = self._lerp_color(self.COLOR_HEALTH_LOW, self.COLOR_HEALTH_MED, t)
            
            # Flash effect when taking damage
            if self.damage_flash_timer > 0:
                flash_intensity = self.damage_flash_timer / 15
                health_color = self._lerp_color(health_color, (255, 255, 255), flash_intensity * 0.5)
            
            health_rect = pygame.Rect(
                self.bar_x + 3,
                current_bar_y + 3,
                health_width,
                self.bar_height - 6
            )
            pygame.draw.rect(surface, health_color, health_rect)
        
        # Draw phase markers (vertical lines at phase thresholds)
        for threshold in self.phase_thresholds:
            if threshold < 1.0:  # Don't draw marker at 100%
                marker_x = self.bar_x + int((self.bar_width - 6) * threshold)
                marker_rect = pygame.Rect(
                    marker_x,
                    current_bar_y + 3,
                    3,
                    self.bar_height - 6
                )
                pygame.draw.rect(surface, self.COLOR_PHASE_MARKER, marker_rect)
        
        # Draw health percentage text
        health_text = f"{int(self.current_health_percent * 100)}%"
        health_surface = self.font_health.render(health_text, True, self.COLOR_TEXT)
        health_rect = health_surface.get_rect(
            center=(self.screen_width // 2, current_bar_y + self.bar_height // 2)
        )
        surface.blit(health_surface, health_rect)
    
    def _lerp_color(self, color1: tuple, color2: tuple, t: float) -> tuple:
        """
        Linear interpolation between two colors
        
        Args:
            color1: First color (R, G, B)
            color2: Second color (R, G, B)
            t: Interpolation factor (0 to 1)
            
        Returns:
            Interpolated color
        """
        return (
            int(color1[0] + (color2[0] - color1[0]) * t),
            int(color1[1] + (color2[1] - color1[1]) * t),
            int(color1[2] + (color2[2] - color1[2]) * t)
        )
