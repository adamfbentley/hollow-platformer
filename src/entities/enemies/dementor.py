"""
Dementor Enemy
Flying ethereal enemy inspired by Harry Potter's Azkaban guards
Floats, hunts player, features detailed sprite rendering
"""

import pygame
import math
import random
from src.world.particles import Particle


class DementorEnemy(pygame.sprite.Sprite):
    """
    Flying Dementor-style enemy (Azkaban guard inspired)
    Floats, hunts player, ethereal and menacing
    WITH ENHANCED PHYSICS AND HITSTUN
    """
    def __init__(self, x, y, patrol_range=300):
        super().__init__()
        self.base_x = x
        self.base_y = y
        self.patrol_range = patrol_range
        self.create_dementor()
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        
        # AI state
        self.state = 'patrol'  # patrol, chase, attack
        self.velocity_x = 0
        self.velocity_y = 0
        self.detection_range = 400
        self.chase_speed = 2.5
        self.patrol_speed = 1.0
        
        # Animation
        self.float_offset = 0
        self.animation_timer = 0
        self.animation_frame = 0
        self.animation_state = 'float'  # float, chase, attack
        self.facing_right = False
        self.animation_frames = {}
        self.create_animation_frames()
        
        # Attack
        self.attack_cooldown = 0
        self.attack_range = 60
        
        # HP System
        self.max_health = 100
        self.current_health = self.max_health
        self.level = 1
        self.xp_reward = 25  # XP given to player on death
        
        # Enhanced physics
        self.knockback_x = 0
        self.knockback_y = 0
        self.knockback_friction = 0.85
        self.knockback_gravity = 0.4
        self.is_grounded = False
        
        # Hitstun system
        self.hitstun_frames = 0
        self.hit_flash_timer = 0
        
        # Visual effects
        self.soul_color = (120, 120, 180)  # For particle effects
        self.particle_group = None  # Set externally
        
    def create_dementor(self):
        """Draw highly detailed ethereal Dementor with flowing animation"""
        # Create at original size first
        temp_surface = pygame.Surface((70, 90), pygame.SRCALPHA)
        
        # Enhanced dark palette
        void_black = (5, 5, 8)
        shadow_deep = (12, 12, 18)
        shadow_dark = (18, 18, 28)
        shadow_mid = (28, 28, 42)
        cloak_dark = (22, 22, 35)
        cloak_mid = (35, 35, 52)
        cloak_light = (48, 48, 65)
        soul_dark = (80, 80, 130)
        soul_glow = (120, 120, 180)
        soul_bright = (160, 160, 220)
        wisp_glow = (60, 60, 100)
        
        # Outer ethereal aura (large, very transparent)
        for radius in range(35, 25, -3):
            alpha = int(15 * (35 - radius) / 10)
            pygame.draw.circle(temp_surface, (*shadow_mid, alpha), (35, 25), radius)
        
        # Main billowing cloak with more detail
        cloak_outer = [
            (35, 12),   # Top
            (25, 16),   # Upper left shoulder
            (18, 22),   # Left shoulder
            (12, 32),   # Upper left side
            (8, 45),    # Mid left
            (5, 60),    # Lower left outer
            (10, 68),   # Left tatter start
            (8, 78),    # Left tatter tip
            (15, 75),   # Left tatter inner
            (20, 82),   # Left inner tatter
            (25, 78),   # Left center
            (30, 86),   # Center left tatter
            (35, 82),   # Center tatter
            (40, 86),   # Center right tatter
            (45, 78),   # Right center
            (50, 82),   # Right inner tatter
            (55, 75),   # Right tatter inner
            (62, 78),   # Right tatter tip
            (60, 68),   # Right tatter start
            (65, 60),   # Lower right outer
            (62, 45),   # Mid right
            (58, 32),   # Upper right side
            (52, 22),   # Right shoulder
            (45, 16),   # Upper right shoulder
        ]
        pygame.draw.polygon(temp_surface, cloak_dark, cloak_outer)
        
        # Multiple cloak layers for depth
        cloak_mid_layer = [
            (35, 14), (28, 20), (22, 30), (18, 45), (20, 60), 
            (25, 72), (35, 76), (45, 72), (50, 60), (52, 45), (48, 30), (42, 20)
        ]
        pygame.draw.polygon(temp_surface, cloak_mid, cloak_mid_layer)
        
        # Inner void (deepest darkness)
        inner_void = [
            (35, 18), (30, 24), (28, 35), (26, 50), (30, 65), (35, 70), (40, 65), (44, 50), (42, 35), (40, 24)
        ]
        pygame.draw.polygon(temp_surface, shadow_deep, inner_void)
        
        # Flowing cloak folds (left side)
        fold_left = [(22, 28), (18, 38), (16, 52), (20, 66)]
        pygame.draw.lines(temp_surface, cloak_light, False, fold_left, 2)
        # Right side folds
        fold_right = [(48, 28), (52, 38), (54, 52), (50, 66)]
        pygame.draw.lines(temp_surface, cloak_light, False, fold_right, 2)
        
        # Tattered edges with detail
        tatter_positions = [(10, 70), (18, 78), (28, 84), (38, 84), (48, 78), (58, 70)]
        for tx, ty in tatter_positions:
            # Wispy tatter strands
            pygame.draw.line(temp_surface, shadow_mid, (tx, ty), (tx - 2, ty + 6), 2)
            pygame.draw.line(temp_surface, shadow_dark, (tx + 2, ty), (tx + 1, ty + 8), 1)
            # Fray effect
            pygame.draw.line(temp_surface, cloak_dark, (tx, ty), (tx + 1, ty + 4), 1)
        
        # Hood structure with depth
        pygame.draw.ellipse(temp_surface, cloak_mid, (25, 10, 20, 22))
        pygame.draw.ellipse(temp_surface, cloak_dark, (27, 12, 16, 18))
        pygame.draw.ellipse(temp_surface, shadow_dark, (29, 14, 12, 14))
        
        # Face void (empty, terrifying darkness)
        pygame.draw.ellipse(temp_surface, void_black, (30, 18, 10, 14))
        # Slight detail in void
        pygame.draw.ellipse(temp_surface, (3, 3, 5), (32, 20, 6, 10))
        
        # Glowing eyes/soul energy with layers
        # Left eye
        pygame.draw.circle(temp_surface, (*wisp_glow, 100), (32, 24), 4)
        pygame.draw.circle(temp_surface, (*soul_glow, 140), (32, 24), 3)
        pygame.draw.circle(temp_surface, soul_bright, (32, 24), 2)
        pygame.draw.circle(temp_surface, (200, 200, 240), (32, 23), 1)
        # Right eye
        pygame.draw.circle(temp_surface, (*wisp_glow, 100), (38, 24), 4)
        pygame.draw.circle(temp_surface, (*soul_glow, 140), (38, 24), 3)
        pygame.draw.circle(temp_surface, soul_bright, (38, 24), 2)
        pygame.draw.circle(temp_surface, (200, 200, 240), (38, 23), 1)
        
        # Ethereal wisps floating around body
        wisp_positions = [
            (15, 25, 5), (55, 28, 4), (10, 40, 4), (60, 42, 5),
            (12, 58, 3), (58, 60, 4), (20, 48, 3), (50, 50, 3)
        ]
        for wx, wy, wr in wisp_positions:
            pygame.draw.circle(temp_surface, (*shadow_mid, 80), (wx, wy), wr)
            pygame.draw.circle(temp_surface, (*wisp_glow, 120), (wx, wy), wr - 1)
            pygame.draw.circle(temp_surface, (*soul_glow, 60), (wx, wy), wr + 2)
        
        # Soul tendrils emanating from body
        tendril_points = [
            [(25, 40), (20, 38), (16, 42), (14, 48)],
            [(45, 42), (50, 40), (54, 44), (56, 50)],
            [(30, 55), (28, 60), (26, 65), (25, 72)],
            [(40, 57), (42, 62), (44, 67), (45, 74)]
        ]
        for tendril in tendril_points:
            pygame.draw.lines(temp_surface, (*soul_dark, 100), False, tendril, 2)
            pygame.draw.lines(temp_surface, (*wisp_glow, 80), False, tendril, 1)
        
        # Scale up 2x for better resolution
        self.image = pygame.transform.scale2x(temp_surface)
        
        # Update rect to match new size
        if hasattr(self, 'rect'):
            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center
    
    def create_animation_frames(self):
        """Create animated frames for floating ethereal Dementor"""
        self.animation_frames = {
            'float': [self.draw_frame_float(i) for i in range(6)],
            'chase': [self.draw_frame_chase(i) for i in range(4)],
            'attack': [self.draw_frame_attack(i) for i in range(3)]
        }
    
    def draw_frame_float(self, frame):
        """Draw floating idle animation - cloak billowing, wisps swirling"""
        surface = pygame.Surface((140, 180), pygame.SRCALPHA)
        
        # Float cycle (0-5 frames)
        progress = frame / 6.0
        float_bob = math.sin(progress * math.pi * 2) * 3
        wisp_rotation = progress * math.pi * 2
        
        # Dark palette
        void_black = (5, 5, 8)
        shadow_deep = (12, 12, 18)
        shadow_dark = (18, 18, 28)
        cloak_dark = (22, 22, 35)
        cloak_mid = (35, 35, 52)
        soul_glow = (120, 120, 180)
        wisp_glow = (60, 60, 100)
        
        # Ethereal aura (pulsing)
        aura_size = 30 + int(math.sin(progress * math.pi * 2) * 5)
        for radius in range(aura_size, aura_size - 10, -2):
            alpha = int(20 * (aura_size - radius) / 10)
            pygame.draw.circle(surface, (*shadow_dark, alpha), (70, 50 + int(float_bob)), radius)
        
        # Main cloak body (billowing)
        cloak_width = 50 + int(math.sin(progress * math.pi * 2) * 8)
        pygame.draw.ellipse(surface, cloak_dark, (70 - cloak_width//2, 40 + int(float_bob), cloak_width, 100))
        
        # Tattered edges
        for i in range(6):
            x_offset = -20 + i * 8
            tatter_y = 130 + int(float_bob) + int(math.sin(progress * math.pi * 2 + i) * 5)
            tatter_points = [
                (70 + x_offset, tatter_y),
                (70 + x_offset - 3, tatter_y + 15),
                (70 + x_offset + 3, tatter_y + 15)
            ]
            pygame.draw.polygon(surface, cloak_mid, tatter_points)
        
        # Hood/head
        pygame.draw.ellipse(surface, shadow_deep, (58, 28 + int(float_bob), 24, 28))
        
        # Face void
        pygame.draw.ellipse(surface, void_black, (60, 36 + int(float_bob), 20, 20))
        
        # Glowing eyes
        eye_glow_intensity = 150 + int(math.sin(progress * math.pi * 4) * 50)
        pygame.draw.circle(surface, (*soul_glow, eye_glow_intensity), (66, 42 + int(float_bob)), 4)
        pygame.draw.circle(surface, (*soul_glow, eye_glow_intensity), (74, 42 + int(float_bob)), 4)
        pygame.draw.circle(surface, (200, 200, 240), (66, 41 + int(float_bob)), 2)
        pygame.draw.circle(surface, (200, 200, 240), (74, 41 + int(float_bob)), 2)
        
        # Swirling wisps
        for i in range(8):
            angle = wisp_rotation + (i * math.pi / 4)
            wisp_x = 70 + int(math.cos(angle) * 40)
            wisp_y = 80 + int(float_bob) + int(math.sin(angle) * 40)
            wisp_size = 3 + int(math.sin(progress * math.pi * 2 + i) * 2)
            pygame.draw.circle(surface, (*wisp_glow, 120), (wisp_x, wisp_y), wisp_size)
            pygame.draw.circle(surface, (*soul_glow, 60), (wisp_x, wisp_y), wisp_size + 2)
        
        return surface
    
    def draw_frame_chase(self, frame):
        """Draw chasing animation - leaning forward, cloak streaming behind"""
        surface = pygame.Surface((140, 180), pygame.SRCALPHA)
        
        # Chase cycle (0-3 frames) - faster animation
        progress = frame / 4.0
        lean_forward = 8
        
        # Colors
        void_black = (5, 5, 8)
        shadow_deep = (12, 12, 18)
        cloak_dark = (22, 22, 35)
        cloak_mid = (35, 35, 52)
        soul_glow = (120, 120, 180)
        wisp_glow = (60, 60, 100)
        
        # Cloak streaming behind (elongated)
        cloak_points = [
            (70 - lean_forward, 40),  # Front top
            (70 + 20, 50),  # Trailing top
            (70 + 35, 110),  # Trailing bottom
            (70 + 10, 130),  # Lower trail
            (70 - lean_forward - 10, 120),  # Front bottom
        ]
        pygame.draw.polygon(surface, cloak_dark, cloak_points)
        # Inner shadow
        inner_points = [
            (70 - lean_forward + 5, 50),
            (70 + 15, 60),
            (70 + 25, 100),
            (70, 115)
        ]
        pygame.draw.polygon(surface, cloak_mid, inner_points)
        
        # Head leaning forward
        pygame.draw.ellipse(surface, shadow_deep, (52, 30, 24, 26))
        
        # Face void
        pygame.draw.ellipse(surface, void_black, (54, 36, 20, 18))
        
        # Eyes - intense glow when chasing
        pygame.draw.circle(surface, (180, 180, 240), (60, 42), 5)
        pygame.draw.circle(surface, soul_glow, (60, 42), 3)
        pygame.draw.circle(surface, (180, 180, 240), (68, 42), 5)
        pygame.draw.circle(surface, soul_glow, (68, 42), 3)
        
        # Motion trail wisps
        for i in range(4):
            trail_x = 70 + 15 + i * 8
            trail_y = 60 + i * 15 + int(math.sin(progress * math.pi * 2 + i) * 5)
            pygame.draw.circle(surface, (*wisp_glow, 100), (trail_x, trail_y), 4)
        
        return surface
    
    def draw_frame_attack(self, frame):
        """Draw attack animation - surging forward, cloak expanding"""
        surface = pygame.Surface((140, 180), pygame.SRCALPHA)
        
        # Attack cycle (0-2 frames) - quick burst
        progress = frame / 3.0
        surge = int(progress * 15)
        
        # Colors
        void_black = (5, 5, 8)
        shadow_deep = (12, 12, 18)
        cloak_dark = (22, 22, 35)
        soul_glow = (120, 120, 180)
        attack_glow = (160, 160, 220)
        
        # Expanding cloak (menacing)
        cloak_expand = 60 + surge
        pygame.draw.ellipse(surface, cloak_dark, (70 - cloak_expand//2, 30, cloak_expand, 110))
        
        # Dark energy radiating
        energy_rings = 3
        for ring in range(energy_rings):
            ring_radius = 30 + surge + (ring * 15)
            alpha = 80 - (ring * 20) - int(progress * 40)
            pygame.draw.circle(surface, (*shadow_deep, max(alpha, 0)), (70, 80), ring_radius, 3)
        
        # Head
        pygame.draw.ellipse(surface, shadow_deep, (58, 25, 24, 28))
        
        # Face void - wider, more threatening
        pygame.draw.ellipse(surface, void_black, (58, 32, 24, 22))
        
        # Eyes - blazing bright during attack
        pygame.draw.circle(surface, attack_glow, (64, 40), 6)
        pygame.draw.circle(surface, soul_glow, (64, 40), 4)
        pygame.draw.circle(surface, (240, 240, 255), (64, 39), 2)
        pygame.draw.circle(surface, attack_glow, (76, 40), 6)
        pygame.draw.circle(surface, soul_glow, (76, 40), 4)
        pygame.draw.circle(surface, (240, 240, 255), (76, 39), 2)
        
        # Grasping tendrils
        for i in range(4):
            angle = (i * math.pi / 2) + (progress * math.pi / 4)
            tendril_reach = 40 + surge
            end_x = 70 + int(math.cos(angle) * tendril_reach)
            end_y = 80 + int(math.sin(angle) * tendril_reach)
            pygame.draw.line(surface, (*soul_glow, 150), (70, 80), (end_x, end_y), 3)
            pygame.draw.circle(surface, (*soul_glow, 180), (end_x, end_y), 5)
        
        return surface
        
    def update(self, player, platforms):
        """AI behavior and movement with enhanced physics"""
        self.float_offset += 0.08
        self.animation_timer += 1
        
        # Update animation frame
        if self.animation_timer % 6 == 0:
            frames_in_state = len(self.animation_frames.get(self.animation_state, [self.image]))
            self.animation_frame = (self.animation_frame + 1) % max(frames_in_state, 1)
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Update hitstun
        if self.hitstun_frames > 0:
            self.hitstun_frames -= 1
            self.hit_flash_timer = (self.hit_flash_timer + 1) % 4
            
            # During hitstun, only apply physics, no AI
            self.apply_physics(platforms)
            return
        
        # Reset hit flash
        self.hit_flash_timer = 0
        
        # Calculate distance to player
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = (dx**2 + dy**2)**0.5
        
        # State machine
        if distance < self.attack_range and self.attack_cooldown == 0:
            self.state = 'attack'
            self.animation_state = 'attack'
        elif distance < self.detection_range:
            self.state = 'chase'
            self.animation_state = 'chase'
        else:
            self.state = 'patrol'
            self.animation_state = 'float'
        
        # Behavior based on state
        if self.state == 'patrol':
            # Float back and forth around spawn point
            patrol_offset = pygame.math.Vector2(1, 0).rotate(self.float_offset * 30).x
            target_x = self.base_x + patrol_offset * self.patrol_range
            
            if abs(self.rect.centerx - target_x) > 5:
                self.velocity_x = self.patrol_speed if target_x > self.rect.centerx else -self.patrol_speed
            else:
                self.velocity_x *= 0.9
            
            # Gentle floating up and down
            self.velocity_y = pygame.math.Vector2(0, 1).rotate(self.float_offset * 40).y * 0.5
            
        elif self.state == 'chase':
            # Hunt the player
            if distance > 0:
                self.velocity_x = (dx / distance) * self.chase_speed
                self.velocity_y = (dy / distance) * self.chase_speed
            
        elif self.state == 'attack':
            # Lunge at player
            if distance > 0:
                self.velocity_x = (dx / distance) * self.chase_speed * 1.5
                self.velocity_y = (dy / distance) * self.chase_speed * 1.5
            self.attack_cooldown = 60  # 1 second cooldown
        
        # Apply movement and physics
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        
        # Apply physics (knockback, gravity)
        self.apply_physics(platforms)
        
        # Floating animation offset
        float_amplitude = 3
        self.rect.y += pygame.math.Vector2(0, 1).rotate(self.float_offset * 20).y * float_amplitude
        
        # Update facing direction
        if self.velocity_x < -0.1:
            self.facing_right = False
        elif self.velocity_x > 0.1:
            self.facing_right = True
        
        # Damping (ghostly drift)
        self.velocity_x *= 0.95
        self.velocity_y *= 0.95
        
        # Keep within reasonable bounds of spawn area (don't drift too far)
        if abs(self.rect.centerx - self.base_x) > self.patrol_range * 2:
            self.rect.centerx = self.base_x + (self.patrol_range * 2 if self.rect.centerx > self.base_x else -self.patrol_range * 2)
        if abs(self.rect.centery - self.base_y) > self.patrol_range * 1.5:
            self.rect.centery = self.base_y + (self.patrol_range * 1.5 if self.rect.centery > self.base_y else -self.patrol_range * 1.5)
    
    def apply_physics(self, platforms):
        """Apply advanced physics: knockback, gravity, friction"""
        # Apply knockback velocity
        if abs(self.knockback_x) > 0.1 or abs(self.knockback_y) > 0.1:
            self.rect.x += self.knockback_x
            self.rect.y += self.knockback_y
            
            # Apply gravity to knockback
            self.knockback_y += self.knockback_gravity
            
            # Apply air resistance/friction
            self.knockback_x *= self.knockback_friction
            self.knockback_y *= 0.98  # Less friction on vertical
            
            # Stop knockback when velocity is very small
            if abs(self.knockback_x) < 0.2:
                self.knockback_x = 0
            if abs(self.knockback_y) < 0.2 and self.knockback_y > 0:
                self.knockback_y = 0
        
        # Check ground collision (for enemies that land)
        self.is_grounded = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # Landing on top
                if self.knockback_y > 0 and self.rect.bottom > platform.rect.top:
                    self.rect.bottom = platform.rect.top
                    self.knockback_y = 0
                    self.is_grounded = True
                    
                    # Spawn dust particles on hard landing
                    if hasattr(self, 'particle_group') and self.particle_group and abs(self.knockback_x) > 3:
                        self.spawn_landing_dust()
                
                # Wall bounce
                elif abs(self.knockback_x) > 2:
                    if self.knockback_x > 0 and self.rect.right > platform.rect.left:
                        self.rect.right = platform.rect.left
                        self.knockback_x *= -0.4  # Bounce with energy loss
                    elif self.knockback_x < 0 and self.rect.left < platform.rect.right:
                        self.rect.left = platform.rect.right
                        self.knockback_x *= -0.4
    
    def spawn_landing_dust(self):
        """Spawn dust particles when landing"""
        if not self.particle_group:
            return
        
        for i in range(8):
            angle = random.uniform(-120, -60)  # Upward spray
            speed = random.uniform(2, 5)
            vel_x = math.cos(math.radians(angle)) * speed
            vel_y = math.sin(math.radians(angle)) * speed
            
            particle = Particle(
                self.rect.centerx + random.randint(-10, 10),
                self.rect.bottom - 2,
                vel_x, vel_y,
                (100, 90, 80),
                lifetime=20,
                size=2,
                particle_type='dust'
            )
            self.particle_group.add(particle)
    
    def draw(self, surface, camera):
        """Custom draw with animated frames and ethereal effects"""
        screen_pos = camera.apply(self)
        
        # Get current animation frame
        frames = self.animation_frames.get(self.animation_state, self.animation_frames['float'])
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
        
        # Hit flash effect during hitstun
        if self.hitstun_frames > 0 and self.hit_flash_timer < 2:
            # Create white flash overlay
            flash_image = image.copy()
            flash_image.fill((255, 255, 255, 180), special_flags=pygame.BLEND_RGBA_ADD)
            image = flash_image
        
        # Draw shadow/aura underneath
        aura_surf = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.circle(aura_surf, (10, 10, 20, 40), (50, 50), 40)
        pygame.draw.circle(aura_surf, (15, 15, 30, 60), (50, 50), 30)
        surface.blit(aura_surf, (screen_pos.x - 25, screen_pos.y - 15))
        
        # Draw main sprite
        surface.blit(image, screen_pos)
        
        # Draw health bar above enemy
        self.draw_health_bar(surface, screen_pos)
        
        # Attack indicator (red glow when attacking)
        if self.state == 'attack' and self.attack_cooldown > 50:
            attack_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
            pygame.draw.circle(attack_surf, (150, 0, 0, 80), (40, 40), 35)
            surface.blit(attack_surf, (screen_pos.x - 15, screen_pos.y - 5))
    
    def draw_health_bar(self, surface, screen_pos):
        """Draw health bar above enemy"""
        if self.current_health >= self.max_health:
            return  # Don't show bar at full health
        
        bar_width = 60
        bar_height = 6
        bar_x = screen_pos.x + (self.rect.width - bar_width) // 2
        bar_y = screen_pos.y - 12
        
        # Background (dark)
        pygame.draw.rect(surface, (40, 20, 20), (bar_x, bar_y, bar_width, bar_height))
        
        # Health (red to green gradient based on health%)
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
    
    def take_damage(self, damage):
        """Take damage from player attack"""
        # Reduce health
        self.current_health -= damage
        
        # Check if dead
        if self.current_health <= 0:
            self.die()
    
    def die(self):
        """Handle enemy death"""
        # Spawn death particles
        if self.particle_group:
            for i in range(20):
                angle = (i / 20) * 360
                velocity = pygame.math.Vector2(5, 0).rotate(angle)
                particle = Particle(
                    self.rect.centerx,
                    self.rect.centery,
                    velocity.x + random.uniform(-1, 1),
                    velocity.y + random.uniform(-1, 1),
                    self.soul_color,
                    lifetime=40,
                    size=4,
                    particle_type='spark'
                )
                self.particle_group.add(particle)
        
        self.kill()
    
    def apply_knockback(self, knockback_x, knockback_y):
        """Apply knockback force with enhanced physics"""
        self.knockback_x = knockback_x
        self.knockback_y = knockback_y
    
    def apply_hitstun(self, frames):
        """Apply hitstun (freeze enemy AI for frames)"""
        self.hitstun_frames = max(self.hitstun_frames, frames)
