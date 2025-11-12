"""
Object Pool System
Reuses objects instead of creating/destroying them
Reduces garbage collection pressure and improves performance
Target: 50% reduction in memory allocations for particles/projectiles
"""

from typing import List, Callable, Any, Optional
import pygame


class ObjectPool:
    """
    Generic object pool for reusing objects
    Maintains a pool of inactive objects that can be activated on demand
    """
    
    def __init__(self, factory_func: Callable[[], Any], initial_size: int = 50, max_size: int = 500):
        """
        Initialize object pool
        
        Args:
            factory_func: Function that creates new objects
            initial_size: Number of objects to pre-create
            max_size: Maximum pool size (prevents memory leaks)
        """
        self.factory_func = factory_func
        self.max_size = max_size
        self.active_objects: List[Any] = []
        self.inactive_objects: List[Any] = []
        
        # Pre-create initial objects
        for _ in range(initial_size):
            obj = self.factory_func()
            self.inactive_objects.append(obj)
    
    def acquire(self) -> Optional[Any]:
        """
        Get an object from the pool
        
        Returns:
            Reused or newly created object, or None if max_size reached
        """
        # Try to reuse inactive object
        if self.inactive_objects:
            obj = self.inactive_objects.pop()
            self.active_objects.append(obj)
            return obj
        
        # Create new object if under max_size
        if len(self.active_objects) < self.max_size:
            obj = self.factory_func()
            self.active_objects.append(obj)
            return obj
        
        # Pool exhausted
        return None
    
    def release(self, obj: Any):
        """
        Return an object to the pool for reuse
        
        Args:
            obj: Object to return to pool
        """
        if obj in self.active_objects:
            self.active_objects.remove(obj)
            self.inactive_objects.append(obj)
    
    def release_all(self):
        """Return all active objects to the pool"""
        self.inactive_objects.extend(self.active_objects)
        self.active_objects.clear()
    
    def clear(self):
        """Clear all objects from the pool"""
        self.active_objects.clear()
        self.inactive_objects.clear()
    
    def get_stats(self) -> dict:
        """
        Get pool statistics
        
        Returns:
            Dict with active count, inactive count, and total size
        """
        return {
            'active': len(self.active_objects),
            'inactive': len(self.inactive_objects),
            'total': len(self.active_objects) + len(self.inactive_objects),
            'utilization': len(self.active_objects) / self.max_size if self.max_size > 0 else 0
        }


class ParticlePool:
    """
    Specialized pool for particle objects
    Handles particle lifecycle and automatic cleanup
    """
    
    def __init__(self, particle_class, initial_size: int = 100, max_size: int = 1000):
        """
        Initialize particle pool
        
        Args:
            particle_class: Class to instantiate for particles
            initial_size: Number of particles to pre-create
            max_size: Maximum particles in pool
        """
        self.particle_class = particle_class
        self.pool = ObjectPool(
            factory_func=lambda: particle_class(0, 0, 0, 0, (255, 255, 255)),
            initial_size=initial_size,
            max_size=max_size
        )
    
    def emit(self, x: int, y: int, vx: float, vy: float, color: tuple, 
             lifetime: int = 30, size: int = 4, fade: bool = True) -> Optional[Any]:
        """
        Emit a particle from the pool
        
        Args:
            x, y: Starting position
            vx, vy: Velocity
            color: RGB color tuple
            lifetime: Frames until particle dies
            size: Particle size in pixels
            fade: Whether to fade out over lifetime
            
        Returns:
            The emitted particle or None if pool exhausted
        """
        particle = self.pool.acquire()
        if particle:
            # Reset particle properties
            particle.rect.x = x
            particle.rect.y = y
            particle.velocity_x = vx
            particle.velocity_y = vy
            particle.color = color
            particle.lifetime = lifetime
            particle.max_lifetime = lifetime
            particle.size = size
            particle.fade = fade
            particle.alpha = 255
            
            # Recreate particle image with new size/color
            if hasattr(particle, 'create_particle_surface'):
                particle.create_particle_surface()
        
        return particle
    
    def update_all(self, sprite_group: pygame.sprite.Group):
        """
        Update all active particles and recycle dead ones
        
        Args:
            sprite_group: Group containing particles
        """
        dead_particles = []
        
        for particle in self.pool.active_objects:
            # Update particle
            if hasattr(particle, 'lifetime'):
                particle.lifetime -= 1
                
                # Mark dead particles
                if particle.lifetime <= 0:
                    dead_particles.append(particle)
                    if particle in sprite_group:
                        sprite_group.remove(particle)
        
        # Recycle dead particles
        for particle in dead_particles:
            self.pool.release(particle)
    
    def clear_all(self, sprite_group: pygame.sprite.Group):
        """
        Clear all particles and return them to pool
        
        Args:
            sprite_group: Group containing particles
        """
        for particle in self.pool.active_objects[:]:
            if particle in sprite_group:
                sprite_group.remove(particle)
        
        self.pool.release_all()
    
    def get_stats(self) -> dict:
        """Get particle pool statistics"""
        return self.pool.get_stats()


class ProjectilePool:
    """
    Specialized pool for projectile objects
    Handles projectile lifecycle and collision cleanup
    """
    
    def __init__(self, projectile_class, initial_size: int = 50, max_size: int = 200):
        """
        Initialize projectile pool
        
        Args:
            projectile_class: Class to instantiate for projectiles
            initial_size: Number of projectiles to pre-create
            max_size: Maximum projectiles in pool
        """
        self.projectile_class = projectile_class
        self.pool = ObjectPool(
            factory_func=lambda: projectile_class(0, 0, 0, 0),
            initial_size=initial_size,
            max_size=max_size
        )
    
    def spawn(self, x: int, y: int, vx: float, vy: float, 
              damage: int = 10, owner=None, projectile_type: str = 'arrow') -> Optional[Any]:
        """
        Spawn a projectile from the pool
        
        Args:
            x, y: Starting position
            vx, vy: Velocity
            damage: Damage dealt on hit
            owner: Entity that fired the projectile
            projectile_type: Type of projectile ('arrow', 'fireball', etc.)
            
        Returns:
            The spawned projectile or None if pool exhausted
        """
        projectile = self.pool.acquire()
        if projectile:
            # Reset projectile properties
            projectile.rect.x = x
            projectile.rect.y = y
            projectile.velocity_x = vx
            projectile.velocity_y = vy
            projectile.damage = damage
            projectile.owner = owner
            projectile.alive = True
            
            if hasattr(projectile, 'projectile_type'):
                projectile.projectile_type = projectile_type
            
            # Reset lifetime if it has one
            if hasattr(projectile, 'lifetime'):
                projectile.lifetime = 300  # 5 seconds at 60 FPS
        
        return projectile
    
    def update_all(self, sprite_group: pygame.sprite.Group, platforms=None):
        """
        Update all active projectiles and recycle dead ones
        
        Args:
            sprite_group: Group containing projectiles
            platforms: Optional list of platforms for collision
        """
        dead_projectiles = []
        
        for projectile in self.pool.active_objects:
            # Check if projectile should be recycled
            if hasattr(projectile, 'alive') and not projectile.alive:
                dead_projectiles.append(projectile)
                if projectile in sprite_group:
                    sprite_group.remove(projectile)
            elif hasattr(projectile, 'lifetime'):
                projectile.lifetime -= 1
                if projectile.lifetime <= 0:
                    dead_projectiles.append(projectile)
                    if projectile in sprite_group:
                        sprite_group.remove(projectile)
        
        # Recycle dead projectiles
        for projectile in dead_projectiles:
            self.pool.release(projectile)
    
    def clear_all(self, sprite_group: pygame.sprite.Group):
        """
        Clear all projectiles and return them to pool
        
        Args:
            sprite_group: Group containing projectiles
        """
        for projectile in self.pool.active_objects[:]:
            if projectile in sprite_group:
                sprite_group.remove(projectile)
        
        self.pool.release_all()
    
    def get_stats(self) -> dict:
        """Get projectile pool statistics"""
        return self.pool.get_stats()


class PoolManager:
    """
    Central manager for all object pools
    Provides unified interface for pool statistics and cleanup
    """
    
    def __init__(self):
        """Initialize pool manager"""
        self.pools = {}
    
    def register_pool(self, name: str, pool):
        """
        Register a pool with the manager
        
        Args:
            name: Identifier for the pool
            pool: Pool object to register
        """
        self.pools[name] = pool
    
    def get_pool(self, name: str):
        """
        Get a registered pool by name
        
        Args:
            name: Pool identifier
            
        Returns:
            Pool object or None if not found
        """
        return self.pools.get(name)
    
    def get_all_stats(self) -> dict:
        """
        Get statistics for all registered pools
        
        Returns:
            Dict mapping pool names to their stats
        """
        stats = {}
        for name, pool in self.pools.items():
            if hasattr(pool, 'get_stats'):
                stats[name] = pool.get_stats()
        return stats
    
    def clear_all(self):
        """Clear all registered pools"""
        for pool in self.pools.values():
            if hasattr(pool, 'clear_all'):
                pool.clear_all(pygame.sprite.Group())
            elif hasattr(pool, 'clear'):
                pool.clear()
    
    def get_total_objects(self) -> int:
        """
        Get total number of objects across all pools
        
        Returns:
            Total object count
        """
        total = 0
        for pool in self.pools.values():
            if hasattr(pool, 'get_stats'):
                stats = pool.get_stats()
                total += stats.get('total', 0)
        return total
    
    def get_memory_efficiency(self) -> float:
        """
        Calculate memory efficiency across all pools
        
        Returns:
            Percentage of pool capacity being utilized (0.0 to 1.0)
        """
        total_active = 0
        total_capacity = 0
        
        for pool in self.pools.values():
            if hasattr(pool, 'get_stats'):
                stats = pool.get_stats()
                total_active += stats.get('active', 0)
                total_capacity += stats.get('total', 0)
        
        return total_active / total_capacity if total_capacity > 0 else 0.0
