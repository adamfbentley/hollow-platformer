"""
Player Entity
Advanced player character with Hollow Knight-inspired physics
Features: acceleration, variable jump, wall slide, dash, double jump, RPG stats, equipment rendering
"""

import pygame
import math
from src.core.constants import (
    FPS, PLAYER_ACCELERATION, PLAYER_MAX_SPEED, PLAYER_FRICTION,
    GRAVITY, JUMP_STRENGTH, MAX_FALL_SPEED, COYOTE_TIME, JUMP_BUFFER_TIME,
    MAX_JUMP_HOLD_TIME, JUMP_HOLD_BOOST, WALL_SLIDE_SPEED,
    WALL_JUMP_X, WALL_JUMP_Y, DASH_SPEED, DASH_DURATION,
    LANDING_IMPACT_THRESHOLD, STONE_LIGHT, WORLD_WIDTH, WORLD_HEIGHT
)
from src.world.particles import Particle
from src.systems.player_stats import PlayerStats
from src.systems.inventory import Inventory
from src.systems.hollow_knight_combat import HollowKnightCombat
from src.systems.weapon import WeaponManager
from src.systems.enhanced_movement import EnhancedMovementController
from src.systems.combat_feel import CombatFeelEnhancer


class Player(pygame.sprite.Sprite):
    """
    Advanced player character with Hollow Knight-inspired physics
    Features: acceleration, variable jump, wall slide, dash, double jump
    """
    def __init__(self, x, y):
        super().__init__()
        # Create player sprite with dark knight appearance
        self.create_player_sprite()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Physics properties
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration_x = 0
        
        # State flags
        self.on_ground = False
        self.on_wall = False
        self.wall_side = 0  # -1 for left wall, 1 for right wall
        self.facing_right = True
        
        # Jump mechanics
        self.jumps_available = 2  # Double jump
        self.max_jumps = 2
        self.jump_held = False
        self.jump_hold_timer = 0
        self.coyote_timer = 0
        self.jump_buffer_timer = 0
        
        # Dash mechanics
        self.can_dash = True
        self.is_dashing = False
        self.dash_timer = 0
        self.dash_direction = 0
        self.dash_cooldown = 0
        
        # Animation state
        self.animation_state = "idle"
        self.animation_frame = 0
        self.animation_timer = 0
        
        # RPG Stats System
        self.stats = PlayerStats()
        
        # Inventory System
        self.inventory = Inventory(grid_size=40)
        
        # Weapon System
        self.weapon_manager = WeaponManager()
        self.current_weapon = self.weapon_manager.get_current_weapon()
        
        # Combat System - Hollow Knight style
        self.combat = HollowKnightCombat(self)
        
        # Enhanced Movement System (Celeste-style)
        self.movement_controller = EnhancedMovementController(self)
        
        # Combat Feel Enhancer (hit pause, screen shake)
        self.combat_feel = CombatFeelEnhancer()
        
        # Sprite manager (set from outside)
        self.sprite_manager = None
        
        # Equipment visuals (stores visual data of equipped items)
        self.equipment_visuals = {
            "weapon": None,
            "armor": None,
            "helm": None,
            "boots": None,
            "amulet": None,
            "ring1": None,
            "ring2": None
        }
        
        # Sound Manager reference (set by game)
        self.sound_manager = None
        
        # Player legacy stats (keeping for compatibility)
        self.score = 0
        self.lives = 3
        
        # Invincibility frames
        self.invincible = False
        self.invincible_timer = 0
        
        # Particle system reference (set by game)
        self.particle_group = None
        
    def spawn_particles(self, particle_type, count, color=None):
        """Spawn visual particles for effects"""
        if not self.particle_group:
            return
        
        import random
        if color is None:
            color = STONE_LIGHT
        
        for _ in range(count):
            if particle_type == 'land':
                # Landing dust
                offset_x = random.randint(-15, 15)
                Particle(
                    self.rect.centerx + offset_x,
                    self.rect.bottom - 5,
                    random.uniform(-2, 2),
                    random.uniform(-3, -1),
                    color,
                    lifetime=20,
                    size=random.randint(2, 4),
                    particle_type='dust'
                ).add(self.particle_group)
            
            elif particle_type == 'dash':
                # Dash trail
                offset_y = random.randint(-10, 10)
                Particle(
                    self.rect.centerx,
                    self.rect.centery + offset_y,
                    random.uniform(-1, 1),
                    random.uniform(-0.5, 0.5),
                    (100, 200, 255),
                    lifetime=15,
                    size=random.randint(3, 6),
                    particle_type='trail'
                ).add(self.particle_group)
            
            elif particle_type == 'wall_slide':
                # Wall sliding sparks
                offset_y = random.randint(-5, 5)
                spark_x = self.rect.right if self.wall_side > 0 else self.rect.left
                Particle(
                    spark_x,
                    self.rect.centery + offset_y,
                    random.uniform(-2, 0) if self.wall_side > 0 else random.uniform(0, 2),
                    random.uniform(-1, 1),
                    (255, 200, 100),
                    lifetime=12,
                    size=2,
                    particle_type='spark'
                ).add(self.particle_group)
            
            elif particle_type == 'jump':
                # Jump dust
                offset_x = random.randint(-12, 12)
                Particle(
                    self.rect.centerx + offset_x,
                    self.rect.bottom - 3,
                    random.uniform(-1.5, 1.5),
                    random.uniform(-2, -0.5),
                    STONE_LIGHT,
                    lifetime=15,
                    size=random.randint(2, 3),
                    particle_type='dust'
                ).add(self.particle_group)
        
    def create_player_sprite(self):
        """Draw a nude humanoid base character with higher resolution"""
        # Increased size for better resolution (doubled from 48x56)
        self.base_size = (96, 112)
        self.image = pygame.Surface(self.base_size, pygame.SRCALPHA)
        self.draw_nude_humanoid()
        
        # Animation frames storage
        self.animation_frames = {
            'idle': [],
            'walk': [],
            'jump': [],
            'fall': [],
            'wall_slide': [],
            'dash': [],
            'attack': []
        }
        self.create_animation_frames()
    
    def draw_nude_humanoid(self):
        """Draw basic nude humanoid base (no armor) - 2x scale for better resolution"""
        self.image.fill((0, 0, 0, 0))
        
        # Scale factor for all coordinates
        s = 2
        
        # Skin tones
        skin_shadow = (120, 90, 70)
        skin_base = (160, 120, 95)
        skin_light = (185, 145, 115)
        hair_dark = (40, 30, 25)
        eye_white = (240, 240, 240)
        eye_pupil = (60, 80, 100)
        
        # Back leg
        pygame.draw.ellipse(self.image, skin_shadow, (18*s, 36*s, 7*s, 14*s))  # Thigh
        pygame.draw.ellipse(self.image, skin_shadow, (17*s, 44*s, 5*s, 10*s))  # Calf
        pygame.draw.ellipse(self.image, skin_base, (16*s, 52*s, 7*s, 4*s))  # Foot
        
        # Back arm
        pygame.draw.ellipse(self.image, skin_shadow, (17*s, 22*s, 5*s, 10*s))  # Upper arm
        pygame.draw.ellipse(self.image, skin_shadow, (15*s, 28*s, 5*s, 9*s))  # Forearm
        pygame.draw.ellipse(self.image, skin_base, (14*s, 35*s, 4*s, 3*s))  # Hand
        
        # Torso (nude upper body)
        pygame.draw.ellipse(self.image, skin_base, (19*s, 18*s, 14*s, 18*s))
        # Muscle definition
        pygame.draw.line(self.image, skin_light, (26*s, 20*s), (26*s, 32*s), 2)  # Center line
        pygame.draw.arc(self.image, skin_light, (21*s, 20*s, 10*s, 8*s), 4.5, 6.3, 2)  # Chest
        
        # Front leg
        pygame.draw.ellipse(self.image, skin_base, (25*s, 36*s, 7*s, 14*s))  # Thigh
        pygame.draw.ellipse(self.image, skin_base, (26*s, 44*s, 5*s, 10*s))  # Calf
        pygame.draw.ellipse(self.image, skin_light, (25*s, 52*s, 7*s, 4*s))  # Foot
        
        # Front arm
        pygame.draw.ellipse(self.image, skin_base, (28*s, 22*s, 5*s, 10*s))  # Upper arm
        pygame.draw.ellipse(self.image, skin_base, (30*s, 28*s, 5*s, 9*s))  # Forearm
        pygame.draw.ellipse(self.image, skin_light, (31*s, 35*s, 4*s, 3*s))  # Hand
        
        # Head (oval shape)
        pygame.draw.ellipse(self.image, skin_base, (25*s, 8*s, 13*s, 14*s))
        pygame.draw.ellipse(self.image, skin_light, (26*s, 9*s, 11*s, 12*s))
        
        # Hair
        hair_points = [(26*s, 10*s), (24*s, 8*s), (22*s, 7*s), (20*s, 7*s), (18*s, 8*s), (17*s, 10*s)]
        pygame.draw.lines(self.image, hair_dark, False, hair_points, 4)
        pygame.draw.lines(self.image, hair_dark, False, hair_points, 3)
        
        # Eye
        pygame.draw.ellipse(self.image, eye_white, (31*s, 12*s, 4*s, 3*s))
        pygame.draw.circle(self.image, eye_pupil, (33*s, 13*s), 2)
        
        # Nose and mouth hints
        pygame.draw.line(self.image, skin_shadow, (35, 14), (35, 16), 1)
        pygame.draw.line(self.image, skin_shadow, (34, 17), (36, 17), 1)
    
    def create_animation_frames(self):
        """Pre-render animation frames with dynamic limb movement"""
        # Idle animation (4 frames - breathing)
        for i in range(4):
            self.animation_frames['idle'].append(self.draw_frame_idle(i))
        
        # Walk animation (6 frames - full walk cycle)
        for i in range(6):
            self.animation_frames['walk'].append(self.draw_frame_walk(i))
        
        # Jump animation (2 frames)
        self.animation_frames['jump'].append(self.draw_frame_jump(True))
        self.animation_frames['jump'].append(self.draw_frame_jump(False))
        
        # Fall animation (2 frames)
        self.animation_frames['fall'].append(self.draw_frame_fall(True))
        self.animation_frames['fall'].append(self.draw_frame_fall(False))
        
        # Dash animation (3 frames - motion blur effect)
        for i in range(3):
            self.animation_frames['dash'].append(self.draw_frame_dash(i))
        
        # Wall slide (2 frames)
        for i in range(2):
            self.animation_frames['wall_slide'].append(self.draw_frame_wall_slide(i))
        
        # Attack animation - generated dynamically based on aim angle
        # We store empty list and generate frames on-the-fly in get_current_frame()
        self.animation_frames['attack'] = []
    
    def draw_frame_idle(self, frame):
        """Draw idle animation frame with subtle breathing"""
        surface = pygame.Surface(self.base_size, pygame.SRCALPHA)
        s = 2  # Scale factor
        
        # Breathing offset (subtle bob)
        breath = math.sin(frame * math.pi / 2) * 1
        
        # Dark fantasy color palette
        skin_shadow = (100, 80, 65)
        skin_base = (130, 105, 85)
        skin_light = (150, 125, 100)
        armor_dark = (25, 25, 30)
        armor_base = (40, 40, 50)
        armor_highlight = (60, 60, 75)
        cape_dark = (20, 15, 25)
        hair_dark = (30, 25, 20)
        eye_glow = (80, 120, 180)
        
        # Cape (behind body)
        cape_points = [
            (26*s, (18+breath)*s), (22*s, (20+breath)*s), (18*s, (28+breath)*s),
            (16*s, (42+breath)*s), (20*s, (52+breath)*s), (26*s, (54+breath)*s),
            (32*s, (54+breath)*s), (38*s, (52+breath)*s), (42*s, (42+breath)*s),
            (40*s, (28+breath)*s), (36*s, (20+breath)*s), (32*s, (18+breath)*s)
        ]
        pygame.draw.polygon(surface, cape_dark, cape_points)
        
        # Back arm (left, relaxed at side)
        self.draw_limb(surface, (17*s, (24+breath)*s), (15*s, (32+breath)*s), 3*s, armor_dark)
        self.draw_limb(surface, (15*s, (32+breath)*s), (16*s, (38+breath)*s), 2*s, skin_shadow)
        
        # Back leg (left)
        self.draw_limb(surface, (25*s, (38+breath)*s), (24*s, (48+breath)*s), 4*s, armor_dark)
        self.draw_limb(surface, (24*s, (48+breath)*s), (23*s, (54+breath)*s), 3*s, armor_base)
        
        # Torso (armored)
        pygame.draw.ellipse(surface, armor_base, (19*s, (18+breath)*s, 14*s, 20*s))
        # Armor plates
        pygame.draw.ellipse(surface, armor_highlight, (21*s, (20+breath)*s, 10*s, 6*s))
        pygame.draw.line(surface, armor_dark, (26*s, (22+breath)*s), (26*s, (34+breath)*s), 2)
        
        # Front leg (right, slightly forward)
        self.draw_limb(surface, (27*s, (38+breath)*s), (28*s, (48+breath)*s), 4*s, armor_dark)
        self.draw_limb(surface, (28*s, (48+breath)*s), (27*s, (54+breath)*s), 3*s, armor_base)
        
        # Front arm (right, hand on sword hilt)
        self.draw_limb(surface, (33*s, (24+breath)*s), (35*s, (30+breath)*s), 3*s, armor_dark)
        self.draw_limb(surface, (35*s, (30+breath)*s), (36*s, (36+breath)*s), 2*s, skin_base)
        
        # Head with helm
        pygame.draw.ellipse(surface, armor_dark, (23*s, (8+breath)*s, 14*s, 14*s))
        pygame.draw.ellipse(surface, (15, 15, 20), (25*s, (12+breath)*s, 10*s, 8*s))  # Face opening
        
        # Glowing eyes
        pygame.draw.circle(surface, eye_glow, (28*s, int((15+breath)*s)), 2)
        pygame.draw.circle(surface, eye_glow, (32*s, int((15+breath)*s)), 2)
        
        # Hair peeking out
        for i in range(3):
            pygame.draw.line(surface, hair_dark, (24*s+i*2, (10+breath)*s), (23*s+i*2, (8+breath)*s), 2)
        
        return surface
    
    def draw_frame_walk(self, frame):
        """Draw walking animation with leg and arm swing"""
        surface = pygame.Surface(self.base_size, pygame.SRCALPHA)
        s = 2
        
        # Walking cycle positions
        progress = frame / 6.0
        leg_swing = math.sin(progress * math.pi * 2) * 6
        arm_swing = math.cos(progress * math.pi * 2) * 4
        bob = abs(math.sin(progress * math.pi * 2)) * 2
        
        # Colors
        skin_shadow = (100, 80, 65)
        skin_base = (130, 105, 85)
        armor_dark = (25, 25, 30)
        armor_base = (40, 40, 50)
        armor_highlight = (60, 60, 75)
        cape_dark = (20, 15, 25)
        eye_glow = (80, 120, 180)
        hair_dark = (30, 25, 20)
        
        # Cape flowing with movement
        cape_sway = arm_swing * 0.5
        cape_points = [
            (26*s, (18-bob)*s), (22*s+cape_sway, (22-bob)*s), (18*s+cape_sway, (30-bob)*s),
            (16*s+cape_sway, (44-bob)*s), (22*s, (52-bob)*s), (26*s, (54-bob)*s),
            (30*s, (54-bob)*s), (36*s, (52-bob)*s), (42*s-cape_sway, (44-bob)*s),
            (40*s-cape_sway, (30-bob)*s), (36*s-cape_sway, (22-bob)*s), (32*s, (18-bob)*s)
        ]
        pygame.draw.polygon(surface, cape_dark, cape_points)
        
        # Back arm (swings opposite to front leg)
        back_arm_y = 30 - arm_swing
        self.draw_limb(surface, (17*s, (24-bob)*s), (14*s, back_arm_y*s), 3*s, armor_dark)
        self.draw_limb(surface, (14*s, back_arm_y*s), (13*s, (back_arm_y+6)*s), 2*s, skin_shadow)
        
        # Back leg (left, swings backward)
        back_leg_angle = -leg_swing
        self.draw_limb(surface, (25*s, (38-bob)*s), (23*s, (48+back_leg_angle-bob)*s), 4*s, armor_dark)
        self.draw_limb(surface, (23*s, (48+back_leg_angle-bob)*s), (22*s, (54-bob)*s), 3*s, armor_base)
        
        # Torso
        pygame.draw.ellipse(surface, armor_base, (19*s, (18-bob)*s, 14*s, 20*s))
        pygame.draw.ellipse(surface, armor_highlight, (21*s, (20-bob)*s, 10*s, 6*s))
        pygame.draw.line(surface, armor_dark, (26*s, (22-bob)*s), (26*s, (34-bob)*s), 2)
        
        # Front leg (right, swings forward)
        front_leg_angle = leg_swing
        self.draw_limb(surface, (27*s, (38-bob)*s), (29*s, (48+front_leg_angle-bob)*s), 4*s, armor_dark)
        self.draw_limb(surface, (29*s, (48+front_leg_angle-bob)*s), (28*s, (54-bob)*s), 3*s, armor_base)
        
        # Front arm (swings with back leg)
        front_arm_y = 30 + arm_swing
        self.draw_limb(surface, (33*s, (24-bob)*s), (36*s, front_arm_y*s), 3*s, armor_dark)
        self.draw_limb(surface, (36*s, front_arm_y*s), (37*s, (front_arm_y+6)*s), 2*s, skin_base)
        
        # Head with helm
        pygame.draw.ellipse(surface, armor_dark, (23*s, (8-bob)*s, 14*s, 14*s))
        pygame.draw.ellipse(surface, (15, 15, 20), (25*s, (12-bob)*s, 10*s, 8*s))
        pygame.draw.circle(surface, eye_glow, (28*s, int((15-bob)*s)), 2)
        pygame.draw.circle(surface, eye_glow, (32*s, int((15-bob)*s)), 2)
        
        # Hair
        for i in range(3):
            pygame.draw.line(surface, hair_dark, (24*s+i*2, (10-bob)*s), (23*s+i*2, (8-bob)*s), 2)
        
        return surface
    
    def draw_frame_jump(self, is_rising):
        """Draw jump animation"""
        surface = pygame.Surface(self.base_size, pygame.SRCALPHA)
        s = 2
        
        # Colors
        armor_dark = (25, 25, 30)
        armor_base = (40, 40, 50)
        armor_highlight = (60, 60, 75)
        cape_dark = (20, 15, 25)
        skin_base = (130, 105, 85)
        eye_glow = (80, 120, 180)
        hair_dark = (30, 25, 20)
        
        y_offset = -2 if is_rising else 0
        
        # Cape flowing upward
        cape_points = [
            (26*s, (16+y_offset)*s), (20*s, (14+y_offset)*s), (14*s, (16+y_offset)*s),
            (12*s, (24+y_offset)*s), (16*s, (32+y_offset)*s), (26*s, (36+y_offset)*s),
            (36*s, (32+y_offset)*s), (40*s, (24+y_offset)*s), (38*s, (16+y_offset)*s),
            (32*s, (14+y_offset)*s)
        ]
        pygame.draw.polygon(surface, cape_dark, cape_points)
        
        # Arms raised
        self.draw_limb(surface, (16*s, (24+y_offset)*s), (12*s, (18+y_offset)*s), 3*s, armor_dark)
        self.draw_limb(surface, (34*s, (24+y_offset)*s), (38*s, (18+y_offset)*s), 3*s, armor_dark)
        
        # Legs bent/extended
        if is_rising:
            # Legs bent upward
            self.draw_limb(surface, (24*s, (38+y_offset)*s), (22*s, (44+y_offset)*s), 4*s, armor_dark)
            self.draw_limb(surface, (28*s, (38+y_offset)*s), (30*s, (44+y_offset)*s), 4*s, armor_dark)
        else:
            # Legs extending
            self.draw_limb(surface, (24*s, (38+y_offset)*s), (20*s, (50+y_offset)*s), 4*s, armor_dark)
            self.draw_limb(surface, (28*s, (38+y_offset)*s), (32*s, (50+y_offset)*s), 4*s, armor_dark)
        
        # Torso
        pygame.draw.ellipse(surface, armor_base, (19*s, (18+y_offset)*s, 14*s, 20*s))
        pygame.draw.ellipse(surface, armor_highlight, (21*s, (20+y_offset)*s, 10*s, 6*s))
        
        # Head
        pygame.draw.ellipse(surface, armor_dark, (23*s, (8+y_offset)*s, 14*s, 14*s))
        pygame.draw.ellipse(surface, (15, 15, 20), (25*s, (12+y_offset)*s, 10*s, 8*s))
        pygame.draw.circle(surface, eye_glow, (28*s, int((15+y_offset)*s)), 2)
        pygame.draw.circle(surface, eye_glow, (32*s, int((15+y_offset)*s)), 2)
        
        return surface
    
    def draw_frame_fall(self, early):
        """Draw falling animation"""
        surface = pygame.Surface(self.base_size, pygame.SRCALPHA)
        s = 2
        
        # Colors
        armor_dark = (25, 25, 30)
        armor_base = (40, 40, 50)
        cape_dark = (20, 15, 25)
        skin_base = (130, 105, 85)
        eye_glow = (80, 120, 180)
        
        y_offset = 2 if not early else 0
        
        # Cape billowing upward dramatically
        cape_points = [
            (26*s, (16+y_offset)*s), (18*s, (10+y_offset)*s), (10*s, (12+y_offset)*s),
            (8*s, (20+y_offset)*s), (14*s, (28+y_offset)*s), (26*s, (32+y_offset)*s),
            (38*s, (28+y_offset)*s), (44*s, (20+y_offset)*s), (42*s, (12+y_offset)*s),
            (34*s, (10+y_offset)*s)
        ]
        pygame.draw.polygon(surface, cape_dark, cape_points)
        
        # Arms windmilling
        angle = -20 if early else 20
        self.draw_limb(surface, (16*s, (24+y_offset)*s), (10*s, (22+angle+y_offset)*s), 3*s, armor_dark)
        self.draw_limb(surface, (34*s, (24+y_offset)*s), (40*s, (22-angle+y_offset)*s), 3*s, armor_dark)
        
        # Legs kicking
        self.draw_limb(surface, (24*s, (38+y_offset)*s), (18*s, (48+y_offset)*s), 4*s, armor_dark)
        self.draw_limb(surface, (28*s, (38+y_offset)*s), (34*s, (48+y_offset)*s), 4*s, armor_dark)
        
        # Torso
        pygame.draw.ellipse(surface, armor_base, (19*s, (18+y_offset)*s, 14*s, 20*s))
        
        # Head
        pygame.draw.ellipse(surface, armor_dark, (23*s, (8+y_offset)*s, 14*s, 14*s))
        pygame.draw.ellipse(surface, (15, 15, 20), (25*s, (12+y_offset)*s, 10*s, 8*s))
        pygame.draw.circle(surface, eye_glow, (28*s, int((15+y_offset)*s)), 2)
        pygame.draw.circle(surface, eye_glow, (32*s, int((15+y_offset)*s)), 2)
        
        return surface
    
    def draw_frame_dash(self, frame):
        """Draw dash animation with motion blur"""
        surface = pygame.Surface(self.base_size, pygame.SRCALPHA)
        s = 2
        
        # Colors with transparency for trail effect
        alpha = 255 - (frame * 60)
        armor_base = (40, 40, 50, alpha)
        cape_dark = (20, 15, 25, alpha)
        
        # Horizontal lean
        lean = frame * 4
        
        # Motion-blurred cape
        cape_points = [
            (26*s-lean, 18*s), (16*s-lean, 20*s), (10*s-lean, 28*s),
            (8*s-lean, 42*s), (16*s, 52*s), (26*s, 54*s)
        ]
        pygame.draw.polygon(surface, cape_dark, cape_points)
        
        # Streamlined body
        pygame.draw.ellipse(surface, armor_base, ((19-lean)*s, 18*s, 14*s, 20*s))
        
        return surface
    
    def draw_frame_wall_slide(self, frame):
        """Draw wall slide animation"""
        surface = pygame.Surface(self.base_size, pygame.SRCALPHA)
        s = 2
        
        # Colors
        armor_dark = (25, 25, 30)
        armor_base = (40, 40, 50)
        cape_dark = (20, 15, 25)
        skin_base = (130, 105, 85)
        eye_glow = (80, 120, 180)
        
        slide_offset = frame * 2
        
        # Cape pressed against wall
        cape_points = [
            (32*s, 18*s), (36*s, 22*s), (38*s, 32*s),
            (38*s, 44*s), (34*s, 52*s), (28*s, 54*s), (26*s, 48*s), (26*s, 24*s)
        ]
        pygame.draw.polygon(surface, cape_dark, cape_points)
        
        # Body pressed against wall
        pygame.draw.ellipse(surface, armor_base, (20*s, (18+slide_offset)*s, 12*s, 20*s))
        
        # One arm stretched up (grabbing wall)
        self.draw_limb(surface, (18*s, (24+slide_offset)*s), (16*s, (12+slide_offset)*s), 3*s, armor_dark)
        self.draw_limb(surface, (16*s, (12+slide_offset)*s), (15*s, (8+slide_offset)*s), 2*s, skin_base)
        
        # Legs bent
        self.draw_limb(surface, (24*s, (38+slide_offset)*s), (28*s, (44+slide_offset)*s), 4*s, armor_dark)
        self.draw_limb(surface, (26*s, (38+slide_offset)*s), (24*s, (46+slide_offset)*s), 4*s, armor_dark)
        
        # Head
        pygame.draw.ellipse(surface, armor_dark, (23*s, (8+slide_offset)*s, 14*s, 14*s))
        pygame.draw.circle(surface, eye_glow, (28*s, int((15+slide_offset)*s)), 2)
        pygame.draw.circle(surface, eye_glow, (32*s, int((15+slide_offset)*s)), 2)
        
        return surface
    
    def draw_frame_attack(self, progress):
        """Draw attack animation with weapon swing aimed at cursor"""
        surface = pygame.Surface(self.base_size, pygame.SRCALPHA)
        s = 2
        
        # Colors
        armor_dark = (25, 25, 30)
        armor_base = (40, 40, 50)
        armor_light = (60, 60, 70)
        cape_dark = (20, 15, 25)
        cape_base = (35, 25, 40)
        skin_base = (130, 105, 85)
        eye_glow = (180, 100, 80)  # Red/orange glow during attack
        weapon_color = (200, 200, 220)
        
        # Attack progress (0.0 to 1.0)
        # Windup (0-0.3), Swing (0.3-0.7), Recovery (0.7-1.0)
        
        # Get aim angle in degrees (convert from radians)
        # Default to horizontal if aim_angle not set
        aim_degrees = math.degrees(self.aim_angle) if hasattr(self, 'aim_angle') else 0
        
        # Adjust aim angle for facing direction
        if not self.facing_right:
            aim_degrees = 180 - aim_degrees
        
        # Body leans into attack toward aim direction
        body_lean = int(progress * 4 * s)
        
        # Cape flowing with motion
        cape_flow = int(progress * 8 * s)
        cape_points = [
            (32*s - cape_flow, 18*s), (24*s - cape_flow, 24*s), (20*s - cape_flow, 36*s),
            (18*s - cape_flow, 48*s), (22*s - cape_flow, 56*s), (30*s, 54*s), (30*s, 24*s)
        ]
        pygame.draw.polygon(surface, cape_dark, cape_points)
        pygame.draw.polygon(surface, cape_base, cape_points, 2)
        
        # Body
        body_x = 24*s + body_lean
        pygame.draw.ellipse(surface, armor_base, (body_x, 18*s, 16*s, 24*s))
        pygame.draw.ellipse(surface, armor_light, (body_x+2*s, 20*s, 12*s, 8*s))
        
        # Weapon arm - swings in arc based on aim angle
        if progress < 0.3:
            # Windup - arm back from target angle
            arm_angle = aim_degrees - 60 + (progress / 0.3) * 30
        elif progress < 0.7:
            # Active swing - arc through target angle
            swing_progress = (progress - 0.3) / 0.4
            start_angle = aim_degrees - 30
            end_angle = aim_degrees + 30
            arm_angle = start_angle + swing_progress * (end_angle - start_angle)
        else:
            # Recovery - continue past target
            recovery = (progress - 0.7) / 0.3
            arm_angle = aim_degrees + 30 + recovery * 20
        
        arm_angle_rad = math.radians(arm_angle)
        shoulder_x = body_x + 8*s
        shoulder_y = 22*s
        
        # Upper arm
        elbow_x = shoulder_x + math.cos(arm_angle_rad) * 10*s
        elbow_y = shoulder_y + math.sin(arm_angle_rad) * 10*s
        self.draw_limb(surface, (shoulder_x, shoulder_y), (elbow_x, elbow_y), 4*s, armor_dark)
        
        # Forearm + weapon
        hand_x = elbow_x + math.cos(arm_angle_rad) * 12*s
        hand_y = elbow_y + math.sin(arm_angle_rad) * 12*s
        self.draw_limb(surface, (elbow_x, elbow_y), (hand_x, hand_y), 3*s, skin_base)
        
        # Weapon (extends from hand)
        weapon_length = 20*s
        weapon_end_x = hand_x + math.cos(arm_angle_rad) * weapon_length
        weapon_end_y = hand_y + math.sin(arm_angle_rad) * weapon_length
        pygame.draw.line(surface, weapon_color, (int(hand_x), int(hand_y)), 
                        (int(weapon_end_x), int(weapon_end_y)), int(3*s))
        
        # Motion blur during active frames
        if 0.3 <= progress <= 0.7:
            blur_alpha = int(100 * (1 - abs(progress - 0.5) * 2))
            blur_surface = pygame.Surface(self.base_size, pygame.SRCALPHA)
            pygame.draw.line(blur_surface, (*weapon_color, blur_alpha), 
                           (int(hand_x), int(hand_y)), 
                           (int(weapon_end_x), int(weapon_end_y)), int(6*s))
            surface.blit(blur_surface, (0, 0))
        
        # Other arm
        other_arm_x = body_x + 12*s
        self.draw_limb(surface, (other_arm_x, 24*s), (other_arm_x - 4*s, 32*s), 4*s, armor_dark)
        self.draw_limb(surface, (other_arm_x - 4*s, 32*s), (other_arm_x - 6*s, 38*s), 3*s, skin_base)
        
        # Legs - stable stance
        self.draw_limb(surface, (body_x + 4*s, 42*s), (body_x + 2*s, 52*s), 5*s, armor_dark)
        self.draw_limb(surface, (body_x + 12*s, 42*s), (body_x + 14*s, 52*s), 5*s, armor_dark)
        self.draw_limb(surface, (body_x + 2*s, 52*s), (body_x, 60*s), 4*s, armor_dark)
        self.draw_limb(surface, (body_x + 14*s, 52*s), (body_x + 16*s, 60*s), 4*s, armor_dark)
        
        # Head - tilts with attack toward aim direction
        head_tilt = int(progress * 3 * s)
        head_angle_offset = int(math.sin(arm_angle_rad) * 2 * s)
        pygame.draw.ellipse(surface, armor_dark, (body_x + 4*s + head_angle_offset, 6*s + head_tilt, 14*s, 14*s))
        
        # Eyes glow during attack
        eye_intensity = int(180 + 75 * progress)
        eye_color = (min(255, eye_intensity), int(100 - 50 * progress), 80)
        pygame.draw.circle(surface, eye_color, (int(body_x + 8*s + head_angle_offset), int(12*s + head_tilt)), 2)
        pygame.draw.circle(surface, eye_color, (int(body_x + 12*s + head_angle_offset), int(12*s + head_tilt)), 2)
        
        return surface
    
    def generate_attack_frame(self, progress):
        """Generate simple attack frame when sprite manager not available"""
        # Simple placeholder - just return idle sprite with weapon extended
        surface = pygame.Surface((64, 64), pygame.SRCALPHA)
        # Copy from animation frames or base image
        if 'idle' in self.animation_frames and len(self.animation_frames['idle']) > 0:
            surface.blit(self.animation_frames['idle'][0], (0, 0))
        else:
            surface.blit(self.image, (0, 0))
        return surface
    
    def draw_limb(self, surface, start_pos, end_pos, thickness, color):
        """Draw a limb segment with rounded ends"""
        pygame.draw.line(surface, color, start_pos, end_pos, int(thickness))
        pygame.draw.circle(surface, color, (int(start_pos[0]), int(start_pos[1])), int(thickness//2))
        pygame.draw.circle(surface, color, (int(end_pos[0]), int(end_pos[1])), int(thickness//2))
    
    def update(self, platforms, coins):
        """Update player with enhanced movement and combat feel"""
        keys = pygame.key.get_pressed()
        
        # Update combat feel (hit pause, screen shake)
        is_paused = self.combat_feel.update()
        if is_paused:
            # Skip update during hit pause for impact
            return
        
        # Update combat system (Hollow Knight style)
        self.combat.update()
        self.combat.update_particles()
        
        # Update weapon system (with safety check)
        if self.current_weapon:
            try:
                self.current_weapon.update()
            except Exception as e:
                print(f"Weapon update error: {e}")
        
        # Update RPG stats (regeneration)
        self.stats.update(1/FPS)  # Delta time in seconds
        
        # Update stamina regeneration
        self.stats.update_stamina()
        
        # Check if player died from stats
        if not self.stats.is_alive():
            self.take_damage()  # Use existing death system
        
        # Update timers
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
            if self.invincible_timer == 0:
                self.invincible = False
        
        # Use enhanced movement controller
        if not self.combat_feel.is_attack_locked():
            self.movement_controller.update(keys, platforms)
        
        # DASH INPUT
        stamina_config = self.weapon_manager.get_stamina_config()
        dash_cost = stamina_config['actions']['dash']
        if keys[pygame.K_LSHIFT] and self.can_dash and self.dash_cooldown == 0 and self.stats.can_afford_stamina(dash_cost):
            self.stats.use_stamina(dash_cost)
            if self.movement_controller.try_dash():
                pass  # Dash handled by controller
        
        # Update horizontal position
        old_x = self.rect.x
        self.rect.x += self.velocity_x
        self.on_wall = self.check_horizontal_collisions(platforms)
        
        # Update vertical position
        old_on_ground = self.on_ground
        self.rect.y += self.velocity_y
        self.on_ground = False
        self.check_vertical_collisions(platforms)
        
        # Reset jumps when landing
        if self.on_ground and not old_on_ground:
            self.jumps_available = self.max_jumps
            self.can_dash = True
            # Landing particles (more if falling fast)
            if self.velocity_y > LANDING_IMPACT_THRESHOLD:
                self.spawn_particles('land', 12)
                # Play hard landing sound
                if self.sound_manager:
                    self.sound_manager.play_sound('player_land_hard', category='player')
            elif self.velocity_y > 4:
                self.spawn_particles('land', 6)
                # Play soft landing sound
                if self.sound_manager:
                    self.sound_manager.play_sound('player_land_soft', category='player')
        
        # Reset dash when landing or touching wall
        if self.on_ground or self.on_wall:
            self.can_dash = True
        
        # Update animation state
        self.update_animation_state()
        
        # Collect coins (grant XP)
        coin_hits = pygame.sprite.spritecollide(self, coins, True)
        if coin_hits:
            self.score += len(coin_hits) * 10
            # Grant XP for collection (5 XP per coin)
            xp_gained = len(coin_hits) * 5
            leveled_up = self.stats.add_xp(xp_gained)
            # Return level-up flag for game to handle UI
            if leveled_up:
                return 'level_up'
        
        # Keep player within world bounds
        if self.rect.left < 0:
            self.rect.left = 0
            self.velocity_x = 0
        if self.rect.right > WORLD_WIDTH:
            self.rect.right = WORLD_WIDTH
            self.velocity_x = 0
            
        # Fall off bottom = lose life
        if self.rect.top > WORLD_HEIGHT:
            self.take_damage()
            self.respawn()
    
    def handle_horizontal_movement(self, keys):
        """Acceleration-based movement with stat modifiers"""
        # Input
        move_input = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_input = -1
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_input = 1
            self.facing_right = True
        
        # Apply stat-based movement speed modifier
        speed_multiplier = self.stats.movement_speed
        
        # Acceleration
        if move_input != 0:
            self.velocity_x += move_input * PLAYER_ACCELERATION * speed_multiplier
        else:
            # Apply friction when no input
            self.velocity_x *= PLAYER_FRICTION
            if abs(self.velocity_x) < 0.1:
                self.velocity_x = 0
        
        # Clamp to max speed (modified by stats)
        max_speed = PLAYER_MAX_SPEED * speed_multiplier
        if abs(self.velocity_x) > max_speed:
            self.velocity_x = max_speed * (1 if self.velocity_x > 0 else -1)
        
        # Reduced air control
        if not self.on_ground and not self.on_wall:
            self.velocity_x *= 0.98
    
    def handle_jump(self, keys):
        """Variable height jump with double jump and wall jump"""
        jump_key = keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]
        
        # Jump input pressed
        if jump_key and not self.jump_held:
            self.jump_held = True
            
            # Wall jump
            if self.on_wall and not self.on_ground:
                self.perform_wall_jump()
            # Regular jump (including coyote time)
            elif (self.on_ground or self.coyote_timer > 0 or self.jumps_available > 0):
                self.perform_jump()
            else:
                # Jump buffering: remember jump input
                self.jump_buffer_timer = JUMP_BUFFER_TIME
        
        # Jump released
        if not jump_key:
            self.jump_held = False
            self.jump_hold_timer = 0
            # Cut jump short if released early
            if self.velocity_y < -2:
                self.velocity_y *= 0.5
        
        # Variable jump height - holding jump makes you go higher
        if self.jump_held and self.velocity_y < 0 and self.jump_hold_timer < MAX_JUMP_HOLD_TIME:
            self.velocity_y -= JUMP_HOLD_BOOST
            self.jump_hold_timer += 1
    
    def perform_jump(self):
        """Execute a jump"""
        if self.on_ground or self.coyote_timer > 0:
            # First jump from ground
            self.velocity_y = JUMP_STRENGTH
            self.coyote_timer = 0
            self.jumps_available = self.max_jumps - 1
            self.spawn_particles('jump', 8)
            # Play jump sound
            if self.sound_manager:
                self.sound_manager.play_sound('player_jump', category='player')
        elif self.jumps_available > 0:
            # Double jump
            self.velocity_y = JUMP_STRENGTH * 0.9
            self.jumps_available -= 1
            self.spawn_particles('jump', 6)
            # Play jump sound (slightly higher pitch for double jump could be added)
            if self.sound_manager:
                self.sound_manager.play_sound('player_jump', category='player')
        
        self.jump_hold_timer = 0
    
    def perform_wall_jump(self):
        """Execute a wall jump"""
        self.velocity_y = WALL_JUMP_Y
        self.velocity_x = WALL_JUMP_X * -self.wall_side
        self.on_wall = False
        self.jumps_available = self.max_jumps - 1
        self.jump_hold_timer = 0
    
    def start_dash(self):
        """Start dash move"""
        self.is_dashing = True
        self.dash_timer = DASH_DURATION
        self.can_dash = False
        self.dash_cooldown = 30  # Cooldown frames
        self.dash_direction = 1 if self.facing_right else -1
        self.velocity_y = 0  # Stop vertical movement during dash
        self.velocity_x = DASH_SPEED * self.dash_direction
        # Play dash sound
        if self.sound_manager:
            self.sound_manager.play_sound('player_dash', category='player')
    
    def handle_dash(self):
        """Handle dash movement"""
        self.dash_timer -= 1
        self.velocity_x = DASH_SPEED * self.dash_direction * (self.dash_timer / DASH_DURATION)
        self.velocity_y = 0
        
        # Spawn dash trail particles
        self.spawn_particles('dash', 2)
        
        if self.dash_timer <= 0:
            self.is_dashing = False
            self.velocity_x *= 0.5
    
    def apply_gravity(self):
        """Apply gravity with wall slide"""
        if self.on_wall and self.velocity_y > 0 and not self.on_ground:
            # Wall slide - slow fall
            self.velocity_y = min(self.velocity_y, WALL_SLIDE_SPEED)
            # Spawn wall slide particles occasionally
            if self.animation_timer % 4 == 0:
                self.spawn_particles('wall_slide', 1)
        else:
            # Normal gravity
            self.velocity_y += GRAVITY
        
        # Terminal velocity
        if self.velocity_y > MAX_FALL_SPEED:
            self.velocity_y = MAX_FALL_SPEED
    
    def check_horizontal_collisions(self, platforms):
        """Handle horizontal collisions and wall detection"""
        on_wall = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_x > 0:  # Moving right
                    self.rect.right = platform.rect.left
                    self.wall_side = 1
                    on_wall = True
                    if not self.is_dashing:
                        self.velocity_x = 0
                elif self.velocity_x < 0:  # Moving left
                    self.rect.left = platform.rect.right
                    self.wall_side = -1
                    on_wall = True
                    if not self.is_dashing:
                        self.velocity_x = 0
        return on_wall
    
    def check_vertical_collisions(self, platforms):
        """Handle vertical collisions"""
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0:  # Falling down
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                elif self.velocity_y < 0:  # Jumping up
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0
    
    def update_animation_state(self):
        """Update animation based on movement state"""
        # Attack animation takes priority
        if self.combat.is_attacking:
            self.animation_state = "attack"
        elif self.is_dashing:
            self.animation_state = "dash"
        elif self.on_wall and not self.on_ground:
            self.animation_state = "wall_slide"
        elif not self.on_ground:
            if self.velocity_y < 0:
                self.animation_state = "jump"
            else:
                self.animation_state = "fall"
        elif abs(self.velocity_x) > 0.5:
            self.animation_state = "walk"
        else:
            self.animation_state = "idle"
        
        # Simple animation timer
        self.animation_timer += 1
        if self.animation_timer > 5:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4
    
    def take_damage(self, damage=20, damage_type='physical'):
        """Player takes damage with RPG stats calculation"""
        if not self.invincible:
            # Use RPG stats system for damage calculation
            actual_damage = self.stats.take_damage(damage, damage_type)
            
            # Play hit sound based on damage amount
            if self.sound_manager:
                if actual_damage > 30:
                    self.sound_manager.play_sound('player_hit_heavy', category='player')
                else:
                    self.sound_manager.play_sound('player_hit_light', category='player')
            
            # Check if player died from stats
            if not self.stats.is_alive():
                self.lives -= 1
                # Play death sound
                if self.sound_manager:
                    self.sound_manager.play_sound('player_die', category='player')
                self.respawn()
            
            # Set invincibility frames
            self.invincible = True
            self.invincible_timer = 90  # 1.5 seconds
            
            return actual_damage
        return 0
    
    def respawn(self):
        """Respawn player at start"""
        self.rect.x = 200
        self.rect.y = 2200
        self.velocity_x = 0
        self.velocity_y = 0
        self.jumps_available = self.max_jumps
        self.can_dash = True
        
        # Restore health on respawn
        self.stats.current_health = self.stats.max_health
    
    def apply_equipment_bonuses(self):
        """Apply stat bonuses from equipped items to player stats"""
        # Get all equipment bonuses
        equipment_stats = self.inventory.get_equipment_stats()
        
        # Update equipment visuals from currently equipped items
        for slot in self.equipment_visuals.keys():
            equipped_item = self.inventory.equipment.get(slot)
            if equipped_item:
                self.equipment_visuals[slot] = equipped_item.visual_data
            else:
                self.equipment_visuals[slot] = None
        
        # Apply bonuses to base attributes
        for stat, value in equipment_stats.items():
            stat_lower = stat.lower()
            
            # Apply to core attributes
            if stat_lower == 'strength':
                self.stats.strength += value
            elif stat_lower == 'dexterity':
                self.stats.dexterity += value
            elif stat_lower == 'intelligence':
                self.stats.intelligence += value
            elif stat_lower == 'vitality':
                self.stats.vitality += value
            
            # Apply direct stat bonuses (bypass attribute calculations)
            elif stat_lower == 'damage':
                self.stats.attack_damage += value
            elif stat_lower == 'defense':
                self.stats.defense += value
            elif stat_lower == 'max_health':
                self.stats.max_health += value
            elif stat_lower == 'max_mana':
                self.stats.max_mana += value
            elif stat_lower == 'movement_speed':
                self.stats.movement_speed += value / 100.0  # Convert percentage
            elif stat_lower == 'mana_regen':
                self.stats.mana_regen += value
            elif stat_lower == 'health_regen':
                self.stats.health_regen += value
            elif stat_lower == 'critical_chance':
                self.stats.critical_chance += value / 100.0  # Convert percentage
            elif stat_lower == 'critical_multiplier':
                self.stats.critical_multiplier += value / 100.0  # Convert percentage
        
        # Recalculate all derived stats with new bonuses
        self.stats.recalculate_stats()
    
    def draw_equipped_items(self, surface, screen_x, screen_y):
        """Render equipped items on player sprite - dynamic with movement"""
        # Player sprite is 48x56 pixels
        # Calculate base positions relative to player sprite center
        center_x = screen_x + 24  # Half of 48
        center_y = screen_y + 28  # Half of 56
        
        # Movement bob effect (subtle vertical oscillation when moving)
        movement_bob = 0
        if abs(self.velocity_x) > 0.5 and self.on_ground:
            # Bob up and down while running
            movement_bob = math.sin(pygame.time.get_ticks() * 0.015) * 1.5
        
        # Dash effect - tilt equipment
        dash_tilt = 0
        if self.is_dashing:
            dash_tilt = 3 if self.facing_right else -3
        
        # Jump/fall lean
        air_lean = 0
        if not self.on_ground:
            if self.velocity_y < -5:  # Jumping up
                air_lean = -2
            elif self.velocity_y > 5:  # Falling
                air_lean = 2
        
        # === DRAW ORDER: Back to front for proper layering ===
        
        # 1. BOOTS (behind player legs) - Fit humanoid feet
        if self.equipment_visuals["boots"]:
            visual = self.equipment_visuals["boots"]
            boot_y = screen_y + 51 + movement_bob
            
            # Back boot (left foot)
            back_boot = pygame.Rect(screen_x + 16, int(boot_y), 7, 5)
            pygame.draw.rect(surface, visual["primary_color"], back_boot, border_radius=2)
            pygame.draw.line(surface, visual["accent_color"],
                           (screen_x + 19, int(boot_y)), 
                           (screen_x + 19, int(boot_y) + 4), 1)
            
            # Front boot (right foot)
            front_boot = pygame.Rect(screen_x + 25, int(boot_y), 7, 5)
            pygame.draw.rect(surface, visual["primary_color"], front_boot, border_radius=2)
            pygame.draw.line(surface, visual["accent_color"],
                           (screen_x + 28, int(boot_y)), 
                           (screen_x + 28, int(boot_y) + 4), 1)
            
            # Shin guards (leg armor extending up from boots)
            # Back leg shin
            back_shin = pygame.Rect(screen_x + 16, int(boot_y) - 10, 6, 10)
            pygame.draw.rect(surface, visual["secondary_color"], back_shin, border_radius=1)
            # Front leg shin
            front_shin = pygame.Rect(screen_x + 25, int(boot_y) - 10, 6, 10)
            pygame.draw.rect(surface, visual["secondary_color"], front_shin, border_radius=1)
            pygame.draw.circle(surface, visual["accent_color"], (screen_x + 28, int(boot_y) - 6), 3)  # Knee guard
        
        # 2. ARMOR (on torso) - Fit humanoid body
        if self.equipment_visuals["armor"]:
            visual = self.equipment_visuals["armor"]
            torso_y = screen_y + 18 + movement_bob * 0.5
            
            # Main chest plate (fits over torso ellipse from y=18, width=14, height=18)
            chest_plate = pygame.Rect(screen_x + 18, int(torso_y), 15, 19)
            pygame.draw.ellipse(surface, visual["primary_color"], chest_plate)
            
            # Chest detail - breastplate segments
            pygame.draw.arc(surface, visual["accent_color"], 
                          (screen_x + 20, int(torso_y) + 2, 11, 10), 4.5, 6.3, 2)
            
            # Shoulder pauldrons (armor shoulders)
            left_shoulder = (screen_x + 17, int(torso_y) + 3)
            right_shoulder = (screen_x + 31, int(torso_y) + 3)
            
            # Left pauldron
            pygame.draw.ellipse(surface, visual["secondary_color"],
                              (left_shoulder[0] - 4, left_shoulder[1] - 3, 8, 7))
            pygame.draw.arc(surface, visual["accent_color"],
                          (left_shoulder[0] - 4, left_shoulder[1] - 3, 8, 7), 3.8, 5.5, 1)
            
            # Right pauldron
            pygame.draw.ellipse(surface, visual["secondary_color"],
                              (right_shoulder[0] - 4, right_shoulder[1] - 3, 8, 7))
            pygame.draw.arc(surface, visual["accent_color"],
                          (right_shoulder[0] - 4, right_shoulder[1] - 3, 8, 7), 3.8, 5.5, 1)
            
            # Central accent stripe (sternum line)
            pygame.draw.line(surface, visual["accent_color"],
                           (center_x, int(torso_y) + 3), 
                           (center_x, int(torso_y) + 16), 2)
            
            # Armor plate segments (ribs)
            for i in range(2):
                y_offset = int(torso_y) + 8 + i * 4
                pygame.draw.line(surface, visual["secondary_color"],
                               (screen_x + 20, y_offset), 
                               (screen_x + 28, y_offset), 1)
            
            # Belt/waist armor
            belt_y = int(torso_y) + 18
            pygame.draw.rect(surface, visual["secondary_color"],
                           (screen_x + 19, belt_y, 11, 3), border_radius=1)
            pygame.draw.circle(surface, visual["accent_color"], (center_x, belt_y + 1), 2)  # Belt buckle
            
            # Arm guards (vambraces) on forearms
            # Back arm guard
            back_arm_guard = pygame.Rect(screen_x + 14, screen_y + 28, 5, 10)
            pygame.draw.ellipse(surface, visual["secondary_color"], back_arm_guard)
            # Front arm guard
            front_arm_guard = pygame.Rect(screen_x + 30, screen_y + 28, 5, 10)
            pygame.draw.ellipse(surface, visual["secondary_color"], front_arm_guard)
        
        # 3. HELM (on head) - Fit humanoid head
        if self.equipment_visuals["helm"]:
            visual = self.equipment_visuals["helm"]
            head_y = screen_y + 7 + movement_bob * 0.3 + air_lean * 0.5
            
            # Main helm shape (covers head ellipse at y=8, width=13, height=14)
            helm_outer = pygame.Rect(screen_x + 24, int(head_y), 16, 15)
            pygame.draw.ellipse(surface, visual["primary_color"], helm_outer)
            
            # Helm face guard
            helm_inner = pygame.Rect(screen_x + 25, int(head_y) + 1, 14, 13)
            pygame.draw.ellipse(surface, visual["secondary_color"], helm_inner)
            
            # Visor slit (where eyes show through)
            if self.facing_right:
                visor_rect = pygame.Rect(screen_x + 30, int(head_y) + 6, 7, 3)
            else:
                visor_rect = pygame.Rect(screen_x + 27, int(head_y) + 6, 7, 3)
            pygame.draw.rect(surface, (20, 25, 35), visor_rect, border_radius=1)
            
            # Glowing eyes through visor
            if self.facing_right:
                eye_pos = (screen_x + 33, int(head_y) + 7)
            else:
                eye_pos = (screen_x + 30, int(head_y) + 7)
            pygame.draw.circle(surface, visual["accent_color"], eye_pos, 2)
            pygame.draw.circle(surface, (255, 255, 255), eye_pos, 1)
            
            # Helm crest/crown
            crest_points = [
                (center_x - 3, int(head_y) + 2),
                (center_x, int(head_y) - 2),
                (center_x + 3, int(head_y) + 2)
            ]
            pygame.draw.polygon(surface, visual["accent_color"], crest_points)
            
            # Curved horn (optional ornament)
            horn_start = (center_x - 2, int(head_y) + 3)
            horn_curve = [
                horn_start,
                (horn_start[0] - 4, horn_start[1] - 2),
                (horn_start[0] - 7, horn_start[1] - 3),
                (horn_start[0] - 9, horn_start[1] - 2)
            ]
            pygame.draw.lines(surface, visual["accent_color"], False, horn_curve, 2)
        
        # 4. WEAPON (in hand - behind or in front depending on state)
        if self.equipment_visuals["weapon"]:
            visual = self.equipment_visuals["weapon"]
            weapon_type = visual.get("weapon_type", "Sword")
            
            # Hand positions with movement dynamics
            hand_y = screen_y + 30 + movement_bob * 0.7 + air_lean
            
            if self.facing_right:
                hand_x = screen_x + 38
                weapon_angle = -15 + dash_tilt
                direction = 1
            else:
                hand_x = screen_x + 10
                weapon_angle = 15 - dash_tilt
                direction = -1
            
            # Weapon sway when moving
            if abs(self.velocity_x) > 0.5 and self.on_ground:
                weapon_angle += math.sin(pygame.time.get_ticks() * 0.02) * 5
            
            # Draw different weapon types
            if weapon_type in ["Sword", "Dagger", "Axe", "Mace"]:
                blade_length = {"Sword": 18, "Dagger": 12, "Axe": 16, "Mace": 14}.get(weapon_type, 18)
                blade_width = {"Sword": 3, "Dagger": 2, "Axe": 5, "Mace": 4}.get(weapon_type, 3)
                
                # Calculate angled blade
                angle_rad = math.radians(weapon_angle)
                tip_x = hand_x + direction * blade_length * math.cos(angle_rad)
                tip_y = int(hand_y + blade_length * math.sin(angle_rad))
                
                # Blade shape
                perp_x = -direction * blade_width * math.sin(angle_rad) / 2
                perp_y = blade_width * math.cos(angle_rad) / 2
                
                blade_points = [
                    (int(hand_x + perp_x), int(hand_y + perp_y)),
                    (int(tip_x + perp_x * 0.3), int(tip_y + perp_y * 0.3)),
                    (int(tip_x), int(tip_y)),
                    (int(tip_x - perp_x * 0.3), int(tip_y - perp_y * 0.3)),
                    (int(hand_x - perp_x), int(hand_y - perp_y))
                ]
                pygame.draw.polygon(surface, visual["primary_color"], blade_points)
                pygame.draw.polygon(surface, visual["accent_color"], blade_points, 1)
                
                # Handle/grip
                handle_length = 6
                handle_points = [
                    (int(hand_x - direction * 2), int(hand_y - 2)),
                    (int(hand_x - direction * 2), int(hand_y + 2))
                ]
                pygame.draw.line(surface, visual["secondary_color"], 
                               handle_points[0], handle_points[1], 3)
                
                # Guard (crossguard)
                guard_offset = 4
                pygame.draw.line(surface, visual["accent_color"],
                               (int(hand_x - guard_offset), int(hand_y)),
                               (int(hand_x + guard_offset), int(hand_y)), 2)
                
            elif weapon_type == "Greatsword":
                blade_length = 26
                blade_width = 5
                
                angle_rad = math.radians(weapon_angle)
                tip_x = hand_x + direction * blade_length * math.cos(angle_rad)
                tip_y = int(hand_y + blade_length * math.sin(angle_rad))
                
                perp_x = -direction * blade_width * math.sin(angle_rad) / 2
                perp_y = blade_width * math.cos(angle_rad) / 2
                
                blade_points = [
                    (int(hand_x + perp_x), int(hand_y + perp_y)),
                    (int(tip_x + perp_x * 0.4), int(tip_y + perp_y * 0.4)),
                    (int(tip_x), int(tip_y)),
                    (int(tip_x - perp_x * 0.4), int(tip_y - perp_y * 0.4)),
                    (int(hand_x - perp_x), int(hand_y - perp_y))
                ]
                pygame.draw.polygon(surface, visual["primary_color"], blade_points)
                pygame.draw.polygon(surface, visual["accent_color"], blade_points, 2)
                
                # Two-handed grip
                pygame.draw.circle(surface, visual["secondary_color"], (int(hand_x), int(hand_y)), 4)
                
            elif weapon_type == "Spear":
                spear_length = 28
                
                angle_rad = math.radians(weapon_angle * 0.7)  # Less angle for spear
                tip_x = hand_x + direction * spear_length * math.cos(angle_rad)
                tip_y = int(hand_y + spear_length * math.sin(angle_rad))
                
                # Shaft
                pygame.draw.line(surface, visual["secondary_color"],
                               (int(hand_x), int(hand_y)), (int(tip_x), int(tip_y)), 2)
                
                # Spearhead (diamond shape)
                head_size = 6
                head_points = [
                    (int(tip_x + direction * head_size), int(tip_y)),
                    (int(tip_x), int(tip_y - head_size * 0.7)),
                    (int(tip_x - direction * head_size * 0.5), int(tip_y)),
                    (int(tip_x), int(tip_y + head_size * 0.7))
                ]
                pygame.draw.polygon(surface, visual["primary_color"], head_points)
                pygame.draw.polygon(surface, visual["accent_color"], head_points, 1)
                
            elif weapon_type in ["Wand", "Staff"]:
                staff_length = 20 if weapon_type == "Staff" else 14
                
                angle_rad = math.radians(weapon_angle * 1.3)
                tip_x = hand_x + direction * staff_length * math.cos(angle_rad)
                tip_y = int(hand_y + staff_length * math.sin(angle_rad) - 4)
                
                # Staff/wand body
                pygame.draw.line(surface, visual["secondary_color"],
                               (int(hand_x), int(hand_y)), (int(tip_x), int(tip_y)), 3)
                
                # Magical orb at tip (pulsing effect)
                orb_pulse = abs(math.sin(pygame.time.get_ticks() * 0.008)) * 1.5 + 3
                pygame.draw.circle(surface, visual["accent_color"], 
                                 (int(tip_x), int(tip_y)), int(orb_pulse))
                pygame.draw.circle(surface, (255, 255, 255), 
                                 (int(tip_x), int(tip_y)), int(orb_pulse * 0.5))
                
                # Magical particles around orb
                particle_angle = pygame.time.get_ticks() * 0.01
                for i in range(3):
                    angle = particle_angle + i * (math.pi * 2 / 3)
                    px = int(tip_x + math.cos(angle) * (orb_pulse + 3))
                    py = int(tip_y + math.sin(angle) * (orb_pulse + 3))
                    pygame.draw.circle(surface, visual["accent_color"], (px, py), 1)
        
        # 5. AMULET (front of chest)
        if self.equipment_visuals["amulet"]:
            visual = self.equipment_visuals["amulet"]
            amulet_y = screen_y + 28 + movement_bob * 0.5
            
            # Chain
            chain_top = (center_x, screen_y + 20)
            chain_bottom = (center_x, int(amulet_y))
            pygame.draw.line(surface, visual["primary_color"], chain_top, chain_bottom, 1)
            
            # Gem pendant
            gem_points = [
                (center_x, int(amulet_y) + 4),
                (center_x - 3, int(amulet_y)),
                (center_x, int(amulet_y) - 3),
                (center_x + 3, int(amulet_y))
            ]
            pygame.draw.polygon(surface, visual["secondary_color"], gem_points)
            pygame.draw.circle(surface, visual["accent_color"], (center_x, int(amulet_y)), 2)
        
        # 6. RINGS (on hands - subtle glow)
        if self.equipment_visuals["ring1"]:
            visual = self.equipment_visuals["ring1"]
            if self.facing_right:
                ring_pos = (screen_x + 10, int(hand_y))
            else:
                ring_pos = (screen_x + 38, int(hand_y))
            # Ring glow effect
            glow_pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 0.5 + 1.5
            pygame.draw.circle(surface, visual["accent_color"], ring_pos, int(glow_pulse) + 1)
            pygame.draw.circle(surface, visual["accent_color"], ring_pos, int(glow_pulse))
        
        if self.equipment_visuals["ring2"]:
            visual = self.equipment_visuals["ring2"]
            if self.facing_right:
                ring_pos = (screen_x + 38, int(hand_y))
            else:
                ring_pos = (screen_x + 10, int(hand_y))
            glow_pulse = abs(math.sin(pygame.time.get_ticks() * 0.006)) * 0.5 + 1.5
            pygame.draw.circle(surface, visual["accent_color"], ring_pos, int(glow_pulse) + 1)
            pygame.draw.circle(surface, visual["accent_color"], ring_pos, int(glow_pulse))
    
    def draw(self, surface, screen_pos=None, camera=None):
        """Custom draw with Hollow Knight combat animations"""
        # Use provided screen position or self.rect
        draw_rect = screen_pos if screen_pos else self.rect
        
        # Check if currently attacking
        if self.combat.is_attacking:
            # Use attack sprites from sprite manager
            if self.sprite_manager:
                # Determine attack state for sprite
                if self.combat.attack_phase.value == "windup":
                    state = "attack_windup"
                    frame = self.combat.attack_timer
                elif self.combat.attack_phase.value == "active":
                    state = "attack_active"
                    frame = self.combat.attack_timer - self.combat.get_windup_duration()
                elif self.combat.attack_phase.value == "recovery":
                    state = "attack_recovery"
                    frame = self.combat.attack_timer - self.combat.get_windup_duration() - self.combat.get_active_duration()
                else:
                    state = "idle"
                    frame = 0
                
                current_frame = self.sprite_manager.get_sprite('player', state, frame)
            else:
                # Fallback to generated frame
                progress = self.combat.get_attack_progress()
                current_frame = self.generate_attack_frame(progress)
        else:
            # Use normal animation frames
            if self.sprite_manager:
                state = self.animation_state if self.animation_state != 'attack' else 'idle'
                current_frame = self.sprite_manager.get_sprite('player', state, self.animation_frame)
            else:
                frames = self.animation_frames.get(self.animation_state, self.animation_frames['idle'])
                if len(frames) > 0:
                    frame_index = self.animation_frame % len(frames)
                    current_frame = frames[frame_index]
                else:
                    current_frame = self.image
        
        # Flip sprite based on facing direction
        if self.facing_right:
            image = current_frame
        else:
            image = pygame.transform.flip(current_frame, True, False)
        
        # Invincibility flash
        if self.invincible and self.invincible_timer % 6 < 3:
            return  # Skip drawing for flash effect
        
        # Draw animated player sprite
        surface.blit(image, draw_rect)
        
        # Draw combat particles (slash effects)
        if camera:
            self.combat.draw_particles(surface, camera)
        
        # Draw equipped items on top of player sprite
        self.draw_equipped_items(surface, draw_rect.x, draw_rect.y)
