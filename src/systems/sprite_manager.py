"""
Sprite Manager - Handles sprite loading and procedural generation
Generates fantasy-style character sprites when image files are not available
"""

import pygame
import math
import os

class SpriteManager:
    """Manages sprite assets and generates placeholder sprites"""
    
    def __init__(self):
        self.sprite_cache = {}
        self.assets_dir = "assets/sprites"
        
    def get_sprite(self, entity_type, state="idle", frame=0):
        """Get sprite for entity, generate if not found"""
        cache_key = f"{entity_type}_{state}_{frame}"
        
        if cache_key in self.sprite_cache:
            return self.sprite_cache[cache_key]
        
        # Try to load from file first
        sprite_path = os.path.join(self.assets_dir, entity_type, f"{state}_{frame}.png")
        if os.path.exists(sprite_path):
            sprite = pygame.image.load(sprite_path).convert_alpha()
            self.sprite_cache[cache_key] = sprite
            return sprite
        
        # Generate procedural sprite
        sprite = self._generate_sprite(entity_type, state, frame)
        self.sprite_cache[cache_key] = sprite
        return sprite
    
    def _generate_sprite(self, entity_type, state, frame):
        """Generate fantasy-style procedural sprite"""
        generators = {
            'player': self._generate_player_sprite,
            'shield_guardian': self._generate_shield_guardian_sprite,
            'berserker': self._generate_berserker_sprite,
            'fire_bat': self._generate_fire_bat_sprite,
            'hollow_warrior': self._generate_hollow_warrior_sprite,
            'dementor': self._generate_dementor_sprite,
            'shadow_archer': self._generate_shadow_archer_sprite,
        }
        
        generator = generators.get(entity_type, self._generate_default_sprite)
        return generator(state, frame)
    
    def _generate_player_sprite(self, state, frame):
        """Generate knight/warrior player sprite with attack animations"""
        size = (64, 64)
        surface = pygame.Surface(size, pygame.SRCALPHA)
        
        # Handle attack animations
        if state in ["attack_windup", "attack_active", "attack_recovery"]:
            return self._generate_player_attack_sprite(state, frame)
        
        # Animation offset
        bob = math.sin(frame * 0.5) * 2 if state == "walk" else 0
        
        # Color palette - Dark knight theme
        armor_dark = (40, 45, 55)
        armor_light = (70, 80, 95)
        cloth = (60, 40, 80)
        accent = (120, 140, 200)  # Blue glow
        
        center_x = 32
        base_y = 48
        
        # Legs
        pygame.draw.rect(surface, armor_dark, (center_x - 6, base_y - 15, 5, 12))
        pygame.draw.rect(surface, armor_dark, (center_x + 1, base_y - 15, 5, 12))
        # Boots
        pygame.draw.rect(surface, (30, 30, 30), (center_x - 7, base_y - 4, 6, 5))
        pygame.draw.rect(surface, (30, 30, 30), (center_x + 1, base_y - 4, 6, 5))
        
        # Torso - armored
        body_rect = pygame.Rect(center_x - 8, base_y - 30 + bob, 16, 18)
        pygame.draw.ellipse(surface, armor_light, body_rect)
        # Chest plate detail
        pygame.draw.rect(surface, armor_dark, (center_x - 6, base_y - 28 + bob, 12, 2))
        pygame.draw.rect(surface, armor_dark, (center_x - 6, base_y - 18 + bob, 12, 2))
        
        # Cape/cloak (behind)
        cape_points = [
            (center_x, base_y - 32 + bob),
            (center_x - 10, base_y - 28 + bob),
            (center_x - 12, base_y - 10),
            (center_x + 12, base_y - 10),
            (center_x + 10, base_y - 28 + bob)
        ]
        pygame.draw.polygon(surface, cloth, cape_points)
        
        # Arms
        # Left arm
        pygame.draw.rect(surface, armor_light, (center_x - 12, base_y - 28 + bob, 4, 14))
        # Right arm
        pygame.draw.rect(surface, armor_light, (center_x + 8, base_y - 28 + bob, 4, 14))
        
        # Shoulder pauldrons
        pygame.draw.circle(surface, armor_dark, (center_x - 10, base_y - 28 + bob), 5)
        pygame.draw.circle(surface, armor_dark, (center_x + 10, base_y - 28 + bob), 5)
        
        # Head - helmet
        head_rect = pygame.Rect(center_x - 7, base_y - 42 + bob, 14, 14)
        pygame.draw.ellipse(surface, armor_light, head_rect)
        # Visor slit
        pygame.draw.rect(surface, (20, 20, 20), (center_x - 4, base_y - 36 + bob, 8, 2))
        # Glowing eyes
        pygame.draw.circle(surface, accent, (center_x - 2, base_y - 36 + bob), 2)
        pygame.draw.circle(surface, accent, (center_x + 2, base_y - 36 + bob), 2)
        # Helmet crest
        crest_points = [
            (center_x - 3, base_y - 40 + bob),
            (center_x, base_y - 46 + bob),
            (center_x + 3, base_y - 40 + bob)
        ]
        pygame.draw.polygon(surface, accent, crest_points)
        
        return surface
    
    def _generate_player_attack_sprite(self, state, frame):
        """
        Generate smooth attack animation frames
        Hollow Knight style - Knight slashing with weapon trail
        """
        size = (96, 96)  # Larger canvas for weapon swing
        surface = pygame.Surface(size, pygame.SRCALPHA)
        
        # Color palette
        armor_dark = (40, 45, 55)
        armor_light = (70, 80, 95)
        cloth = (60, 40, 80)
        accent = (120, 140, 200)
        weapon_blade = (220, 230, 255)
        weapon_trail = (180, 200, 255, 128)
        
        center_x = 48
        base_y = 68
        
        # Determine attack progress (0.0 to 1.0)
        if state == "attack_windup":
            progress = 0.0 + (frame * 0.25)  # 0.0 to 0.3
        elif state == "attack_active":
            progress = 0.3 + (frame * 0.1)   # 0.3 to 0.7
        elif state == "attack_recovery":
            progress = 0.7 + (frame * 0.1)   # 0.7 to 1.0
        else:
            progress = 0.0
        
        progress = min(progress, 1.0)
        
        # Body lean and positioning based on attack progress
        if progress < 0.3:
            # Windup - leaning back
            lean = -4
            arm_angle = -60  # Back
        elif progress < 0.7:
            # Active - swinging forward
            swing_prog = (progress - 0.3) / 0.4
            lean = int(-4 + swing_prog * 12)
            arm_angle = -60 + swing_prog * 180  # -60° to 120°
        else:
            # Recovery - follow through
            recovery = (progress - 0.7) / 0.3
            lean = int(8 - recovery * 4)
            arm_angle = 120 + recovery * 20  # 120° to 140°
        
        # Cape flowing with motion (behind everything)
        cape_flow = int(progress * 12)
        cape_points = [
            (center_x + lean - 8, base_y - 32),
            (center_x + lean - 14 - cape_flow, base_y - 28),
            (center_x + lean - 16 - cape_flow, base_y - 10),
            (center_x + lean - 12 - cape_flow, base_y + 2),
            (center_x + lean - 4, base_y)
        ]
        pygame.draw.polygon(surface, cloth, cape_points)
        
        # Legs (grounded, stable stance)
        pygame.draw.rect(surface, armor_dark, (center_x - 6, base_y - 15, 5, 12))
        pygame.draw.rect(surface, armor_dark, (center_x + 1, base_y - 15, 5, 12))
        # Boots
        pygame.draw.rect(surface, (30, 30, 30), (center_x - 7, base_y - 4, 6, 5))
        pygame.draw.rect(surface, (30, 30, 30), (center_x + 1, base_y - 4, 6, 5))
        
        # Torso - armored (leaning)
        body_rect = pygame.Rect(center_x + lean - 8, base_y - 30, 16, 18)
        pygame.draw.ellipse(surface, armor_light, body_rect)
        pygame.draw.rect(surface, armor_dark, (center_x + lean - 6, base_y - 28, 12, 2))
        pygame.draw.rect(surface, armor_dark, (center_x + lean - 6, base_y - 18, 12, 2))
        
        # Arms - attacking arm extended
        # Calculate arm position based on swing
        arm_rad = math.radians(arm_angle)
        arm_length = 20
        arm_end_x = center_x + lean + int(math.cos(arm_rad) * arm_length)
        arm_end_y = base_y - 25 + int(math.sin(arm_rad) * arm_length)
        
        # Draw arm
        pygame.draw.line(surface, armor_light, 
                        (center_x + lean + 6, base_y - 26), 
                        (arm_end_x, arm_end_y), 5)
        # Shoulder
        pygame.draw.circle(surface, armor_dark, (center_x + lean + 10, base_y - 28), 5)
        
        # Other arm (static)
        pygame.draw.rect(surface, armor_light, (center_x + lean - 12, base_y - 28, 4, 14))
        pygame.draw.circle(surface, armor_dark, (center_x + lean - 10, base_y - 28), 5)
        
        # Head - helmet (turns slightly with swing)
        head_turn = int(lean * 0.5)
        head_rect = pygame.Rect(center_x + lean + head_turn - 7, base_y - 42, 14, 14)
        pygame.draw.ellipse(surface, armor_light, head_rect)
        # Visor
        pygame.draw.rect(surface, (20, 20, 20), (center_x + lean + head_turn - 4, base_y - 36, 8, 2))
        # Glowing eyes (brighter during active phase)
        eye_brightness = accent if progress < 0.5 else (255, 180, 100)
        pygame.draw.circle(surface, eye_brightness, (center_x + lean + head_turn - 2, base_y - 36), 2)
        pygame.draw.circle(surface, eye_brightness, (center_x + lean + head_turn + 2, base_y - 36), 2)
        # Helmet crest
        crest_points = [
            (center_x + lean + head_turn - 3, base_y - 40),
            (center_x + lean + head_turn, base_y - 46),
            (center_x + lean + head_turn + 3, base_y - 40)
        ]
        pygame.draw.polygon(surface, accent, crest_points)
        
        # Weapon - Nail/Sword extending from hand
        weapon_length = 28
        weapon_angle_rad = math.radians(arm_angle + 45)  # Weapon extends from arm
        weapon_start_x = arm_end_x
        weapon_start_y = arm_end_y
        weapon_end_x = weapon_start_x + int(math.cos(weapon_angle_rad) * weapon_length)
        weapon_end_y = weapon_start_y + int(math.sin(weapon_angle_rad) * weapon_length)
        
        # Weapon trail during active phase
        if 0.3 <= progress <= 0.7:
            # Draw motion blur trail
            trail_steps = 5
            for i in range(trail_steps):
                trail_progress = progress - (i * 0.05)
                if trail_progress < 0.3:
                    continue
                    
                trail_swing = (trail_progress - 0.3) / 0.4
                trail_angle = -60 + trail_swing * 180
                trail_rad = math.radians(trail_angle)
                trail_weapon_rad = math.radians(trail_angle + 45)
                
                trail_arm_x = center_x + lean + int(math.cos(trail_rad) * arm_length)
                trail_arm_y = base_y - 25 + int(math.sin(trail_rad) * arm_length)
                trail_end_x = trail_arm_x + int(math.cos(trail_weapon_rad) * weapon_length)
                trail_end_y = trail_arm_y + int(math.sin(trail_weapon_rad) * weapon_length)
                
                # Fading trail
                alpha = int(100 - (i * 15))
                trail_surf = pygame.Surface((4, 4), pygame.SRCALPHA)
                pygame.draw.circle(trail_surf, (*weapon_trail[:3], alpha), (2, 2), 2)
                surface.blit(trail_surf, (trail_end_x - 2, trail_end_y - 2))
        
        # Main weapon blade (thicker line for visibility)
        pygame.draw.line(surface, weapon_blade, 
                        (weapon_start_x, weapon_start_y),
                        (weapon_end_x, weapon_end_y), 4)
        # Blade edge highlight
        pygame.draw.line(surface, (255, 255, 255),
                        (weapon_start_x, weapon_start_y),
                        (weapon_end_x, weapon_end_y), 2)
        
        # Weapon tip glow during active
        if 0.3 <= progress <= 0.7:
            pygame.draw.circle(surface, (255, 255, 255, 200), (weapon_end_x, weapon_end_y), 6)
            pygame.draw.circle(surface, accent, (weapon_end_x, weapon_end_y), 4)
        
        return surface
    
    def _generate_shield_guardian_sprite(self, state, frame):
        """Generate heavily armored tank with large shield"""
        size = (80, 80)
        surface = pygame.Surface(size, pygame.SRCALPHA)
        
        # Colors - Heavy armor
        armor_primary = (180, 180, 200)  # Steel
        armor_dark = (100, 100, 120)
        shield_color = (150, 150, 170)
        shield_glow = (100, 150, 255) if state == "shield_bash" else (80, 120, 200)
        
        center_x = 40
        base_y = 65
        
        # Large shield (in front)
        shield_width = 24
        shield_height = 40
        shield_rect = pygame.Rect(center_x - shield_width//2, base_y - 50, shield_width, shield_height)
        pygame.draw.ellipse(surface, shield_color, shield_rect)
        # Shield boss (center)
        pygame.draw.circle(surface, shield_glow, (center_x, base_y - 30), 6)
        pygame.draw.circle(surface, (255, 255, 255), (center_x, base_y - 30), 3)
        # Shield border
        pygame.draw.ellipse(surface, armor_dark, shield_rect, 3)
        
        # Body (behind shield, partially visible)
        # Legs
        pygame.draw.rect(surface, armor_dark, (center_x - 8, base_y - 20, 6, 18))
        pygame.draw.rect(surface, armor_dark, (center_x + 2, base_y - 20, 6, 18))
        
        # Torso (bulky)
        body_rect = pygame.Rect(center_x - 12, base_y - 42, 24, 24)
        pygame.draw.ellipse(surface, armor_primary, body_rect)
        
        # Helmet (above shield)
        helmet_rect = pygame.Rect(center_x - 10, base_y - 58, 20, 18)
        pygame.draw.ellipse(surface, armor_primary, helmet_rect)
        # Visor
        pygame.draw.rect(surface, (30, 30, 40), (center_x - 6, base_y - 52, 12, 3))
        # Red glowing eyes
        pygame.draw.circle(surface, (255, 100, 100), (center_x - 3, base_y - 51), 2)
        pygame.draw.circle(surface, (255, 100, 100), (center_x + 3, base_y - 51), 2)
        
        # Shoulder plates (massive)
        pygame.draw.circle(surface, armor_dark, (center_x - 16, base_y - 42), 8)
        pygame.draw.circle(surface, armor_dark, (center_x + 16, base_y - 42), 8)
        
        # Weapon arm (holding shield)
        pygame.draw.rect(surface, armor_primary, (center_x - 18, base_y - 40, 6, 16))
        
        return surface
    
    def _generate_berserker_sprite(self, state, frame):
        """Generate wild berserker warrior"""
        size = (64, 72)
        surface = pygame.Surface(size, pygame.SRCALPHA)
        
        # Colors
        is_raged = (state == "rage")
        skin = (200, 150, 130)
        muscle = (180, 130, 110)
        cloth = (80, 60, 50)
        rage_glow = (255, 50, 50) if is_raged else (150, 100, 100)
        
        center_x = 32
        base_y = 60
        
        # Animation - aggressive lean forward
        lean = -5 if state in ["attacking", "rage"] else 0
        
        # Legs (muscular)
        pygame.draw.rect(surface, muscle, (center_x - 7, base_y - 18, 6, 16))
        pygame.draw.rect(surface, muscle, (center_x + 1, base_y - 18, 6, 16))
        # Torn pants
        pygame.draw.rect(surface, cloth, (center_x - 7, base_y - 18, 6, 10))
        pygame.draw.rect(surface, cloth, (center_x + 1, base_y - 18, 6, 10))
        
        # Torso (bare-chested, muscular)
        body_rect = pygame.Rect(center_x - 10 + lean, base_y - 40, 20, 24)
        pygame.draw.ellipse(surface, skin, body_rect)
        # Muscle definition
        pygame.draw.arc(surface, muscle, (center_x - 8 + lean, base_y - 38, 7, 12), 0, 3.14, 2)
        pygame.draw.arc(surface, muscle, (center_x + 1 + lean, base_y - 38, 7, 12), 0, 3.14, 2)
        
        # Arms (huge, muscular)
        # Left arm
        pygame.draw.rect(surface, skin, (center_x - 16 + lean, base_y - 38, 7, 18))
        pygame.draw.circle(surface, muscle, (center_x - 12 + lean, base_y - 32), 5)
        # Right arm
        pygame.draw.rect(surface, skin, (center_x + 9 + lean, base_y - 38, 7, 18))
        pygame.draw.circle(surface, muscle, (center_x + 12 + lean, base_y - 32), 5)
        
        # Head - wild, unkempt
        head_rect = pygame.Rect(center_x - 8 + lean, base_y - 52, 16, 16)
        pygame.draw.ellipse(surface, skin, head_rect)
        # Wild hair
        for i in range(5):
            hair_x = center_x - 6 + i * 3 + lean
            hair_points = [
                (hair_x, base_y - 52),
                (hair_x - 2, base_y - 58),
                (hair_x + 2, base_y - 54)
            ]
            pygame.draw.polygon(surface, (60, 40, 30), hair_points)
        
        # Face - aggressive
        # Eyes (rage glow)
        pygame.draw.circle(surface, rage_glow, (center_x - 3 + lean, base_y - 46), 3)
        pygame.draw.circle(surface, rage_glow, (center_x + 3 + lean, base_y - 46), 3)
        # Mouth (snarl)
        pygame.draw.line(surface, (100, 50, 50), (center_x - 4 + lean, base_y - 40), 
                        (center_x + 4 + lean, base_y - 40), 2)
        
        # Rage aura
        if is_raged:
            for ring in range(3):
                radius = 30 + ring * 8
                alpha = 60 - ring * 20
                rage_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(rage_surf, (*rage_glow, alpha), (radius, radius), radius, 3)
                surface.blit(rage_surf, (center_x - radius, base_y - 35 - radius))
        
        # Weapon (large axe)
        weapon_x = center_x + 12 + lean
        weapon_y = base_y - 30
        # Handle
        pygame.draw.rect(surface, (80, 50, 30), (weapon_x, weapon_y, 3, 20))
        # Axe head
        axe_points = [
            (weapon_x - 8, weapon_y + 5),
            (weapon_x + 10, weapon_y),
            (weapon_x + 10, weapon_y + 10),
            (weapon_x - 8, weapon_y + 15)
        ]
        pygame.draw.polygon(surface, (120, 120, 140), axe_points)
        pygame.draw.polygon(surface, (80, 80, 90), axe_points, 2)
        
        return surface
    
    def _generate_fire_bat_sprite(self, state, frame):
        """Generate small fire bat sprite"""
        size = (48, 48)
        surface = pygame.Surface(size, pygame.SRCALPHA)
        
        center_x = 24
        center_y = 24
        
        # Animation - wing flap
        wing_angle = math.sin(frame * 0.8) * 15
        
        # Colors - fire theme
        body_color = (160, 40, 20)
        fire_orange = (255, 140, 0)
        fire_yellow = (255, 200, 50)
        
        # Body
        body_rect = pygame.Rect(center_x - 8, center_y - 6, 16, 12)
        pygame.draw.ellipse(surface, body_color, body_rect)
        # Fire glow around body
        glow_rect = body_rect.inflate(4, 4)
        pygame.draw.ellipse(surface, fire_orange, glow_rect, 2)
        
        # Wings (bat-like, on fire)
        # Left wing
        left_wing_points = [
            (center_x - 8, center_y),
            (center_x - 20, center_y - wing_angle),
            (center_x - 18, center_y + 4),
            (center_x - 10, center_y + 2)
        ]
        pygame.draw.polygon(surface, (100, 30, 30), left_wing_points)
        pygame.draw.lines(surface, fire_orange, False, left_wing_points, 2)
        
        # Right wing
        right_wing_points = [
            (center_x + 8, center_y),
            (center_x + 20, center_y - wing_angle),
            (center_x + 18, center_y + 4),
            (center_x + 10, center_y + 2)
        ]
        pygame.draw.polygon(surface, (100, 30, 30), right_wing_points)
        pygame.draw.lines(surface, fire_orange, False, right_wing_points, 2)
        
        # Head
        pygame.draw.circle(surface, body_color, (center_x, center_y - 4), 5)
        # Ears (pointed)
        pygame.draw.polygon(surface, body_color, [
            (center_x - 5, center_y - 7),
            (center_x - 8, center_y - 12),
            (center_x - 3, center_y - 6)
        ])
        pygame.draw.polygon(surface, body_color, [
            (center_x + 5, center_y - 7),
            (center_x + 8, center_y - 12),
            (center_x + 3, center_y - 6)
        ])
        
        # Eyes (glowing)
        pygame.draw.circle(surface, fire_yellow, (center_x - 2, center_y - 4), 2)
        pygame.draw.circle(surface, fire_yellow, (center_x + 2, center_y - 4), 2)
        pygame.draw.circle(surface, (255, 255, 255), (center_x - 2, center_y - 4), 1)
        pygame.draw.circle(surface, (255, 255, 255), (center_x + 2, center_y - 4), 1)
        
        # Fire trail particles
        for i in range(3):
            particle_y = center_y + 6 + i * 4
            particle_size = 3 - i
            pygame.draw.circle(surface, fire_orange, (center_x, particle_y), particle_size)
        
        return surface
    
    def _generate_hollow_warrior_sprite(self, state, frame):
        """Generate hollow/undead warrior"""
        size = (56, 64)
        surface = pygame.Surface(size, pygame.SRCALPHA)
        
        # Colors - undead theme
        bone = (200, 190, 170)
        armor = (60, 60, 70)
        glow = (100, 255, 150)  # Ghostly green
        
        center_x = 28
        base_y = 56
        
        # Legs (skeletal)
        pygame.draw.rect(surface, bone, (center_x - 5, base_y - 16, 3, 14))
        pygame.draw.rect(surface, bone, (center_x + 2, base_y - 16, 3, 14))
        # Knee joints
        pygame.draw.circle(surface, bone, (center_x - 3, base_y - 8), 3)
        pygame.draw.circle(surface, bone, (center_x + 3, base_y - 8), 3)
        
        # Torso (armored ribcage)
        body_rect = pygame.Rect(center_x - 8, base_y - 34, 16, 20)
        pygame.draw.ellipse(surface, armor, body_rect)
        # Ribs (visible through armor)
        for i in range(4):
            rib_y = base_y - 32 + i * 4
            pygame.draw.line(surface, bone, (center_x - 6, rib_y), (center_x + 6, rib_y), 1)
        
        # Arms (skeletal with armor)
        # Left arm
        pygame.draw.rect(surface, bone, (center_x - 12, base_y - 32, 3, 16))
        pygame.draw.circle(surface, armor, (center_x - 10, base_y - 28), 4)
        # Right arm (sword arm)
        pygame.draw.rect(surface, bone, (center_x + 9, base_y - 32, 3, 16))
        pygame.draw.circle(surface, armor, (center_x + 10, base_y - 28), 4)
        
        # Head (skull)
        skull_rect = pygame.Rect(center_x - 7, base_y - 46, 14, 14)
        pygame.draw.ellipse(surface, bone, skull_rect)
        # Eye sockets (glowing)
        pygame.draw.circle(surface, (30, 30, 30), (center_x - 3, base_y - 42), 3)
        pygame.draw.circle(surface, (30, 30, 30), (center_x + 3, base_y - 42), 3)
        pygame.draw.circle(surface, glow, (center_x - 3, base_y - 42), 2)
        pygame.draw.circle(surface, glow, (center_x + 3, base_y - 42), 2)
        # Jaw
        pygame.draw.rect(surface, bone, (center_x - 4, base_y - 36, 8, 4))
        
        # Helmet (broken)
        helmet_points = [
            (center_x - 8, base_y - 46),
            (center_x, base_y - 50),
            (center_x + 8, base_y - 46)
        ]
        pygame.draw.polygon(surface, armor, helmet_points)
        
        # Sword (rusty)
        sword_x = center_x + 12
        sword_y = base_y - 20
        pygame.draw.rect(surface, (100, 80, 70), (sword_x, sword_y, 2, 16))  # Blade
        pygame.draw.rect(surface, (80, 60, 50), (sword_x - 2, sword_y + 16, 6, 3))  # Guard
        pygame.draw.rect(surface, (60, 50, 40), (sword_x, sword_y + 19, 2, 4))  # Handle
        
        return surface
    
    def _generate_dementor_sprite(self, state, frame):
        """Generate floating dementor/ghost sprite"""
        size = (56, 72)
        surface = pygame.Surface(size, pygame.SRCALPHA)
        
        # Float animation
        float_offset = math.sin(frame * 0.3) * 4
        
        # Colors - dark ethereal
        cloak_dark = (20, 20, 40)
        cloak_edge = (40, 40, 80)
        soul_glow = (150, 180, 255)
        
        center_x = 28
        base_y = 60 + float_offset
        
        # Flowing cloak/robe
        cloak_points = [
            (center_x, base_y - 50),
            (center_x - 16, base_y - 40),
            (center_x - 18, base_y - 10),
            (center_x - 12, base_y),
            (center_x + 12, base_y),
            (center_x + 18, base_y - 10),
            (center_x + 16, base_y - 40)
        ]
        pygame.draw.polygon(surface, cloak_dark, cloak_points)
        pygame.draw.lines(surface, cloak_edge, True, cloak_points, 2)
        
        # Tattered edges
        for i in range(0, 10, 2):
            tatter_x = center_x - 12 + i * 2.4
            pygame.draw.line(surface, cloak_dark, 
                           (tatter_x, base_y), 
                           (tatter_x + 2, base_y + 8), 2)
        
        # Hood (dark void face)
        hood_rect = pygame.Rect(center_x - 10, base_y - 54, 20, 18)
        pygame.draw.ellipse(surface, cloak_dark, hood_rect)
        # Face void (darker)
        face_rect = pygame.Rect(center_x - 8, base_y - 50, 16, 14)
        pygame.draw.ellipse(surface, (10, 10, 20), face_rect)
        
        # Glowing eyes (soul energy)
        pygame.draw.circle(surface, soul_glow, (center_x - 4, base_y - 46), 3)
        pygame.draw.circle(surface, soul_glow, (center_x + 4, base_y - 46), 3)
        pygame.draw.circle(surface, (255, 255, 255), (center_x - 4, base_y - 46), 1)
        pygame.draw.circle(surface, (255, 255, 255), (center_x + 4, base_y - 46), 1)
        
        # Skeletal hands
        # Left hand
        pygame.draw.rect(surface, (180, 180, 170), (center_x - 16, base_y - 30, 3, 8))
        for finger in range(3):
            pygame.draw.line(surface, (180, 180, 170),
                           (center_x - 16 + finger, base_y - 22),
                           (center_x - 16 + finger, base_y - 18), 1)
        # Right hand
        pygame.draw.rect(surface, (180, 180, 170), (center_x + 13, base_y - 30, 3, 8))
        for finger in range(3):
            pygame.draw.line(surface, (180, 180, 170),
                           (center_x + 13 + finger, base_y - 22),
                           (center_x + 13 + finger, base_y - 18), 1)
        
        # Soul drain effect (if attacking)
        if state == "attacking":
            for ring in range(3):
                radius = 20 + ring * 6
                alpha = 80 - ring * 20
                soul_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(soul_surf, (*soul_glow, alpha), (radius, radius), radius, 2)
                surface.blit(soul_surf, (center_x - radius, base_y - 45 - radius))
        
        return surface
    
    def _generate_shadow_archer_sprite(self, state, frame):
        """Generate nimble archer sprite"""
        size = (56, 64)
        surface = pygame.Surface(size, pygame.SRCALPHA)
        
        # Colors - rogue/ranger theme
        leather = (80, 60, 40)
        cloth_dark = (40, 50, 40)
        skin = (180, 140, 120)
        wood = (100, 70, 40)
        
        center_x = 28
        base_y = 56
        
        # Stance - archer pose
        lean = -3 if state == "attacking" else 0
        
        # Legs (crouched stance)
        pygame.draw.rect(surface, cloth_dark, (center_x - 5 + lean, base_y - 16, 4, 14))
        pygame.draw.rect(surface, cloth_dark, (center_x + 1 + lean, base_y - 16, 4, 14))
        # Boots
        pygame.draw.rect(surface, leather, (center_x - 6 + lean, base_y - 3, 5, 4))
        pygame.draw.rect(surface, leather, (center_x + 1 + lean, base_y - 3, 5, 4))
        
        # Torso (light armor)
        body_rect = pygame.Rect(center_x - 7 + lean, base_y - 34, 14, 20)
        pygame.draw.ellipse(surface, leather, body_rect)
        # Leather straps
        pygame.draw.line(surface, (60, 40, 20), 
                        (center_x - 6 + lean, base_y - 32),
                        (center_x + 6 + lean, base_y - 28), 2)
        pygame.draw.line(surface, (60, 40, 20),
                        (center_x - 6 + lean, base_y - 28),
                        (center_x + 6 + lean, base_y - 32), 2)
        
        # Arms
        # Left arm (bow holding)
        pygame.draw.rect(surface, skin, (center_x - 12 + lean, base_y - 32, 3, 12))
        # Right arm (drawing)
        pygame.draw.rect(surface, skin, (center_x + 9 + lean, base_y - 32, 3, 12))
        
        # Head (hooded)
        head_rect = pygame.Rect(center_x - 6 + lean, base_y - 46, 12, 14)
        pygame.draw.ellipse(surface, skin, head_rect)
        # Hood
        hood_points = [
            (center_x - 8 + lean, base_y - 46),
            (center_x + lean, base_y - 52),
            (center_x + 8 + lean, base_y - 46),
            (center_x + 6 + lean, base_y - 42),
            (center_x - 6 + lean, base_y - 42)
        ]
        pygame.draw.polygon(surface, cloth_dark, hood_points)
        
        # Eyes (focused)
        pygame.draw.circle(surface, (255, 200, 100), (center_x - 2 + lean, base_y - 42), 2)
        pygame.draw.circle(surface, (255, 200, 100), (center_x + 2 + lean, base_y - 42), 2)
        
        # Bow (in front)
        bow_x = center_x - 14 + lean
        bow_top = base_y - 38
        bow_bottom = base_y - 18
        # Bow limbs (curved)
        pygame.draw.arc(surface, wood, (bow_x - 4, bow_top, 8, 20), -1.57, 1.57, 3)
        # Bow string
        if state == "attacking":
            # Drawn back
            pygame.draw.line(surface, (220, 220, 200),
                           (bow_x, bow_top), (center_x + 8 + lean, base_y - 28), 1)
            pygame.draw.line(surface, (220, 220, 200),
                           (bow_x, bow_bottom), (center_x + 8 + lean, base_y - 28), 1)
            # Arrow
            pygame.draw.line(surface, wood,
                           (center_x + 8 + lean, base_y - 28),
                           (bow_x - 10, base_y - 28), 2)
        else:
            # Relaxed
            pygame.draw.line(surface, (220, 220, 200),
                           (bow_x, bow_top), (bow_x, bow_bottom), 1)
        
        # Quiver on back
        pygame.draw.rect(surface, leather, (center_x + 4 + lean, base_y - 38, 4, 12))
        # Arrow fletching visible
        for i in range(3):
            arrow_y = base_y - 36 + i * 3
            pygame.draw.line(surface, (200, 50, 50), 
                           (center_x + 5 + lean, arrow_y),
                           (center_x + 7 + lean, arrow_y - 2), 1)
        
        return surface
    
    def _generate_default_sprite(self, state, frame):
        """Default sprite for unknown entities"""
        size = (48, 48)
        surface = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(surface, (100, 100, 100), (12, 12, 24, 24))
        pygame.draw.circle(surface, (150, 150, 150), (24, 24), 8)
        return surface
