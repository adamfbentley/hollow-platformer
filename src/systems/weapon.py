"""
Weapon System
Data-driven weapon implementation with unique movesets per weapon type
Supports combos, special abilities, and stat scaling
"""

import pygame
import json
import os
import math
from typing import Optional, Tuple, List


class Weapon:
    """
    Base weapon class
    All weapons inherit from this and can override attack behavior
    """
    
    def __init__(self, weapon_id: str, weapon_data: dict):
        """
        Initialize weapon from data
        
        Args:
            weapon_id: Unique identifier for weapon
            weapon_data: Dictionary containing weapon configuration
        """
        self.id = weapon_id
        self.name = weapon_data['name']
        self.description = weapon_data['description']
        self.weapon_type = weapon_data['weapon_type']
        self.rarity = weapon_data['rarity']
        
        # Stats
        self.base_damage = weapon_data['stats']['base_damage']
        self.attack_speed = weapon_data['stats']['attack_speed']
        self.crit_chance = weapon_data['stats']['crit_chance']
        self.crit_multiplier = weapon_data['stats']['crit_multiplier']
        self.knockback = weapon_data['stats']['knockback']
        self.range = weapon_data['stats']['range']
        
        # Stamina costs
        self.stamina_light = weapon_data['stamina']['light_attack']
        self.stamina_heavy = weapon_data['stamina']['heavy_attack']
        self.stamina_finisher = weapon_data['stamina']['combo_finisher']
        
        # Attack timing (frames)
        self.windup_frames = weapon_data['attack_timing']['windup_frames']
        self.active_frames = weapon_data['attack_timing']['active_frames']
        self.recovery_frames = weapon_data['attack_timing']['recovery_frames']
        self.combo_window = weapon_data['attack_timing']['combo_window']
        
        # Hitbox
        self.hitbox_width = weapon_data['hitbox']['width']
        self.hitbox_height = weapon_data['hitbox']['height']
        self.hitbox_offset_x = weapon_data['hitbox']['offset_x']
        self.hitbox_offset_y = weapon_data['hitbox']['offset_y']
        self.arc_sweep = weapon_data['hitbox']['arc_sweep']
        
        # Visual effects
        self.screen_shake = weapon_data['effects']['screen_shake']
        self.hit_freeze = weapon_data['effects']['hit_freeze']
        self.particle_count = weapon_data['effects']['particle_count']
        self.particle_color = tuple(weapon_data['effects']['particle_color'])
        
        # Special effects (if any)
        self.stun_chance = weapon_data['effects'].get('stun_chance', 0.0)
        self.stun_duration = weapon_data['effects'].get('stun_duration', 0)
        
        # Combo system
        self.combo_chain = weapon_data['combo_chain']
        self.special_ability = weapon_data.get('special_ability')
        
        # Current attack state
        self.current_attack_type = 'light'  # light, heavy, finisher
        self.attack_frame = 0
        self.attack_phase = 'idle'  # idle, windup, active, recovery
        self.combo_count = 0
        self.combo_timer = 0
        
    def start_attack(self, attack_type: str = 'light') -> bool:
        """
        Start an attack with this weapon
        
        Args:
            attack_type: 'light', 'heavy', or 'finisher'
            
        Returns:
            True if attack started successfully
        """
        if self.attack_phase != 'idle':
            return False
        
        self.current_attack_type = attack_type
        self.attack_frame = 0
        self.attack_phase = 'windup'
        self.combo_timer = self.combo_window
        
        return True
    
    def update(self) -> dict:
        """
        Update weapon state
        
        Returns:
            Dictionary with current frame info (phase, frame, hitbox_active)
        """
        # Safety check for infinite loops
        if self.attack_frame > 1000:
            self.attack_phase = 'idle'
            self.attack_frame = 0
            return {'phase': 'idle', 'frame': 0, 'hitbox_active': False}
        
        if self.attack_phase == 'idle':
            # Decrement combo timer
            if self.combo_timer > 0:
                self.combo_timer -= 1
                if self.combo_timer == 0:
                    self.combo_count = 0
            return {'phase': 'idle', 'frame': 0, 'hitbox_active': False}
        
        prev_phase = self.attack_phase
        self.attack_frame += 1
        
        # State transitions
        if self.attack_phase == 'windup':
            if self.attack_frame >= self.windup_frames:
                self.attack_phase = 'active'
                self.attack_frame = 0
        
        elif self.attack_phase == 'active':
            if self.attack_frame >= self.active_frames:
                self.attack_phase = 'recovery'
                self.attack_frame = 0
        
        elif self.attack_phase == 'recovery':
            if self.attack_frame >= self.recovery_frames:
                self.attack_phase = 'idle'
                self.attack_frame = 0
                self.combo_count += 1
                if self.combo_count >= len(self.combo_chain):
                    self.combo_count = 0
        
        # Debug: Log phase transitions
        if prev_phase != self.attack_phase:
            print(f"[Weapon] {prev_phase} -> {self.attack_phase}")
        
        return {
            'phase': self.attack_phase,
            'frame': self.attack_frame,
            'hitbox_active': self.attack_phase == 'active'
        }
    
    def get_hitbox(self, player_rect: pygame.Rect, facing_right: bool) -> Optional[pygame.Rect]:
        """
        Calculate attack hitbox based on player position and facing direction
        
        Args:
            player_rect: Player's rect
            facing_right: True if player facing right
            
        Returns:
            Pygame Rect for hitbox, or None if attack not active
        """
        if self.attack_phase != 'active':
            return None
        
        # Calculate hitbox position
        if facing_right:
            hitbox_x = player_rect.centerx + self.hitbox_offset_x
        else:
            hitbox_x = player_rect.centerx - self.hitbox_offset_x - self.hitbox_width
        
        hitbox_y = player_rect.centery + self.hitbox_offset_y
        
        return pygame.Rect(hitbox_x, hitbox_y, self.hitbox_width, self.hitbox_height)
    
    def calculate_damage(self, player_stats, is_crit: bool = False, combo_bonus: float = 0.0) -> int:
        """
        Calculate total damage including player stats and bonuses
        
        Args:
            player_stats: PlayerStats object
            is_crit: Whether this is a critical hit
            combo_bonus: Damage bonus from combo (0.0 to 1.0)
            
        Returns:
            Final damage value
        """
        # Base damage + stat scaling
        damage = self.base_damage
        
        # Add player stat bonuses (handled by player_stats)
        damage += player_stats.attack_damage - 10  # Subtract base to avoid double counting
        
        # Apply critical hit multiplier
        if is_crit:
            damage *= self.crit_multiplier
        
        # Apply combo bonus
        damage *= (1.0 + combo_bonus)
        
        return int(damage)
    
    def get_stamina_cost(self) -> int:
        """
        Get stamina cost for current attack type
        
        Returns:
            Stamina cost
        """
        if self.current_attack_type == 'light':
            return self.stamina_light
        elif self.current_attack_type == 'heavy':
            return self.stamina_heavy
        else:  # finisher
            return self.stamina_finisher
    
    def can_cancel_to_dodge(self) -> bool:
        """
        Check if current attack can be canceled into dodge
        
        Returns:
            True if can cancel (during windup phase)
        """
        return self.attack_phase == 'windup'
    
    def is_attack_active(self) -> bool:
        """
        Check if attack is in active phase (hitbox enabled)
        
        Returns:
            True if in active phase
        """
        return self.attack_phase == 'active'
    
    def reset(self):
        """Reset weapon to idle state"""
        self.attack_phase = 'idle'
        self.attack_frame = 0
        self.combo_count = 0
        self.combo_timer = 0
    
    def draw_debug(self, surface: pygame.Surface, camera, player_rect: pygame.Rect, facing_right: bool):
        """
        Draw debug visualization of weapon hitbox
        
        Args:
            surface: Surface to draw on
            camera: Camera for offset
            player_rect: Player position
            facing_right: Player facing direction
        """
        hitbox = self.get_hitbox(player_rect, facing_right)
        if hitbox:
            # Convert to screen coordinates
            screen_hitbox = pygame.Rect(
                hitbox.x - camera.x,
                hitbox.y - camera.y,
                hitbox.width,
                hitbox.height
            )
            
            # Draw hitbox
            color = (255, 0, 0, 128) if self.attack_phase == 'active' else (255, 255, 0, 128)
            pygame.draw.rect(surface, color, screen_hitbox, 2)
            
            # Draw arc indicator
            if self.arc_sweep > 0:
                center = (screen_hitbox.centerx, screen_hitbox.centery)
                pygame.draw.circle(surface, color, center, self.range, 1)


class WeaponManager:
    """
    Manages weapon collection and switching
    Handles loading weapon data from JSON
    """
    
    def __init__(self, data_path: str = 'data/weapon_data.json'):
        """
        Initialize weapon manager
        
        Args:
            data_path: Path to weapon data JSON file
        """
        self.data_path = data_path
        self.weapon_data = {}
        self.scaling_data = {}
        self.stamina_config = {}
        self.combat_modifiers = {}
        
        self.weapons = {}  # weapon_id -> Weapon instance
        self.current_weapon_id = 'sword'
        
        self.load_weapon_data()
    
    def load_weapon_data(self):
        """Load weapon data from JSON file"""
        if not os.path.exists(self.data_path):
            print(f"Warning: Weapon data not found at {self.data_path}")
            return
        
        with open(self.data_path, 'r') as f:
            data = json.load(f)
        
        self.weapon_data = data.get('weapons', {})
        self.scaling_data = data.get('weapon_scaling', {})
        self.stamina_config = data.get('stamina_system', {})
        self.combat_modifiers = data.get('combat_modifiers', {})
        
        # Create weapon instances
        for weapon_id, weapon_info in self.weapon_data.items():
            self.weapons[weapon_id] = Weapon(weapon_id, weapon_info)
    
    def get_weapon(self, weapon_id: str) -> Optional[Weapon]:
        """
        Get weapon instance by ID
        
        Args:
            weapon_id: Weapon identifier
            
        Returns:
            Weapon instance or None if not found
        """
        return self.weapons.get(weapon_id)
    
    def get_current_weapon(self) -> Weapon:
        """Get currently equipped weapon"""
        return self.weapons.get(self.current_weapon_id, list(self.weapons.values())[0])
    
    def switch_weapon(self, weapon_id: str) -> bool:
        """
        Switch to different weapon
        
        Args:
            weapon_id: ID of weapon to switch to
            
        Returns:
            True if switched successfully
        """
        if weapon_id in self.weapons:
            # Reset current weapon
            current = self.get_current_weapon()
            if current:
                current.reset()
            
            self.current_weapon_id = weapon_id
            return True
        return False
    
    def get_available_weapons(self) -> List[str]:
        """
        Get list of available weapon IDs
        
        Returns:
            List of weapon IDs
        """
        return list(self.weapons.keys())
    
    def get_stamina_config(self) -> dict:
        """Get stamina system configuration"""
        return self.stamina_config
    
    def get_combat_modifiers(self) -> dict:
        """Get combat modifier configuration"""
        return self.combat_modifiers
