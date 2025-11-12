"""
Inventory System for RPG Platformer
Handles item storage, equipment slots, and inventory management
"""

import pygame


class Item:
    """Base class for all items in the game"""
    def __init__(self, name, item_type, rarity="Common", stats=None, description="", stackable=False, max_stack=1, visual_data=None):
        self.name = name
        self.item_type = item_type  # "weapon", "armor", "helm", "boots", "amulet", "ring", "consumable", "material", "quest"
        self.rarity = rarity  # "Common", "Uncommon", "Rare", "Epic", "Legendary", "Unique"
        self.stats = stats if stats else {}  # e.g., {"strength": 5, "damage": 10}
        self.description = description
        self.stackable = stackable
        self.max_stack = max_stack
        self.stack_count = 1
        
        # Visual properties
        self.icon_color = self.get_rarity_color()
        self.visual_data = visual_data if visual_data else self.get_default_visual_data()
        self._icon_surface = None  # Cached icon
    
    def get_default_visual_data(self):
        """Get default visual data based on item type"""
        # Color schemes for different item types
        if self.item_type == "weapon":
            return {
                "primary_color": (180, 180, 200),  # Steel gray
                "secondary_color": (120, 90, 60),   # Handle brown
                "accent_color": self.icon_color     # Rarity glow
            }
        elif self.item_type == "armor":
            return {
                "primary_color": (160, 140, 120),   # Leather/metal
                "secondary_color": (100, 90, 80),   # Dark trim
                "accent_color": self.icon_color
            }
        elif self.item_type == "helm":
            return {
                "primary_color": (150, 150, 160),
                "secondary_color": (80, 80, 90),
                "accent_color": self.icon_color
            }
        elif self.item_type == "boots":
            return {
                "primary_color": (100, 80, 60),
                "secondary_color": (60, 50, 40),
                "accent_color": self.icon_color
            }
        elif self.item_type in ["amulet", "ring"]:
            return {
                "primary_color": (200, 180, 100),   # Gold
                "secondary_color": self.icon_color,  # Gem color
                "accent_color": (255, 255, 200)      # Shine
            }
        else:
            return {
                "primary_color": (150, 150, 150),
                "secondary_color": (100, 100, 100),
                "accent_color": self.icon_color
            }
    
    def generate_icon(self, size=48):
        """Generate icon sprite for this item"""
        if self._icon_surface and self._icon_surface.get_size() == (size, size):
            return self._icon_surface
        
        icon = pygame.Surface((size, size), pygame.SRCALPHA)
        colors = self.visual_data
        
        # Draw different icon types based on item type
        if self.item_type == "weapon":
            self._draw_weapon_icon(icon, size, colors)
        elif self.item_type == "armor":
            self._draw_armor_icon(icon, size, colors)
        elif self.item_type == "helm":
            self._draw_helm_icon(icon, size, colors)
        elif self.item_type == "boots":
            self._draw_boots_icon(icon, size, colors)
        elif self.item_type == "amulet":
            self._draw_amulet_icon(icon, size, colors)
        elif self.item_type == "ring":
            self._draw_ring_icon(icon, size, colors)
        elif self.item_type == "consumable":
            self._draw_potion_icon(icon, size, colors)
        else:
            self._draw_generic_icon(icon, size, colors)
        
        self._icon_surface = icon
        return icon
    
    def _draw_weapon_icon(self, surface, size, colors):
        """Draw weapon icon (sword shape)"""
        center = size // 2
        # Blade
        blade_points = [(center, size - 8), (center - 3, 8), (center, 4), (center + 3, 8)]
        pygame.draw.polygon(surface, colors["primary_color"], blade_points)
        pygame.draw.polygon(surface, (255, 255, 255, 100), blade_points, 2)
        # Handle
        pygame.draw.rect(surface, colors["secondary_color"], 
                        (center - 2, size - 12, 4, 8))
        # Guard
        pygame.draw.rect(surface, colors["accent_color"],
                        (center - 6, size - 12, 12, 2))
    
    def _draw_armor_icon(self, surface, size, colors):
        """Draw armor icon (chest plate shape)"""
        center = size // 2
        # Body
        pygame.draw.rect(surface, colors["primary_color"],
                        (center - 10, size // 3, 20, size // 2))
        # Shoulders
        pygame.draw.circle(surface, colors["secondary_color"],
                          (center - 10, size // 3 + 5), 6)
        pygame.draw.circle(surface, colors["secondary_color"],
                          (center + 10, size // 3 + 5), 6)
        # Accent line
        pygame.draw.line(surface, colors["accent_color"],
                        (center, size // 3 + 2), (center, size - 8), 2)
    
    def _draw_helm_icon(self, surface, size, colors):
        """Draw helmet icon"""
        center = size // 2
        # Main helm
        pygame.draw.ellipse(surface, colors["primary_color"],
                           (center - 12, 8, 24, 28))
        # Visor
        pygame.draw.rect(surface, (50, 50, 70),
                        (center - 8, 18, 16, 8))
        # Accent
        pygame.draw.arc(surface, colors["accent_color"],
                       (center - 10, 10, 20, 20), 3.14, 0, 2)
    
    def _draw_boots_icon(self, surface, size, colors):
        """Draw boots icon"""
        center = size // 2
        # Left boot
        pygame.draw.rect(surface, colors["primary_color"],
                        (center - 12, size - 16, 8, 12))
        pygame.draw.ellipse(surface, colors["secondary_color"],
                           (center - 12, size - 16, 8, 6))
        # Right boot
        pygame.draw.rect(surface, colors["primary_color"],
                        (center + 4, size - 16, 8, 12))
        pygame.draw.ellipse(surface, colors["secondary_color"],
                           (center + 4, size - 16, 8, 6))
    
    def _draw_amulet_icon(self, surface, size, colors):
        """Draw amulet icon"""
        center = size // 2
        # Chain
        pygame.draw.arc(surface, colors["primary_color"],
                       (center - 10, 4, 20, 20), 0, 3.14, 2)
        # Gem
        gem_points = [(center, size - 12), (center - 8, size - 20),
                     (center, size - 26), (center + 8, size - 20)]
        pygame.draw.polygon(surface, colors["secondary_color"], gem_points)
        pygame.draw.polygon(surface, colors["accent_color"], gem_points, 2)
    
    def _draw_ring_icon(self, surface, size, colors):
        """Draw ring icon"""
        center = size // 2
        # Band
        pygame.draw.circle(surface, colors["primary_color"],
                          (center, center), 10, 3)
        # Gem
        pygame.draw.circle(surface, colors["secondary_color"],
                          (center, center - 8), 4)
        pygame.draw.circle(surface, colors["accent_color"],
                          (center - 1, center - 9), 2)
    
    def _draw_potion_icon(self, surface, size, colors):
        """Draw potion/consumable icon"""
        center = size // 2
        # Bottle
        pygame.draw.rect(surface, (200, 200, 220),
                        (center - 6, 12, 12, 24))
        # Liquid
        pygame.draw.rect(surface, colors["accent_color"],
                        (center - 5, 18, 10, 16))
        # Cork
        pygame.draw.rect(surface, (150, 100, 50),
                        (center - 4, 8, 8, 5))
    
    def _draw_generic_icon(self, surface, size, colors):
        """Draw generic icon"""
        center = size // 2
        pygame.draw.rect(surface, colors["primary_color"],
                        (8, 8, size - 16, size - 16))
        pygame.draw.rect(surface, colors["accent_color"],
                        (8, 8, size - 16, size - 16), 2)
    
    def get_rarity_color(self):
        """Get color based on item rarity"""
        rarity_colors = {
            "Common": (150, 150, 150),      # Gray
            "Uncommon": (30, 255, 0),       # Green
            "Rare": (0, 112, 221),          # Blue
            "Epic": (163, 53, 238),         # Purple
            "Legendary": (255, 128, 0),     # Orange
            "Unique": (255, 215, 0)         # Gold
        }
        return rarity_colors.get(self.rarity, (255, 255, 255))
    
    def can_stack_with(self, other):
        """Check if this item can stack with another item"""
        if not self.stackable or not other.stackable:
            return False
        return (self.name == other.name and 
                self.item_type == other.item_type and
                self.rarity == other.rarity)
    
    def add_to_stack(self, amount=1):
        """Add items to stack, returns overflow amount"""
        space_available = self.max_stack - self.stack_count
        amount_to_add = min(amount, space_available)
        self.stack_count += amount_to_add
        return amount - amount_to_add  # Return overflow
    
    def remove_from_stack(self, amount=1):
        """Remove items from stack, returns actual amount removed"""
        amount_to_remove = min(amount, self.stack_count)
        self.stack_count -= amount_to_remove
        return amount_to_remove
    
    def split_stack(self, amount):
        """Split stack into two, returns new item with specified amount"""
        if not self.stackable or amount >= self.stack_count:
            return None
        
        self.stack_count -= amount
        new_item = Item(
            self.name, self.item_type, self.rarity,
            self.stats.copy(), self.description,
            self.stackable, self.max_stack
        )
        new_item.stack_count = amount
        return new_item
    
    def get_stat_summary(self):
        """Get formatted string of item stats"""
        if not self.stats:
            return ""
        
        stat_lines = []
        for stat, value in self.stats.items():
            prefix = "+" if value > 0 else ""
            stat_lines.append(f"{prefix}{value} {stat.capitalize()}")
        return "\n".join(stat_lines)
    
    def __str__(self):
        if self.stackable and self.stack_count > 1:
            return f"{self.name} x{self.stack_count}"
        return self.name


class Inventory:
    """Player inventory with grid storage and equipment slots"""
    def __init__(self, grid_size=40):
        self.grid_size = grid_size
        self.grid = [None] * grid_size  # Main inventory grid
        
        # Equipment slots
        self.equipment = {
            "weapon": None,
            "armor": None,
            "helm": None,
            "boots": None,
            "amulet": None,
            "ring1": None,
            "ring2": None
        }
        
        # Currency
        self.gold = 0
    
    def add_item(self, item, slot=None):
        """
        Add item to inventory
        If slot is specified, try to add to that slot
        Returns True if successful, False if inventory full
        """
        # If item is stackable, try to stack with existing items first
        if item.stackable:
            for i, existing_item in enumerate(self.grid):
                if existing_item and existing_item.can_stack_with(item):
                    overflow = existing_item.add_to_stack(item.stack_count)
                    if overflow == 0:
                        return True
                    item.stack_count = overflow
        
        # Find empty slot or use specified slot
        if slot is not None and 0 <= slot < self.grid_size:
            if self.grid[slot] is None:
                self.grid[slot] = item
                return True
            return False
        
        # Find first empty slot
        for i in range(self.grid_size):
            if self.grid[i] is None:
                self.grid[i] = item
                return True
        
        return False  # Inventory full
    
    def remove_item(self, slot):
        """Remove and return item from slot"""
        if 0 <= slot < self.grid_size:
            item = self.grid[slot]
            self.grid[slot] = None
            return item
        return None
    
    def swap_items(self, slot1, slot2):
        """Swap items between two slots"""
        if 0 <= slot1 < self.grid_size and 0 <= slot2 < self.grid_size:
            self.grid[slot1], self.grid[slot2] = self.grid[slot2], self.grid[slot1]
            return True
        return False
    
    def move_item(self, from_slot, to_slot):
        """
        Move item from one slot to another
        Handles stacking if applicable
        """
        if not (0 <= from_slot < self.grid_size and 0 <= to_slot < self.grid_size):
            return False
        
        from_item = self.grid[from_slot]
        to_item = self.grid[to_slot]
        
        if from_item is None:
            return False
        
        # If target slot is empty, simple move
        if to_item is None:
            self.grid[to_slot] = from_item
            self.grid[from_slot] = None
            return True
        
        # If items can stack, try to stack them
        if from_item.can_stack_with(to_item):
            overflow = to_item.add_to_stack(from_item.stack_count)
            if overflow == 0:
                self.grid[from_slot] = None
            else:
                from_item.stack_count = overflow
            return True
        
        # Otherwise swap items
        self.swap_items(from_slot, to_slot)
        return True
    
    def equip_item(self, slot):
        """
        Equip item from inventory slot to appropriate equipment slot
        Returns True if successful
        """
        if not (0 <= slot < self.grid_size):
            return False
        
        item = self.grid[slot]
        if item is None:
            return False
        
        # Check if item type matches an equipment slot
        if item.item_type not in self.equipment:
            return False
        
        # Special handling for rings (two ring slots)
        if item.item_type == "ring":
            if self.equipment["ring1"] is None:
                self.equipment["ring1"] = item
                self.grid[slot] = None
                return True
            elif self.equipment["ring2"] is None:
                self.equipment["ring2"] = item
                self.grid[slot] = None
                return True
            else:
                # Both ring slots full, swap with ring1
                old_ring = self.equipment["ring1"]
                self.equipment["ring1"] = item
                self.grid[slot] = old_ring
                return True
        
        # Handle other equipment slots
        old_item = self.equipment[item.item_type]
        self.equipment[item.item_type] = item
        self.grid[slot] = old_item  # Put old item back in inventory (or None)
        return True
    
    def unequip_item(self, equipment_slot):
        """
        Unequip item from equipment slot to inventory
        Returns True if successful (if there's space in inventory)
        """
        if equipment_slot not in self.equipment:
            return False
        
        item = self.equipment[equipment_slot]
        if item is None:
            return False
        
        # Try to add to inventory
        if self.add_item(item):
            self.equipment[equipment_slot] = None
            return True
        
        return False  # No space in inventory
    
    def get_equipment_stats(self):
        """Calculate total stat bonuses from all equipped items"""
        total_stats = {}
        
        for slot, item in self.equipment.items():
            if item and item.stats:
                for stat, value in item.stats.items():
                    total_stats[stat] = total_stats.get(stat, 0) + value
        
        return total_stats
    
    def get_item_at_slot(self, slot):
        """Get item at inventory slot"""
        if 0 <= slot < self.grid_size:
            return self.grid[slot]
        return None
    
    def get_equipped_item(self, slot_name):
        """Get equipped item from equipment slot"""
        return self.equipment.get(slot_name)
    
    def is_full(self):
        """Check if inventory is completely full"""
        return all(slot is not None for slot in self.grid)
    
    def get_empty_slots(self):
        """Get number of empty slots"""
        return sum(1 for slot in self.grid if slot is None)
    
    def clear_inventory(self):
        """Clear all items from inventory (debugging/testing)"""
        self.grid = [None] * self.grid_size
        for key in self.equipment:
            self.equipment[key] = None
        self.gold = 0
    
    def save_data(self):
        """Save inventory data to dict"""
        return {
            "grid_size": self.grid_size,
            "grid": [
                {
                    "name": item.name,
                    "type": item.item_type,
                    "rarity": item.rarity,
                    "stats": item.stats,
                    "description": item.description,
                    "stackable": item.stackable,
                    "max_stack": item.max_stack,
                    "stack_count": item.stack_count
                } if item else None
                for item in self.grid
            ],
            "equipment": {
                slot: {
                    "name": item.name,
                    "type": item.item_type,
                    "rarity": item.rarity,
                    "stats": item.stats,
                    "description": item.description,
                    "stackable": item.stackable,
                    "max_stack": item.max_stack,
                    "stack_count": item.stack_count
                } if item else None
                for slot, item in self.equipment.items()
            },
            "gold": self.gold
        }
    
    def load_data(self, data):
        """Load inventory data from dict"""
        self.grid_size = data.get("grid_size", 40)
        self.gold = data.get("gold", 0)
        
        # Load grid items
        grid_data = data.get("grid", [])
        self.grid = []
        for item_data in grid_data:
            if item_data:
                item = Item(
                    item_data["name"],
                    item_data["type"],
                    item_data["rarity"],
                    item_data["stats"],
                    item_data.get("description", ""),
                    item_data.get("stackable", False),
                    item_data.get("max_stack", 1)
                )
                item.stack_count = item_data.get("stack_count", 1)
                self.grid.append(item)
            else:
                self.grid.append(None)
        
        # Load equipment
        equipment_data = data.get("equipment", {})
        for slot in self.equipment.keys():
            item_data = equipment_data.get(slot)
            if item_data:
                item = Item(
                    item_data["name"],
                    item_data["type"],
                    item_data["rarity"],
                    item_data["stats"],
                    item_data.get("description", ""),
                    item_data.get("stackable", False),
                    item_data.get("max_stack", 1)
                )
                item.stack_count = item_data.get("stack_count", 1)
                self.equipment[slot] = item
            else:
                self.equipment[slot] = None


# Example item templates for testing
def create_test_items():
    """Create sample items for testing"""
    items = []
    
    # Weapons
    items.append(Item(
        "Rusty Sword", "weapon", "Common",
        {"damage": 5, "strength": 2},
        "A worn blade that's seen better days."
    ))
    
    items.append(Item(
        "Knight's Blade", "weapon", "Rare",
        {"damage": 15, "strength": 5, "dexterity": 3},
        "A well-crafted blade used by royal knights."
    ))
    
    # Armor
    items.append(Item(
        "Leather Vest", "armor", "Common",
        {"defense": 5, "vitality": 3},
        "Basic leather protection."
    ))
    
    items.append(Item(
        "Steel Plate", "armor", "Epic",
        {"defense": 25, "vitality": 10, "strength": 5},
        "Heavy steel armor that provides excellent protection."
    ))
    
    # Helm
    items.append(Item(
        "Iron Helm", "helm", "Uncommon",
        {"defense": 8, "vitality": 5},
        "A sturdy iron helmet."
    ))
    
    # Boots
    items.append(Item(
        "Swift Boots", "boots", "Rare",
        {"dexterity": 8, "movement_speed": 15},
        "Enchanted boots that enhance mobility."
    ))
    
    # Accessories
    items.append(Item(
        "Ruby Ring", "ring", "Epic",
        {"strength": 7, "vitality": 5, "fire_damage": 10},
        "A ring embedded with a glowing ruby."
    ))
    
    items.append(Item(
        "Mystic Amulet", "amulet", "Legendary",
        {"intelligence": 15, "mana": 100, "mana_regen": 5},
        "An ancient amulet radiating magical power."
    ))
    
    # Consumables
    items.append(Item(
        "Health Potion", "consumable", "Common",
        {"heal": 50},
        "Restores 50 HP.",
        stackable=True, max_stack=99
    ))
    
    items.append(Item(
        "Mana Potion", "consumable", "Common",
        {"restore_mana": 30},
        "Restores 30 Mana.",
        stackable=True, max_stack=99
    ))
    
    # Materials
    items.append(Item(
        "Soul Essence", "material", "Rare",
        {},
        "A crystallized soul used in crafting.",
        stackable=True, max_stack=999
    ))
    
    return items
