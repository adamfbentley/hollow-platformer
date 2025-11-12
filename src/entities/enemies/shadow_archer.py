"""
Shadow Archer Enemy
Ranged enemy that keeps distance and shoots arrows
"""

import pygame
import math
import random
from src.world.particles import Particle
from src.entities.enemies.projectile import Projectile


class ShadowArcher(pygame.sprite.Sprite):
    """Ranged enemy that keeps distance and shoots arrows"""
    
    def __init__(self, x, y, patrol_range=300):
        super().__init__()
        self.image = self.create_archer_sprite()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Movement
        self.velocity_x = 0
        self.velocity_y = 0
        self.patrol_start_x = x
        self.patrol_range = patrol_range
        self.patrol_speed = 1.0
        self.retreat_speed = 2.5
        
        # Combat
        self.max_health = 60
        self.current_health = 60
        self.level = 1
        self.xp_reward = 30
        self.attack_damage = 15
        self.attack_range = 400  # Long range
        self.min_distance = 200  # Keeps this distance from player
        self.attack_cooldown = 0
        self.attack_cooldown_max = 90  # 1.5 seconds
        self.is_aiming = False
        self.aim_time = 0
        self.aim_time_max = 30  # Half second to aim
        
        # State
        self.state = 'patrol'  # patrol, retreat, aim, shoot
        self.facing_right = True
        
        # Physics
        self.gravity = 0.8
        self.on_ground = False
        self.knockback_x = 0
        self.knockback_y = 0
        self.knockback_friction = 0.85
        
        # Hitstun
        self.hitstun_frames = 0
        self.hit_flash_timer = 0
        
        # Visuals
        self.soul_color = (100, 80, 150)
        self.particle_group = None
        self.projectile_group = None
    
    def create_archer_sprite(self):
        """Create archer sprite - 2x scale"""
        temp_surface = pygame.Surface((35, 45), pygame.SRCALPHA)
        
        # Colors
        cloak = (40, 30, 50)
        hood = (30, 20, 40)
        bow = (60, 45, 30)
        soul_glow = (120, 90, 180)
        
        # Legs
        pygame.draw.rect(temp_surface, cloak, (12, 30, 6, 15))
        pygame.draw.rect(temp_surface, cloak, (17, 30, 6, 15))
        
        # Body (cloak)
        pygame.draw.ellipse(temp_surface, cloak, (10, 18, 15, 20))
        
        # Hood
        pygame.draw.ellipse(temp_surface, hood, (8, 8, 19, 18))
        
        # Face void
        pygame.draw.ellipse(temp_surface, (0, 0, 0), (12, 12, 11, 10))
        
        # Glowing eyes
        pygame.draw.circle(temp_surface, soul_glow, (15, 16), 2)
        pygame.draw.circle(temp_surface, soul_glow, (20, 16), 2)
        
        # Bow (held at side)
        pygame.draw.arc(temp_surface, bow, (25, 15, 8, 18), 0, math.pi, 2)
        
        # Scale up 2x for better resolution
        return pygame.transform.scale2x(temp_surface)
    
    def update(self, player, platforms, projectile_group):
        """Update archer AI"""
        self.projectile_group = projectile_group
        
        # Update timers
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Hitstun
        if self.hitstun_frames > 0:
            self.hitstun_frames -= 1
            self.apply_physics(platforms)
            return
        
        # Get distance to player
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        
        # State machine
        if distance < self.min_distance:
            # Too close - retreat
            self.state = 'retreat'
            self.is_aiming = False
            self.aim_time = 0
            
            # Move away from player
            if dx > 0:
                self.velocity_x = -self.retreat_speed
                self.facing_right = False
            else:
                self.velocity_x = self.retreat_speed
                self.facing_right = True
                
        elif distance <= self.attack_range and self.attack_cooldown == 0:
            # In range - aim and shoot
            if not self.is_aiming:
                self.state = 'aim'
                self.is_aiming = True
                self.aim_time = 0
                self.velocity_x = 0
            
            # Face player
            self.facing_right = dx > 0
            
            # Aiming
            self.aim_time += 1
            if self.aim_time >= self.aim_time_max:
                # Fire!
                self.shoot_arrow(player)
                self.is_aiming = False
                self.aim_time = 0
                self.attack_cooldown = self.attack_cooldown_max
                self.state = 'patrol'
        else:
            # Patrol
            self.state = 'patrol'
            self.is_aiming = False
            self.aim_time = 0
            
            # Patrol movement
            if self.rect.x < self.patrol_start_x - self.patrol_range:
                self.velocity_x = self.patrol_speed
                self.facing_right = True
            elif self.rect.x > self.patrol_start_x + self.patrol_range:
                self.velocity_x = -self.patrol_speed
                self.facing_right = False
            elif self.velocity_x == 0:
                self.velocity_x = self.patrol_speed if random.random() > 0.5 else -self.patrol_speed
        
        self.apply_physics(platforms)
    
    def shoot_arrow(self, player):
        """Fire an arrow at the player"""
        if not self.projectile_group:
            return
        
        # Spawn arrow from archer position
        arrow_x = self.rect.centerx + (10 if self.facing_right else -10)
        arrow_y = self.rect.centery
        
        # Aim slightly ahead of player if they're moving
        target_x = player.rect.centerx + player.velocity_x * 10
        target_y = player.rect.centery
        
        projectile = Projectile(
            arrow_x, arrow_y,
            target_x, target_y,
            damage=self.attack_damage,
            speed=8,
            projectile_type='arrow'
        )
        self.projectile_group.add(projectile)
    
    def apply_physics(self, platforms):
        """Apply physics"""
        # Apply knockback with friction
        self.velocity_x += self.knockback_x
        self.velocity_y += self.knockback_y
        self.knockback_x *= self.knockback_friction
        self.knockback_y *= self.knockback_friction
        
        if abs(self.knockback_x) < 0.1:
            self.knockback_x = 0
        if abs(self.knockback_y) < 0.1:
            self.knockback_y = 0
        
        # Apply gravity
        self.velocity_y += self.gravity
        
        # Update position
        self.rect.x += int(self.velocity_x)
        self.rect.y += int(self.velocity_y)
        
        # Platform collision
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # Landing on top
                if self.velocity_y > 0 and self.rect.bottom > platform.rect.top:
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                # Hit ceiling
                elif self.velocity_y < 0 and self.rect.top < platform.rect.bottom:
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0
    
    def take_damage(self, damage):
        """Take damage"""
        self.current_health -= damage
        self.hit_flash_timer = 4
        
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
        """Draw archer"""
        screen_pos = camera.apply(self)
        
        # Flip based on direction
        if self.facing_right:
            image = self.image
        else:
            image = pygame.transform.flip(self.image, True, False)
        
        # Hit flash
        if self.hitstun_frames > 0 and self.hit_flash_timer < 2:
            flash_image = image.copy()
            flash_image.fill((255, 255, 255, 180), special_flags=pygame.BLEND_RGBA_ADD)
            image = flash_image
        
        surface.blit(image, screen_pos)
        
        # Draw aim indicator when aiming
        if self.is_aiming and self.aim_time > 0:
            aim_progress = self.aim_time / self.aim_time_max
            indicator_size = int(8 * aim_progress)
            indicator_color = (200, 50, 50) if aim_progress > 0.8 else (200, 200, 50)
            pygame.draw.circle(surface, indicator_color, 
                             (screen_pos.x + 17, screen_pos.y + 10), 
                             indicator_size, 2)
        
        self.draw_health_bar(surface, screen_pos)
    
    def draw_health_bar(self, surface, screen_pos):
        """Draw health bar"""
        if self.current_health >= self.max_health:
            return
        
        bar_width = 35
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
