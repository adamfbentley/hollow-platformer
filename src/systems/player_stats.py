"""
Player Stats System for RPG
Handles attributes, derived stats, experience, and leveling
"""

import math
import random


class PlayerStats:
    """
    Core RPG stats system with attributes and derived combat stats
    Inspired by Path of Exile's attribute system
    """
    
    def __init__(self):
        # === CORE ATTRIBUTES ===
        self.strength = 10          # Affects melee damage, carry weight, HP
        self.dexterity = 10         # Affects attack speed, dodge chance, accuracy
        self.intelligence = 10      # Affects magic damage, mana pool, mana regen
        self.vitality = 10          # Affects health pool, health regen, resistance
        
        # === EXPERIENCE & LEVELING ===
        self.level = 1
        self.current_xp = 0
        self.xp_to_next_level = self.calculate_xp_for_level(2)
        
        # Points to spend
        self.attribute_points = 0   # Gained on level-up
        self.skill_points = 0       # For skill tree (future)
        
        # === DERIVED STATS (calculated from attributes) ===
        # Health
        self.max_health = 100
        self.current_health = 100
        self.health_regen = 0.1     # HP per second
        
        # Mana
        self.max_mana = 50
        self.current_mana = 50
        self.mana_regen = 0.5       # Mana per second
        
        # Stamina (Dark Souls-style)
        self.max_stamina = 100
        self.current_stamina = 100
        self.stamina_regen = 5.0    # Stamina per second
        self.stamina_regen_delay = 0  # Frames before regen starts after action
        self.stamina_regen_delay_max = 30  # 0.5 seconds at 60 FPS
        
        # Combat - Offense
        self.base_damage = 10
        self.attack_damage = 10
        self.attack_speed = 1.0     # Multiplier (1.0 = normal)
        self.critical_chance = 0.05 # 5% base
        self.critical_multiplier = 1.5  # 150% damage on crit
        
        # Combat - Defense
        self.defense = 0            # Flat damage reduction
        self.armor = 0              # Percentage damage reduction
        self.dodge_chance = 0.0     # Chance to avoid attack
        self.elemental_resistance = 0.0  # % reduction to elemental damage
        
        # Movement
        self.movement_speed = 1.0   # Multiplier for base speed
        
        # Utility
        self.carry_weight = 100     # Max inventory weight
        self.item_rarity = 1.0      # Better drops
        
        # Calculate initial derived stats
        self.recalculate_stats()
    
    def calculate_xp_for_level(self, target_level):
        """Calculate XP required to reach target level"""
        # Formula: 100 * level^1.5 (exponential scaling)
        return int(100 * math.pow(target_level, 1.5))
    
    def add_xp(self, amount):
        """
        Add experience points and check for level-up
        Returns True if leveled up
        """
        self.current_xp += amount
        
        # Check for level-up (can level multiple times)
        leveled_up = False
        while self.current_xp >= self.xp_to_next_level:
            self.level_up()
            leveled_up = True
        
        return leveled_up
    
    def level_up(self):
        """Level up the player, grant rewards"""
        # Carry over excess XP
        self.current_xp -= self.xp_to_next_level
        self.level += 1
        
        # Calculate new XP requirement
        self.xp_to_next_level = self.calculate_xp_for_level(self.level + 1)
        
        # Grant rewards
        self.attribute_points += 5  # 5 points per level
        self.skill_points += 1      # 1 skill point per level
        
        # Recalculate stats with new level
        self.recalculate_stats()
        
        # Heal to full on level-up
        self.current_health = self.max_health
        self.current_mana = self.max_mana
        
        print(f"LEVEL UP! Now level {self.level}")
        print(f"Gained 5 attribute points and 1 skill point!")
    
    def add_attribute_point(self, attribute_name):
        """
        Spend an attribute point on an attribute
        Returns True if successful
        """
        if self.attribute_points <= 0:
            return False
        
        attribute_name = attribute_name.lower()
        
        if attribute_name == 'strength':
            self.strength += 1
        elif attribute_name == 'dexterity':
            self.dexterity += 1
        elif attribute_name == 'intelligence':
            self.intelligence += 1
        elif attribute_name == 'vitality':
            self.vitality += 1
        else:
            return False
        
        self.attribute_points -= 1
        self.recalculate_stats()
        return True
    
    def recalculate_stats(self):
        """
        Recalculate all derived stats based on attributes
        This should be called whenever attributes change
        """
        # === HEALTH ===
        # Base 100 + 10 per vitality + 5 per level
        old_max_health = self.max_health
        self.max_health = 100 + (self.vitality * 10) + (self.level * 5)
        
        # Adjust current health proportionally if max changed
        if old_max_health > 0:
            health_percent = self.current_health / old_max_health
            self.current_health = int(self.max_health * health_percent)
        else:
            self.current_health = self.max_health
        
        # Health regen: 0.1 base + 0.05 per vitality point
        self.health_regen = 0.1 + (self.vitality * 0.05)
        
        # === MANA ===
        # Base 50 + 5 per intelligence + 2 per level
        old_max_mana = self.max_mana
        self.max_mana = 50 + (self.intelligence * 5) + (self.level * 2)
        
        # Adjust current mana proportionally
        if old_max_mana > 0:
            mana_percent = self.current_mana / old_max_mana
            self.current_mana = int(self.max_mana * mana_percent)
        else:
            self.current_mana = self.max_mana
        
        # Mana regen: 0.5 base + 0.1 per intelligence
        self.mana_regen = 0.5 + (self.intelligence * 0.1)
        
        # === STAMINA ===
        # Max stamina: 100 base + 5 per vitality + 2 per level
        old_max_stamina = self.max_stamina
        self.max_stamina = 100 + (self.vitality * 5) + (self.level * 2)
        
        # Adjust current stamina proportionally
        if old_max_stamina > 0:
            stamina_percent = self.current_stamina / old_max_stamina
            self.current_stamina = self.max_stamina * stamina_percent
        else:
            self.current_stamina = self.max_stamina
        
        # Stamina regen: 5.0 base + 0.2 per vitality
        self.stamina_regen = 5.0 + (self.vitality * 0.2)
        
        # === OFFENSE ===
        # Base damage: 10 + strength + level/2
        self.base_damage = 10 + self.strength + (self.level // 2)
        self.attack_damage = self.base_damage  # Modified by equipment
        
        # Attack speed: 1.0 base + 2% per dexterity point
        self.attack_speed = 1.0 + (self.dexterity * 0.02)
        
        # Critical chance: 5% base + 0.1% per dexterity
        self.critical_chance = 0.05 + (self.dexterity * 0.001)
        
        # === DEFENSE ===
        # Defense (flat reduction): strength * 0.5
        self.defense = self.strength * 0.5
        
        # Armor (% reduction): vitality * 0.3%
        self.armor = self.vitality * 0.003
        
        # Dodge chance: dexterity * 0.3%
        self.dodge_chance = self.dexterity * 0.003
        
        # Elemental resistance: intelligence * 0.2%
        self.elemental_resistance = self.intelligence * 0.002
        
        # === UTILITY ===
        # Movement speed: 1.0 base + 1% per dexterity point (capped at 1.5x)
        self.movement_speed = min(1.5, 1.0 + (self.dexterity * 0.01))
        
        # Carry weight: 100 base + 5 per strength
        self.carry_weight = 100 + (self.strength * 5)
        
        # Item rarity: 1.0 base + 1% per intelligence
        self.item_rarity = 1.0 + (self.intelligence * 0.01)
    
    def roll_critical(self):
        """Roll for a critical hit based on critical_chance"""
        return random.random() < self.critical_chance
    
    def take_damage(self, damage, damage_type='physical'):
        """
        Apply damage to player with defense calculations
        Returns actual damage taken
        """
        # Apply defense (flat reduction)
        damage = max(0, damage - self.defense)
        
        # Apply armor (percentage reduction for physical)
        if damage_type == 'physical':
            damage = damage * (1 - min(0.75, self.armor))  # Cap at 75% reduction
        elif damage_type in ['fire', 'ice', 'lightning', 'poison']:
            # Elemental damage uses elemental resistance
            damage = damage * (1 - min(0.75, self.elemental_resistance))
        
        # Round and apply
        actual_damage = int(damage)
        self.current_health = max(0, self.current_health - actual_damage)
        
        return actual_damage
    
    def heal(self, amount):
        """Heal the player, cannot exceed max health"""
        self.current_health = min(self.max_health, self.current_health + amount)
    
    def restore_mana(self, amount):
        """Restore mana, cannot exceed max mana"""
        self.current_mana = min(self.max_mana, self.current_mana + amount)
    
    def use_mana(self, amount):
        """
        Attempt to use mana for an ability
        Returns True if enough mana, False otherwise
        """
        if self.current_mana >= amount:
            self.current_mana -= amount
            return True
        return False
    
    def use_stamina(self, amount):
        """
        Attempt to use stamina for an action
        Returns True if enough stamina, False otherwise
        """
        if self.current_stamina >= amount:
            self.current_stamina -= amount
            # Reset regen delay
            self.stamina_regen_delay = self.stamina_regen_delay_max
            return True
        return False
    
    def restore_stamina(self, amount):
        """Restore stamina, cannot exceed max stamina"""
        self.current_stamina = min(self.max_stamina, self.current_stamina + amount)
    
    def update_stamina(self):
        """
        Update stamina regeneration
        Call this every frame (60 times per second)
        """
        # Handle regen delay
        if self.stamina_regen_delay > 0:
            self.stamina_regen_delay -= 1
            return
        
        # Regenerate stamina
        if self.current_stamina < self.max_stamina:
            # Regen per frame = regen_per_second / 60
            regen_this_frame = self.stamina_regen / 60.0
            self.restore_stamina(regen_this_frame)
    
    def is_exhausted(self):
        """Check if player is out of stamina"""
        return self.current_stamina <= 0
    
    def can_afford_stamina(self, amount):
        """Check if player has enough stamina for an action"""
        return self.current_stamina >= amount
        return False
    
    def update(self, delta_time):
        """Update regeneration (delta_time in seconds)"""
        # Health regeneration
        if self.current_health < self.max_health:
            self.current_health = min(self.max_health, 
                                     self.current_health + self.health_regen * delta_time)
        
        # Mana regeneration
        if self.current_mana < self.max_mana:
            self.current_mana = min(self.max_mana,
                                   self.current_mana + self.mana_regen * delta_time)
    
    def is_alive(self):
        """Check if player is still alive"""
        return self.current_health > 0
    
    def get_xp_progress_percent(self):
        """Get XP progress as percentage (0.0 to 1.0)"""
        if self.xp_to_next_level == 0:
            return 1.0
        return self.current_xp / self.xp_to_next_level
    
    def get_stat_summary(self):
        """Return a formatted summary of all stats (for UI display)"""
        return {
            'level': self.level,
            'xp': self.current_xp,
            'xp_needed': self.xp_to_next_level,
            'xp_percent': self.get_xp_progress_percent(),
            
            'strength': self.strength,
            'dexterity': self.dexterity,
            'intelligence': self.intelligence,
            'vitality': self.vitality,
            
            'health': f"{int(self.current_health)}/{self.max_health}",
            'mana': f"{int(self.current_mana)}/{self.max_mana}",
            
            'damage': f"{self.attack_damage:.1f}",
            'attack_speed': f"{self.attack_speed:.2f}x",
            'crit_chance': f"{self.critical_chance*100:.1f}%",
            'crit_multi': f"{self.critical_multiplier*100:.0f}%",
            
            'defense': f"{self.defense:.1f}",
            'armor': f"{self.armor*100:.1f}%",
            'dodge': f"{self.dodge_chance*100:.1f}%",
            'ele_res': f"{self.elemental_resistance*100:.1f}%",
            
            'movement_speed': f"{self.movement_speed:.2f}x",
            'carry_weight': f"{self.carry_weight}",
            
            'attribute_points': self.attribute_points,
            'skill_points': self.skill_points,
        }
    
    def save_data(self):
        """Return dictionary of stats for saving"""
        return {
            'level': self.level,
            'current_xp': self.current_xp,
            'strength': self.strength,
            'dexterity': self.dexterity,
            'intelligence': self.intelligence,
            'vitality': self.vitality,
            'current_health': self.current_health,
            'current_mana': self.current_mana,
            'attribute_points': self.attribute_points,
            'skill_points': self.skill_points,
        }
    
    def load_data(self, data):
        """Load stats from save data dictionary"""
        self.level = data.get('level', 1)
        self.current_xp = data.get('current_xp', 0)
        self.strength = data.get('strength', 10)
        self.dexterity = data.get('dexterity', 10)
        self.intelligence = data.get('intelligence', 10)
        self.vitality = data.get('vitality', 10)
        self.current_health = data.get('current_health', 100)
        self.current_mana = data.get('current_mana', 50)
        self.attribute_points = data.get('attribute_points', 0)
        self.skill_points = data.get('skill_points', 0)
        
        # Recalculate derived stats
        self.xp_to_next_level = self.calculate_xp_for_level(self.level + 1)
        self.recalculate_stats()
