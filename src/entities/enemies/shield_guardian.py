"""
Shield Guardian Enemy
Defensive tank enemy that blocks frontal attacks and uses shield bash
"""

import pygame
import math
import random

class ShieldGuardian(pygame.sprite.Sprite):
    """Tank enemy with shield that blocks frontal attacks"""
    
    def __init__(self, x, y, patrol_range=200):
        super().__init__()
        
        # Visual
        self.rect = pygame.Rect(x, y, 70, 90)
        self.patrol_center = x
        self.patrol_range = patrol_range
        
        # Stats
        self.max_health = 250
        self.health = self.max_health
        self.damage = 20  # Shield bash damage
        self.sword_damage = 15
        self.speed = 1.5
        self.armor = 5  # Damage reduction
        
        # Physics
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.facing_right = True
        
        # Combat state
        self.state = "patrol"  # patrol, chase, shield_bash, sword_slash, stunned
        self.state_timer = 0
        
        # Shield mechanics
        self.shield_blocking = True
        self.shield_bash_cooldown = 0
        self.shield_bash_windup = 0
        self.shield_bash_active = 0
        self.shield_bash_recovery = 0
        
        # Sword attack
        self.sword_cooldown = 0
        
        # Attack hitbox
        self.attack_hitbox = None
        
        # Particles
        self.particle_group = None
        
        # Animation
        self.animation_timer = 0
        self.hit_flash = 0
        
        # XP/Gold rewards
        self.xp_reward = 30
        self.gold_reward = 20
    
    def update(self, player, platforms):
        """Update shield guardian AI and physics"""
        # Update timers
        if self.shield_bash_cooldown > 0:
            self.shield_bash_cooldown -= 1
        if self.sword_cooldown > 0:
            self.sword_cooldown -= 1
        if self.state_timer > 0:
            self.state_timer -= 1
        if self.hit_flash > 0:
            self.hit_flash -= 1
        
        self.animation_timer += 1
        
        # State machine
        if self.state == "patrol":
            self._patrol_behavior(player)
        elif self.state == "chase":
            self._chase_behavior(player)
        elif self.state == "shield_bash":
            self._shield_bash_behavior()
        elif self.state == "sword_slash":
            self._sword_slash_behavior()
        elif self.state == "stunned":
            # Do nothing while stunned
            if self.state_timer <= 0:
                self.state = "chase"
        
        # Apply physics
        self._apply_gravity()
        self._apply_movement(platforms)
        
        # Always face player
        if hasattr(player, 'rect'):
            if player.rect.centerx < self.rect.centerx:
                self.facing_right = False
            else:
                self.facing_right = True
    
    def _patrol_behavior(self, player):
        """Patrol between two points"""
        # Check if player is in range
        if hasattr(player, 'rect'):
            distance = abs(player.rect.centerx - self.rect.centerx)
            if distance < 400:
                self.state = "chase"
                return
        
        # Simple patrol
        if self.rect.centerx < self.patrol_center - self.patrol_range:
            self.velocity_x = self.speed
        elif self.rect.centerx > self.patrol_center + self.patrol_range:
            self.velocity_x = -self.speed
        
    def _chase_behavior(self, player):
        """Chase player and attempt attacks"""
        if not hasattr(player, 'rect'):
            return
        
        distance = abs(player.rect.centerx - self.rect.centerx)
        
        # If far away, return to patrol
        if distance > 500:
            self.state = "patrol"
            return
        
        # Shield bash if close and ready
        if distance < 100 and self.shield_bash_cooldown == 0:
            self.state = "shield_bash"
            self.shield_bash_windup = 30
            self.shield_bash_cooldown = 180  # 3 second cooldown
            return
        
        # Sword slash if shield bash on cooldown and very close
        if distance < 80 and self.sword_cooldown == 0 and self.shield_bash_cooldown > 60:
            self.state = "sword_slash"
            self.state_timer = 40
            self.sword_cooldown = 120  # 2 second cooldown
            self.shield_blocking = False
            return
        
        # Move toward player
        if player.rect.centerx < self.rect.centerx:
            self.velocity_x = -self.speed
        else:
            self.velocity_x = self.speed
    
    def _shield_bash_behavior(self):
        """Execute shield bash attack"""
        # Windup phase
        if self.shield_bash_windup > 0:
            self.shield_bash_windup -= 1
            self.velocity_x = 0
            
            if self.shield_bash_windup == 0:
                # Start active phase
                self.shield_bash_active = 15
                # Charge forward
                self.velocity_x = (10 if self.facing_right else -10)
                
                # Create attack hitbox
                hitbox_x = self.rect.right if self.facing_right else self.rect.left - 80
                self.attack_hitbox = pygame.Rect(hitbox_x, self.rect.y, 80, self.rect.height)
        
        # Active phase
        elif self.shield_bash_active > 0:
            self.shield_bash_active -= 1
            # Continue charging
            
            if self.shield_bash_active == 0:
                # Start recovery
                self.shield_bash_recovery = 40
                self.velocity_x = 0
                self.attack_hitbox = None
                self.shield_blocking = False  # Vulnerable during recovery
        
        # Recovery phase
        elif self.shield_bash_recovery > 0:
            self.shield_bash_recovery -= 1
            
            if self.shield_bash_recovery == 0:
                self.shield_blocking = True
                self.state = "chase"
    
    def _sword_slash_behavior(self):
        """Quick sword slash when shield is down"""
        # Simple sword attack
        if self.state_timer == 30:
            # Create sword hitbox
            hitbox_x = self.rect.right if self.facing_right else self.rect.left - 60
            self.attack_hitbox = pygame.Rect(hitbox_x, self.rect.y, 60, self.rect.height)
        elif self.state_timer == 20:
            self.attack_hitbox = None
        elif self.state_timer == 0:
            self.shield_blocking = True
            self.state = "chase"
    
    def _apply_gravity(self):
        """Apply gravity"""
        if not self.on_ground:
            self.velocity_y += 0.5
            if self.velocity_y > 15:
                self.velocity_y = 15
    
    def _apply_movement(self, platforms):
        """Apply movement and handle collisions"""
        # Apply friction when not actively moving
        if self.state not in ["shield_bash"]:
            self.velocity_x *= 0.85
        
        # Horizontal movement
        self.rect.x += self.velocity_x
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_x > 0:
                    self.rect.right = platform.rect.left
                elif self.velocity_x < 0:
                    self.rect.left = platform.rect.right
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
        """Take damage with shield blocking logic"""
        # Check if damage is from front (blocked by shield)
        if self.shield_blocking and attacker_pos:
            # Determine if attack is from front
            attack_from_right = attacker_pos[0] > self.rect.centerx
            if attack_from_right == self.facing_right:
                # Attack from front - blocked!
                self.hit_flash = 10
                return 0  # No damage
        
        # Apply armor reduction
        actual_damage = max(1, damage - self.armor)
        
        # Check for backstab (from behind = 2x damage)
        if attacker_pos:
            attack_from_right = attacker_pos[0] > self.rect.centerx
            if attack_from_right != self.facing_right:
                # Attack from behind
                actual_damage *= 2
        
        self.health -= actual_damage
        self.hit_flash = 10
        
        # Death
        if self.health <= 0:
            self.kill()
            # Spawn particles
            if self.particle_group:
                for _ in range(15):
                    from src.world import Particle
                    particle = Particle(
                        self.rect.centerx + random.randint(-20, 20),
                        self.rect.centery + random.randint(-20, 20),
                        color=(100, 100, 100),
                        lifetime=30
                    )
                    self.particle_group.add(particle)
        
        return actual_damage
    
    def get_attack_hitbox(self):
        """Get current attack hitbox for collision detection"""
        return self.attack_hitbox
    
    def get_attack_damage(self):
        """Get current attack damage"""
        if self.state == "shield_bash":
            return self.damage
        elif self.state == "sword_slash":
            return self.sword_damage
        return 0
    
    def draw(self, screen, camera):
        """Draw the shield guardian"""
        # Get screen position
        screen_rect = camera.apply(self)
        
        # Hit flash
    def draw(self, screen, camera):
        """Draw the shield guardian with sprite"""
        screen_rect = camera.apply(self)
        
        # Get sprite if sprite manager is available
        if hasattr(self, 'sprite_manager') and self.sprite_manager:
            # Determine animation state
            if self.state == "shield_bash":
                sprite_state = "shield_bash"
            elif self.state == "stunned":
                sprite_state = "idle"
            else:
                sprite_state = self.state
            
            # Get frame based on animation timer
            frame = (pygame.time.get_ticks() // 100) % 4
            
            # Get sprite
            sprite = self.sprite_manager.get_sprite('shield_guardian', sprite_state, frame)
            
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
            if self.hit_flash > 0:
                color = (255, 255, 255)
            else:
                color = (150, 150, 150)  # Gray armor
            
            # Body
            pygame.draw.rect(screen, color, screen_rect)
            
            # Shield (in front)
            shield_width = 50
            shield_height = 70
            if self.facing_right:
                shield_x = screen_rect.right - 10
            else:
                shield_x = screen_rect.left - shield_width + 10
            
            shield_rect = pygame.Rect(shield_x, screen_rect.centery - shield_height//2, 
                                      shield_width, shield_height)
            
            # Shield color - glows during bash windup
            if self.shield_bash_windup > 0:
                shield_color = (200, 200, 255)  # Blue glow
            elif not self.shield_blocking:
                shield_color = (100, 100, 120)  # Darkened
            else:
                shield_color = (180, 180, 200)  # Normal silver
            
            pygame.draw.rect(screen, shield_color, shield_rect, border_radius=5)
            pygame.draw.rect(screen, (255, 215, 0), shield_rect, 3, border_radius=5)  # Gold trim
            
            # Direction indicator
            eye_x = screen_rect.centerx + (10 if self.facing_right else -10)
            pygame.draw.circle(screen, (255, 0, 0), (eye_x, screen_rect.centery - 10), 5)
        
        # Health bar (always show)
        bar_width = 60
        bar_height = 6
        bar_x = screen_rect.centerx - bar_width // 2
        bar_y = screen_rect.top - 15
        
        # Background
        pygame.draw.rect(screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        # Health
        health_width = int((self.health / self.max_health) * bar_width)
        pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, health_width, bar_height))
        
        # Debug: Draw attack hitbox
        if self.attack_hitbox:
            hitbox_screen = camera.apply_pos(self.attack_hitbox.x, self.attack_hitbox.y)
            hitbox_rect = pygame.Rect(hitbox_screen[0], hitbox_screen[1], 
                                      self.attack_hitbox.width, self.attack_hitbox.height)
            pygame.draw.rect(screen, (255, 255, 0), hitbox_rect, 2)

