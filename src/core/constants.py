"""
Game Constants
All game constants centralized for easy balancing and configuration
"""

# Screen & Display
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60
FULLSCREEN = True

# World Size (Horizontal Medieval Village)
WORLD_WIDTH = 8000
WORLD_HEIGHT = 1200

# Colors - Medieval Fantasy Village Palette
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)
DARK_GRAY = (40, 40, 40)
LIGHT_GRAY = (100, 100, 100)
CYAN = (0, 255, 255)
PURPLE = (128, 0, 128)

# Medieval Village Environment Colors
SKY_BLUE = (135, 206, 235)
GRASS_GREEN = (34, 139, 34)
DIRT_BROWN = (101, 67, 33)
STONE_GRAY = (128, 128, 128)
WOOD_BROWN = (139, 90, 43)
ROOF_RED = (139, 69, 19)
STONE_DARK = (80, 80, 80)
STONE_LIGHT = (160, 160, 160)
COBBLESTONE = (105, 105, 105)

# Legacy Colors (for compatibility)
CAVERN_BG = SKY_BLUE
STONE_MID = STONE_GRAY
MOSS_GREEN = GRASS_GREEN
MOSS_LIGHT = (124, 252, 0)
GLOW_BLUE = (100, 180, 255)
GLOW_CYAN = (80, 220, 255)
ACCENT_TEAL = (50, 150, 140)

# Physics Constants
GRAVITY = 0.55
MAX_FALL_SPEED = 14

# Player Movement
PLAYER_ACCELERATION = 1.2
PLAYER_FRICTION = 0.88
PLAYER_MAX_SPEED = 7
PLAYER_AIR_CONTROL = 0.6

# Jump Mechanics
JUMP_STRENGTH = -13.5
JUMP_HOLD_BOOST = 0.35
MAX_JUMP_HOLD_TIME = 18
COYOTE_TIME = 7
JUMP_BUFFER_TIME = 10

# Wall Mechanics
WALL_SLIDE_SPEED = 1.8
WALL_SLIDE_FRICTION = 0.92
WALL_JUMP_X = 9
WALL_JUMP_Y = -12.5

# Dash Mechanics
DASH_SPEED = 18
DASH_DURATION = 12
DASH_TRAIL_LENGTH = 5

# Visual Feedback
LANDING_IMPACT_THRESHOLD = 8  # Velocity for landing particles
