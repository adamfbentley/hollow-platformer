"""
Hollow Warrior Enemy
Ground-based melee enemy inspired by Hollow Knight
Patrols platforms, chases player, attacks in melee range
"""

import pygame
import math
import random
from src.world.particles import Particle


class HollowWarrior(pygame.sprite.Sprite):
    """
    Ground-based melee enemy - Hollow Knight-inspired warrior
    Patrols platforms, chases player, attacks in melee range
    """
    def __init__(self, x, y, patrol_range=200):
        super().__init__()
        self.create_warrior_sprite()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # AI state
        self.state = 'patrol'  # patrol, chase, attack
        self.velocity_x = 0
        self.velocity_y = 0
        self.patrol_start_x = x
        self.patrol_range = patrol_range
        self.detection_range = 300
        self.chase_speed = 3.0
        self.patrol_speed = 1.5
        self.facing_right = True
        
        # Attack
        self.attack_cooldown = 0
        self.attack_range = 50
        self.attack_damage = 15
        self.is_attacking = False
        self.attack_frame = 0
        
        # Animation
        self.animation_timer = 0
        self.animation_frame = 0
        self.animation_state = 'patrol'  # patrol, chase, attack
        self.animation_frames = {}
        self.create_animation_frames()
        
        # HP System
        self.max_health = 80
        self.current_health = self.max_health
        self.level = 1
        self.xp_reward = 20
        
        # Physics
        self.gravity = 0.8
        self.on_ground = False
        self.knockback_x = 0
        self.knockback_y = 0
        self.knockback_friction = 0.85
        
        # Hitstun
        self.hitstun_frames = 0
        self.hit_flash_timer = 0
        
        # Visual
        self.soul_color = (80, 80, 120)
        self.particle_group = None
    
    def create_warrior_sprite(self):
        """Draw a dark hollow warrior - 2x scale"""
        temp_surface = pygame.Surface((40, 50), pygame.SRCALPHA)
        
        # Dark knight colors
        dark_metal = (45, 45, 55)
        metal = (65, 65, 75)
        metal_light = (85, 85, 95)
        void_black = (10, 10, 15)
        soul_glow = (100, 100, 150)
        
        # Body (armored)
        pygame.draw.ellipse(temp_surface, dark_metal, (12, 20, 16, 22))  # Torso
        
        # Legs
        pygame.draw.rect(temp_surface, dark_metal, (14, 38, 5, 10))  # Left leg
        pygame.draw.rect(temp_surface, metal, (21, 38, 5, 10))  # Right leg
        
        # Arms
        pygame.draw.rect(temp_surface, dark_metal, (8, 22, 4, 12))  # Left arm
        pygame.draw.rect(temp_surface, metal, (28, 22, 4, 12))  # Right arm
        
        # Shoulders (pauldrons)
        pygame.draw.ellipse(temp_surface, metal_light, (7, 18, 8, 6))
        pygame.draw.ellipse(temp_surface, metal_light, (25, 18, 8, 6))
        
        # Helm
        pygame.draw.ellipse(temp_surface, dark_metal, (13, 8, 14, 16))
        pygame.draw.ellipse(temp_surface, void_black, (15, 10, 10, 12))
        
        # Glowing eyes
        pygame.draw.circle(temp_surface, soul_glow, (17, 14), 2)
        pygame.draw.circle(temp_surface, soul_glow, (23, 14), 2)
        
        # Weapon (sword)
        pygame.draw.rect(temp_surface, metal_light, (35, 24, 3, 18))  # Blade
        pygame.draw.rect(temp_surface, dark_metal, (34, 40, 5, 3))  # Guard
        pygame.draw.rect(temp_surface, metal, (36, 42, 2, 5))  # Handle
        
        # Scale up 2x for better resolution
        self.image = pygame.transform.scale2x(temp_surface)
    
    def create_animation_frames(self):
        """Create animated frames for warrior with articulated limbs"""
        self.animation_frames = {
            'patrol': [self.draw_frame_walk(i) for i in range(4)],
            'chase': [self.draw_frame_walk(i) for i in range(4)],
            'attack': [self.draw_frame_attack(i) for i in range(3)]
        }
    
    def draw_limb(self, surface, start_pos, end_pos, thickness, color):
        """Draw articulated limb with rounded ends"""
        pygame.draw.line(surface, color, start_pos, end_pos, thickness)
        pygame.draw.circle(surface, color, start_pos, thickness // 2)
        pygame.draw.circle(surface, color, end_pos, thickness // 2)
    
    def draw_frame_walk(self, frame):
        """Draw walking animation with swinging arms and legs"""
        surface = pygame.Surface((80, 100), pygame.SRCALPHA)
        
        # Walk cycle
        progress = frame / 4.0
        leg_swing = int(math.sin(progress * math.pi * 2) * 12)
        arm_swing = int(math.cos(progress * math.pi * 2) * 8)
        bob = abs(math.sin(progress * math.pi * 2)) * 3
        
        # Colors
        dark_metal = (45, 45, 55)
        metal = (65, 65, 75)
        metal_light = (85, 85, 95)
        void_black = (10, 10, 15)
        soul_glow = (100, 100, 150)
        
        # Body
        body_y = 40 - int(bob)
        pygame.draw.ellipse(surface, dark_metal, (32, body_y, 16, 22))
        
        # Legs with articulation
        hip_y = body_y + 22
        # Left leg
        knee_x_l = 36 + leg_swing
        knee_y_l = hip_y + 12
        self.draw_limb(surface, (36, hip_y), (knee_x_l, knee_y_l), 6, dark_metal)
        self.draw_limb(surface, (knee_x_l, knee_y_l), (knee_x_l, knee_y_l + 14), 6, dark_metal)
        # Right leg
        knee_x_r = 44 - leg_swing
        knee_y_r = hip_y + 12
        self.draw_limb(surface, (44, hip_y), (knee_x_r, knee_y_r), 6, metal)
        self.draw_limb(surface, (knee_x_r, knee_y_r), (knee_x_r, knee_y_r + 14), 6, metal)
        
        # Arms with articulation
        shoulder_y = body_y + 4
        # Left arm
        elbow_x_l = 28 + arm_swing
        elbow_y_l = shoulder_y + 10
        self.draw_limb(surface, (32, shoulder_y), (elbow_x_l, elbow_y_l), 5, dark_metal)
        self.draw_limb(surface, (elbow_x_l, elbow_y_l), (elbow_x_l - 2, elbow_y_l + 12), 5, dark_metal)
        # Right arm (holding sword)
        elbow_x_r = 48 - arm_swing
        elbow_y_r = shoulder_y + 10
        self.draw_limb(surface, (48, shoulder_y), (elbow_x_r, elbow_y_r), 5, metal)
        self.draw_limb(surface, (elbow_x_r, elbow_y_r), (elbow_x_r + 2, elbow_y_r + 12), 5, metal)
        
        # Shoulders
        pygame.draw.ellipse(surface, metal_light, (27, body_y - 2, 8, 6))
        pygame.draw.ellipse(surface, metal_light, (45, body_y - 2, 8, 6))
        
        # Helm/head
        head_y = body_y - 12
        pygame.draw.ellipse(surface, dark_metal, (33, head_y, 14, 16))
        pygame.draw.ellipse(surface, void_black, (35, head_y + 2, 10, 12))
        
        # Eyes
        pygame.draw.circle(surface, soul_glow, (37, head_y + 6), 2)
        pygame.draw.circle(surface, soul_glow, (43, head_y + 6), 2)
        
        # Sword
        sword_x = elbow_x_r + 4
        sword_y = elbow_y_r + 12
        pygame.draw.rect(surface, metal_light, (sword_x, sword_y, 3, 18))
        pygame.draw.rect(surface, dark_metal, (sword_x - 1, sword_y + 14, 5, 2))
        
        return surface
    
    def draw_frame_attack(self, frame):
        """Draw attack animation - sword swing"""
        surface = pygame.Surface((80, 100), pygame.SRCALPHA)
        
        # Attack progress
        progress = frame / 3.0
        sword_angle = -90 + (progress * 180)  # Swing from up to down
        arm_extend = int(progress * 10)
        
        # Colors
        dark_metal = (45, 45, 55)
        metal = (65, 65, 75)
        metal_light = (85, 85, 95)
        void_black = (10, 10, 15)
        soul_glow = (100, 100, 150)
        attack_glow = (180, 180, 220)
        
        # Body
        body_y = 40
        pygame.draw.ellipse(surface, dark_metal, (32, body_y, 16, 22))
        
        # Legs (stable)
        hip_y = body_y + 22
        self.draw_limb(surface, (36, hip_y), (36, hip_y + 12), 6, dark_metal)
        self.draw_limb(surface, (36, hip_y + 12), (36, hip_y + 26), 6, dark_metal)
        self.draw_limb(surface, (44, hip_y), (44, hip_y + 12), 6, metal)
        self.draw_limb(surface, (44, hip_y + 12), (44, hip_y + 26), 6, metal)
        
        # Left arm (back for balance)
        shoulder_y = body_y + 4
        self.draw_limb(surface, (32, shoulder_y), (20, shoulder_y + 8), 5, dark_metal)
        self.draw_limb(surface, (20, shoulder_y + 8), (16, shoulder_y + 18), 5, dark_metal)
        
        # Right arm (attacking, extended)
        attack_shoulder_x = 48 + arm_extend
        attack_elbow_x = attack_shoulder_x + 8
        attack_elbow_y = shoulder_y + 8
        self.draw_limb(surface, (48, shoulder_y), (attack_elbow_x, attack_elbow_y), 5, metal)
        self.draw_limb(surface, (attack_elbow_x, attack_elbow_y), (attack_elbow_x + 4, attack_elbow_y + 12), 5, metal)
        
        # Shoulders
        pygame.draw.ellipse(surface, metal_light, (27, body_y - 2, 8, 6))
        pygame.draw.ellipse(surface, metal_light, (45, body_y - 2, 8, 6))
        
        # Helm/head
        head_y = body_y - 12
        pygame.draw.ellipse(surface, dark_metal, (33, head_y, 14, 16))
        pygame.draw.ellipse(surface, void_black, (35, head_y + 2, 10, 12))
        
        # Eyes glowing during attack
        pygame.draw.circle(surface, attack_glow, (37, head_y + 6), 3)
        pygame.draw.circle(surface, attack_glow, (43, head_y + 6), 3)
        pygame.draw.circle(surface, (240, 240, 255), (37, head_y + 5), 1)
        pygame.draw.circle(surface, (240, 240, 255), (43, head_y + 5), 1)
        
        # Sword with motion trail
        sword_start_x = attack_elbow_x + 4
        sword_start_y = attack_elbow_y + 12
        sword_length = 24
        sword_end_x = sword_start_x + int(math.cos(math.radians(sword_angle)) * sword_length)
        sword_end_y = sword_start_y + int(math.sin(math.radians(sword_angle)) * sword_length)
        
        # Motion trail
        if frame > 0:
            trail_alpha = 100 - (frame * 30)
            trail_surface = pygame.Surface((80, 100), pygame.SRCALPHA)
            pygame.draw.line(trail_surface, (*metal_light, trail_alpha), (sword_start_x, sword_start_y), (sword_end_x, sword_end_y), 5)
            surface.blit(trail_surface, (0, 0))
        
        # Main sword
        pygame.draw.line(surface, metal_light, (sword_start_x, sword_start_y), (sword_end_x, sword_end_y), 4)
        pygame.draw.circle(surface, metal_light, (sword_start_x, sword_start_y), 3)
        pygame.draw.circle(surface, (180, 180, 200), (sword_end_x, sword_end_y), 2)
        
        return surface
    
    def update(self, player, platforms):
        """AI and physics"""
        self.animation_timer += 1
        
        # Update animation frame
        if self.animation_timer % 8 == 0:
            frames_in_state = len(self.animation_frames.get(self.animation_state, [self.image]))
            self.animation_frame = (self.animation_frame + 1) % max(frames_in_state, 1)
        
        if self.hitstun_frames > 0:
            self.hitstun_frames -= 1
            self.hit_flash_timer = (self.hit_flash_timer + 1) % 4
            self.apply_physics(platforms)
            return
        
        self.hit_flash_timer = 0
        
        # Calculate distance to player
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.sqrt(dx*dx + dy*dy)
        
        # State machine
        if distance < self.attack_range and self.attack_cooldown == 0:
            self.state = 'attack'
            self.animation_state = 'attack'
        elif distance < self.detection_range:
            self.state = 'chase'
            self.animation_state = 'chase'
        else:
            self.state = 'patrol'
            self.animation_state = 'patrol'
        
        # Behavior
        if self.state == 'patrol':
            # Patrol back and forth
            if self.rect.x < self.patrol_start_x - self.patrol_range:
                self.velocity_x = self.patrol_speed
                self.facing_right = True
            elif self.rect.x > self.patrol_start_x + self.patrol_range:
                self.velocity_x = -self.patrol_speed
                self.facing_right = False
            
            # Keep current direction
            if self.velocity_x == 0:
                self.velocity_x = self.patrol_speed if self.facing_right else -self.patrol_speed
        
        elif self.state == 'chase':
            # Chase player
            if dx > 10:
                self.velocity_x = self.chase_speed
                self.facing_right = True
            elif dx < -10:
                self.velocity_x = -self.chase_speed
                self.facing_right = False
            else:
                self.velocity_x = 0
        
        elif self.state == 'attack':
            self.velocity_x = 0
            if not self.is_attacking:
                self.start_attack()
        
        # Update attack
        if self.is_attacking:
            self.attack_frame += 1
            if self.attack_frame >= 15:  # Attack animation length
                self.is_attacking = False
                self.attack_frame = 0
                self.attack_cooldown = 45
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Apply physics
        self.apply_physics(platforms)
    
    def start_attack(self):
        """Start attack animation"""
        self.is_attacking = True
        self.attack_frame = 0
    
    def apply_physics(self, platforms):
        """Ground-based physics"""
        # Apply knockback
        if abs(self.knockback_x) > 0.1 or abs(self.knockback_y) > 0.1:
            self.rect.x += self.knockback_x
            self.rect.y += self.knockback_y
            self.knockback_x *= self.knockback_friction
            self.knockback_y *= 0.98
            
            if abs(self.knockback_x) < 0.2:
                self.knockback_x = 0
            if abs(self.knockback_y) < 0.2:
                self.knockback_y = 0
        
        # Gravity
        self.velocity_y += self.gravity
        self.velocity_y = min(self.velocity_y, 15)
        
        # Apply velocity
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        
        # Platform collision
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # Landing
                if self.velocity_y > 0 and self.rect.bottom > platform.rect.top:
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                # Ceiling
                elif self.velocity_y < 0 and self.rect.top < platform.rect.bottom:
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0
    
    def take_damage(self, damage):
        """Take damage"""
        self.current_health -= damage
        if self.current_health <= 0:
            self.die()
    
    def die(self):
        """Death"""
        if self.particle_group:
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
        """Apply knockback"""
        self.knockback_x = knockback_x
        self.knockback_y = knockback_y
    
    def apply_hitstun(self, frames):
        """Apply hitstun"""
        self.hitstun_frames = max(self.hitstun_frames, frames)
    
    def draw(self, surface, camera):
        """Draw warrior with animated frames"""
        screen_pos = camera.apply(self)
        
        # Get current animation frame
        frames = self.animation_frames.get(self.animation_state, self.animation_frames['patrol'])
        if len(frames) > 0:
            frame_index = self.animation_frame % len(frames)
            current_frame = frames[frame_index]
        else:
            current_frame = self.image
        
        # Flip based on direction
        if self.facing_right:
            image = current_frame
        else:
            image = pygame.transform.flip(current_frame, True, False)
        
        # Hit flash
        if self.hitstun_frames > 0 and self.hit_flash_timer < 2:
            flash_image = image.copy()
            flash_image.fill((255, 255, 255, 180), special_flags=pygame.BLEND_RGBA_ADD)
            image = flash_image
        
        surface.blit(image, screen_pos)
        self.draw_health_bar(surface, screen_pos)
    
    def draw_health_bar(self, surface, screen_pos):
        """Draw health bar"""
        if self.current_health >= self.max_health:
            return
        
        bar_width = 40
        bar_height = 4
        bar_x = screen_pos.x
        bar_y = screen_pos.y - 8
        
        pygame.draw.rect(surface, (40, 20, 20), (bar_x, bar_y, bar_width, bar_height))
        
        health_percent = self.current_health / self.max_health
        health_width = int(bar_width * health_percent)
        
        if health_percent > 0.6:
            health_color = (50, 200, 50)
        elif health_percent > 0.3:
            health_color = (220, 180, 50)
        else:
            health_color = (220, 50, 50)
        
        pygame.draw.rect(surface, health_color, (bar_x, bar_y, health_width, bar_height))
        pygame.draw.rect(surface, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 1)
