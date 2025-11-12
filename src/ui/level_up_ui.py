"""
Level-Up UI Overlay
Displays when player levels up, allows attribute point allocation
"""

import pygame


class LevelUpUI:
    """
    UI overlay for spending attribute points after leveling up
    """
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.is_open = False
        self.player_stats = None
        
        # UI dimensions
        self.panel_width = 600
        self.panel_height = 500
        self.panel_x = (screen_width - self.panel_width) // 2
        self.panel_y = (screen_height - self.panel_height) // 2
        
        # Colors
        self.bg_color = (20, 22, 35, 230)  # Semi-transparent dark
        self.border_color = (100, 120, 200)
        self.text_color = (220, 220, 240)
        self.highlight_color = (150, 200, 255)
        self.gold_color = (255, 215, 0)
        self.button_color = (60, 70, 100)
        self.button_hover_color = (80, 100, 140)
        
        # Fonts
        try:
            self.title_font = pygame.font.Font(None, 48)
            self.header_font = pygame.font.Font(None, 36)
            self.stat_font = pygame.font.Font(None, 28)
            self.small_font = pygame.font.Font(None, 22)
        except:
            self.title_font = pygame.font.SysFont('arial', 48, bold=True)
            self.header_font = pygame.font.SysFont('arial', 36, bold=True)
            self.stat_font = pygame.font.SysFont('arial', 28)
            self.small_font = pygame.font.SysFont('arial', 22)
        
        # Buttons for each attribute
        self.attribute_buttons = {}
        button_width = 40
        button_height = 40
        start_y = self.panel_y + 180
        spacing = 70
        
        attributes = ['strength', 'dexterity', 'intelligence', 'vitality']
        for i, attr in enumerate(attributes):
            button_x = self.panel_x + self.panel_width - 100
            button_y = start_y + (i * spacing)
            self.attribute_buttons[attr] = {
                'rect': pygame.Rect(button_x, button_y, button_width, button_height),
                'hovered': False
            }
        
        # Close button
        self.close_button = {
            'rect': pygame.Rect(self.panel_x + self.panel_width - 100, 
                              self.panel_y + self.panel_height - 60, 80, 40),
            'hovered': False,
            'text': 'Close'
        }
        
        # Animation
        self.animation_timer = 0
        self.particle_effects = []
    
    def open(self, player_stats):
        """Open the level-up UI with player stats"""
        self.is_open = True
        self.player_stats = player_stats
        self.animation_timer = 0
        self.create_level_up_particles()
    
    def close(self):
        """Close the level-up UI"""
        self.is_open = False
        self.player_stats = None
    
    def create_level_up_particles(self):
        """Create particle burst effect for level-up"""
        import random
        self.particle_effects = []
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        for _ in range(30):
            angle = random.uniform(0, 360)
            speed = random.uniform(2, 6)
            self.particle_effects.append({
                'x': center_x,
                'y': center_y,
                'vx': speed * pygame.math.Vector2(1, 0).rotate(angle).x,
                'vy': speed * pygame.math.Vector2(0, 1).rotate(angle).y,
                'life': random.randint(30, 60),
                'color': self.gold_color
            })
    
    def handle_event(self, event):
        """Handle mouse events"""
        if not self.is_open or not self.player_stats:
            return False
        
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            
            # Update button hover states
            for attr, button_data in self.attribute_buttons.items():
                button_data['hovered'] = button_data['rect'].collidepoint(mouse_pos)
            
            self.close_button['hovered'] = self.close_button['rect'].collidepoint(mouse_pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = event.pos
                
                # Check attribute buttons
                for attr, button_data in self.attribute_buttons.items():
                    if button_data['rect'].collidepoint(mouse_pos):
                        if self.player_stats.add_attribute_point(attr):
                            # Success sound would go here
                            print(f"Added point to {attr}")
                        return True
                
                # Check close button
                if self.close_button['rect'].collidepoint(mouse_pos):
                    self.close()
                    return True
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                self.close()
                return True
        
        return False
    
    def update(self):
        """Update animations"""
        if not self.is_open:
            return
        
        self.animation_timer += 1
        
        # Update particles
        for particle in self.particle_effects[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.2  # Gravity
            particle['life'] -= 1
            
            if particle['life'] <= 0:
                self.particle_effects.remove(particle)
    
    def draw(self, screen):
        """Draw the level-up UI overlay"""
        if not self.is_open or not self.player_stats:
            return
        
        # Draw particles
        for particle in self.particle_effects:
            alpha = int(255 * (particle['life'] / 60))
            size = max(2, int(4 * (particle['life'] / 60)))
            particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, (*particle['color'], alpha), (size, size), size)
            screen.blit(particle_surf, (int(particle['x']) - size, int(particle['y']) - size))
        
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Main panel
        panel_surf = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
        panel_surf.fill(self.bg_color)
        pygame.draw.rect(panel_surf, self.border_color, (0, 0, self.panel_width, self.panel_height), 3)
        
        # Title
        title_text = self.title_font.render("LEVEL UP!", True, self.gold_color)
        title_rect = title_text.get_rect(centerx=self.panel_width // 2, top=20)
        panel_surf.blit(title_text, title_rect)
        
        # Level display
        level_text = self.header_font.render(f"Level {self.player_stats.level}", True, self.highlight_color)
        level_rect = level_text.get_rect(centerx=self.panel_width // 2, top=70)
        panel_surf.blit(level_text, level_rect)
        
        # Available points
        points_text = self.stat_font.render(
            f"Available Attribute Points: {self.player_stats.attribute_points}", 
            True, self.gold_color if self.player_stats.attribute_points > 0 else self.text_color
        )
        points_rect = points_text.get_rect(centerx=self.panel_width // 2, top=120)
        panel_surf.blit(points_text, points_rect)
        
        # Attributes
        start_y = 180
        spacing = 70
        
        attributes = [
            ('Strength', 'strength', f"Melee damage, HP, carry weight"),
            ('Dexterity', 'dexterity', f"Attack speed, dodge, accuracy"),
            ('Intelligence', 'intelligence', f"Magic damage, mana, resistances"),
            ('Vitality', 'vitality', f"Max health, health regen, defense")
        ]
        
        for i, (name, attr_key, description) in enumerate(attributes):
            y_pos = start_y + (i * spacing)
            
            # Attribute name
            attr_text = self.stat_font.render(name, True, self.text_color)
            panel_surf.blit(attr_text, (40, y_pos))
            
            # Current value
            value = getattr(self.player_stats, attr_key)
            value_text = self.header_font.render(str(value), True, self.highlight_color)
            panel_surf.blit(value_text, (250, y_pos - 5))
            
            # Description
            desc_text = self.small_font.render(description, True, (180, 180, 200))
            panel_surf.blit(desc_text, (40, y_pos + 28))
            
            # + Button (relative to panel)
            button = self.attribute_buttons[attr_key]
            button_rect_local = button['rect'].copy()
            button_rect_local.x -= self.panel_x
            button_rect_local.y -= self.panel_y
            
            button_color = self.button_hover_color if button['hovered'] else self.button_color
            if self.player_stats.attribute_points <= 0:
                button_color = (40, 40, 50)  # Disabled
            
            pygame.draw.rect(panel_surf, button_color, button_rect_local, border_radius=5)
            pygame.draw.rect(panel_surf, self.border_color, button_rect_local, 2, border_radius=5)
            
            plus_text = self.header_font.render("+", True, self.text_color)
            plus_rect = plus_text.get_rect(center=button_rect_local.center)
            panel_surf.blit(plus_text, plus_rect)
        
        # Close button
        close_rect_local = self.close_button['rect'].copy()
        close_rect_local.x -= self.panel_x
        close_rect_local.y -= self.panel_y
        
        close_color = self.button_hover_color if self.close_button['hovered'] else self.button_color
        pygame.draw.rect(panel_surf, close_color, close_rect_local, border_radius=5)
        pygame.draw.rect(panel_surf, self.border_color, close_rect_local, 2, border_radius=5)
        
        close_text = self.stat_font.render(self.close_button['text'], True, self.text_color)
        close_text_rect = close_text.get_rect(center=close_rect_local.center)
        panel_surf.blit(close_text, close_text_rect)
        
        # Blit panel to screen
        screen.blit(panel_surf, (self.panel_x, self.panel_y))
