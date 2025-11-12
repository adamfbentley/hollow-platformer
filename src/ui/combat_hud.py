"""
Combat HUD - Stamina, Weapon Indicator, and Combo Display
Professional UI for the combat system
"""

import pygame
from typing import Optional


class CombatHUD:
    """
    Professional combat HUD showing stamina, weapon, and combo info
    Similar to Hollow Knight's minimalist yet informative UI
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        """
        Initialize combat HUD
        
        Args:
            screen_width: Width of the game screen
            screen_height: Height of the game screen
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Font initialization
        pygame.font.init()
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_large = pygame.font.Font(None, 48)
        
        # HUD positioning (top-left corner near health/XP bars)
        self.hud_x = 30
        self.health_bar_y = 30  # Health bar position
        self.xp_bar_y = 70      # XP bar position
        self.stamina_bar_y = 110  # Stamina bar below XP
        
        # Stamina bar dimensions
        self.stamina_bar_width = 200
        self.stamina_bar_height = 20
        
        # Weapon indicator positioning (below stamina)
        self.weapon_indicator_y = 145
        
        # Combo counter positioning (center-top)
        self.combo_x = screen_width // 2
        self.combo_y = 100
        
        # Animation timers
        self.combo_flash_timer = 0
        self.combo_flash_duration = 30  # frames
        self.weapon_switch_timer = 0
        self.weapon_switch_duration = 60  # frames
        
        # Colors
        self.COLOR_STAMINA_FULL = (100, 255, 100)    # Bright green
        self.COLOR_STAMINA_MED = (255, 255, 100)     # Yellow
        self.COLOR_STAMINA_LOW = (255, 100, 100)     # Red
        self.COLOR_STAMINA_EMPTY = (80, 80, 80)      # Dark gray
        self.COLOR_STAMINA_DELAY = (255, 150, 50)    # Orange (regen delay)
        self.COLOR_OUTLINE = (40, 40, 40)            # Dark outline
        self.COLOR_BACKGROUND = (20, 20, 20, 180)    # Semi-transparent bg
        self.COLOR_TEXT = (255, 255, 255)            # White text
        self.COLOR_TEXT_DIM = (180, 180, 180)        # Dim text
        self.COLOR_COMBO = (255, 200, 50)            # Gold for combo
        
    def draw_stamina_bar(self, surface: pygame.Surface, current_stamina: float, 
                        max_stamina: float, regen_delay: int, exhausted: bool):
        """
        Draw stamina bar with color gradient and regen delay indicator
        
        Args:
            surface: Surface to draw on
            current_stamina: Current stamina value
            max_stamina: Maximum stamina value
            regen_delay: Current regen delay counter
            exhausted: Whether player is exhausted
        """
        # Calculate stamina percentage
        stamina_percent = current_stamina / max_stamina if max_stamina > 0 else 0
        
        # Background bar (dark)
        bg_rect = pygame.Rect(
            self.hud_x, 
            self.stamina_bar_y, 
            self.stamina_bar_width, 
            self.stamina_bar_height
        )
        pygame.draw.rect(surface, self.COLOR_OUTLINE, bg_rect.inflate(4, 4))
        pygame.draw.rect(surface, self.COLOR_BACKGROUND, bg_rect)
        
        # Foreground bar (colored based on stamina level)
        if stamina_percent > 0:
            # Color interpolation based on stamina level
            if stamina_percent > 0.6:
                color = self.COLOR_STAMINA_FULL
            elif stamina_percent > 0.3:
                # Interpolate between green and yellow
                t = (stamina_percent - 0.3) / 0.3
                color = self._lerp_color(self.COLOR_STAMINA_MED, self.COLOR_STAMINA_FULL, t)
            else:
                # Interpolate between red and yellow
                t = stamina_percent / 0.3
                color = self._lerp_color(self.COLOR_STAMINA_LOW, self.COLOR_STAMINA_MED, t)
            
            # Add pulsing effect when exhausted
            if exhausted:
                pulse = abs((pygame.time.get_ticks() % 1000) / 500 - 1)  # 0 to 1 to 0
                color = self._lerp_color(self.COLOR_STAMINA_LOW, (255, 50, 50), pulse * 0.5)
            
            stamina_width = int(self.stamina_bar_width * stamina_percent)
            stamina_rect = pygame.Rect(
                self.hud_x, 
                self.stamina_bar_y, 
                stamina_width, 
                self.stamina_bar_height
            )
            pygame.draw.rect(surface, color, stamina_rect)
        
        # Regen delay indicator (orange overlay on right side)
        if regen_delay > 0:
            delay_text = self.font_small.render("!", True, self.COLOR_STAMINA_DELAY)
            delay_pos = (
                self.hud_x + self.stamina_bar_width + 10,
                self.stamina_bar_y
            )
            surface.blit(delay_text, delay_pos)
        
        # Stamina text (current/max)
        stamina_text = f"{int(current_stamina)}/{int(max_stamina)}"
        text_surface = self.font_small.render(stamina_text, True, self.COLOR_TEXT)
        text_rect = text_surface.get_rect(
            midleft=(self.hud_x + self.stamina_bar_width + 30, 
                    self.stamina_bar_y + self.stamina_bar_height // 2)
        )
        surface.blit(text_surface, text_rect)
        
        # "STAMINA" label
        label = self.font_small.render("STAMINA", True, self.COLOR_TEXT_DIM)
        label_rect = label.get_rect(
            bottomleft=(self.hud_x, self.stamina_bar_y - 5)
        )
        surface.blit(label, label_rect)
    
    def draw_weapon_indicator(self, surface: pygame.Surface, weapon_name: str, 
                             weapon_damage: int, weapon_type: str, hotkey: str,
                             attack_speed: float, stamina_cost_light: int, 
                             stamina_cost_heavy: int):
        """
        Draw current weapon information
        
        Args:
            surface: Surface to draw on
            weapon_name: Name of the weapon
            weapon_damage: Base damage
            weapon_type: Type of weapon (sword, dagger, etc.)
            hotkey: Hotkey to activate (1-5)
            attack_speed: Attack speed multiplier
            stamina_cost_light: Light attack stamina cost
            stamina_cost_heavy: Heavy attack stamina cost
        """
        y_pos = self.weapon_indicator_y
        
        # Weapon name (larger, bold)
        name_surface = self.font_medium.render(weapon_name.upper(), True, self.COLOR_TEXT)
        name_rect = name_surface.get_rect(topleft=(self.hud_x, y_pos))
        surface.blit(name_surface, name_rect)
        
        # Hotkey indicator (small, in brackets)
        hotkey_text = f"[{hotkey}]"
        hotkey_surface = self.font_small.render(hotkey_text, True, self.COLOR_TEXT_DIM)
        hotkey_rect = hotkey_surface.get_rect(
            midleft=(name_rect.right + 10, name_rect.centery)
        )
        surface.blit(hotkey_surface, hotkey_rect)
        
        # Weapon switch animation (flash effect)
        if self.weapon_switch_timer > 0:
            self.weapon_switch_timer -= 1
            alpha = int((self.weapon_switch_timer / self.weapon_switch_duration) * 100)
            flash_surface = pygame.Surface((300, 80), pygame.SRCALPHA)
            flash_surface.fill((255, 200, 50, alpha))
            surface.blit(flash_surface, (self.hud_x - 10, y_pos - 10))
        
        # Stats (small text below name)
        stats_y = y_pos + 35
        
        # Damage
        dmg_text = f"DMG: {weapon_damage}"
        dmg_surface = self.font_small.render(dmg_text, True, self.COLOR_TEXT_DIM)
        surface.blit(dmg_surface, (self.hud_x, stats_y))
        
        # Attack speed
        speed_text = f"SPD: {attack_speed:.1f}x"
        speed_surface = self.font_small.render(speed_text, True, self.COLOR_TEXT_DIM)
        surface.blit(speed_surface, (self.hud_x + 80, stats_y))
        
        # Stamina costs
        stamina_text = f"L:{stamina_cost_light} H:{stamina_cost_heavy}"
        stamina_surface = self.font_small.render(stamina_text, True, self.COLOR_TEXT_DIM)
        surface.blit(stamina_surface, (self.hud_x + 170, stats_y))
    
    def draw_combo_counter(self, surface: pygame.Surface, combo_count: int, 
                          combo_timer: int, combo_window: int, is_active: bool):
        """
        Draw combo counter in center-top of screen
        
        Args:
            surface: Surface to draw on
            combo_count: Current combo count
            combo_timer: Current combo timer
            combo_window: Max combo window duration
            is_active: Whether combo is currently active
        """
        if not is_active or combo_count <= 1:
            # Don't show for single hits
            return
        
        # Combo text with hits
        combo_text = f"{combo_count} HIT COMBO!"
        
        # Scale text based on combo count (bigger = better)
        scale = 1.0 + (min(combo_count, 10) * 0.1)  # Up to 2x at 10 hits
        font_size = int(48 * scale)
        combo_font = pygame.font.Font(None, font_size)
        
        # Flash effect when combo increases
        if self.combo_flash_timer > 0:
            self.combo_flash_timer -= 1
            flash_intensity = self.combo_flash_timer / self.combo_flash_duration
            color = self._lerp_color(self.COLOR_COMBO, (255, 255, 255), flash_intensity)
        else:
            color = self.COLOR_COMBO
        
        # Main combo text
        text_surface = combo_font.render(combo_text, True, color)
        text_rect = text_surface.get_rect(center=(self.combo_x, self.combo_y))
        
        # Outline for visibility
        outline_surface = combo_font.render(combo_text, True, (0, 0, 0))
        for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
            outline_rect = text_surface.get_rect(center=(self.combo_x + dx, self.combo_y + dy))
            surface.blit(outline_surface, outline_rect)
        
        surface.blit(text_surface, text_rect)
        
        # Combo timer bar (shows remaining time)
        if combo_timer > 0:
            timer_percent = combo_timer / combo_window
            bar_width = 200
            bar_height = 6
            bar_x = self.combo_x - bar_width // 2
            bar_y = self.combo_y + 40
            
            # Background
            bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
            pygame.draw.rect(surface, (40, 40, 40), bg_rect)
            
            # Foreground (timer)
            timer_width = int(bar_width * timer_percent)
            timer_color = self._lerp_color((255, 50, 50), (255, 200, 50), timer_percent)
            timer_rect = pygame.Rect(bar_x, bar_y, timer_width, bar_height)
            pygame.draw.rect(surface, timer_color, timer_rect)
    
    def trigger_combo_flash(self):
        """Trigger flash animation when combo increases"""
        self.combo_flash_timer = self.combo_flash_duration
    
    def trigger_weapon_switch(self):
        """Trigger flash animation when weapon switches"""
        self.weapon_switch_timer = self.weapon_switch_duration
    
    def _lerp_color(self, color1: tuple, color2: tuple, t: float) -> tuple:
        """
        Linear interpolation between two colors
        
        Args:
            color1: First color (R, G, B)
            color2: Second color (R, G, B)
            t: Interpolation factor (0 to 1)
            
        Returns:
            Interpolated color
        """
        return (
            int(color1[0] + (color2[0] - color1[0]) * t),
            int(color1[1] + (color2[1] - color1[1]) * t),
            int(color1[2] + (color2[2] - color1[2]) * t)
        )
    
    def draw(self, surface: pygame.Surface, player):
        """
        Draw all combat HUD elements
        
        Args:
            surface: Surface to draw on
            player: Player object with stats, weapon, and combat info
        """
        # Stamina bar
        self.draw_stamina_bar(
            surface,
            player.stats.current_stamina,
            player.stats.max_stamina,
            player.stats.stamina_regen_delay,
            player.stats.is_exhausted()
        )
        
        # Weapon indicator
        if player.current_weapon:
            weapon = player.current_weapon
            weapon_hotkeys = {
                'sword': '1',
                'dagger': '2',
                'greatsword': '3',
                'spear': '4',
                'hammer': '5'
            }
            hotkey = weapon_hotkeys.get(weapon.name.lower(), '?')
            
            self.draw_weapon_indicator(
                surface,
                weapon.name,
                weapon.base_damage,
                weapon.weapon_type,
                hotkey,
                weapon.attack_speed,
                weapon.stamina_light,
                weapon.stamina_heavy
            )
        
        # Combo counter (if active and combo > 1)
        if player.combat.is_attacking and player.combat.combo_count > 1:
            self.draw_combo_counter(
                surface,
                player.combat.combo_count,
                player.combat.combo_timer,
                player.combat.combo_window,
                True
            )
