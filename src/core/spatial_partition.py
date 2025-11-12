"""
Spatial Partitioning System - Quadtree Implementation
Optimizes collision detection from O(n²) to O(n log n)
Target: 10x performance improvement with 100+ entities
"""

import pygame
from typing import List, Set, Tuple


class QuadtreeNode:
    """
    A node in the Quadtree spatial partitioning structure
    Recursively divides 2D space into 4 quadrants
    """
    
    MAX_OBJECTS = 10  # Max objects before subdivision
    MAX_LEVELS = 5    # Max subdivision depth
    
    def __init__(self, level: int, bounds: pygame.Rect):
        """
        Initialize quadtree node
        
        Args:
            level: Current depth in tree (0 = root)
            bounds: Rectangle defining this node's space
        """
        self.level = level
        self.bounds = bounds
        self.objects: List[pygame.sprite.Sprite] = []
        self.nodes: List['QuadtreeNode'] = []  # 4 child nodes when subdivided
        
    def clear(self):
        """Clear all objects and subdivisions"""
        self.objects.clear()
        
        for node in self.nodes:
            node.clear()
        
        self.nodes.clear()
    
    def subdivide(self):
        """Split this node into 4 child quadrants"""
        sub_width = self.bounds.width // 2
        sub_height = self.bounds.height // 2
        x = self.bounds.x
        y = self.bounds.y
        
        # Create 4 child nodes: top-left, top-right, bottom-left, bottom-right
        self.nodes = [
            QuadtreeNode(self.level + 1, pygame.Rect(x, y, sub_width, sub_height)),
            QuadtreeNode(self.level + 1, pygame.Rect(x + sub_width, y, sub_width, sub_height)),
            QuadtreeNode(self.level + 1, pygame.Rect(x, y + sub_height, sub_width, sub_height)),
            QuadtreeNode(self.level + 1, pygame.Rect(x + sub_width, y + sub_height, sub_width, sub_height))
        ]
    
    def get_index(self, rect: pygame.Rect) -> int:
        """
        Determine which quadrant an object belongs to
        
        Returns:
            0-3: Quadrant index (TL, TR, BL, BR)
            -1: Object doesn't fit completely in any quadrant (straddles boundary)
        """
        index = -1
        
        # Calculate midpoints
        vertical_midpoint = self.bounds.x + self.bounds.width / 2
        horizontal_midpoint = self.bounds.y + self.bounds.height / 2
        
        # Object is in top half
        top_quadrant = (rect.y < horizontal_midpoint and 
                       rect.y + rect.height < horizontal_midpoint)
        
        # Object is in bottom half
        bottom_quadrant = rect.y > horizontal_midpoint
        
        # Object is in left half
        if rect.x < vertical_midpoint and rect.x + rect.width < vertical_midpoint:
            if top_quadrant:
                index = 0  # Top-left
            elif bottom_quadrant:
                index = 2  # Bottom-left
        
        # Object is in right half
        elif rect.x > vertical_midpoint:
            if top_quadrant:
                index = 1  # Top-right
            elif bottom_quadrant:
                index = 3  # Bottom-right
        
        return index
    
    def insert(self, obj: pygame.sprite.Sprite) -> bool:
        """
        Insert an object into the quadtree
        
        Args:
            obj: Sprite with rect attribute
            
        Returns:
            True if successfully inserted
        """
        # If we have child nodes, try to insert into appropriate child
        if self.nodes:
            index = self.get_index(obj.rect)
            
            if index != -1:
                return self.nodes[index].insert(obj)
        
        # Otherwise, add to this node
        self.objects.append(obj)
        
        # If we have too many objects and haven't reached max depth, subdivide
        if len(self.objects) > self.MAX_OBJECTS and self.level < self.MAX_LEVELS:
            if not self.nodes:
                self.subdivide()
            
            # Try to push objects down into child nodes
            i = 0
            while i < len(self.objects):
                index = self.get_index(self.objects[i].rect)
                if index != -1:
                    self.nodes[index].insert(self.objects.pop(i))
                else:
                    i += 1
        
        return True
    
    def retrieve(self, rect: pygame.Rect) -> List[pygame.sprite.Sprite]:
        """
        Retrieve all objects that could collide with given rect
        
        Args:
            rect: Query rectangle
            
        Returns:
            List of potentially colliding objects
        """
        return_objects = []
        
        # Get objects in child nodes if subdivided
        if self.nodes:
            index = self.get_index(rect)
            
            # If object fits in a specific quadrant, only check that quadrant
            if index != -1:
                return_objects.extend(self.nodes[index].retrieve(rect))
            else:
                # Object straddles boundary, check all quadrants
                for node in self.nodes:
                    return_objects.extend(node.retrieve(rect))
        
        # Add objects from this node
        return_objects.extend(self.objects)
        
        return return_objects
    
    def draw_debug(self, surface: pygame.Surface, camera=None):
        """
        Draw quadtree boundaries for debugging
        
        Args:
            surface: Pygame surface to draw on
            camera: Optional camera for offset
        """
        # Draw this node's boundary
        if camera:
            draw_rect = pygame.Rect(
                self.bounds.x - camera.offset_x,
                self.bounds.y - camera.offset_y,
                self.bounds.width,
                self.bounds.height
            )
        else:
            draw_rect = self.bounds
        
        # Color based on depth
        colors = [
            (255, 0, 0),    # Level 0: Red
            (255, 165, 0),  # Level 1: Orange
            (255, 255, 0),  # Level 2: Yellow
            (0, 255, 0),    # Level 3: Green
            (0, 0, 255),    # Level 4: Blue
            (128, 0, 128)   # Level 5: Purple
        ]
        color = colors[min(self.level, len(colors) - 1)]
        
        pygame.draw.rect(surface, color, draw_rect, 1)
        
        # Draw child nodes
        for node in self.nodes:
            node.draw_debug(surface, camera)


class SpatialPartition:
    """
    Main spatial partitioning system using Quadtree
    Manages efficient collision detection for game entities
    """
    
    def __init__(self, world_bounds: pygame.Rect):
        """
        Initialize spatial partition system
        
        Args:
            world_bounds: Total world boundary rectangle
        """
        self.world_bounds = world_bounds
        self.root = QuadtreeNode(0, world_bounds)
        self.debug_enabled = False
        
    def clear(self):
        """Clear and rebuild the quadtree"""
        self.root.clear()
    
    def insert_all(self, sprites: List[pygame.sprite.Sprite]):
        """
        Insert multiple sprites into the quadtree
        
        Args:
            sprites: List of sprites to insert
        """
        for sprite in sprites:
            if hasattr(sprite, 'rect'):
                self.root.insert(sprite)
    
    def query(self, rect: pygame.Rect) -> List[pygame.sprite.Sprite]:
        """
        Query for potential collisions with given rect
        
        Args:
            rect: Query rectangle
            
        Returns:
            List of sprites that could collide
        """
        return self.root.retrieve(rect)
    
    def query_point(self, x: int, y: int) -> List[pygame.sprite.Sprite]:
        """
        Query for objects at a specific point
        
        Args:
            x, y: Point coordinates
            
        Returns:
            List of sprites at that point
        """
        point_rect = pygame.Rect(x, y, 1, 1)
        return self.root.retrieve(point_rect)
    
    def query_radius(self, center_x: int, center_y: int, radius: int) -> List[pygame.sprite.Sprite]:
        """
        Query for objects within radius of a point
        
        Args:
            center_x, center_y: Center point
            radius: Search radius
            
        Returns:
            List of sprites within radius
        """
        query_rect = pygame.Rect(
            center_x - radius,
            center_y - radius,
            radius * 2,
            radius * 2
        )
        candidates = self.root.retrieve(query_rect)
        
        # Filter to actual circle distance
        results = []
        for sprite in candidates:
            dx = sprite.rect.centerx - center_x
            dy = sprite.rect.centery - center_y
            distance_sq = dx * dx + dy * dy
            if distance_sq <= radius * radius:
                results.append(sprite)
        
        return results
    
    def get_nearby_entities(self, entity: pygame.sprite.Sprite, range_rect: pygame.Rect = None) -> List[pygame.sprite.Sprite]:
        """
        Get entities near a given entity
        
        Args:
            entity: Reference entity
            range_rect: Optional custom search rect (defaults to entity rect)
            
        Returns:
            List of nearby entities (excluding the query entity)
        """
        if range_rect is None:
            range_rect = entity.rect
        
        nearby = self.root.retrieve(range_rect)
        
        # Remove the query entity itself
        if entity in nearby:
            nearby.remove(entity)
        
        return nearby
    
    def rebuild(self, all_sprites: List[pygame.sprite.Sprite]):
        """
        Full rebuild of the quadtree
        Call this every frame with updated entity positions
        
        Args:
            all_sprites: All active sprites in the world
        """
        self.clear()
        self.insert_all(all_sprites)
    
    def toggle_debug(self):
        """Toggle debug visualization"""
        self.debug_enabled = not self.debug_enabled
    
    def draw_debug(self, surface: pygame.Surface, camera=None):
        """
        Draw quadtree for debugging
        
        Args:
            surface: Surface to draw on
            camera: Optional camera for offset
        """
        if self.debug_enabled:
            self.root.draw_debug(surface, camera)
    
    def get_stats(self) -> dict:
        """
        Get statistics about quadtree performance
        
        Returns:
            Dict with stats (total_nodes, max_depth, avg_objects_per_node)
        """
        def count_nodes(node, depth_counts):
            depth_counts[node.level] = depth_counts.get(node.level, 0) + 1
            for child in node.nodes:
                count_nodes(child, depth_counts)
        
        depth_counts = {}
        count_nodes(self.root, depth_counts)
        
        return {
            'total_nodes': sum(depth_counts.values()),
            'max_depth': max(depth_counts.keys()) if depth_counts else 0,
            'nodes_per_level': depth_counts
        }
