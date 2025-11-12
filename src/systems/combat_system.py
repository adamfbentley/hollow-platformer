"""
Enhanced Combat System for RPG Platformer
Advanced physics, hitstun, screen shake, detailed attack phases, and particle effects
"""

import pygame
import math
import random


class ScreenShake:
    """Handles screen shake effects for impactful hits"""
    
    def __init__(self):
        self.shake_amount = 0
        self.shake_duration = 0
        self.shake_offset_x = 0
        self.shake_offset_y = 0
    
    def add_shake(self, intensity, duration=10):
        """Add screen shake effect"""
        self.shake_amount = max(self.shake_amount, intensity)
        self.shake_duration = max(self.shake_duration, duration)
    
    def update(self):
        """Update shake effect"""
        if self.shake_duration > 0:
            self.shake_duration -= 1
            self.shake_offset_x = random.randint(-self.shake_amount, self.shake_amount)
            self.shake_offset_y = random.randint(-self.shake_amount, self.shake_amount)
            
            # Decay shake amount
            self.shake_amount = max(0, self.shake_amount - 1)
        else:
            self.shake_offset_x = 0
            self.shake_offset_y = 0
    
    def get_offset(self):
        """Get current shake offset"""
        return (self.shake_offset_x, self.shake_offset_y)


class HitFreeze:
    """Handles hit freeze/hit stop for impactful moments"""
    
    def __init__(self):
        self.freeze_frames = 0
        self.max_freeze = 0
    
    def add_freeze(self, frames):
        """Add hit freeze frames"""
        self.freeze_frames = max(self.freeze_frames, frames)
        self.max_freeze = self.freeze_frames
    
    def is_frozen(self):
        """Check if currently frozen"""
        return self.freeze_frames > 0
    
    def update(self):
        """Update freeze timer"""
        if self.freeze_frames > 0:
            self.freeze_frames -= 1


class AttackPhases:
    """Manages attack animation phases: windup, active, recovery"""
    WINDUP = "windup"
    ACTIVE = "active"
    RECOVERY = "recovery"
    NONE = "none"


class MeleeAttack:
    """Enhanced melee combat with sophisticated physics and timing"""
    
    def __init__(self, player):
        self.player = player
        
        # Sound manager reference (set by game)
        self.sound_manager = None
        
        # Attack state with phases
        self.is_attacking = False
        self.attack_frame = 0
        self.attack_phase = AttackPhases.NONE
        
        # Attack timing (frames)
        self.windup_frames = 3      # Before hitbox becomes active
        self.active_frames = 6       # Hitbox is active
        self.recovery_frames = 5     # After attack, before next action
        self.total_frames = self.windup_frames + self.active_frames + self.recovery_frames
        
        self.attack_cooldown = 0
        self.attack_cooldown_max = 15
        
        # Combo system with timing
        self.combo_count = 0
        self.max_combo = 5
        self.combo_timer = 0
        self.combo_window = 45  # Frames to continue combo
        self.combo_indicator_flash = 0
        
        # Heavy attack
        self.charging_heavy = False
        self.heavy_charge_time = 0
        self.heavy_charge_required = 30
        self.is_heavy_attack = False
        
        # Attack properties
        self.attack_range = 50
        self.attack_arc = 90  # Degrees
        self.base_knockback = 12
        
        # Mouse-based aiming
        self.mouse_pos = (0, 0)
        self.attack_angle = 0
        self.attack_rotation = 0  # For visual weapon rotation
        
        # Directional attacks (can attack up/down/side)
        self.attack_direction = (1, 0)  # Normalized direction vector
        
        # Hit tracking
        self.hit_enemies = set()
        self.hit_count_this_attack = 0
        
        # Visual effects
        self.weapon_trail_points = []  # For advanced weapon trails
        self.slash_particles = []
        
        # Attack canceling
        self.can_cancel = False
        self.cancel_window_start = 4  # Frame when canceling becomes available
    
    def update(self):
        """Update attack state with detailed phase management"""
        # Update attack animation phases
        if self.is_attacking:
            self.attack_frame += 1
            
            # Determine current phase
            if self.attack_frame <= self.windup_frames:
                self.attack_phase = AttackPhases.WINDUP
                self.can_cancel = False
            elif self.attack_frame <= self.windup_frames + self.active_frames:
                self.attack_phase = AttackPhases.ACTIVE
                self.can_cancel = (self.attack_frame >= self.cancel_window_start)
            else:
                self.attack_phase = AttackPhases.RECOVERY
                self.can_cancel = True
            
            # Update weapon rotation for visual effect
            progress = self.attack_frame / self.total_frames
            self.attack_rotation = math.sin(progress * math.pi) * 180
            
            # End attack
            if self.attack_frame >= self.total_frames:
                self.end_attack()
        
        # Update cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Update combo timer
        if self.combo_timer > 0:
            self.combo_timer -= 1
            # Flash indicator near end of combo window
            if self.combo_timer < 15:
                self.combo_indicator_flash = (self.combo_indicator_flash + 1) % 6
            else:
                self.combo_indicator_flash = 0
            
            if self.combo_timer == 0:
                self.combo_count = 0
        
        # Update heavy attack charge
        if self.charging_heavy:
            self.heavy_charge_time += 1
        
        # Update weapon trail
        self.update_weapon_trail()
    
    def update_weapon_trail(self):
        """Update weapon trail effect"""
        if self.is_attacking and self.attack_phase == AttackPhases.ACTIVE:
            # Add trail point
            player_center = (self.player.rect.centerx, self.player.rect.centery)
            angle = self.attack_angle + math.radians(self.attack_rotation)
            trail_length = self.attack_range
            
            trail_x = player_center[0] + math.cos(angle) * trail_length
            trail_y = player_center[1] + math.sin(angle) * trail_length
            
            self.weapon_trail_points.append({
                'pos': (trail_x, trail_y),
                'life': 8,
                'alpha': 255
            })
        
        # Update and remove old trail points
        for point in self.weapon_trail_points[:]:
            point['life'] -= 1
            point['alpha'] = int(255 * (point['life'] / 8))
            if point['life'] <= 0:
                self.weapon_trail_points.remove(point)
    
    def try_attack(self, heavy=False):
        """Attempt to start an attack"""
        # Allow attack canceling during cancel window
        if self.is_attacking and not self.can_cancel:
            return False
        
        if self.attack_cooldown > 0:
            return False
        
        if heavy:
            self.charging_heavy = True
            self.heavy_charge_time = 0
            return True
        else:
            self.start_attack(heavy=False)
            return True
    
    def release_heavy_attack(self):
        """Release heavy attack if charged enough"""
        if self.charging_heavy:
            if self.heavy_charge_time >= self.heavy_charge_required:
                self.start_attack(heavy=True)
            else:
                self.start_attack(heavy=False)
            self.charging_heavy = False
            self.heavy_charge_time = 0
    
    def start_attack(self, heavy=False):
        """Start an attack with proper initialization"""
        # End previous attack if canceling
        if self.is_attacking:
            self.end_attack()
        
        self.is_attacking = True
        self.is_heavy_attack = heavy
        self.attack_frame = 0
        self.attack_phase = AttackPhases.WINDUP
        self.hit_enemies.clear()
        self.hit_count_this_attack = 0
        self.weapon_trail_points.clear()
        
        # Play attack whoosh sound
        if self.sound_manager:
            self.sound_manager.play_sound('player_attack_woosh', category='player')
        
        # Calculate attack angle from player to mouse
        dx = self.mouse_pos[0] - self.player.rect.centerx
        dy = self.mouse_pos[1] - self.player.rect.centery
        self.attack_angle = math.atan2(dy, dx)
        
        # Normalized direction vector
        magnitude = math.sqrt(dx*dx + dy*dy)
        if magnitude > 0:
            self.attack_direction = (dx / magnitude, dy / magnitude)
        else:
            self.attack_direction = (1, 0)
        
        # Apply attack speed from stats
        attack_speed_mult = self.player.stats.attack_speed
        self.attack_cooldown_max = max(8, int(15 / attack_speed_mult))
        self.attack_cooldown = self.attack_cooldown_max
        
        # Heavy attack modifiers
        if heavy:
            self.attack_cooldown *= 1.5
            self.windup_frames = 5
            self.active_frames = 8
            self.recovery_frames = 8
        else:
            self.windup_frames = 3
            self.active_frames = 6
            self.recovery_frames = 5
        
        self.total_frames = self.windup_frames + self.active_frames + self.recovery_frames
        
        # Update combo
        if self.combo_timer > 0 and self.combo_count < self.max_combo:
            self.combo_count += 1
        else:
            self.combo_count = 1
        
        self.combo_timer = self.combo_window
    
    def end_attack(self):
        """End attack animation"""
        self.is_attacking = False
        self.attack_frame = 0
        self.attack_phase = AttackPhases.NONE
        self.is_heavy_attack = False
        self.hit_enemies.clear()
        self.can_cancel = False
    
    def get_attack_hitbox(self):
        """Get the hitbox for current attack"""
        if not self.is_attacking or self.attack_phase != AttackPhases.ACTIVE:
            return None
        
        # Calculate attack direction from player to mouse
        player_center_x = self.player.rect.centerx
        player_center_y = self.player.rect.centery
        
        # Determine range based on attack type
        attack_range = self.attack_range
        if self.is_heavy_attack:
            attack_range *= 1.3
        
        # Project hitbox in direction of attack
        hitbox_offset_x = math.cos(self.attack_angle) * (attack_range * 0.6)
        hitbox_offset_y = math.sin(self.attack_angle) * (attack_range * 0.6)
        
        hitbox_size = attack_range if self.is_heavy_attack else int(attack_range * 0.85)
        hitbox_x = player_center_x + hitbox_offset_x - hitbox_size // 2
        hitbox_y = player_center_y + hitbox_offset_y - hitbox_size // 2
        
        hitbox = pygame.Rect(hitbox_x, hitbox_y, hitbox_size, hitbox_size)
        
        return hitbox
    
    def calculate_damage(self):
        """Calculate attack damage with all modifiers"""
        base_damage = self.player.stats.attack_damage
        
        # Combo multiplier (each hit in combo does 12% more damage)
        combo_mult = 1.0 + (self.combo_count - 1) * 0.12
        
        # Heavy attack multiplier
        heavy_mult = 1.8 if self.is_heavy_attack else 1.0
        
        # Critical hit check (improved algorithm)
        crit_chance = self.player.stats.critical_chance
        is_crit = random.random() < crit_chance
        crit_mult = self.player.stats.critical_multiplier if is_crit else 1.0
        
        # Attack phase damage modifier (early hits do slightly more)
        phase_progress = (self.attack_frame - self.windup_frames) / self.active_frames
        phase_mult = 1.0 + (1.0 - phase_progress) * 0.15  # Up to 15% more damage early
        
        total_damage = base_damage * combo_mult * heavy_mult * crit_mult * phase_mult
        
        return int(total_damage), is_crit
    
    def calculate_knockback(self):
        """Calculate knockback vector with physics"""
        base_kb = self.base_knockback
        
        # Heavy attacks have more knockback
        if self.is_heavy_attack:
            base_kb *= 1.8
        
        # Combo increases knockback slightly
        combo_mult = 1.0 + (self.combo_count - 1) * 0.1
        
        knockback_force = base_kb * combo_mult
        
        # Calculate knockback direction (same as attack direction)
        kb_x = self.attack_direction[0] * knockback_force
        kb_y = self.attack_direction[1] * knockback_force * 0.7  # Less vertical knockback
        
        # Add slight upward component for juggle potential
        kb_y -= 2
        
        return kb_x, kb_y
    
    def check_hit_enemy(self, enemy, screen_shake, hit_freeze):
        """Check if attack hits an enemy and apply effects"""
        if not self.is_attacking or self.attack_phase != AttackPhases.ACTIVE:
            return False
        
        # Don't hit same enemy multiple times in one attack
        if enemy in self.hit_enemies:
            return False
        
        hitbox = self.get_attack_hitbox()
        if hitbox is None:
            return False
        
        # Check collision
        if hitbox.colliderect(enemy.rect):
            self.hit_enemies.add(enemy)
            self.hit_count_this_attack += 1
            
            # Calculate damage
            damage, is_crit = self.calculate_damage()
            
            # Apply damage to enemy
            enemy.take_damage(damage)
            
            # Calculate and apply knockback
            kb_x, kb_y = self.calculate_knockback()
            enemy.apply_knockback(kb_x, kb_y)
            
            # Apply hitstun
            hitstun_frames = 12 if self.is_heavy_attack else 8
            if hasattr(enemy, 'apply_hitstun'):
                enemy.apply_hitstun(hitstun_frames)
            
            # Screen shake (more intense for heavy/crit)
            shake_intensity = 3
            if self.is_heavy_attack:
                shake_intensity = 6
            if is_crit:
                shake_intensity += 2
            screen_shake.add_shake(shake_intensity, duration=8)
            
            # Hit freeze for heavy attacks and crits
            if self.is_heavy_attack:
                hit_freeze.add_freeze(4)
            elif is_crit:
                hit_freeze.add_freeze(2)
            
            # Spawn hit effects
            self.spawn_hit_effects(enemy, damage, is_crit)
            
            return True
        
        return False
    
    def spawn_hit_effects(self, enemy, damage, is_crit):
        """Spawn advanced visual effects for hits"""
        if not self.player.particle_group:
            return
        
        from platformer_game import Particle, DamageNumber
        
        # Calculate hit position (along attack direction)
        hit_x = enemy.rect.centerx
        hit_y = enemy.rect.centery
        
        # Damage number
        damage_number = DamageNumber(hit_x, hit_y - 20, damage, is_crit)
        self.player.particle_group.add(damage_number)
        
        # Impact particles (directional burst)
        num_particles = 15 if self.is_heavy_attack else 10
        if is_crit:
            num_particles += 5
        
        for i in range(num_particles):
            # Spray in direction of attack with spread
            spread_angle = random.uniform(-45, 45)
            angle = self.attack_angle + math.radians(spread_angle)
            speed = random.uniform(3, 8)
            
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            
            # Color based on hit type
            if is_crit:
                color = (255, 50, 50)  # Red for crits
            elif self.is_heavy_attack:
                color = (255, 200, 50)  # Orange for heavy
            else:
                color = (200, 200, 255)  # Blue-white for normal
            
            size = random.randint(3, 6) if self.is_heavy_attack else random.randint(2, 4)
            lifetime = random.randint(20, 35)
            
            particle = Particle(
                hit_x, hit_y,
                vel_x, vel_y,
                color, size, lifetime
            )
            self.player.particle_group.add(particle)
        
        # Soul/blood splatter particles
        for i in range(8):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 5)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed - 1  # Slight upward bias
            
            # Get enemy color if available
            if hasattr(enemy, 'soul_color'):
                color = enemy.soul_color
            else:
                color = (150, 150, 200)
            
            size = random.randint(2, 5)
            lifetime = random.randint(25, 40)
            
            particle = Particle(
                hit_x + random.randint(-10, 10),
                hit_y + random.randint(-10, 10),
                vel_x, vel_y,
                color, size, lifetime
            )
            self.player.particle_group.add(particle)
        
        # Shockwave ring for heavy attacks
        if self.is_heavy_attack:
            for i in range(12):
                angle = (i / 12) * math.pi * 2
                speed = 6
                vel_x = math.cos(angle) * speed
                vel_y = math.sin(angle) * speed
                
                particle = Particle(
                    hit_x, hit_y,
                    vel_x, vel_y,
                    (255, 255, 200), 3, 15
                )
                self.player.particle_group.add(particle)
