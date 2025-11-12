"""
Hollow Knight-Style Combat System
Simple directional melee combat with smooth animations
No aiming - attacks in facing direction with arc hitbox
"""

import pygame
import math
from enum import Enum

class AttackType(Enum):
    """Types of attacks"""
    LIGHT = "light"
    HEAVY = "heavy"
    UPWARD = "upward"  # Hollow Knight's up-slash

class AttackPhase(Enum):
    """Attack animation phases"""
    NONE = "none"
    WINDUP = "windup"
    ACTIVE = "active"
    RECOVERY = "recovery"

class HollowKnightCombat:
    """
    Hollow Knight-inspired melee combat system
    - Simple directional attacks (no aiming)
    - Arc hitboxes in facing direction
    - Smooth 3-hit combo chains
    - Attack momentum and commitment
    """
    
    def __init__(self, player):
        self.player = player
        
        # Attack state
        self.is_attacking = False
        self.attack_type = None
        self.attack_phase = AttackPhase.NONE
        self.attack_timer = 0
        self.attack_frame = 0
        
        # Combo system
        self.combo_count = 0  # 0, 1, 2 (3 hit combo)
        self.combo_timer = 0
        self.combo_window = 15  # Frames to continue combo
        self.next_attack_queued = False
        
        # Timing (in frames at 60 FPS)
        # Hollow Knight has very tight, responsive attacks
        self.light_timings = {
            'windup': 4,    # Very short windup (0.067s)
            'active': 8,    # Active hit window (0.133s)
            'recovery': 10  # Recovery before next action (0.167s)
        }
        
        self.heavy_timings = {
            'windup': 8,    # Longer windup (0.133s)
            'active': 12,   # Longer active window (0.2s)
            'recovery': 18  # Longer recovery (0.3s)
        }
        
        self.upward_timings = {
            'windup': 5,    # Quick startup
            'active': 10,   # Good active window
            'recovery': 12  # Medium recovery
        }
        
        # Hitbox properties
        self.attack_range = 45  # Range in pixels
        self.attack_arc = 120   # Arc angle in degrees (Hollow Knight: ~120°)
        
        # Visual effects
        self.slash_particles = []
        self.hit_enemies = set()  # Track hit enemies this attack
        
    def try_attack(self, attack_type='light', is_up_attack=False):
        """
        Attempt to start an attack
        Returns True if attack started
        """
        # Can only attack if not already attacking, or queueing combo
        if self.is_attacking:
            # Allow combo queueing during late active phase or recovery
            if self.attack_phase == AttackPhase.ACTIVE and self.attack_timer > self.get_active_duration() * 0.6:
                self.next_attack_queued = True
                return False
            elif self.attack_phase == AttackPhase.RECOVERY:
                self.next_attack_queued = True
                return False
            return False
        
        # Determine attack type
        if is_up_attack:
            self.attack_type = AttackType.UPWARD
        elif attack_type == 'heavy':
            self.attack_type = AttackType.HEAVY
        else:
            self.attack_type = AttackType.LIGHT
        
        # Start attack
        self._start_attack()
        return True
    
    def _start_attack(self):
        """Initialize attack state"""
        self.is_attacking = True
        self.attack_phase = AttackPhase.WINDUP
        self.attack_timer = 0
        self.attack_frame = 0
        self.hit_enemies.clear()
        
        # Combo tracking
        if self.combo_timer > 0:
            # Continue combo
            self.combo_count = min(self.combo_count + 1, 2)
        else:
            # Start new combo
            self.combo_count = 0
        
        self.combo_timer = self.combo_window
        
        # Apply attack momentum (Hollow Knight slides forward slightly)
        if self.player.on_ground:
            momentum = 2.5 if self.attack_type == AttackType.LIGHT else 2.0
            if self.player.facing_right:
                self.player.velocity_x = max(self.player.velocity_x, momentum)
            else:
                self.player.velocity_x = min(self.player.velocity_x, -momentum)
        
        # Lock movement during windup
        if hasattr(self.player, 'combat_feel'):
            windup_duration = self.get_windup_duration()
            self.player.combat_feel.start_attack_lock(windup_duration)
    
    def update(self):
        """Update combat state"""
        # Update combo timer
        if self.combo_timer > 0:
            self.combo_timer -= 1
            if self.combo_timer == 0:
                self.combo_count = 0
        
        # Update attack if active
        if not self.is_attacking:
            return
        
        self.attack_timer += 1
        
        # Phase transitions
        if self.attack_phase == AttackPhase.WINDUP:
            if self.attack_timer >= self.get_windup_duration():
                self._enter_active_phase()
        
        elif self.attack_phase == AttackPhase.ACTIVE:
            if self.attack_timer >= self.get_windup_duration() + self.get_active_duration():
                self._enter_recovery_phase()
        
        elif self.attack_phase == AttackPhase.RECOVERY:
            if self.attack_timer >= self.get_total_duration():
                self._end_attack()
    
    def _enter_active_phase(self):
        """Enter active attack phase"""
        self.attack_phase = AttackPhase.ACTIVE
        
        # Spawn slash effect particles
        self._spawn_slash_particles()
        
        # Play attack sound (if available)
        if hasattr(self.player, 'audio_manager'):
            self.player.audio_manager.play_sound('attack', 'swing')
    
    def _enter_recovery_phase(self):
        """Enter recovery phase"""
        self.attack_phase = AttackPhase.RECOVERY
        
        # Check for queued combo attack
        if self.next_attack_queued and self.combo_count < 2:
            # Will start next attack after minimal recovery
            pass
    
    def _end_attack(self):
        """End attack sequence"""
        # Check for queued attack
        if self.next_attack_queued and self.combo_count < 2:
            self.next_attack_queued = False
            self._start_attack()
            return
        
        self.is_attacking = False
        self.attack_phase = AttackPhase.NONE
        self.attack_timer = 0
        self.attack_frame = 0
        self.next_attack_queued = False
    
    def get_windup_duration(self):
        """Get windup duration for current attack"""
        if self.attack_type == AttackType.LIGHT:
            return self.light_timings['windup']
        elif self.attack_type == AttackType.HEAVY:
            return self.heavy_timings['windup']
        elif self.attack_type == AttackType.UPWARD:
            return self.upward_timings['windup']
        return 4
    
    def get_active_duration(self):
        """Get active duration for current attack"""
        if self.attack_type == AttackType.LIGHT:
            return self.light_timings['active']
        elif self.attack_type == AttackType.HEAVY:
            return self.heavy_timings['active']
        elif self.attack_type == AttackType.UPWARD:
            return self.upward_timings['active']
        return 8
    
    def get_recovery_duration(self):
        """Get recovery duration for current attack"""
        if self.attack_type == AttackType.LIGHT:
            return self.light_timings['recovery']
        elif self.attack_type == AttackType.HEAVY:
            return self.heavy_timings['recovery']
        elif self.attack_type == AttackType.UPWARD:
            return self.upward_timings['recovery']
        return 10
    
    def get_total_duration(self):
        """Get total attack duration"""
        return self.get_windup_duration() + self.get_active_duration() + self.get_recovery_duration()
    
    def get_attack_progress(self):
        """Get attack progress as 0.0 to 1.0"""
        if not self.is_attacking:
            return 0.0
        return min(self.attack_timer / self.get_total_duration(), 1.0)
    
    def get_hitbox(self):
        """
        Get attack hitbox as a rect
        Returns None if not in active phase
        """
        if self.attack_phase != AttackPhase.ACTIVE:
            return None
        
        # Calculate hitbox based on attack type and facing direction
        center_x = self.player.rect.centerx
        center_y = self.player.rect.centery
        
        if self.attack_type == AttackType.UPWARD:
            # Upward slash - arc above player
            hitbox_rect = pygame.Rect(
                center_x - self.attack_range // 2,
                center_y - self.attack_range,
                self.attack_range,
                self.attack_range
            )
        else:
            # Horizontal slash - arc in front
            if self.player.facing_right:
                hitbox_rect = pygame.Rect(
                    center_x,
                    center_y - self.attack_range // 2,
                    self.attack_range,
                    self.attack_range
                )
            else:
                hitbox_rect = pygame.Rect(
                    center_x - self.attack_range,
                    center_y - self.attack_range // 2,
                    self.attack_range,
                    self.attack_range
                )
        
        return hitbox_rect
    
    def check_hit(self, enemy):
        """
        Check if attack hits an enemy
        Returns True if hit (and not already hit this attack)
        """
        if not self.is_attacking or self.attack_phase != AttackPhase.ACTIVE:
            return False
        
        # Don't hit same enemy twice in one attack
        if id(enemy) in self.hit_enemies:
            return False
        
        hitbox = self.get_hitbox()
        if hitbox and hitbox.colliderect(enemy.rect):
            # Additional arc check for more precise hitbox
            if self._is_in_attack_arc(enemy):
                self.hit_enemies.add(id(enemy))
                
                # Trigger combat feel effects
                if hasattr(self.player, 'combat_feel'):
                    is_heavy = self.attack_type == AttackType.HEAVY
                    self.player.combat_feel.register_hit(is_heavy)
                
                return True
        
        return False
    
    def _is_in_attack_arc(self, enemy):
        """Check if enemy is within attack arc"""
        dx = enemy.rect.centerx - self.player.rect.centerx
        dy = enemy.rect.centery - self.player.rect.centery
        
        # Get angle to enemy
        angle = math.degrees(math.atan2(dy, dx))
        
        # Normalize to 0-360
        if angle < 0:
            angle += 360
        
        # Get attack direction angle
        if self.attack_type == AttackType.UPWARD:
            target_angle = 270  # Up
        elif self.player.facing_right:
            target_angle = 0    # Right
        else:
            target_angle = 180  # Left
        
        # Check if within arc
        angle_diff = abs(angle - target_angle)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff
        
        return angle_diff <= self.attack_arc / 2
    
    def get_damage(self):
        """Get damage for current attack"""
        base_damage = self.player.stats.get_stat('attack')
        
        # Damage multipliers
        if self.attack_type == AttackType.LIGHT:
            return base_damage * 1.0
        elif self.attack_type == AttackType.HEAVY:
            return base_damage * 1.8
        elif self.attack_type == AttackType.UPWARD:
            return base_damage * 1.2
        
        return base_damage
    
    def _spawn_slash_particles(self):
        """Spawn visual slash effect particles"""
        # Create arc of particles for slash effect
        center_x = self.player.rect.centerx
        center_y = self.player.rect.centery
        
        # Determine slash direction
        if self.attack_type == AttackType.UPWARD:
            base_angle = -90  # Up
        elif self.player.facing_right:
            base_angle = 0    # Right
        else:
            base_angle = 180  # Left
        
        # Spawn particles in arc
        num_particles = 8
        for i in range(num_particles):
            angle_offset = (i / num_particles - 0.5) * self.attack_arc
            angle = math.radians(base_angle + angle_offset)
            
            # Position along arc
            distance = self.attack_range * 0.7
            px = center_x + math.cos(angle) * distance
            py = center_y + math.sin(angle) * distance
            
            # Velocity outward
            speed = 3.0
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            # Color based on combo
            if self.combo_count == 0:
                color = (200, 220, 255)  # White-blue
            elif self.combo_count == 1:
                color = (255, 220, 180)  # Orange
            else:
                color = (255, 150, 150)  # Red (final hit)
            
            from src.world.particles import Particle
            particle = Particle(
                px, py, vx, vy,
                color=color,
                lifetime=12,
                size=4,
                fade=True
            )
            self.slash_particles.append(particle)
    
    def update_particles(self):
        """Update slash effect particles"""
        self.slash_particles = [p for p in self.slash_particles if p.update()]
    
    def draw_particles(self, surface, camera):
        """Draw slash effect particles"""
        for particle in self.slash_particles:
            particle.draw(surface, camera)
    
    def draw_debug(self, surface, camera):
        """Draw debug visualization of hitboxes"""
        if not self.is_attacking:
            return
        
        hitbox = self.get_hitbox()
        if hitbox:
            # Draw hitbox
            debug_rect = pygame.Rect(
                hitbox.x - camera.x,
                hitbox.y - camera.y,
                hitbox.width,
                hitbox.height
            )
            
            # Color based on phase
            if self.attack_phase == AttackPhase.WINDUP:
                color = (255, 255, 0, 100)  # Yellow
            elif self.attack_phase == AttackPhase.ACTIVE:
                color = (255, 0, 0, 150)    # Red
            else:
                color = (100, 100, 100, 50) # Gray
            
            # Draw semi-transparent
            s = pygame.Surface((debug_rect.width, debug_rect.height), pygame.SRCALPHA)
            s.fill(color)
            surface.blit(s, (debug_rect.x, debug_rect.y))
