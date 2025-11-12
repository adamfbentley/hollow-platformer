"""
Boss Fight System - Base Boss Class
Professional boss framework with phase system and AI state machine
Inspired by Hollow Knight, Dark Souls, and Cuphead boss design
"""

import pygame
import random
from enum import Enum
from typing import Optional, List, Dict, Callable


class BossState(Enum):
    """Boss AI states"""
    IDLE = "idle"
    TAUNT = "taunt"
    PATTERN_SELECT = "pattern_select"
    ATTACK_WINDUP = "attack_windup"
    ATTACK_EXECUTE = "attack_execute"
    ATTACK_RECOVERY = "attack_recovery"
    VULNERABLE = "vulnerable"
    PHASE_TRANSITION = "phase_transition"
    STUNNED = "stunned"
    DEFEATED = "defeated"


class AttackPattern:
    """Represents a boss attack pattern"""
    
    def __init__(self, name: str, damage: int, windup_frames: int, 
                 execute_frames: int, recovery_frames: int, 
                 telegraph_color: tuple = (255, 100, 100),
                 is_special: bool = False):
        """
        Initialize attack pattern
        
        Args:
            name: Name of the attack
            damage: Damage dealt
            windup_frames: Frames before attack executes (telegraph)
            execute_frames: Active damage frames
            recovery_frames: Vulnerable frames after attack
            telegraph_color: Color for telegraph indicator
            is_special: Whether this is a phase-specific special attack
        """
        self.name = name
        self.damage = damage
        self.windup_frames = windup_frames
        self.execute_frames = execute_frames
        self.recovery_frames = recovery_frames
        self.telegraph_color = telegraph_color
        self.is_special = is_special
        self.cooldown = 0
        self.max_cooldown = 180  # 3 seconds at 60 FPS


class BossPhase:
    """Represents a boss phase with specific patterns and behavior"""
    
    def __init__(self, phase_number: int, health_threshold: float,
                 attack_patterns: List[AttackPattern],
                 attack_frequency: int = 120,
                 special_attack_chance: float = 0.2):
        """
        Initialize boss phase
        
        Args:
            phase_number: Phase number (1, 2, 3, etc.)
            health_threshold: HP% when this phase activates (0.0 to 1.0)
            attack_patterns: List of available attack patterns
            attack_frequency: Frames between attacks
            special_attack_chance: Chance to use special attacks
        """
        self.phase_number = phase_number
        self.health_threshold = health_threshold
        self.attack_patterns = attack_patterns
        self.attack_frequency = attack_frequency
        self.special_attack_chance = special_attack_chance
        self.transition_played = False


class BaseBoss:
    """
    Base class for all boss enemies
    Implements phase system, AI state machine, and attack patterns
    """
    
    def __init__(self, x: int, y: int, name: str, max_health: int):
        """
        Initialize base boss
        
        Args:
            x: Starting x position
            y: Starting y position
            name: Boss name (displayed in UI)
            max_health: Maximum health
        """
        # Basic properties
        self.name = name
        self.max_health = max_health
        self.current_health = max_health
        
        # Position and physics
        self.rect = pygame.Rect(x, y, 100, 120)  # Default size (override in subclass)
        self.velocity_x = 0
        self.velocity_y = 0
        self.facing_right = False
        self.on_ground = False
        
        # State machine
        self.state = BossState.IDLE
        self.state_timer = 0
        self.state_frame = 0
        
        # Phase system
        self.phases: List[BossPhase] = []
        self.current_phase_index = 0
        self.phase_transition_duration = 180  # 3 seconds
        
        # Combat
        self.current_attack: Optional[AttackPattern] = None
        self.attack_timer = 0
        self.attack_cooldown = 0
        self.is_invulnerable = False
        self.damage_flash_timer = 0
        
        # AI behavior
        self.target_player = None
        self.decision_timer = 0
        self.decision_cooldown = 60  # 1 second between decisions
        
        # Visual effects
        self.telegraph_alpha = 0
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        
        # Arena
        self.arena_bounds = None  # Set by arena
        
        # Flags
        self.intro_played = False
        self.is_defeated = False
        self.can_take_damage = True
        
    def add_phase(self, phase: BossPhase):
        """Add a phase to the boss"""
        self.phases.append(phase)
        self.phases.sort(key=lambda p: p.health_threshold, reverse=True)
    
    def get_current_phase(self) -> Optional[BossPhase]:
        """Get the current active phase based on health"""
        if not self.phases:
            return None
            
        health_percent = self.current_health / self.max_health
        
        for phase in self.phases:
            if health_percent <= phase.health_threshold:
                return phase
        
        return self.phases[-1]  # Return last phase if none match
    
    def check_phase_transition(self) -> bool:
        """
        Check if boss should transition to a new phase
        
        Returns:
            True if phase transition should occur
        """
        current_phase = self.get_current_phase()
        if not current_phase:
            return False
        
        phase_index = self.phases.index(current_phase)
        
        # Check if we've moved to a new phase
        if phase_index != self.current_phase_index:
            if not current_phase.transition_played:
                self.current_phase_index = phase_index
                return True
        
        return False
    
    def take_damage(self, damage: int, knockback_x: float = 0, knockback_y: float = 0):
        """
        Boss takes damage
        
        Args:
            damage: Damage amount
            knockback_x: Horizontal knockback
            knockback_y: Vertical knockback
        """
        if self.is_invulnerable or not self.can_take_damage:
            return
        
        self.current_health -= damage
        self.damage_flash_timer = 10
        
        # Apply knockback
        self.velocity_x += knockback_x
        self.velocity_y += knockback_y
        
        # Check for phase transition
        if self.check_phase_transition():
            self.trigger_phase_transition()
        
        # Check for defeat
        if self.current_health <= 0:
            self.current_health = 0
            self.trigger_defeat()
    
    def trigger_phase_transition(self):
        """Trigger phase transition"""
        self.state = BossState.PHASE_TRANSITION
        self.state_timer = self.phase_transition_duration
        self.is_invulnerable = True
        
        current_phase = self.get_current_phase()
        if current_phase:
            current_phase.transition_played = True
    
    def trigger_defeat(self):
        """Trigger boss defeat"""
        self.state = BossState.DEFEATED
        self.is_defeated = True
        self.can_take_damage = False
    
    def select_attack_pattern(self) -> Optional[AttackPattern]:
        """
        Select an attack pattern based on current phase
        
        Returns:
            Selected attack pattern or None
        """
        current_phase = self.get_current_phase()
        if not current_phase:
            return None
        
        # Filter available patterns (not on cooldown)
        available_patterns = [p for p in current_phase.attack_patterns 
                            if p.cooldown <= 0]
        
        if not available_patterns:
            return None
        
        # Decide if we should use a special attack
        use_special = random.random() < current_phase.special_attack_chance
        
        if use_special:
            special_patterns = [p for p in available_patterns if p.is_special]
            if special_patterns:
                return random.choice(special_patterns)
        
        # Use regular attack
        return random.choice(available_patterns)
    
    def update_state_machine(self, player):
        """
        Update boss AI state machine
        
        Args:
            player: Player object
        """
        self.state_frame += 1
        self.target_player = player
        
        # Update cooldowns
        current_phase = self.get_current_phase()
        if current_phase:
            for pattern in current_phase.attack_patterns:
                if pattern.cooldown > 0:
                    pattern.cooldown -= 1
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= 1
        
        # State machine logic
        if self.state == BossState.IDLE:
            self._update_idle()
        elif self.state == BossState.TAUNT:
            self._update_taunt()
        elif self.state == BossState.PATTERN_SELECT:
            self._update_pattern_select()
        elif self.state == BossState.ATTACK_WINDUP:
            self._update_attack_windup()
        elif self.state == BossState.ATTACK_EXECUTE:
            self._update_attack_execute()
        elif self.state == BossState.ATTACK_RECOVERY:
            self._update_attack_recovery()
        elif self.state == BossState.VULNERABLE:
            self._update_vulnerable()
        elif self.state == BossState.PHASE_TRANSITION:
            self._update_phase_transition()
        elif self.state == BossState.STUNNED:
            self._update_stunned()
        elif self.state == BossState.DEFEATED:
            self._update_defeated()
    
    def _update_idle(self):
        """Update idle state"""
        self.decision_timer += 1
        
        if self.decision_timer >= self.decision_cooldown and self.attack_cooldown <= 0:
            self.state = BossState.PATTERN_SELECT
            self.state_frame = 0
            self.decision_timer = 0
    
    def _update_taunt(self):
        """Update taunt state"""
        if self.state_frame >= 60:  # 1 second taunt
            self.state = BossState.IDLE
            self.state_frame = 0
    
    def _update_pattern_select(self):
        """Update pattern selection state"""
        self.current_attack = self.select_attack_pattern()
        
        if self.current_attack:
            self.state = BossState.ATTACK_WINDUP
            self.state_frame = 0
            self.attack_timer = self.current_attack.windup_frames
        else:
            # No attacks available, go back to idle
            self.state = BossState.IDLE
            self.state_frame = 0
    
    def _update_attack_windup(self):
        """Update attack windup (telegraph) state"""
        if not self.current_attack:
            self.state = BossState.IDLE
            return
        
        # Update telegraph visual
        self.telegraph_alpha = int((self.state_frame / self.current_attack.windup_frames) * 200)
        
        if self.state_frame >= self.current_attack.windup_frames:
            self.state = BossState.ATTACK_EXECUTE
            self.state_frame = 0
            self.attack_timer = self.current_attack.execute_frames
    
    def _update_attack_execute(self):
        """Update attack execution state"""
        if not self.current_attack:
            self.state = BossState.IDLE
            return
        
        # This is where subclasses implement actual attack logic
        self.execute_attack_logic()
        
        if self.state_frame >= self.current_attack.execute_frames:
            self.state = BossState.ATTACK_RECOVERY
            self.state_frame = 0
            self.attack_timer = self.current_attack.recovery_frames
    
    def _update_attack_recovery(self):
        """Update attack recovery state"""
        if not self.current_attack:
            self.state = BossState.IDLE
            return
        
        if self.state_frame >= self.current_attack.recovery_frames:
            # Set cooldown and reset
            self.current_attack.cooldown = self.current_attack.max_cooldown
            self.attack_cooldown = 60  # 1 second global cooldown
            self.current_attack = None
            self.telegraph_alpha = 0
            
            self.state = BossState.IDLE
            self.state_frame = 0
    
    def _update_vulnerable(self):
        """Update vulnerable state (optional: for specific mechanics)"""
        if self.state_frame >= 120:  # 2 seconds vulnerable
            self.state = BossState.IDLE
            self.state_frame = 0
    
    def _update_phase_transition(self):
        """Update phase transition state"""
        # Shake effect during transition
        if self.state_frame % 10 < 5:
            self.shake_offset_x = random.randint(-5, 5)
            self.shake_offset_y = random.randint(-5, 5)
        else:
            self.shake_offset_x = 0
            self.shake_offset_y = 0
        
        if self.state_frame >= self.phase_transition_duration:
            self.is_invulnerable = False
            self.state = BossState.TAUNT
            self.state_frame = 0
            self.shake_offset_x = 0
            self.shake_offset_y = 0
    
    def _update_stunned(self):
        """Update stunned state"""
        if self.state_frame >= 120:  # 2 seconds stunned
            self.state = BossState.IDLE
            self.state_frame = 0
    
    def _update_defeated(self):
        """Update defeated state"""
        # Death animation logic (handled by subclass)
        pass
    
    def execute_attack_logic(self):
        """
        Execute the current attack's logic
        Override this in subclasses for specific attack implementations
        """
        pass
    
    def update(self, player, platforms: list):
        """
        Update boss logic
        
        Args:
            player: Player object
            platforms: List of platforms
        """
        if not self.intro_played:
            return
        
        # Update state machine
        self.update_state_machine(player)
        
        # Apply gravity if not flying boss
        if not self.is_flying():
            self.velocity_y += 0.5
        
        # Apply velocity
        self.rect.x += int(self.velocity_x) + self.shake_offset_x
        self.rect.y += int(self.velocity_y) + self.shake_offset_y
        
        # Platform collision (if not flying)
        if not self.is_flying():
            self.handle_platform_collision(platforms)
        
        # Apply friction
        self.velocity_x *= 0.85
        
        # Face player
        if self.target_player and self.state not in [BossState.DEFEATED, BossState.PHASE_TRANSITION]:
            self.facing_right = self.rect.centerx < self.target_player.rect.centerx
    
    def is_flying(self) -> bool:
        """
        Whether this boss flies (override in subclass)
        
        Returns:
            True if boss flies
        """
        return False
    
    def handle_platform_collision(self, platforms: list):
        """Handle collision with platforms"""
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # Landing on top
                if self.velocity_y > 0 and self.rect.bottom <= platform.rect.top + 20:
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
    
    def draw(self, surface: pygame.Surface, camera):
        """
        Draw boss
        
        Args:
            surface: Surface to draw on
            camera: Camera object
        """
        # Apply camera offset
        screen_pos = camera.apply(self)
        
        # Draw telegraph indicator during windup
        if self.state == BossState.ATTACK_WINDUP and self.current_attack:
            telegraph_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            telegraph_surface.fill((*self.current_attack.telegraph_color, self.telegraph_alpha))
            surface.blit(telegraph_surface, (screen_pos.x, screen_pos.y))
        
        # Draw boss rect (placeholder - override with actual sprite)
        color = (255, 0, 0) if self.damage_flash_timer > 0 else (150, 50, 150)
        if self.is_invulnerable:
            color = (100, 100, 200)
        
        pygame.draw.rect(surface, color, (screen_pos.x, screen_pos.y, self.rect.width, self.rect.height))
        
        # Draw boss name (debug)
        font = pygame.font.Font(None, 24)
        name_surface = font.render(self.name, True, (255, 255, 255))
        name_rect = name_surface.get_rect(center=(screen_pos.x + self.rect.width // 2, screen_pos.y - 20))
        surface.blit(name_surface, name_rect)
    
    def get_health_percent(self) -> float:
        """
        Get health as percentage
        
        Returns:
            Health percentage (0.0 to 1.0)
        """
        return self.current_health / self.max_health if self.max_health > 0 else 0.0
    
    def play_intro(self):
        """Trigger intro sequence"""
        self.intro_played = True
        self.state = BossState.TAUNT
        self.state_frame = 0
