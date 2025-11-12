"""
Berserker Enemy
Glass cannon that enters rage mode at 50% HP - faster, stronger, more vulnerable
"""

import pygame
import math
import random

class Berserker(pygame.sprite.Sprite):
    """Aggressive melee attacker with rage mode transformation"""
    
    def __init__(self, x, y, patrol_range=200):
        super().__init__()
        
        # Visual
        self.rect = pygame.Rect(x, y, 60, 85)
        self.patrol_center = x
        self.patrol_range = patrol_range
        
        # Stats
        self.max_health = 150
        self.health = self.max_health
        self.base_damage = 30
        self.base_speed = 3.0
        self.current_damage = self.base_damage
        self.current_speed = self.base_speed
        
        # Rage mode
        self.is_enraged = False
        self.rage_threshold = self.max_health * 0.5
        self.rage_damage_mult = 1.5
        self.rage_speed_mult = 1.67
        self.rage_vulnerability = 1.5  # Takes 50% more damage
        
        # Physics
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.facing_right = True
        
        # Combat state
        self.state = "patrol"  # patrol, chase, attack, leap
        self.state_timer = 0
        
        # Attack cooldowns
        self.attack_cooldown = 0
        self.leap_cooldown = 0
        
        # Attack tracking
        self.attack_hitbox = None
        self.attack_active = False
        
        # Particles
        self.particle_group = None
        
        # Animation
        self.animation_timer = 0
        self.hit_flash = 0
        self.rage_glow = 0
        
        # XP/Gold rewards
        self.xp_reward = 50
        self.gold_reward = 30
    
    def update(self, player, platforms):
        """Update berserker AI and physics"""
        # Update timers
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.leap_cooldown > 0:
            self.leap_cooldown -= 1
        if self.state_timer > 0:
            self.state_timer -= 1
        if self.hit_flash > 0:
            self.hit_flash -= 1
        
        self.animation_timer += 1
        
        # Check for rage mode activation
        if not self.is_enraged and self.health <= self.rage_threshold:
            self._enter_rage_mode()
        
        # Rage glow effect
        if self.is_enraged:
            self.rage_glow = (self.rage_glow + 5) % 60
        
        # State machine
        if self.state == "patrol":
            self._patrol_behavior(player)
        elif self.state == "chase":
            self._chase_behavior(player)
        elif self.state == "attack":
            self._attack_behavior()
        elif self.state == "leap":
            self._leap_behavior()
        
        # Apply physics
        self._apply_gravity()
        self._apply_movement(platforms)
        
        # Face player
        if hasattr(player, 'rect'):
            if player.rect.centerx < self.rect.centerx:
                self.facing_right = False
            else:
                self.facing_right = True
    
    def _enter_rage_mode(self):
        """Transform into rage mode"""
        self.is_enraged = True
        self.current_damage = int(self.base_damage * self.rage_damage_mult)
        self.current_speed = self.base_speed * self.rage_speed_mult
        
        # Visual effect
        if self.particle_group:
            for _ in range(20):
                from src.world import Particle
                angle = random.random() * math.pi * 2
                speed = random.uniform(2, 5)
                particle = Particle(
                    self.rect.centerx + random.randint(-30, 30),
                    self.rect.centery + random.randint(-30, 30),
                    math.cos(angle) * speed,
                    math.sin(angle) * speed,
                    color=(255, 0, 0),
                    lifetime=40
                )
                self.particle_group.add(particle)
    
    def _patrol_behavior(self, player):
        """Patrol or detect player"""
        if hasattr(player, 'rect'):
            distance = abs(player.rect.centerx - self.rect.centerx)
            if distance < 500:
                self.state = "chase"
                return
        
        # Patrol
        if self.rect.centerx < self.patrol_center - self.patrol_range:
            self.velocity_x = self.current_speed
        elif self.rect.centerx > self.patrol_center + self.patrol_range:
            self.velocity_x = -self.current_speed
    
    def _chase_behavior(self, player):
        """Chase player aggressively"""
        if not hasattr(player, 'rect'):
            return
        
        distance = abs(player.rect.centerx - self.rect.centerx)
        
        # If far away, return to patrol
        if distance > 600:
            self.state = "patrol"
            return
        
        # Leap attack if enraged and ready
        if self.is_enraged and distance < 300 and distance > 100 and self.leap_cooldown == 0:
            self.state = "leap"
            self.state_timer = 30  # Leap duration
            self.leap_cooldown = 300  # 5 second cooldown
            # Launch toward player
            direction = 1 if player.rect.centerx > self.rect.centerx else -1
            self.velocity_x = direction * 8
            self.velocity_y = -12
            return
        
        # Regular attack if close
        if distance < 80 and self.attack_cooldown == 0:
            self.state = "attack"
            self.state_timer = 30 if not self.is_enraged else 20  # Faster in rage
            self.attack_cooldown = 120 if not self.is_enraged else 60  # Faster attacks in rage
            return
        
        # Sprint toward player
        if player.rect.centerx < self.rect.centerx:
            self.velocity_x = -self.current_speed
        else:
            self.velocity_x = self.current_speed
    
    def _attack_behavior(self):
        """Execute melee attack"""
        # Create hitbox during active frames
        if self.state_timer == 20 or (self.is_enraged and self.state_timer == 15):
            hitbox_x = self.rect.right if self.facing_right else self.rect.left - 70
            self.attack_hitbox = pygame.Rect(hitbox_x, self.rect.y, 70, self.rect.height)
            self.attack_active = True
            
            # Spawn particles
            if self.particle_group:
                for _ in range(5):
                    from src.world import Particle
                    particle = Particle(
                        hitbox_x + 35,
                        self.rect.centery,
                        random.uniform(-2, 2),
                        random.uniform(-2, 2),
                        color=(255, 50, 50) if self.is_enraged else (200, 200, 200),
                        lifetime=15
                    )
                    self.particle_group.add(particle)
        
        # Clear hitbox
        if self.state_timer == 10:
            self.attack_hitbox = None
            self.attack_active = False
        
        # Return to chase
        if self.state_timer == 0:
            self.state = "chase"
    
    def _leap_behavior(self):
        """Execute leap attack (rage mode only)"""
        # Create AOE hitbox on landing
        if self.on_ground and self.state_timer > 0:
            # Impact!
            aoe_hitbox = pygame.Rect(
                self.rect.centerx - 80,
                self.rect.centery - 40,
                160, 80
            )
            self.attack_hitbox = aoe_hitbox
            self.attack_active = True
            
            # Impact particles
            if self.particle_group:
                for _ in range(30):
                    from src.world import Particle
                    angle = random.random() * math.pi * 2
                    speed = random.uniform(3, 8)
                    particle = Particle(
                        self.rect.centerx + random.randint(-60, 60),
                        self.rect.bottom,
                        math.cos(angle) * speed,
                        math.sin(angle) * speed,
                        color=(255, 100, 0),
                        lifetime=25
                    )
                    self.particle_group.add(particle)
            
            self.state_timer = 0
        
        if self.state_timer == 0:
            self.attack_hitbox = None
            self.attack_active = False
            self.state = "chase"
    
    def _apply_gravity(self):
        """Apply gravity"""
        if not self.on_ground:
            self.velocity_y += 0.5
            if self.velocity_y > 15:
                self.velocity_y = 15
    
    def _apply_movement(self, platforms):
        """Apply movement and handle collisions"""
        # Friction
        if self.state not in ["leap"]:
            self.velocity_x *= 0.88
        
        # Horizontal movement
        self.rect.x += self.velocity_x
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_x > 0:
                    self.rect.right = platform.rect.left
                elif self.velocity_x < 0:
                    self.rect.left = platform.rect.right
                if self.state != "leap":
                    self.velocity_x = 0
        
        # Vertical movement
        self.rect.y += self.velocity_y
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.on_ground = True
                    self.velocity_y = 0
                elif self.velocity_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0
    
    def take_damage(self, damage, attacker_pos=None):
        """Take damage with rage mode vulnerability"""
        actual_damage = damage
        
        # Increased damage in rage mode
        if self.is_enraged:
            actual_damage = int(damage * self.rage_vulnerability)
        
        self.health -= actual_damage
        self.hit_flash = 10
        
        # Death
        if self.health <= 0:
            self.kill()
            # Death particles
            if self.particle_group:
                for _ in range(25):
                    from src.world import Particle
                    angle = random.random() * math.pi * 2
                    speed = random.uniform(2, 6)
                    particle = Particle(
                        self.rect.centerx + random.randint(-30, 30),
                        self.rect.centery + random.randint(-30, 30),
                        math.cos(angle) * speed,
                        math.sin(angle) * speed,
                        color=(255, 0, 0) if self.is_enraged else (150, 150, 150),
                        lifetime=40
                    )
                    self.particle_group.add(particle)
        
        return actual_damage
    
    def get_attack_hitbox(self):
        """Get current attack hitbox"""
        return self.attack_hitbox if self.attack_active else None
    
    def get_attack_damage(self):
        """Get current attack damage"""
        return self.current_damage
    
    def draw(self, screen, camera):
        """Draw the berserker with sprite"""
        screen_rect = camera.apply(self)
        
        # Get sprite if sprite manager is available
        if hasattr(self, 'sprite_manager') and self.sprite_manager:
            # Determine animation state
            sprite_state = "rage" if self.is_enraged else self.state
            
            # Get frame based on animation timer
            frame = (pygame.time.get_ticks() // 100) % 4
            
            # Get sprite
            sprite = self.sprite_manager.get_sprite('berserker', sprite_state, frame)
            
            # Flip if facing left
            if not self.facing_right:
                sprite = pygame.transform.flip(sprite, True, False)
            
            # Apply hit flash
            if self.hit_flash > 0:
                sprite = sprite.copy()
                sprite.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_ADD)
            
            # Center sprite on rect
            sprite_rect = sprite.get_rect(center=screen_rect.center)
            screen.blit(sprite, sprite_rect)
        else:
            # Fallback to geometric rendering
            # Rage glow aura
            if self.is_enraged:
                glow_intensity = int(100 + 155 * (math.sin(self.rage_glow / 10) + 1) / 2)
                aura_rect = screen_rect.inflate(20, 20)
                pygame.draw.rect(screen, (glow_intensity, 0, 0), aura_rect, 3)
            
            # Body color
            if self.hit_flash > 0:
                color = (255, 255, 255)
            elif self.is_enraged:
                color = (200, 50, 50)  # Red when enraged
            else:
                color = (180, 140, 100)  # Tan/brown normal
            
            # Body
            pygame.draw.rect(screen, color, screen_rect)
            
            # Battle scars (marks)
            scar_color = (150, 0, 0) if self.is_enraged else (100, 80, 60)
            pygame.draw.line(screen, scar_color, 
                            (screen_rect.left + 15, screen_rect.top + 20),
                            (screen_rect.left + 25, screen_rect.top + 35), 3)
            
            # Eyes (glowing red in rage)
            eye_color = (255, 0, 0) if self.is_enraged else (50, 50, 50)
            eye_x = screen_rect.centerx + (8 if self.facing_right else -8)
            pygame.draw.circle(screen, eye_color, (eye_x, screen_rect.top + 20), 6)
        
        # Health bar (always show)
        bar_width = 60
        bar_height = 6
        bar_x = screen_rect.centerx - bar_width // 2
        bar_y = screen_rect.top - 15
        
        # Background
        pygame.draw.rect(screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        # Health
        health_width = int((self.health / self.max_health) * bar_width)
        health_color = (255, 0, 0) if self.is_enraged else (0, 255, 0)
        pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))
        
        # Rage threshold indicator
        rage_threshold_x = bar_x + int((self.rage_threshold / self.max_health) * bar_width)
        pygame.draw.line(screen, (255, 255, 0), 
                        (rage_threshold_x, bar_y), 
                        (rage_threshold_x, bar_y + bar_height), 2)
        
        # Debug: Draw attack hitbox
        if self.attack_hitbox:
            hitbox_screen = camera.apply_pos(self.attack_hitbox.x, self.attack_hitbox.y)
            hitbox_rect = pygame.Rect(hitbox_screen[0], hitbox_screen[1], 
                                      self.attack_hitbox.width, self.attack_hitbox.height)
            pygame.draw.rect(screen, (255, 255, 0), hitbox_rect, 2)

        
        # Weapon (axes)
        weapon_color = (100, 100, 100)
        if self.facing_right:
            pygame.draw.line(screen, weapon_color,
                           (screen_rect.right - 5, screen_rect.centery),
                           (screen_rect.right + 15, screen_rect.centery - 20), 4)
        else:
            pygame.draw.line(screen, weapon_color,
                           (screen_rect.left + 5, screen_rect.centery),
                           (screen_rect.left - 15, screen_rect.centery - 20), 4)
        
        # Health bar
        bar_width = 60
        bar_height = 6
        bar_x = screen_rect.centerx - bar_width // 2
        bar_y = screen_rect.top - 15
        
        pygame.draw.rect(screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        health_width = int((self.health / self.max_health) * bar_width)
        health_color = (255, 0, 0) if self.is_enraged else (0, 255, 0)
        pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))
        
        # Draw attack hitbox (debug)
        if self.attack_hitbox:
            hitbox_screen = camera.apply_pos(self.attack_hitbox.x, self.attack_hitbox.y)
            hitbox_rect = pygame.Rect(hitbox_screen[0], hitbox_screen[1], 
                                      self.attack_hitbox.width, self.attack_hitbox.height)
            pygame.draw.rect(screen, (255, 100, 0), hitbox_rect, 2)
