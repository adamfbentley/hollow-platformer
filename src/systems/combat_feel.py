"""
Enhanced Combat Feel
Implements satisfying combat inspired by Dead Cells and Hollow Knight
"""

import pygame
import math

class CombatFeelEnhancer:
    """Adds juice and impact to combat"""
    
    def __init__(self):
        # Hit pause parameters (freeze frame on hit)
        self.hit_pause_duration = 0
        self.hit_pause_timer = 0
        
        # Screen shake
        self.shake_intensity = 0
        self.shake_duration = 0
        self.shake_timer = 0
        
        # Attack commitment (can't move during certain frames)
        self.attack_lock_timer = 0
        
        # Combo system
        self.combo_window = 30  # Frames to continue combo
        self.combo_timer = 0
        self.combo_count = 0
        self.max_combo = 4
        
        # Cancel windows (Dead Cells style)
        self.can_cancel = False
        self.cancel_window_start = 5  # Frame when cancel becomes available
        
    def trigger_hit_pause(self, intensity=3):
        """Freeze frame effect on hit"""
        self.hit_pause_duration = intensity
        self.hit_pause_timer = intensity
    
    def trigger_screen_shake(self, intensity=5, duration=10):
        """Screen shake on heavy hit"""
        self.shake_intensity = max(self.shake_intensity, intensity)
        self.shake_duration = max(self.shake_duration, duration)
        self.shake_timer = self.shake_duration
    
    def update(self):
        """Update combat feel timers"""
        # Hit pause
        if self.hit_pause_timer > 0:
            self.hit_pause_timer -= 1
            return True  # Signal to pause game update
        
        # Screen shake
        if self.shake_timer > 0:
            self.shake_timer -= 1
        
        # Attack lock
        if self.attack_lock_timer > 0:
            self.attack_lock_timer -= 1
        
        # Combo timer
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo_count = 0
        
        return False
    
    def get_shake_offset(self):
        """Get current camera shake offset"""
        if self.shake_timer <= 0:
            return (0, 0)
        
        import random
        progress = 1.0 - (self.shake_timer / self.shake_duration)
        current_intensity = self.shake_intensity * (1.0 - progress)
        
        offset_x = random.uniform(-current_intensity, current_intensity)
        offset_y = random.uniform(-current_intensity, current_intensity)
        return (int(offset_x), int(offset_y))
    
    def is_attack_locked(self):
        """Check if player movement is locked by attack"""
        return self.attack_lock_timer > 0
    
    def start_attack_lock(self, duration):
        """Lock player movement during attack windup"""
        self.attack_lock_timer = duration
    
    def register_hit(self, is_heavy=False):
        """Register a successful hit"""
        if is_heavy:
            self.trigger_hit_pause(5)
            self.trigger_screen_shake(8, 12)
        else:
            self.trigger_hit_pause(2)
            self.trigger_screen_shake(4, 6)
        
        # Update combo
        if self.combo_timer > 0 and self.combo_count < self.max_combo:
            self.combo_count += 1
        else:
            self.combo_count = 1
        self.combo_timer = self.combo_window
