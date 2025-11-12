"""
Shadow Knight Boss
First boss encounter - melee focused with sword attacks
Inspired by Hollow Knight's boss design philosophy
"""

import pygame
import random
from src.entities.enemies.base_boss import BaseBoss, BossPhase, AttackPattern, BossState


class ShadowKnight(BaseBoss):
    """
    Shadow Knight - First Boss
    
    A skilled knight corrupted by shadow magic
    Phases:
    - Phase 1 (100%-66%): Basic sword attacks, slow and predictable
    - Phase 2 (66%-33%): Faster attacks, dash attacks added
    - Phase 3 (33%-0%): Berserker mode, combo attacks, more aggressive
    """
    
    def __init__(self, x: int, y: int):
        """Initialize Shadow Knight boss"""
        super().__init__(x, y, "SHADOW KNIGHT", max_health=1000)
        
        # Boss-specific properties
        self.rect = pygame.Rect(x, y, 80, 100)
        self.movement_speed = 2.0
        self.dash_speed = 15.0
        
        # Attack tracking
        self.attack_hitbox = None
        self.dash_attacking = False
        
        # Setup phases
        self._setup_phases()
    
    def _setup_phases(self):
        """Setup all boss phases with attack patterns"""
        
        # === PHASE 1: Basic Attacks (100% - 66%) ===
        phase1_patterns = [
            AttackPattern(
                name="Sword Slash",
                damage=15,
                windup_frames=30,
                execute_frames=15,
                recovery_frames=30,
                telegraph_color=(255, 100, 100)
            ),
            AttackPattern(
                name="Overhead Smash",
                damage=25,
                windup_frames=45,
                execute_frames=10,
                recovery_frames=40,
                telegraph_color=(255, 50, 50)
            ),
            AttackPattern(
                name="Spin Attack",
                damage=20,
                windup_frames=35,
                execute_frames=20,
                recovery_frames=35,
                telegraph_color=(200, 100, 200),
                is_special=True
            )
        ]
        
        phase1 = BossPhase(
            phase_number=1,
            health_threshold=1.0,
            attack_patterns=phase1_patterns,
            attack_frequency=120,
            special_attack_chance=0.15
        )
        self.add_phase(phase1)
        
        # === PHASE 2: Aggressive (66% - 33%) ===
        phase2_patterns = [
            AttackPattern(
                name="Quick Slash",
                damage=18,
                windup_frames=20,
                execute_frames=12,
                recovery_frames=25,
                telegraph_color=(255, 150, 100)
            ),
            AttackPattern(
                name="Dash Slash",
                damage=30,
                windup_frames=25,
                execute_frames=20,
                recovery_frames=30,
                telegraph_color=(255, 200, 50),
                is_special=True
            ),
            AttackPattern(
                name="Double Slash",
                damage=20,
                windup_frames=30,
                execute_frames=25,
                recovery_frames=35,
                telegraph_color=(255, 100, 255)
            ),
            AttackPattern(
                name="Spin Attack",
                damage=25,
                windup_frames=30,
                execute_frames=20,
                recovery_frames=30,
                telegraph_color=(200, 100, 200),
                is_special=True
            )
        ]
        
        phase2 = BossPhase(
            phase_number=2,
            health_threshold=0.66,
            attack_patterns=phase2_patterns,
            attack_frequency=90,
            special_attack_chance=0.25
        )
        self.add_phase(phase2)
        
        # === PHASE 3: Berserker (33% - 0%) ===
        phase3_patterns = [
            AttackPattern(
                name="Fury Slash",
                damage=22,
                windup_frames=15,
                execute_frames=10,
                recovery_frames=20,
                telegraph_color=(255, 50, 50)
            ),
            AttackPattern(
                name="Dash Slash",
                damage=35,
                windup_frames=20,
                execute_frames=15,
                recovery_frames=25,
                telegraph_color=(255, 200, 50)
            ),
            AttackPattern(
                name="Triple Combo",
                damage=15,  # Per hit
                windup_frames=25,
                execute_frames=40,
                recovery_frames=40,
                telegraph_color=(255, 0, 255),
                is_special=True
            ),
            AttackPattern(
                name="Berserker Spin",
                damage=30,
                windup_frames=35,
                execute_frames=30,
                recovery_frames=35,
                telegraph_color=(150, 0, 150),
                is_special=True
            )
        ]
        
        phase3 = BossPhase(
            phase_number=3,
            health_threshold=0.33,
            attack_patterns=phase3_patterns,
            attack_frequency=70,
            special_attack_chance=0.35
        )
        self.add_phase(phase3)
    
    def execute_attack_logic(self):
        """Execute attack-specific logic"""
        if not self.current_attack or not self.target_player:
            return
        
        attack_name = self.current_attack.name
        
        # Different logic for different attacks
        if attack_name in ["Sword Slash", "Quick Slash", "Fury Slash"]:
            self._execute_basic_slash()
        elif attack_name == "Overhead Smash":
            self._execute_overhead_smash()
        elif attack_name in ["Spin Attack", "Berserker Spin"]:
            self._execute_spin_attack()
        elif attack_name == "Dash Slash":
            self._execute_dash_slash()
        elif attack_name == "Double Slash":
            self._execute_double_slash()
        elif attack_name == "Triple Combo":
            self._execute_triple_combo()
    
    def _execute_basic_slash(self):
        """Execute basic sword slash"""
        # Create hitbox in front of boss
        hitbox_width = 60
        hitbox_height = 80
        
        if self.facing_right:
            hitbox_x = self.rect.right
        else:
            hitbox_x = self.rect.left - hitbox_width
        
        self.attack_hitbox = pygame.Rect(
            hitbox_x,
            self.rect.y,
            hitbox_width,
            hitbox_height
        )
    
    def _execute_overhead_smash(self):
        """Execute overhead smash"""
        # Larger hitbox in front, slightly below
        hitbox_width = 70
        hitbox_height = 90
        
        if self.facing_right:
            hitbox_x = self.rect.right
        else:
            hitbox_x = self.rect.left - hitbox_width
        
        self.attack_hitbox = pygame.Rect(
            hitbox_x,
            self.rect.y + 20,
            hitbox_width,
            hitbox_height
        )
    
    def _execute_spin_attack(self):
        """Execute spin attack (360 degree)"""
        # Circular hitbox around boss
        self.attack_hitbox = pygame.Rect(
            self.rect.x - 40,
            self.rect.y - 20,
            self.rect.width + 80,
            self.rect.height + 40
        )
    
    def _execute_dash_slash(self):
        """Execute dash slash"""
        # Dash towards player during windup
        if self.state == BossState.ATTACK_WINDUP and self.state_frame == 1:
            # Set dash direction
            direction = 1 if self.facing_right else -1
            self.velocity_x = self.dash_speed * direction
            self.dash_attacking = True
        
        # Hitbox extends during dash
        if self.dash_attacking:
            hitbox_width = 80
            hitbox_height = self.rect.height
            
            if self.facing_right:
                hitbox_x = self.rect.x
            else:
                hitbox_x = self.rect.x - hitbox_width + self.rect.width
            
            self.attack_hitbox = pygame.Rect(
                hitbox_x,
                self.rect.y,
                hitbox_width,
                hitbox_height
            )
        
        # Stop dash at end of execute
        if self.state == BossState.ATTACK_RECOVERY and self.state_frame == 1:
            self.dash_attacking = False
            self.velocity_x *= 0.2
    
    def _execute_double_slash(self):
        """Execute double slash combo"""
        # Two hitboxes at different frames
        execute_progress = self.state_frame / self.current_attack.execute_frames
        
        if execute_progress < 0.5:
            # First slash
            self._execute_basic_slash()
        else:
            # Second slash (slightly different timing)
            self._execute_basic_slash()
    
    def _execute_triple_combo(self):
        """Execute triple combo"""
        # Three slashes at different timings
        execute_progress = self.state_frame / self.current_attack.execute_frames
        
        if execute_progress < 0.33 or (0.33 <= execute_progress < 0.66) or execute_progress >= 0.66:
            self._execute_basic_slash()
    
    def get_attack_hitbox(self) -> pygame.Rect:
        """
        Get current attack hitbox
        
        Returns:
            Attack hitbox rectangle or None
        """
        return self.attack_hitbox
    
    def update(self, player, platforms: list):
        """
        Update Shadow Knight
        
        Args:
            player: Player object
            platforms: List of platforms
        """
        super().update(player, platforms)
        
        # Clear attack hitbox when not executing
        if self.state != BossState.ATTACK_EXECUTE:
            self.attack_hitbox = None
        
        # Movement AI (walk towards player when idle or in recovery)
        if self.state in [BossState.IDLE, BossState.ATTACK_RECOVERY] and player:
            distance_to_player = player.rect.centerx - self.rect.centerx
            
            # Move towards player if too far
            if abs(distance_to_player) > 100:
                move_direction = 1 if distance_to_player > 0 else -1
                self.velocity_x += move_direction * self.movement_speed * 0.3
    
    def draw(self, surface: pygame.Surface, camera):
        """
        Draw Shadow Knight
        
        Args:
            surface: Surface to draw on
            camera: Camera object
        """
        # Draw base boss
        super().draw(surface, camera)
        
        # Draw attack hitbox (debug visualization)
        if self.attack_hitbox:
            screen_pos = camera.apply_pos(self.attack_hitbox.x, self.attack_hitbox.y)
            
            # Semi-transparent red hitbox
            hitbox_surface = pygame.Surface(self.attack_hitbox.size, pygame.SRCALPHA)
            hitbox_surface.fill((255, 0, 0, 100))
            surface.blit(hitbox_surface, screen_pos)
