"""
Enhanced Player Menu with Tabbed Interface
Combines character stats and inventory in a polished fantasy-themed UI
"""

import pygame


class EnhancedPlayerMenu:
    """
    Tabbed player menu with Character Stats and Inventory tabs
    Fantasy aesthetic with perfect text alignment
    """
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.is_open = False
        self.current_tab = "character"  # "character" or "inventory"
        self.player_stats = None
        self.player_inventory = None
        
        # UI Layout
        self.panel_width = 1400
        self.panel_height = 800
        self.panel_x = (screen_width - self.panel_width) // 2
        self.panel_y = (screen_height - self.panel_height) // 2
        
        # Tab dimensions
        self.tab_width = 200
        self.tab_height = 50
        self.tab_y = self.panel_y + 20
        
        # Content area
        self.content_x = self.panel_x + 40
        self.content_y = self.panel_y + 90
        self.content_width = self.panel_width - 80
        self.content_height = self.panel_height - 140
        
        # Fantasy color scheme (Hollow Knight inspired)
        self.bg_overlay = (0, 0, 0, 200)
        self.panel_bg = (20, 22, 35)
        self.panel_border = (120, 140, 200)
        self.tab_inactive = (35, 40, 60)
        self.tab_active = (50, 60, 85)
        self.tab_border = (80, 100, 150)
        self.text_primary = (230, 235, 250)
        self.text_secondary = (180, 190, 220)
        self.text_header = (200, 220, 255)
        self.gold_color = (255, 215, 0)
        self.accent_cyan = (100, 200, 255)
        self.stat_positive = (120, 255, 150)
        self.divider_color = (60, 70, 100)
        
        # Rarity colors
        self.rarity_colors = {
            "Common": (150, 150, 150),
            "Uncommon": (30, 255, 0),
            "Rare": (0, 112, 221),
            "Epic": (163, 53, 238),
            "Legendary": (255, 128, 0),
            "Unique": (255, 215, 0)
        }
        
        # Fonts
        self.font_title = pygame.font.Font(None, 48)
        self.font_tab = pygame.font.Font(None, 32)
        self.font_header = pygame.font.Font(None, 28)
        self.font_normal = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)
        
        # Inventory UI components
        self.slot_size = 54
        self.slot_padding = 6
        self.grid_cols = 8
        self.grid_rows = 5
        
        # Equipment slots layout (relative to content area)
        self.equipment_panel_width = 340
        self.equipment_slots = {
            "helm": (150, 30),
            "amulet": (150, 100),
            "weapon": (40, 170),
            "armor": (150, 170),
            "ring1": (40, 240),
            "ring2": (260, 240),
            "boots": (150, 310)
        }
        
        # Drag and drop state
        self.dragging = False
        self.dragged_item = None
        self.drag_source_slot = None
        self.drag_source_type = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        
        # Hover state
        self.hovered_item = None
        self.hovered_slot = None
        self.hovered_type = None
    
    def toggle(self, player_stats, player_inventory):
        """Toggle menu open/closed"""
        self.is_open = not self.is_open
        if self.is_open:
            self.player_stats = player_stats
            self.player_inventory = player_inventory
        else:
            # Cancel dragging when closing
            self.dragging = False
            self.dragged_item = None
    
    def open_to_tab(self, tab_name, player_stats, player_inventory):
        """Open menu to specific tab"""
        self.is_open = True
        self.current_tab = tab_name
        self.player_stats = player_stats
        self.player_inventory = player_inventory
    
    def close(self):
        """Close the menu"""
        self.is_open = False
        self.dragging = False
        self.dragged_item = None
    
    def switch_tab(self, tab_name):
        """Switch to different tab"""
        self.current_tab = tab_name
        self.dragging = False
        self.dragged_item = None
    
    def handle_event(self, event):
        """Handle input events"""
        if not self.is_open:
            return False
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check tab clicks
            if self.check_tab_click(mouse_pos):
                return True
            
            # Handle inventory tab interactions
            if self.current_tab == "inventory":
                return self.handle_inventory_event(event, mouse_pos)
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging and self.current_tab == "inventory":
                mouse_pos = pygame.mouse.get_pos()
                self.end_drag(mouse_pos)
                return True
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_TAB:
                self.close()
                return True
            elif event.key == pygame.K_i:
                if self.current_tab == "inventory":
                    self.close()
                else:
                    self.switch_tab("inventory")
                return True
            # Tab navigation with 1 and 2 keys
            elif event.key == pygame.K_1:
                self.switch_tab("character")
                return True
            elif event.key == pygame.K_2:
                self.switch_tab("inventory")
                return True
        
        return False
    
    def check_tab_click(self, mouse_pos):
        """Check if a tab was clicked"""
        x, y = mouse_pos
        
        # Character tab
        char_tab_x = self.panel_x + 40
        if (char_tab_x <= x <= char_tab_x + self.tab_width and
            self.tab_y <= y <= self.tab_y + self.tab_height):
            self.switch_tab("character")
            return True
        
        # Inventory tab
        inv_tab_x = char_tab_x + self.tab_width + 10
        if (inv_tab_x <= x <= inv_tab_x + self.tab_width and
            self.tab_y <= y <= self.tab_y + self.tab_height):
            self.switch_tab("inventory")
            return True
        
        return False
    
    def handle_inventory_event(self, event, mouse_pos):
        """Handle inventory-specific events"""
        # Check inventory grid click
        grid_slot = self.get_inventory_slot_at_pos(mouse_pos)
        if grid_slot is not None:
            item = self.player_inventory.get_item_at_slot(grid_slot)
            if item:
                self.start_drag(item, grid_slot, "inventory", mouse_pos)
                return True
        
        # Check equipment slot click
        equipment_slot = self.get_equipment_slot_at_pos(mouse_pos)
        if equipment_slot:
            item = self.player_inventory.get_equipped_item(equipment_slot)
            if item:
                self.start_drag(item, equipment_slot, "equipment", mouse_pos)
                return True
        
        return False
    
    def start_drag(self, item, source_slot, source_type, mouse_pos):
        """Start dragging an item"""
        self.dragging = True
        self.dragged_item = item
        self.drag_source_slot = source_slot
        self.drag_source_type = source_type
        
        if source_type == "inventory":
            slot_x, slot_y = self.get_grid_slot_position(source_slot)
        else:
            slot_x, slot_y = self.get_equipment_slot_position(source_slot)
        
        self.drag_offset_x = mouse_pos[0] - slot_x
        self.drag_offset_y = mouse_pos[1] - slot_y
    
    def end_drag(self, mouse_pos):
        """End dragging and place item"""
        if not self.dragging:
            return
        
        target_grid_slot = self.get_inventory_slot_at_pos(mouse_pos)
        target_equipment_slot = self.get_equipment_slot_at_pos(mouse_pos)
        
        if target_grid_slot is not None:
            if self.drag_source_type == "inventory":
                self.player_inventory.move_item(self.drag_source_slot, target_grid_slot)
            elif self.drag_source_type == "equipment":
                item = self.player_inventory.get_equipped_item(self.drag_source_slot)
                self.player_inventory.equipment[self.drag_source_slot] = None
                existing_item = self.player_inventory.get_item_at_slot(target_grid_slot)
                if existing_item:
                    if not self.player_inventory.add_item(item):
                        self.player_inventory.equipment[self.drag_source_slot] = item
                else:
                    self.player_inventory.grid[target_grid_slot] = item
        
        elif target_equipment_slot:
            if self.drag_source_type == "inventory":
                item = self.player_inventory.get_item_at_slot(self.drag_source_slot)
                if item.item_type == target_equipment_slot or \
                   (item.item_type == "ring" and target_equipment_slot in ["ring1", "ring2"]):
                    old_equipment = self.player_inventory.equipment[target_equipment_slot]
                    self.player_inventory.equipment[target_equipment_slot] = item
                    self.player_inventory.grid[self.drag_source_slot] = old_equipment
            elif self.drag_source_type == "equipment":
                if self.drag_source_slot != target_equipment_slot:
                    if self.drag_source_slot in ["ring1", "ring2"] and target_equipment_slot in ["ring1", "ring2"]:
                        self.player_inventory.equipment[self.drag_source_slot], self.player_inventory.equipment[target_equipment_slot] = \
                            self.player_inventory.equipment[target_equipment_slot], self.player_inventory.equipment[self.drag_source_slot]
        
        self.dragging = False
        self.dragged_item = None
        self.drag_source_slot = None
        self.drag_source_type = None
    
    def update_hover(self):
        """Update hover state for tooltips"""
        if self.dragging or self.current_tab != "inventory":
            self.hovered_item = None
            return
        
        mouse_pos = pygame.mouse.get_pos()
        
        grid_slot = self.get_inventory_slot_at_pos(mouse_pos)
        if grid_slot is not None:
            item = self.player_inventory.get_item_at_slot(grid_slot)
            if item:
                self.hovered_item = item
                self.hovered_slot = grid_slot
                self.hovered_type = "inventory"
                return
        
        equipment_slot = self.get_equipment_slot_at_pos(mouse_pos)
        if equipment_slot:
            item = self.player_inventory.get_equipped_item(equipment_slot)
            if item:
                self.hovered_item = item
                self.hovered_slot = equipment_slot
                self.hovered_type = "equipment"
                return
        
        self.hovered_item = None
        self.hovered_slot = None
        self.hovered_type = None
    
    def get_inventory_slot_at_pos(self, pos):
        """Get inventory grid slot at mouse position"""
        if self.current_tab != "inventory":
            return None
        
        x, y = pos
        grid_start_x = self.content_x + self.equipment_panel_width + 60
        grid_start_y = self.content_y + 80
        
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                slot_index = row * self.grid_cols + col
                slot_x = grid_start_x + col * (self.slot_size + self.slot_padding)
                slot_y = grid_start_y + row * (self.slot_size + self.slot_padding)
                
                if (slot_x <= x <= slot_x + self.slot_size and
                    slot_y <= y <= slot_y + self.slot_size):
                    return slot_index
        
        return None
    
    def get_equipment_slot_at_pos(self, pos):
        """Get equipment slot at mouse position"""
        if self.current_tab != "inventory":
            return None
        
        x, y = pos
        equip_base_x = self.content_x + 20
        equip_base_y = self.content_y + 80
        
        for slot_name, (offset_x, offset_y) in self.equipment_slots.items():
            slot_x = equip_base_x + offset_x
            slot_y = equip_base_y + offset_y
            
            if (slot_x <= x <= slot_x + self.slot_size and
                slot_y <= y <= slot_y + self.slot_size):
                return slot_name
        
        return None
    
    def get_grid_slot_position(self, slot_index):
        """Get screen position of inventory grid slot"""
        grid_start_x = self.content_x + self.equipment_panel_width + 60
        grid_start_y = self.content_y + 80
        
        row = slot_index // self.grid_cols
        col = slot_index % self.grid_cols
        x = grid_start_x + col * (self.slot_size + self.slot_padding)
        y = grid_start_y + row * (self.slot_size + self.slot_padding)
        return x, y
    
    def get_equipment_slot_position(self, slot_name):
        """Get screen position of equipment slot"""
        equip_base_x = self.content_x + 20
        equip_base_y = self.content_y + 80
        
        offset_x, offset_y = self.equipment_slots[slot_name]
        return equip_base_x + offset_x, equip_base_y + offset_y
    
    def draw(self, screen):
        """Draw the enhanced player menu"""
        if not self.is_open:
            return
        
        # Update hover state
        self.update_hover()
        
        # Draw overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(self.bg_overlay[3])
        screen.blit(overlay, (0, 0))
        
        # Draw main panel
        pygame.draw.rect(screen, self.panel_bg,
                        (self.panel_x, self.panel_y, self.panel_width, self.panel_height))
        pygame.draw.rect(screen, self.panel_border,
                        (self.panel_x, self.panel_y, self.panel_width, self.panel_height), 3)
        
        # Draw decorative corner accents
        self.draw_corner_accents(screen)
        
        # Draw tabs
        self.draw_tabs(screen)
        
        # Draw content based on active tab
        if self.current_tab == "character":
            self.draw_character_tab(screen)
        elif self.current_tab == "inventory":
            self.draw_inventory_tab(screen)
        
        # Draw tooltip (always on top)
        if self.hovered_item and not self.dragging:
            self.draw_tooltip(screen)
        
        # Draw dragged item (top layer)
        if self.dragging and self.dragged_item:
            self.draw_dragged_item(screen)
        
        # Draw controls hint
        self.draw_controls_hint(screen)
    
    def draw_corner_accents(self, screen):
        """Draw decorative corner accents for fantasy feel"""
        accent_size = 30
        accent_color = self.accent_cyan
        
        corners = [
            (self.panel_x, self.panel_y),
            (self.panel_x + self.panel_width, self.panel_y),
            (self.panel_x, self.panel_y + self.panel_height),
            (self.panel_x + self.panel_width, self.panel_y + self.panel_height)
        ]
        
        for i, (cx, cy) in enumerate(corners):
            if i == 0:  # Top-left
                pygame.draw.line(screen, accent_color, (cx + 5, cy + 5), (cx + accent_size, cy + 5), 2)
                pygame.draw.line(screen, accent_color, (cx + 5, cy + 5), (cx + 5, cy + accent_size), 2)
            elif i == 1:  # Top-right
                pygame.draw.line(screen, accent_color, (cx - 5, cy + 5), (cx - accent_size, cy + 5), 2)
                pygame.draw.line(screen, accent_color, (cx - 5, cy + 5), (cx - 5, cy + accent_size), 2)
            elif i == 2:  # Bottom-left
                pygame.draw.line(screen, accent_color, (cx + 5, cy - 5), (cx + accent_size, cy - 5), 2)
                pygame.draw.line(screen, accent_color, (cx + 5, cy - 5), (cx + 5, cy - accent_size), 2)
            elif i == 3:  # Bottom-right
                pygame.draw.line(screen, accent_color, (cx - 5, cy - 5), (cx - accent_size, cy - 5), 2)
                pygame.draw.line(screen, accent_color, (cx - 5, cy - 5), (cx - 5, cy - accent_size), 2)
    
    def draw_tabs(self, screen):
        """Draw tab navigation"""
        tabs = [
            ("character", "CHARACTER", self.panel_x + 40),
            ("inventory", "INVENTORY", self.panel_x + 250)
        ]
        
        for tab_id, tab_label, tab_x in tabs:
            is_active = (tab_id == self.current_tab)
            
            # Tab background
            tab_color = self.tab_active if is_active else self.tab_inactive
            pygame.draw.rect(screen, tab_color,
                           (tab_x, self.tab_y, self.tab_width, self.tab_height))
            
            # Tab border
            border_width = 3 if is_active else 2
            border_color = self.accent_cyan if is_active else self.tab_border
            pygame.draw.rect(screen, border_color,
                           (tab_x, self.tab_y, self.tab_width, self.tab_height), border_width)
            
            # Tab text
            text_color = self.text_header if is_active else self.text_secondary
            text = self.font_tab.render(tab_label, True, text_color)
            text_rect = text.get_rect(center=(tab_x + self.tab_width // 2, self.tab_y + self.tab_height // 2))
            screen.blit(text, text_rect)
            
            # Active tab indicator
            if is_active:
                pygame.draw.line(screen, self.accent_cyan,
                               (tab_x + 10, self.tab_y + self.tab_height),
                               (tab_x + self.tab_width - 10, self.tab_y + self.tab_height), 3)
    
    def draw_character_tab(self, screen):
        """Draw character stats tab"""
        if not self.player_stats:
            return
        
        stats = self.player_stats
        
        # Title
        title = self.font_title.render("CHARACTER", True, self.text_header)
        screen.blit(title, (self.content_x, self.content_y))
        
        # Divider
        pygame.draw.line(screen, self.divider_color,
                        (self.content_x, self.content_y + 50),
                        (self.content_x + self.content_width, self.content_y + 50), 2)
        
        # Two column layout
        col1_x = self.content_x + 40
        col2_x = self.content_x + self.content_width // 2 + 40
        start_y = self.content_y + 80
        
        # LEFT COLUMN - Core Info & Attributes
        y = start_y
        
        # Level and XP
        level_text = self.font_header.render(f"LEVEL {stats.level}", True, self.gold_color)
        screen.blit(level_text, (col1_x, y))
        y += 40
        
        # XP Bar
        xp_bar_width = 400
        xp_bar_height = 25
        xp_needed = stats.calculate_xp_for_level(stats.level + 1) - stats.calculate_xp_for_level(stats.level)
        xp_progress = stats.current_xp - stats.calculate_xp_for_level(stats.level)
        xp_percent = min(1.0, xp_progress / xp_needed if xp_needed > 0 else 0)
        
        pygame.draw.rect(screen, (30, 35, 50), (col1_x, y, xp_bar_width, xp_bar_height))
        pygame.draw.rect(screen, self.accent_cyan, (col1_x, y, int(xp_bar_width * xp_percent), xp_bar_height))
        pygame.draw.rect(screen, self.divider_color, (col1_x, y, xp_bar_width, xp_bar_height), 2)
        
        xp_text = self.font_small.render(f"{xp_progress} / {xp_needed} XP", True, self.text_primary)
        xp_text_rect = xp_text.get_rect(center=(col1_x + xp_bar_width // 2, y + xp_bar_height // 2))
        screen.blit(xp_text, xp_text_rect)
        y += 50
        
        # Available Points
        if stats.attribute_points > 0:
            points_text = self.font_normal.render(f"Attribute Points: {stats.attribute_points}", True, self.stat_positive)
            screen.blit(points_text, (col1_x, y))
            y += 30
        
        if stats.skill_points > 0:
            skill_text = self.font_normal.render(f"Skill Points: {stats.skill_points}", True, self.stat_positive)
            screen.blit(skill_text, (col1_x, y))
            y += 30
        
        y += 20
        
        # CORE ATTRIBUTES
        attr_header = self.font_header.render("CORE ATTRIBUTES", True, self.text_header)
        screen.blit(attr_header, (col1_x, y))
        y += 40
        
        attributes = [
            ("Strength", stats.strength, "Melee Damage, Max HP, Defense"),
            ("Dexterity", stats.dexterity, "Attack Speed, Movement, Critical"),
            ("Intelligence", stats.intelligence, "Spell Damage, Max Mana, Regen"),
            ("Vitality", stats.vitality, "HP, HP Regen, Resistances")
        ]
        
        for attr_name, attr_value, attr_desc in attributes:
            # Attribute name and value (aligned)
            name_text = self.font_normal.render(f"{attr_name}:", True, self.text_secondary)
            screen.blit(name_text, (col1_x, y))
            
            value_text = self.font_normal.render(str(attr_value), True, self.text_primary)
            screen.blit(value_text, (col1_x + 180, y))
            
            # Description
            desc_text = self.font_small.render(attr_desc, True, self.text_secondary)
            screen.blit(desc_text, (col1_x + 20, y + 25))
            y += 60
        
        # RIGHT COLUMN - Derived Stats
        y = start_y
        
        # Offense header
        offense_header = self.font_header.render("OFFENSE", True, self.text_header)
        screen.blit(offense_header, (col2_x, y))
        y += 40
        
        offense_stats = [
            ("Base Damage", f"{stats.base_damage}"),
            ("Attack Damage", f"{stats.attack_damage}"),
            ("Attack Speed", f"{stats.attack_speed:.2f}x"),
            ("Critical Chance", f"{stats.critical_chance * 100:.1f}%"),
            ("Critical Multiplier", f"{stats.critical_multiplier:.1f}x"),
        ]
        
        for stat_name, stat_value in offense_stats:
            self.draw_aligned_stat(screen, col2_x, y, stat_name, stat_value)
            y += 30
        
        y += 20
        
        # Defense header
        defense_header = self.font_header.render("DEFENSE", True, self.text_header)
        screen.blit(defense_header, (col2_x, y))
        y += 40
        
        defense_stats = [
            ("Max Health", f"{stats.max_health:.0f}"),
            ("Current Health", f"{stats.current_health:.0f}"),
            ("HP Regen/sec", f"{stats.health_regen:.2f}"),
            ("Defense", f"{stats.defense:.1f}"),
            ("Armor", f"{stats.armor * 100:.1f}%"),
            ("Dodge Chance", f"{stats.dodge_chance * 100:.1f}%"),
        ]
        
        for stat_name, stat_value in defense_stats:
            self.draw_aligned_stat(screen, col2_x, y, stat_name, stat_value)
            y += 30
        
        y += 20
        
        # Utility header
        utility_header = self.font_header.render("UTILITY", True, self.text_header)
        screen.blit(utility_header, (col2_x, y))
        y += 40
        
        utility_stats = [
            ("Max Mana", f"{stats.max_mana:.0f}"),
            ("Current Mana", f"{stats.current_mana:.0f}"),
            ("Mana Regen/sec", f"{stats.mana_regen:.1f}"),
            ("Movement Speed", f"{stats.movement_speed:.2f}x"),
        ]
        
        for stat_name, stat_value in utility_stats:
            self.draw_aligned_stat(screen, col2_x, y, stat_name, stat_value)
            y += 30
    
    def draw_aligned_stat(self, screen, x, y, name, value):
        """Draw perfectly aligned stat line"""
        name_text = self.font_normal.render(f"{name}:", True, self.text_secondary)
        screen.blit(name_text, (x, y))
        
        value_text = self.font_normal.render(value, True, self.text_primary)
        screen.blit(value_text, (x + 280, y))
    
    def draw_inventory_tab(self, screen):
        """Draw inventory and equipment tab"""
        if not self.player_inventory:
            return
        
        # Title and gold
        title = self.font_title.render("INVENTORY", True, self.text_header)
        screen.blit(title, (self.content_x, self.content_y))
        
        gold_text = self.font_header.render(f"{self.player_inventory.gold} Gold", True, self.gold_color)
        screen.blit(gold_text, (self.content_x + self.content_width - 200, self.content_y))
        
        # Divider
        pygame.draw.line(screen, self.divider_color,
                        (self.content_x, self.content_y + 50),
                        (self.content_x + self.content_width, self.content_y + 50), 2)
        
        # EQUIPMENT PANEL (Left)
        self.draw_equipment_panel(screen)
        
        # INVENTORY GRID (Right)
        self.draw_inventory_grid(screen)
    
    def draw_equipment_panel(self, screen):
        """Draw equipment slots panel"""
        equip_x = self.content_x + 20
        equip_y = self.content_y + 80
        
        # Panel background
        panel_rect = pygame.Rect(equip_x - 10, equip_y - 10,
                                self.equipment_panel_width, 500)
        pygame.draw.rect(screen, (25, 28, 40), panel_rect)
        pygame.draw.rect(screen, self.divider_color, panel_rect, 2)
        
        # Header
        header = self.font_header.render("EQUIPMENT", True, self.text_header)
        screen.blit(header, (equip_x, equip_y - 40))
        
        # Draw each equipment slot
        for slot_name, (offset_x, offset_y) in self.equipment_slots.items():
            slot_x = equip_x + offset_x
            slot_y = equip_y + offset_y
            
            is_hovered = (self.hovered_type == "equipment" and 
                         self.hovered_slot == slot_name and 
                         not self.dragging)
            
            # Slot background
            slot_color = (50, 55, 75) if is_hovered else (35, 40, 60)
            pygame.draw.rect(screen, slot_color, 
                           (slot_x, slot_y, self.slot_size, self.slot_size))
            pygame.draw.rect(screen, self.divider_color, 
                           (slot_x, slot_y, self.slot_size, self.slot_size), 2)
            
            # Slot label
            label = self.font_small.render(slot_name.upper(), True, self.text_secondary)
            label_rect = label.get_rect(centerx=slot_x + self.slot_size // 2, 
                                        y=slot_y + self.slot_size + 5)
            screen.blit(label, label_rect)
            
            # Draw equipped item
            item = self.player_inventory.get_equipped_item(slot_name)
            if item and not (self.dragging and self.drag_source_type == "equipment" 
                           and self.drag_source_slot == slot_name):
                self.draw_item_in_slot(screen, item, slot_x, slot_y)
    
    def draw_inventory_grid(self, screen):
        """Draw inventory grid"""
        grid_x = self.content_x + self.equipment_panel_width + 60
        grid_y = self.content_y + 80
        
        # Grid background
        grid_width = self.grid_cols * (self.slot_size + self.slot_padding) - self.slot_padding
        grid_height = self.grid_rows * (self.slot_size + self.slot_padding) - self.slot_padding
        
        grid_rect = pygame.Rect(grid_x - 10, grid_y - 10,
                               grid_width + 20, grid_height + 20)
        pygame.draw.rect(screen, (25, 28, 40), grid_rect)
        pygame.draw.rect(screen, self.divider_color, grid_rect, 2)
        
        # Header
        empty_slots = self.player_inventory.get_empty_slots()
        header = self.font_header.render(f"STORAGE ({empty_slots}/{self.player_inventory.grid_size} free)", 
                                        True, self.text_header)
        screen.blit(header, (grid_x, grid_y - 40))
        
        # Draw slots
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                slot_index = row * self.grid_cols + col
                slot_x = grid_x + col * (self.slot_size + self.slot_padding)
                slot_y = grid_y + row * (self.slot_size + self.slot_padding)
                
                is_hovered = (self.hovered_type == "inventory" and 
                            self.hovered_slot == slot_index and 
                            not self.dragging)
                
                # Slot background
                slot_color = (50, 55, 75) if is_hovered else (35, 40, 60)
                pygame.draw.rect(screen, slot_color,
                               (slot_x, slot_y, self.slot_size, self.slot_size))
                pygame.draw.rect(screen, self.divider_color,
                               (slot_x, slot_y, self.slot_size, self.slot_size), 1)
                
                # Draw item
                item = self.player_inventory.get_item_at_slot(slot_index)
                if item and not (self.dragging and self.drag_source_type == "inventory" 
                               and self.drag_source_slot == slot_index):
                    self.draw_item_in_slot(screen, item, slot_x, slot_y)
    
    def draw_item_in_slot(self, screen, item, x, y):
        """Draw item icon in slot"""
        # Draw actual item icon using its visual generation
        icon_size = self.slot_size - 8
        icon = item.generate_icon(icon_size)
        icon_rect = icon.get_rect(center=(x + self.slot_size // 2, y + self.slot_size // 2))
        screen.blit(icon, icon_rect)
        
        # Border with rarity color
        border_rect = pygame.Rect(x + 2, y + 2, self.slot_size - 4, self.slot_size - 4)
        pygame.draw.rect(screen, item.icon_color, border_rect, 2)
        
        # Stack count
        if item.stackable and item.stack_count > 1:
            count_text = self.font_small.render(str(item.stack_count), True, (255, 255, 255))
            count_bg = pygame.Rect(x + 4, y + self.slot_size - 18, 
                                  count_text.get_width() + 4, count_text.get_height() + 2)
            pygame.draw.rect(screen, (0, 0, 0, 180), count_bg)
            screen.blit(count_text, (x + 6, y + self.slot_size - 18))
    
    def draw_dragged_item(self, screen):
        """Draw item being dragged"""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        item_x = mouse_x - self.drag_offset_x
        item_y = mouse_y - self.drag_offset_y
        
        # Draw item icon
        icon = self.dragged_item.generate_icon(self.slot_size - 8)
        drag_surface = pygame.Surface((self.slot_size, self.slot_size), pygame.SRCALPHA)
        icon_rect = icon.get_rect(center=(self.slot_size // 2, self.slot_size // 2))
        drag_surface.blit(icon, icon_rect)
        
        # Border
        pygame.draw.rect(drag_surface, self.dragged_item.icon_color,
                        (0, 0, self.slot_size, self.slot_size), 2)
        
        # Make semi-transparent
        drag_surface.set_alpha(200)
        screen.blit(drag_surface, (item_x, item_y))
        
        abbrev = self.dragged_item.name[:3].upper()
        text = self.font_normal.render(abbrev, True, (255, 255, 255))
        text_rect = text.get_rect(center=(item_x + self.slot_size // 2, 
                                          item_y + self.slot_size // 2 - 5))
        screen.blit(text, text_rect)
        
        if self.dragged_item.stackable and self.dragged_item.stack_count > 1:
            count_text = self.font_small.render(str(self.dragged_item.stack_count), 
                                              True, (255, 255, 255))
            screen.blit(count_text, (item_x + 6, item_y + self.slot_size - 18))
    
    def draw_tooltip(self, screen):
        """Draw item tooltip"""
        if not self.hovered_item:
            return
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Build tooltip lines
        lines = [
            self.hovered_item.name,
            f"[{self.hovered_item.rarity}] {self.hovered_item.item_type.capitalize()}",
            ""
        ]
        
        if self.hovered_item.stats:
            for stat, value in self.hovered_item.stats.items():
                prefix = "+" if value > 0 else ""
                lines.append(f"{prefix}{value} {stat.replace('_', ' ').capitalize()}")
            lines.append("")
        
        if self.hovered_item.description:
            lines.append(self.hovered_item.description)
        
        # Calculate size
        line_height = 24
        padding = 15
        max_width = max(self.font_normal.size(line)[0] for line in lines)
        tooltip_width = max_width + padding * 2
        tooltip_height = len(lines) * line_height + padding * 2
        
        # Position
        tooltip_x = mouse_x + 15
        tooltip_y = mouse_y + 15
        
        if tooltip_x + tooltip_width > self.screen_width:
            tooltip_x = mouse_x - tooltip_width - 15
        if tooltip_y + tooltip_height > self.screen_height:
            tooltip_y = mouse_y - tooltip_height - 15
        
        # Draw background
        pygame.draw.rect(screen, (20, 22, 35),
                        (tooltip_x, tooltip_y, tooltip_width, tooltip_height))
        pygame.draw.rect(screen, self.hovered_item.icon_color,
                        (tooltip_x, tooltip_y, tooltip_width, tooltip_height), 2)
        
        # Draw text
        y_offset = padding
        for i, line in enumerate(lines):
            if i == 0:  # Item name
                text = self.font_header.render(line, True, self.hovered_item.icon_color)
            elif i == 1:  # Type/rarity
                text = self.font_small.render(line, True, self.text_secondary)
            elif line and line[0] in ['+', '-']:  # Stats
                text = self.font_normal.render(line, True, self.stat_positive)
            else:  # Description
                text = self.font_small.render(line, True, self.text_secondary)
            
            screen.blit(text, (tooltip_x + padding, tooltip_y + y_offset))
            y_offset += line_height
    
    def draw_controls_hint(self, screen):
        """Draw control hints at bottom"""
        hints = "TAB/ESC: Close  |  1: Character  |  2: Inventory  |  Drag items to equip/move"
        hint_text = self.font_small.render(hints, True, self.text_secondary)
        hint_rect = hint_text.get_rect(center=(self.panel_x + self.panel_width // 2, 
                                               self.panel_y + self.panel_height - 20))
        screen.blit(hint_text, hint_rect)
