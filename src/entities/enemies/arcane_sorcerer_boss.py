"""
Arcane Sorcerer Boss
A powerful mage boss with ranged attacks, teleportation, and area-of-effect spells
"""

import pygame
import random
import math
from src.entities.enemies.base_boss import BaseBoss, BossPhase, AttackPattern, BossState


class MagicProjectile:
    """Magic projectile fired by the sorcerer"""
    def __init__(self, x, y, target_x, target_y, damage, speed=8.0, homing=False):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.damage = damage
        self.speed = speed
        self.homing = homing
        self.lifetime = 180  # 3 seconds at 60fps
        self.active = True
        
        # Calculate direction
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx*dx + dy*dy)
        if distance > 0:
            self.velocity_x = (dx / distance) * speed
            self.velocity_y = (dy / distance) * speed
        else:
            self.velocity_x = 0
            self.velocity_y = 0
    
    def update(self, player_rect=None):
        """Update projectile position"""
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.active = False
            return
        
        # Homing behavior
        if self.homing and player_rect:
            dx = player_rect.centerx - self.rect.centerx
            dy = player_rect.centery - self.rect.centery
            distance = math.sqrt(dx*dx + dy*dy)
            if distance > 0:
                # Gradually adjust direction
                target_vx = (dx / distance) * self.speed
                target_vy = (dy / distance) * self.speed
                self.velocity_x += (target_vx - self.velocity_x) * 0.05
                self.velocity_y += (target_vy - self.velocity_y) * 0.05
        
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
    
    def draw(self, surface, camera):
        """Draw projectile"""
        screen_pos = camera.apply_pos(self.rect.x, self.rect.y)
        
        # Draw glowing orb
        color = (150, 100, 255) if not self.homing else (255, 100, 150)
        pygame.draw.circle(surface, color, (int(screen_pos[0] + 10), int(screen_pos[1] + 10)), 10)
        # Glow effect
        glow_color = (*color, 100)
        glow_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, glow_color, (15, 15), 15)
        surface.blit(glow_surface, (screen_pos[0] - 5, screen_pos[1] - 5))


class ArcaneSorcerer(BaseBoss):
    """
    Second boss - Ranged magic user with teleportation and AOE attacks
    Contrasts with melee Shadow Knight by keeping distance and using projectiles
    """
    
    def __init__(self, x, y):
        super().__init__(
            x=x,
            y=y,
            name="Arcane Sorcerer",
            max_health=800
        )
        
        # Override rect size
        self.rect = pygame.Rect(x, y, 70, 90)
        
        self.preferred_distance = 300  # Prefers to keep distance from player
        self.teleport_distance = 400
        self.teleport_cooldown = 0
        self.teleport_cooldown_max = 120  # 2 seconds
        
        # Magic projectiles
        self.projectiles = []
        self.max_projectiles = 20
        
        # Visual effects
        self.teleport_effect_timer = 0
        self.charging_spell = False
        self.spell_charge_timer = 0
        
        self._setup_phases()
    
    def _setup_phases(self):
        """Setup boss phases with escalating spell patterns"""
        
        # Phase 1 (100% - 66%): Basic spells
        phase1_patterns = [
            AttackPattern(
                name="Magic Bolt",
                damage=12,
                windup_frames=30,
                execute_frames=10,
                recovery_frames=40,
                telegraph_color=(150, 100, 255)
            ),
            AttackPattern(
                name="Triple Shot",
                damage=10,
                windup_frames=45,
                execute_frames=20,
                recovery_frames=50,
                telegraph_color=(100, 150, 255)
            ),
            AttackPattern(
                name="Arcane Wave",
                damage=18,
                windup_frames=60,
                execute_frames=30,
                recovery_frames=60,
                telegraph_color=(200, 150, 255)
            ),
        ]
        phase1 = BossPhase(
            phase_number=1,
            health_threshold=1.0,
            attack_patterns=phase1_patterns,
            attack_frequency=90,
            special_attack_chance=0.2
        )
        
        # Phase 2 (66% - 33%): Aggressive spells + homing
        phase2_patterns = [
            AttackPattern(
                name="Homing Orb",
                damage=15,
                windup_frames=40,
                execute_frames=15,
                recovery_frames=45,
                telegraph_color=(255, 100, 200)
            ),
            AttackPattern(
                name="Pentagram Burst",
                damage=12,
                windup_frames=50,
                execute_frames=25,
                recovery_frames=55,
                telegraph_color=(150, 100, 255)
            ),
            AttackPattern(
                name="Chaos Barrage",
                damage=10,
                windup_frames=35,
                execute_frames=40,
                recovery_frames=50,
                telegraph_color=(255, 150, 100)
            ),
            AttackPattern(
                name="Teleport Strike",
                damage=20,
                windup_frames=30,
                execute_frames=20,
                recovery_frames=60,
                telegraph_color=(100, 255, 255)
            ),
        ]
        phase2 = BossPhase(
            phase_number=2,
            health_threshold=0.66,
            attack_patterns=phase2_patterns,
            attack_frequency=70,
            special_attack_chance=0.35
        )
        
        # Phase 3 (33% - 0%): Desperate powerful spells
        phase3_patterns = [
            AttackPattern(
                name="Dark Meteor",
                damage=25,
                windup_frames=70,
                execute_frames=30,
                recovery_frames=70,
                telegraph_color=(150, 0, 0)
            ),
            AttackPattern(
                name="Void Spiral",
                damage=15,
                windup_frames=45,
                execute_frames=50,
                recovery_frames=55,
                telegraph_color=(100, 0, 150)
            ),
            AttackPattern(
                name="Reality Tear",
                damage=30,
                windup_frames=90,
                execute_frames=40,
                recovery_frames=80,
                telegraph_color=(255, 0, 255)
            ),
            AttackPattern(
                name="Desperate Barrage",
                damage=12,
                windup_frames=25,
                execute_frames=60,
                recovery_frames=45,
                telegraph_color=(255, 100, 100)
            ),
        ]
        phase3 = BossPhase(
            phase_number=3,
            health_threshold=0.33,
            attack_patterns=phase3_patterns,
            attack_frequency=50,
            special_attack_chance=0.5
        )
        
        self.add_phase(phase1)
        self.add_phase(phase2)
        self.add_phase(phase3)
    
    def execute_attack_logic(self, player_rect):
        """Execute the current attack pattern"""
        if not self.current_attack:
            return
        
        attack_name = self.current_attack.name
        
        # Route to specific attack implementation
        if attack_name == "Magic Bolt":
            self._execute_magic_bolt(player_rect)
        elif attack_name == "Triple Shot":
            self._execute_triple_shot(player_rect)
        elif attack_name == "Arcane Wave":
            self._execute_arcane_wave(player_rect)
        elif attack_name == "Homing Orb":
            self._execute_homing_orb(player_rect)
        elif attack_name == "Pentagram Burst":
            self._execute_pentagram_burst(player_rect)
        elif attack_name == "Chaos Barrage":
            self._execute_chaos_barrage(player_rect)
        elif attack_name == "Teleport Strike":
            self._execute_teleport_strike(player_rect)
        elif attack_name == "Dark Meteor":
            self._execute_dark_meteor(player_rect)
        elif attack_name == "Void Spiral":
            self._execute_void_spiral(player_rect)
        elif attack_name == "Reality Tear":
            self._execute_reality_tear(player_rect)
        elif attack_name == "Desperate Barrage":
            self._execute_desperate_barrage(player_rect)
    
    def _execute_magic_bolt(self, player_rect):
        """Fire a single magic bolt at player"""
        if self.state_frame == 0:
            projectile = MagicProjectile(
                self.rect.centerx, self.rect.centery,
                player_rect.centerx, player_rect.centery,
                self.current_attack.damage, speed=10.0
            )
            self.projectiles.append(projectile)
    
    def _execute_triple_shot(self, player_rect):
        """Fire three bolts in a spread pattern"""
        if self.state_frame == 0:
            angles = [-20, 0, 20]
            for angle in angles:
                # Calculate direction with angle offset
                dx = player_rect.centerx - self.rect.centerx
                dy = player_rect.centery - self.rect.centery
                angle_rad = math.radians(angle)
                rotated_x = dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
                rotated_y = dx * math.sin(angle_rad) + dy * math.cos(angle_rad)
                
                target_x = self.rect.centerx + rotated_x
                target_y = self.rect.centery + rotated_y
                
                projectile = MagicProjectile(
                    self.rect.centerx, self.rect.centery,
                    target_x, target_y,
                    self.current_attack.damage, speed=9.0
                )
                self.projectiles.append(projectile)
    
    def _execute_arcane_wave(self, player_rect):
        """Fire a wave of 5 projectiles"""
        if self.state_frame % 5 == 0 and self.state_frame < 25:
            projectile = MagicProjectile(
                self.rect.centerx, self.rect.centery,
                player_rect.centerx, player_rect.centery,
                self.current_attack.damage, speed=8.0
            )
            self.projectiles.append(projectile)
    
    def _execute_homing_orb(self, player_rect):
        """Fire a homing projectile"""
        if self.state_frame == 0:
            projectile = MagicProjectile(
                self.rect.centerx, self.rect.centery,
                player_rect.centerx, player_rect.centery,
                self.current_attack.damage, speed=6.0, homing=True
            )
            self.projectiles.append(projectile)
    
    def _execute_pentagram_burst(self, player_rect):
        """Fire projectiles in a pentagram pattern (5 directions)"""
        if self.state_frame == 0:
            for i in range(5):
                angle = (360 / 5) * i
                angle_rad = math.radians(angle)
                distance = 500
                target_x = self.rect.centerx + math.cos(angle_rad) * distance
                target_y = self.rect.centery + math.sin(angle_rad) * distance
                
                projectile = MagicProjectile(
                    self.rect.centerx, self.rect.centery,
                    target_x, target_y,
                    self.current_attack.damage, speed=7.0
                )
                self.projectiles.append(projectile)
    
    def _execute_chaos_barrage(self, player_rect):
        """Rapid fire random projectiles"""
        if self.state_frame % 4 == 0:
            # Random spread around player
            spread = 100
            target_x = player_rect.centerx + random.randint(-spread, spread)
            target_y = player_rect.centery + random.randint(-spread, spread)
            
            projectile = MagicProjectile(
                self.rect.centerx, self.rect.centery,
                target_x, target_y,
                self.current_attack.damage, speed=12.0
            )
            self.projectiles.append(projectile)
    
    def _execute_teleport_strike(self, player_rect):
        """Teleport near player and create shockwave"""
        if self.state_frame == 0:
            # Teleport to side of player
            side = random.choice([-1, 1])
            self.rect.x = player_rect.centerx + (side * 150)
            self.rect.y = player_rect.centery - 50
            self.teleport_effect_timer = 30
            
            # Create shockwave projectiles
            for i in range(8):
                angle = (360 / 8) * i
                angle_rad = math.radians(angle)
                distance = 300
                target_x = self.rect.centerx + math.cos(angle_rad) * distance
                target_y = self.rect.centery + math.sin(angle_rad) * distance
                
                projectile = MagicProjectile(
                    self.rect.centerx, self.rect.centery,
                    target_x, target_y,
                    self.current_attack.damage, speed=6.0
                )
                self.projectiles.append(projectile)
    
    def _execute_dark_meteor(self, player_rect):
        """Large slow projectile with high damage"""
        if self.state_frame == 0:
            projectile = MagicProjectile(
                self.rect.centerx, self.rect.centery - 200,
                player_rect.centerx, player_rect.centery,
                self.current_attack.damage, speed=5.0
            )
            projectile.rect.width = 40
            projectile.rect.height = 40
            self.projectiles.append(projectile)
    
    def _execute_void_spiral(self, player_rect):
        """Spiral pattern of projectiles"""
        if self.state_frame % 3 == 0:
            angle = (self.state_frame * 15) % 360
            angle_rad = math.radians(angle)
            distance = 500
            target_x = self.rect.centerx + math.cos(angle_rad) * distance
            target_y = self.rect.centery + math.sin(angle_rad) * distance
            
            projectile = MagicProjectile(
                self.rect.centerx, self.rect.centery,
                target_x, target_y,
                self.current_attack.damage, speed=8.0
            )
            self.projectiles.append(projectile)
    
    def _execute_reality_tear(self, player_rect):
        """Create multiple homing orbs"""
        if self.state_frame % 10 == 0 and self.state_frame < 40:
            projectile = MagicProjectile(
                self.rect.centerx + random.randint(-50, 50),
                self.rect.centery + random.randint(-50, 50),
                player_rect.centerx, player_rect.centery,
                self.current_attack.damage, speed=5.0, homing=True
            )
            self.projectiles.append(projectile)
    
    def _execute_desperate_barrage(self, player_rect):
        """Extremely rapid fire in desperation"""
        if self.state_frame % 2 == 0:
            projectile = MagicProjectile(
                self.rect.centerx, self.rect.centery,
                player_rect.centerx + random.randint(-80, 80),
                player_rect.centery + random.randint(-80, 80),
                self.current_attack.damage, speed=14.0
            )
            self.projectiles.append(projectile)
    
    def update(self, player_rect, platforms):
        """Update sorcerer AI and projectiles"""
        # Update projectiles
        self.projectiles = [p for p in self.projectiles if p.active]
        for projectile in self.projectiles:
            projectile.update(player_rect)
        
        # Limit projectile count
        if len(self.projectiles) > self.max_projectiles:
            self.projectiles = self.projectiles[-self.max_projectiles:]
        
        # Update teleport cooldown
        if self.teleport_cooldown > 0:
            self.teleport_cooldown -= 1
        
        # Update effects
        if self.teleport_effect_timer > 0:
            self.teleport_effect_timer -= 1
        
        # Movement AI - keep distance from player
        if self.state in [BossState.IDLE, BossState.PATTERN_SELECT]:
            distance_to_player = abs(self.rect.centerx - player_rect.centerx)
            
            # Too close - teleport away if cooldown ready
            if distance_to_player < 200 and self.teleport_cooldown == 0:
                direction = 1 if self.rect.centerx < player_rect.centerx else -1
                self.rect.x += direction * -self.teleport_distance
                self.teleport_cooldown = self.teleport_cooldown_max
                self.teleport_effect_timer = 30
            # Maintain preferred distance
            elif distance_to_player < self.preferred_distance - 50:
                # Move away
                direction = 1 if self.rect.centerx > player_rect.centerx else -1
                self.velocity_x = direction * 2.0
            elif distance_to_player > self.preferred_distance + 50:
                # Move closer
                direction = 1 if self.rect.centerx < player_rect.centerx else -1
                self.velocity_x = direction * 2.0
            else:
                # Maintain position
                self.velocity_x *= 0.8
        
        # Call parent update
        super().update(player_rect, platforms)
    
    def get_projectiles(self):
        """Get all active projectiles"""
        return self.projectiles
    
    def get_attack_hitbox(self):
        """
        Get attack hitbox for collision detection
        Arcane Sorcerer doesn't have melee attacks, returns None
        Projectiles are checked separately
        """
        return None
    
    def draw(self, surface: pygame.Surface, camera):
        """Draw sorcerer and projectiles"""
        # Draw projectiles first (behind boss)
        for projectile in self.projectiles:
            projectile.draw(surface, camera)
        
        # Teleport effect
        if self.teleport_effect_timer > 0:
            screen_pos = camera.apply(self)
            alpha = int((self.teleport_effect_timer / 30) * 255)
            teleport_surface = pygame.Surface((self.rect.width + 40, self.rect.height + 40), pygame.SRCALPHA)
            pygame.draw.circle(teleport_surface, (150, 100, 255, alpha), 
                             (teleport_surface.get_width() // 2, teleport_surface.get_height() // 2),
                             max(self.rect.width, self.rect.height) // 2 + 20)
            surface.blit(teleport_surface, (screen_pos.x - 20, screen_pos.y - 20))
        
        # Call parent draw
        super().draw(surface, camera)
        
        # Override boss color to be more magical
        screen_pos = camera.apply(self)
        color = (100, 50, 200) if self.damage_flash_timer == 0 else (255, 0, 0)
        if self.is_invulnerable:
            color = (150, 100, 255)
        
        pygame.draw.rect(surface, color, (screen_pos.x, screen_pos.y, self.rect.width, self.rect.height))
        
        # Draw charging effect during windup
        if self.state == BossState.ATTACK_WINDUP and self.current_attack:
            charge_alpha = int((self.state_frame / self.current_attack.windup_frames) * 200)
            charge_surface = pygame.Surface((self.rect.width + 20, self.rect.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(charge_surface, (150, 100, 255, charge_alpha), 
                           (0, 0, charge_surface.get_width(), charge_surface.get_height()), 3)
            surface.blit(charge_surface, (screen_pos.x - 10, screen_pos.y - 10))
        
        # Draw boss name
        font = pygame.font.Font(None, 24)
        name_surface = font.render(self.name, True, (200, 150, 255))
        name_rect = name_surface.get_rect(center=(screen_pos.x + self.rect.width // 2, screen_pos.y - 20))
        surface.blit(name_surface, name_rect)
