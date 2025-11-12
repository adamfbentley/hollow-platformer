"""
Hollow Platformer - Main Entry Point
A 2D action RPG platformer with Hollow Knight-inspired mechanics

To run: python main.py
"""

import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Import from modular structure
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, FULLSCREEN
from src.core.spatial_partition import SpatialPartition
from src.entities.player import Player
from src.entities.enemies import DementorEnemy, HollowWarrior, ShadowArcher, ShieldGuardian, Berserker, FireBat
from src.entities.enemies.shadow_knight_boss import ShadowKnight
from src.entities.enemies.arcane_sorcerer_boss import ArcaneSorcerer
from src.world import Platform, Camera, ParallaxLayer, Coin, DecorativeElement, Particle
from src.systems import PlayerStats
from src.systems.combat_system import ScreenShake, HitFreeze

# Import UI systems
try:
    from src.ui.level_up_ui import LevelUpUI
    from src.ui.enhanced_player_menu import EnhancedPlayerMenu
    from src.ui.combat_hud import CombatHUD
    from src.ui.boss_health_bar import BossHealthBar
except ImportError as e:
    LevelUpUI = None
    EnhancedPlayerMenu = None
    CombatHUD = None
    BossHealthBar = None
    print(f"Warning: UI modules not found: {e}. Some features may be disabled.")

# Import Audio systems
from src.systems.sound_manager import SoundManager
from src.systems.music_manager import MusicManager, MusicState


class Game:
    """
    Main game class
    Manages game state, levels, and game loop
    """
    def __init__(self):
        # Create fullscreen or windowed
        if FULLSCREEN:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Hollow Platformer")
        
        # Show system cursor (no custom cursor needed for melee combat)
        pygame.mouse.set_visible(True)
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font(None, 36)
        self.gold_color = (255, 215, 0)
        
        # Combat systems
        self.screen_shake = ScreenShake()
        self.hit_freeze = HitFreeze()
        
        # Audio systems
        self.sound_manager = SoundManager(max_simultaneous_sounds=32)
        self.music_manager = MusicManager()
        print("Audio systems initialized")
        
        # Sprite/Art system
        from src.systems.sprite_manager import SpriteManager
        self.sprite_manager = SpriteManager()
        print("Sprite manager initialized")
        
        # UI systems
        if LevelUpUI:
            self.level_up_ui = LevelUpUI(SCREEN_WIDTH, SCREEN_HEIGHT)
        else:
            self.level_up_ui = None
            
        if EnhancedPlayerMenu:
            self.player_menu = EnhancedPlayerMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
        else:
            self.player_menu = None
        
        # Combat HUD (stamina, weapon, combo)
        if CombatHUD:
            self.combat_hud = CombatHUD(SCREEN_WIDTH, SCREEN_HEIGHT)
        else:
            self.combat_hud = None
        
        # Boss health bar
        if BossHealthBar:
            self.boss_health_bar = BossHealthBar(SCREEN_WIDTH, SCREEN_HEIGHT)
        else:
            self.boss_health_bar = None
        
        # Camera
        from src.core.constants import WORLD_WIDTH, WORLD_HEIGHT
        self.camera = Camera(WORLD_WIDTH, WORLD_HEIGHT)
        
        # Spatial partitioning for optimized collision detection
        self.spatial_partition = SpatialPartition(pygame.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT))
        self.spatial_debug = False  # Toggle with F3
        
        # Parallax background layers
        self.parallax_layers = [
            ParallaxLayer(0.1, 0),
            ParallaxLayer(0.3, 100),
            ParallaxLayer(0.5, 200),
            ParallaxLayer(0.7, 300),
        ]
        
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.decorations = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        
        # Game state
        self.show_level_up = False
        self.paused = False
        
        # Create level
        self.setup_level()
        
    def setup_level(self):
        """Create a basic test level"""
        # Create player
        self.player = Player(300, 1000)
        self.player.particle_group = self.particles
        self.player.sound_manager = self.sound_manager  # Give player access to sound manager
        self.player.combat.sound_manager = self.sound_manager  # Give combat system access to sound manager
        self.player.sprite_manager = self.sprite_manager  # Give player access to sprite manager
        self.all_sprites.add(self.player)
        
        # Connect player menu to player
        if self.player_menu:
            self.player_menu.player_stats = self.player.stats
            self.player_menu.player_inventory = self.player.inventory
        
        # Create simple platform layout for testing
        from src.core.constants import WORLD_WIDTH
        
        # Ground
        ground = Platform(0, 1100, WORLD_WIDTH, 100, 'stone')
        self.platforms.add(ground)
        self.all_sprites.add(ground)
        
        # Test platforms
        test_platforms = [
            (200, 1000, 200, 20),
            (500, 900, 180, 20),
            (800, 800, 200, 20),
            (1200, 900, 150, 20),
            (1500, 1000, 200, 20),
            # Boss 2 arena platforms (around x=3500)
            (3200, 1000, 200, 20),
            (3000, 900, 150, 20),
            (3400, 850, 180, 20),
            (3700, 950, 150, 20),
            (3900, 850, 200, 20),
        ]
        
        for x, y, w, h in test_platforms:
            platform = Platform(x, y, w, h, 'stone')
            self.platforms.add(platform)
            self.all_sprites.add(platform)
        
        # Add some coins
        for i in range(10):
            coin = Coin(300 + i * 200, 1000)
            self.coins.add(coin)
            self.all_sprites.add(coin)
        
        # Add test enemies
        dementor = DementorEnemy(600, 950, patrol_range=200)
        dementor.particle_group = self.particles
        dementor.sprite_manager = self.sprite_manager
        self.enemies.add(dementor)
        self.all_sprites.add(dementor)
        
        warrior = HollowWarrior(1000, 1050, patrol_range=150)
        warrior.particle_group = self.particles
        warrior.sprite_manager = self.sprite_manager
        self.enemies.add(warrior)
        self.all_sprites.add(warrior)
        
        archer = ShadowArcher(1400, 1050, patrol_range=200)
        archer.particle_group = self.particles
        archer.sprite_manager = self.sprite_manager
        self.enemies.add(archer)
        self.all_sprites.add(archer)
        
        # NEW ENEMIES - Week 5
        # Shield Guardian (tank at x=800)
        shield_guardian = ShieldGuardian(800, 1050, patrol_range=150)
        shield_guardian.particle_group = self.particles
        shield_guardian.sprite_manager = self.sprite_manager
        self.enemies.add(shield_guardian)
        self.all_sprites.add(shield_guardian)
        
        # Berserker (glass cannon at x=1200)
        berserker = Berserker(1200, 1050, patrol_range=180)
        berserker.particle_group = self.particles
        berserker.sprite_manager = self.sprite_manager
        self.enemies.add(berserker)
        self.all_sprites.add(berserker)
        
        # Fire Bat (suicide bomber at x=1000, in air)
        fire_bat = FireBat(1000, 800)
        fire_bat.particle_group = self.particles
        fire_bat.sprite_manager = self.sprite_manager
        self.enemies.add(fire_bat)
        self.all_sprites.add(fire_bat)
        
        # Boss 1 - Shadow Knight (melee boss at x=2000)
        self.boss1 = ShadowKnight(2000, 1050)
        self.boss1_active = False
        
        # Boss 2 - Arcane Sorcerer (ranged boss at x=3500)
        self.boss2 = ArcaneSorcerer(3500, 1050)
        self.boss2_active = False
        
        # Current active boss reference
        self.current_boss = None
        self.boss_active = False
        
        # Add decorations
        for i in range(5):
            crystal = DecorativeElement(400 + i * 300, 1070, 'crystal')
            self.decorations.add(crystal)
            self.all_sprites.add(crystal)
    
    def handle_events(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    
                # Toggle player menu (TAB)
                if event.key == pygame.K_TAB and self.player_menu:
                    self.paused = not self.paused
                
                # Toggle spatial partition debug (F3)
                if event.key == pygame.K_F3:
                    self.spatial_debug = not self.spatial_debug
                    self.spatial_partition.toggle_debug()
                
                # Level up UI input
                if self.show_level_up and self.level_up_ui:
                    if event.key == pygame.K_1:
                        self.player.stats.add_attribute('strength')
                        self.show_level_up = False
                        self.paused = False
                    elif event.key == pygame.K_2:
                        self.player.stats.add_attribute('dexterity')
                        self.show_level_up = False
                        self.paused = False
                    elif event.key == pygame.K_3:
                        self.player.stats.add_attribute('intelligence')
                        self.show_level_up = False
                        self.paused = False
                    elif event.key == pygame.K_4:
                        self.player.stats.add_attribute('vitality')
                        self.show_level_up = False
                        self.paused = False
            
            # Player menu input
            if self.paused and self.player_menu:
                self.player_menu.handle_event(event)
            
            # Combat input - Hollow Knight style (keyboard only)
            if event.type == pygame.KEYDOWN and not self.paused:
                # Get current key state for checking up
                current_keys = pygame.key.get_pressed()
                is_up_attack = current_keys[pygame.K_w] or current_keys[pygame.K_UP]
                
                # Attack on Z, X, or J key (Hollow Knight uses Z/X)
                if event.key in [pygame.K_z, pygame.K_x, pygame.K_j]:
                    try:
                        # Determine attack type
                        # X or heavy key = heavy attack
                        is_heavy = event.key == pygame.K_x
                        
                        # Try to start attack
                        if self.player.combat.try_attack('heavy' if is_heavy else 'light', is_up_attack):
                            # Consume stamina
                            stamina_cost = 20 if is_heavy else 10
                            if self.player.stats.can_afford_stamina(stamina_cost):
                                self.player.stats.use_stamina(stamina_cost)
                    except Exception as e:
                        print(f"Combat input error: {e}")
                        import traceback
                        traceback.print_exc()
            
            # Weapon switching hotkeys
            if event.type == pygame.KEYDOWN and not self.paused:
                weapon_switched = False
                if event.key == pygame.K_1:
                    self.player.weapon_manager.switch_weapon('sword')
                    self.player.current_weapon = self.player.weapon_manager.get_current_weapon()
                    weapon_switched = True
                elif event.key == pygame.K_2:
                    self.player.weapon_manager.switch_weapon('dagger')
                    self.player.current_weapon = self.player.weapon_manager.get_current_weapon()
                    weapon_switched = True
                elif event.key == pygame.K_3:
                    self.player.weapon_manager.switch_weapon('greatsword')
                    self.player.current_weapon = self.player.weapon_manager.get_current_weapon()
                    weapon_switched = True
                elif event.key == pygame.K_4:
                    self.player.weapon_manager.switch_weapon('spear')
                    self.player.current_weapon = self.player.weapon_manager.get_current_weapon()
                    weapon_switched = True
                elif event.key == pygame.K_5:
                    self.player.weapon_manager.switch_weapon('hammer')
                    self.player.current_weapon = self.player.weapon_manager.get_current_weapon()
                    weapon_switched = True
                
                # Trigger weapon switch animation
                if weapon_switched and self.combat_hud:
                    self.combat_hud.trigger_weapon_switch()
                elif event.key == pygame.K_5:
                    self.player.weapon_manager.switch_weapon('hammer')
                    self.player.current_weapon = self.player.weapon_manager.get_current_weapon()
    
    def update(self):
        """Update game state"""
        if self.paused:
            return
        
        # Update audio systems
        self.music_manager.update()
        
        # Update listener position for spatial audio (follow camera/player)
        self.sound_manager.set_listener_position(
            self.player.rect.centerx,
            self.player.rect.centery
        )
        
        # Rebuild spatial partition with current entity positions
        all_collidable = list(self.enemies) + list(self.platforms) + list(self.coins) + list(self.projectiles)
        self.spatial_partition.rebuild(all_collidable)
        
        # Update player
        result = self.player.update(self.platforms, self.coins)
        
        # Check for level up
        if result == 'level_up':
            self.show_level_up = True
            self.paused = True
        
        # Update camera
        self.camera.update(self.player)
        
        # Update enemies - use spatial partition for nearby platforms
        for enemy in self.enemies:
            # Get nearby platforms instead of checking all platforms
            nearby_platforms = self.spatial_partition.query(enemy.rect.inflate(100, 100))
            nearby_platforms = [p for p in nearby_platforms if isinstance(p, Platform)]
            
            if isinstance(enemy, (HollowWarrior, DementorEnemy)):
                enemy.update(self.player, nearby_platforms)
            elif isinstance(enemy, ShadowArcher):
                enemy.update(self.player, nearby_platforms, self.projectiles)
            elif isinstance(enemy, (ShieldGuardian, Berserker)):
                # New enemies use same update signature
                enemy.update(self.player, nearby_platforms)
            elif isinstance(enemy, FireBat):
                # Fire Bat doesn't need platforms (flying)
                enemy.update(self.player)
        
        # Update projectiles with spatial partition
        for projectile in self.projectiles:
            nearby_platforms = self.spatial_partition.query(projectile.rect.inflate(50, 50))
            nearby_platforms = [p for p in nearby_platforms if isinstance(p, Platform)]
            projectile.update(nearby_platforms)
        
        # Update boss system (check both bosses)
        # Boss 1 - Shadow Knight
        if not self.boss1_active and abs(self.player.rect.centerx - self.boss1.rect.centerx) < 400:
            self.boss1_active = True
            self.current_boss = self.boss1
            self.boss_active = True
            self.current_boss.play_intro()
            if self.boss_health_bar:
                phase_thresholds = [phase.health_threshold for phase in self.current_boss.phases]
                self.boss_health_bar.activate(self.current_boss.name, phase_thresholds)
        
        # Boss 2 - Arcane Sorcerer
        if not self.boss2_active and abs(self.player.rect.centerx - self.boss2.rect.centerx) < 400:
            self.boss2_active = True
            self.current_boss = self.boss2
            self.boss_active = True
            self.current_boss.play_intro()
            if self.boss_health_bar:
                phase_thresholds = [phase.health_threshold for phase in self.current_boss.phases]
                self.boss_health_bar.activate(self.current_boss.name, phase_thresholds)
        
        # Update active boss
        if self.boss_active and self.current_boss:
            nearby_platforms = self.spatial_partition.query(self.current_boss.rect.inflate(200, 400))
            nearby_platforms = [p for p in nearby_platforms if isinstance(p, Platform)]
            self.current_boss.update(self.player, nearby_platforms)
            
            # Update boss health bar
            if self.boss_health_bar:
                self.boss_health_bar.update(self.current_boss)
        
        # Check player combat hits - Hollow Knight style
        # Only check hits during active frames
        if self.player.combat.is_attacking:
            try:
                # Get hitbox from new combat system
                attack_hitbox = self.player.combat.get_hitbox()
                
                if attack_hitbox:
                    # Spatial partition query for performance (only check nearby enemies)
                    nearby_entities = self.spatial_partition.query(attack_hitbox)
                    nearby_enemies = [e for e in nearby_entities if e in self.enemies]
                    
                    # Check each enemy for collision using combat system
                    for enemy in nearby_enemies:
                        # Use combat system's check_hit (handles hit tracking)
                        if self.player.combat.check_hit(enemy):
                            # Calculate damage
                            damage = self.player.combat.get_damage()
                            
                            # Apply damage to enemy
                            enemy.take_damage(damage)
                            
                            # Knockback
                            knockback_x = 8 if self.player.facing_right else -8
                            knockback_y = -3
                            if hasattr(enemy, 'velocity_x'):
                                enemy.velocity_x = knockback_x
                                enemy.velocity_y = knockback_y
                            
                            # Visual feedback already handled by combat system
                            
                    # Check boss hit
                    if self.current_boss and attack_hitbox.colliderect(self.current_boss.rect):
                        if self.player.combat.check_hit(self.current_boss):
                            damage = self.player.combat.get_damage()
                            self.current_boss.take_damage(damage)
                            
                            # Knockback for boss
                            knockback_x = 5 if self.player.facing_right else -5
                            if hasattr(self.current_boss, 'velocity_x'):
                                self.current_boss.velocity_x = knockback_x
                        
            except Exception as e:
                print(f"Combat hit detection error: {e}")
                import traceback
                traceback.print_exc()
        
        # Check boss hitting player
        if self.boss_active and self.current_boss and not self.current_boss.is_defeated:
            boss_hitbox = self.current_boss.get_attack_hitbox()
            if boss_hitbox and boss_hitbox.colliderect(self.player.rect):
                if self.current_boss.current_attack:
                    damage = self.current_boss.current_attack.damage
                    self.player.stats.take_damage(damage)
                    # Knockback player
                    knockback_direction = 1 if self.current_boss.facing_right else -1
                    self.player.velocity_x += knockback_direction * 10
                    self.player.velocity_y = -8
        
        # Check Arcane Sorcerer projectiles hitting player
        if self.boss_active and self.current_boss and isinstance(self.current_boss, ArcaneSorcerer):
            for projectile in self.current_boss.get_projectiles():
                if projectile.active and projectile.rect.colliderect(self.player.rect):
                    self.player.stats.take_damage(projectile.damage)
                    projectile.active = False
                    # Small knockback
                    dx = self.player.rect.centerx - projectile.rect.centerx
                    knockback_dir = 1 if dx > 0 else -1
                    self.player.velocity_x += knockback_dir * 5
                    self.player.velocity_y = -5
        
        # Check enemy attacks on player
        for enemy in self.enemies:
            # Check for Fire Bat explosion
            if isinstance(enemy, FireBat) and hasattr(enemy, 'get_explosion_hitbox'):
                explosion_hitbox = enemy.get_explosion_hitbox()
                if explosion_hitbox and explosion_hitbox.colliderect(self.player.rect):
                    damage = enemy.get_explosion_damage()
                    self.player.take_damage(damage)
                    # Explosion knockback
                    dx = self.player.rect.centerx - enemy.rect.centerx
                    dy = self.player.rect.centery - enemy.rect.centery
                    distance = max(1, (dx**2 + dy**2)**0.5)
                    knockback_force = 10
                    self.player.velocity_x += (dx / distance) * knockback_force
                    self.player.velocity_y += (dy / distance) * knockback_force
            # Check for attack hitbox (new enemies like Shield Guardian and Berserker)
            elif hasattr(enemy, 'get_attack_hitbox'):
                attack_hitbox = enemy.get_attack_hitbox()
                if attack_hitbox and attack_hitbox.colliderect(self.player.rect):
                    damage = enemy.get_attack_damage() if hasattr(enemy, 'get_attack_damage') else 10
                    self.player.take_damage(damage)
            # Fallback for old enemy types
            elif enemy.rect.colliderect(self.player.rect):
                if hasattr(enemy, 'is_attacking') and enemy.is_attacking:
                    damage = getattr(enemy, 'attack_damage', 10)
                    self.player.take_damage(damage)
        
        # Check projectile hits on player
        projectile_hits = pygame.sprite.spritecollide(self.player, self.projectiles, True)
        for proj in projectile_hits:
            self.player.take_damage(proj.damage)
        
        # Update particles
        self.particles.update()
        
        # Update decorations
        self.decorations.update()
        
        # Update combat systems
        self.screen_shake.update()
        self.hit_freeze.update()
    
    def draw(self):
        """Draw everything"""
        from src.core.constants import SKY_BLUE
        
        # Background
        self.screen.fill(SKY_BLUE)
        
        # Draw parallax layers
        for layer in self.parallax_layers:
            offset_x, offset_y = layer.get_offset(self.camera.x, self.camera.y)
            # Simple gradient for parallax effect
            color_shift = int(layer.scroll_speed * 50)
            bg_color = (
                max(0, SKY_BLUE[0] - color_shift),
                max(0, SKY_BLUE[1] - color_shift),
                max(0, SKY_BLUE[2] - color_shift)
            )
            pygame.draw.rect(self.screen, bg_color, (0, int(offset_y), SCREEN_WIDTH, 200))
        
        # Draw decorations
        for decoration in self.decorations:
            self.screen.blit(decoration.image, self.camera.apply(decoration))
        
        # Draw platforms
        for platform in self.platforms:
            self.screen.blit(platform.image, self.camera.apply(platform))
        
        # Draw coins
        for coin in self.coins:
            self.screen.blit(coin.image, self.camera.apply(coin))
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera)
        
        # Draw boss (if active)
        if self.boss_active and self.current_boss:
            self.current_boss.draw(self.screen, self.camera)
        
        # Draw projectiles
        for proj in self.projectiles:
            self.screen.blit(proj.image, self.camera.apply(proj))
        
        # Draw player (with camera for combat particles)
        player_screen_pos = self.camera.apply(self.player)
        self.player.draw(self.screen, player_screen_pos, self.camera)
        
        # Draw particles
        for particle in self.particles:
            particle_pos = self.camera.apply_pos(particle.rect.x, particle.rect.y)
            temp_rect = particle.rect.copy()
            particle.rect.x = particle_pos[0]
            particle.rect.y = particle_pos[1]
            self.screen.blit(particle.image, particle.rect)
            particle.rect = temp_rect
        
        # Draw spatial partition debug (F3 to toggle)
        if self.spatial_debug:
            self.spatial_partition.draw_debug(self.screen, self.camera)
            # Draw stats
            stats = self.spatial_partition.get_stats()
            debug_font = pygame.font.Font(None, 24)
            debug_text = f"Quadtree Nodes: {stats['total_nodes']} | Max Depth: {stats['max_depth']}"
            debug_surface = debug_font.render(debug_text, True, (0, 255, 0))
            self.screen.blit(debug_surface, (10, 100))
        
        # Draw UI
        self.draw_ui()
        
        # Draw boss health bar (on top of everything)
        if self.boss_active and self.boss_health_bar:
            self.boss_health_bar.draw(self.screen)
        
        pygame.display.flip()
    
    def draw_ui(self):
        """Draw UI elements"""
        # Health bar
        bar_width = 200
        bar_height = 20
        bar_x = 20
        bar_y = 20
        
        # Background
        pygame.draw.rect(self.screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))
        
        # Health
        health_percent = self.player.stats.current_health / self.player.stats.max_health
        health_width = int(bar_width * health_percent)
        pygame.draw.rect(self.screen, (200, 50, 50), (bar_x, bar_y, health_width, bar_height))
        
        # Border
        pygame.draw.rect(self.screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Health text
        health_text = self.font.render(f"HP: {int(self.player.stats.current_health)}/{int(self.player.stats.max_health)}", 
                                       True, (255, 255, 255))
        self.screen.blit(health_text, (bar_x + 5, bar_y - 2))
        
        # Level and XP
        level_text = self.font.render(f"Level {self.player.stats.level}", True, self.gold_color)
        self.screen.blit(level_text, (bar_x, bar_y + 30))
        
        xp_text = self.font.render(f"XP: {self.player.stats.current_xp}/{self.player.stats.xp_to_next_level}", 
                                   True, (200, 200, 200))
        self.screen.blit(xp_text, (bar_x, bar_y + 60))
        
        # Score
        score_text = self.font.render(f"Score: {self.player.score}", True, self.gold_color)
        self.screen.blit(score_text, (SCREEN_WIDTH - 250, 20))
        
        # Level up UI
        if self.show_level_up and self.level_up_ui:
            self.level_up_ui.draw(self.screen, self.player.stats)
        
        # Combat HUD (stamina, weapon, combo)
        if self.combat_hud:
            self.combat_hud.draw(self.screen, self.player)
        
        # Player menu
        if self.paused and self.player_menu:
            self.player_menu.draw(self.screen)
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            
            # Always update core systems (weapon state machines, combat timing)
            # Even during hit freeze to prevent state machine bugs
            self.update()
            
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


def main():
    """Entry point for the game"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
