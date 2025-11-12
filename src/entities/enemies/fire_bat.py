"""
Fire Bat Enemy
Small flying suicide bomber that explodes on contact or when killed
"""

import pygame
import math
import random

class FireBat(pygame.sprite.Sprite):
    """Small kamikaze flying enemy that explodes"""
    
    def __init__(self, x, y):
        super().__init__()
        
        # Visual
        self.rect = pygame.Rect(x, y, 40, 40)
        
        # Stats
        self.max_health = 20  # One-hit kill
        self.health = self.max_health
        self.explosion_damage = 40
        self.explosion_radius = 100
        self.speed = 3.0
        
        # Physics
        self.velocity_x = 0
        self.velocity_y = 0
        
        # AI state
        self.time_alive = 0
        self.max_lifetime = 600  # 10 seconds before auto-explode
        self.activated = False
        self.exploding = False
        self.explosion_timer = 0
        
        # Visual effects
        self.glow_intensity = 100
        self.animation_timer = 0
        self.particle_spawn_timer = 0
        
        # Particles
        self.particle_group = None
        
        # XP/Gold rewards
        self.xp_reward = 10
        self.gold_reward = 5
        
        # Explosion tracking (for collision check)
        self.has_exploded = False
        self.explosion_rect = None
    
    def update(self, player, platforms=None):
        """Update fire bat AI"""
        self.animation_timer += 1
        self.time_alive += 1
        
        # Increase glow as time passes
        glow_progress = self.time_alive / self.max_lifetime
        self.glow_intensity = int(100 + 155 * glow_progress)
        
        # Auto-explode after max lifetime
        if self.time_alive >= self.max_lifetime:
            self.explode()
            return
        
        # If exploding, count down
        if self.exploding:
            self.explosion_timer += 1
            if self.explosion_timer >= 30:  # 0.5 second explosion duration
                self.kill()
            return
        
        # Fly toward player
        if hasattr(player, 'rect'):
            self.activated = True
            
            # Calculate direction to player
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Check if close enough to explode
            if distance < 30:
                self.explode()
                return
            
            # Move toward player
            if distance > 0:
                self.velocity_x = (dx / distance) * self.speed
                self.velocity_y = (dy / distance) * self.speed
        
        # Apply movement
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        
        # Spawn fire trail particles
        self.particle_spawn_timer += 1
        if self.particle_spawn_timer >= 3:
            self.particle_spawn_timer = 0
            if self.particle_group:
                from src.world import Particle
                # Fire trail
                particle = Particle(
                    self.rect.centerx + random.randint(-5, 5),
                    self.rect.centery + random.randint(-5, 5),
                    random.uniform(-1, 1),
                    random.uniform(1, 3),  # Drift upward
                    color=(255, random.randint(100, 200), 0),
                    lifetime=20
                )
                self.particle_group.add(particle)
    
    def explode(self):
        """Trigger explosion"""
        if self.has_exploded:
            return
        
        self.exploding = True
        self.has_exploded = True
        self.explosion_timer = 0
        
        # Create explosion hitbox for collision detection
        self.explosion_rect = pygame.Rect(
            self.rect.centerx - self.explosion_radius,
            self.rect.centery - self.explosion_radius,
            self.explosion_radius * 2,
            self.explosion_radius * 2
        )
        
        # Spawn explosion particles
        if self.particle_group:
            for _ in range(40):
                from src.world import Particle
                angle = random.random() * math.pi * 2
                speed = random.randint(2, 8)
                particle = Particle(
                    self.rect.centerx,
                    self.rect.centery,
                    math.cos(angle) * speed,
                    math.sin(angle) * speed,
                    color=(255, random.randint(150, 255), random.randint(0, 100)),
                    lifetime=30
                )
                self.particle_group.add(particle)
    
    def take_damage(self, damage, attacker_pos=None):
        """Take damage - always causes explosion"""
        self.health -= damage
        
        # Always explode when killed
        if self.health <= 0 or not self.exploding:
            self.explode()
        
        return damage
    
    def get_explosion_hitbox(self):
        """Get explosion hitbox for damage check"""
        if self.exploding and self.explosion_timer < 5:  # Only deal damage in first few frames
            return self.explosion_rect
        return None
    
    def get_explosion_damage(self):
        """Get explosion damage"""
        return self.explosion_damage
    
    def draw(self, screen, camera):
        """Draw the fire bat with sprite"""
        screen_rect = camera.apply(self)
        
        if self.exploding:
            # Draw expanding explosion
            expansion = self.explosion_timer / 30.0
            explosion_size = int(self.explosion_radius * expansion)
            
            # Outer ring
            pygame.draw.circle(screen, (255, 100, 0), screen_rect.center, explosion_size, 3)
            # Inner glow
            inner_size = int(explosion_size * 0.7)
            if inner_size > 0:
                pygame.draw.circle(screen, (255, 200, 0), screen_rect.center, inner_size, 2)
        else:
            # Get sprite if sprite manager is available
            if hasattr(self, 'sprite_manager') and self.sprite_manager:
                # Get frame based on animation timer
                frame = (pygame.time.get_ticks() // 100) % 4
                
                # Get sprite
                sprite = self.sprite_manager.get_sprite('fire_bat', 'idle', frame)
                
                # Center sprite on rect
                sprite_rect = sprite.get_rect(center=screen_rect.center)
                screen.blit(sprite, sprite_rect)
            else:
                # Fallback to geometric rendering
                # Fire bat body - small bat with flames
                # Body
                bat_color = (self.glow_intensity, 0, 0)
                pygame.draw.ellipse(screen, bat_color, screen_rect)
                
                # Glowing aura
                aura_size = 5 + int(5 * math.sin(self.animation_timer / 5))
                aura_rect = screen_rect.inflate(aura_size, aura_size)
                aura_color = (255, 100, 0)
                pygame.draw.ellipse(screen, aura_color, aura_rect, 2)
                
                # Eyes (glowing)
                eye_y = screen_rect.centery - 5
                pygame.draw.circle(screen, (255, 255, 0), (screen_rect.centerx - 8, eye_y), 3)
                pygame.draw.circle(screen, (255, 255, 0), (screen_rect.centerx + 8, eye_y), 3)
                
                # Wings (simple lines)
                wing_offset = int(8 * math.sin(self.animation_timer / 3))
                # Left wing
                pygame.draw.line(screen, (200, 50, 0),
                               (screen_rect.left, screen_rect.centery),
                               (screen_rect.left - 15, screen_rect.centery + wing_offset), 2)
                # Right wing
                pygame.draw.line(screen, (200, 50, 0),
                               (screen_rect.right, screen_rect.centery),
                               (screen_rect.right + 15, screen_rect.centery + wing_offset), 2)
            
            # Fuse indicator (how close to auto-explode)
            fuse_progress = self.time_alive / self.max_lifetime
            if fuse_progress > 0.5:
                # Warning indicator
                warning_text = "!"
                font = pygame.font.Font(None, 24)
                text_surf = font.render(warning_text, True, (255, 255, 0))
                text_rect = text_surf.get_rect(center=(screen_rect.centerx, screen_rect.top - 10))
                screen.blit(text_surf, text_rect)
