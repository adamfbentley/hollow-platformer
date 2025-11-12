"""
Resource Manager
Centralized loading and caching system for game assets (images, sounds, fonts)
Prevents duplicate loading and manages memory efficiently
"""

import pygame
import os
from typing import Dict, Optional
from pathlib import Path


class ResourceManager:
    """
    Manages game resources with caching and lazy loading
    Prevents loading the same resource multiple times
    """
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        
        # Resource caches
        self._images: Dict[str, pygame.Surface] = {}
        self._sounds: Dict[str, pygame.mixer.Sound] = {}
        self._fonts: Dict[tuple, pygame.font.Font] = {}  # (name, size) -> Font
        self._music: Dict[str, str] = {}  # name -> filepath
        
        # Statistics
        self._stats = {
            'images_loaded': 0,
            'sounds_loaded': 0,
            'fonts_loaded': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        # Configuration
        self.default_colorkey = None  # Set to color for transparency
        self.convert_alpha = True  # Use convert_alpha() for images
        
        # Debug mode
        self.debug = False
    
    def load_image(self, filename: str, colorkey=None, scale: tuple = None) -> pygame.Surface:
        """
        Load an image with caching
        
        Args:
            filename: Path to image file relative to base_path
            colorkey: Color to treat as transparent (or -1 for top-left pixel)
            scale: Tuple (width, height) to scale image, or None to keep original
        
        Returns:
            Loaded pygame Surface
        """
        # Create cache key including scale
        cache_key = f"{filename}_{scale}" if scale else filename
        
        # Check cache
        if cache_key in self._images:
            self._stats['cache_hits'] += 1
            return self._images[cache_key]
        
        # Load image
        self._stats['cache_misses'] += 1
        filepath = self.base_path / filename
        
        try:
            image = pygame.image.load(str(filepath))
            
            # Apply colorkey
            if colorkey is not None:
                if colorkey == -1:
                    colorkey = image.get_at((0, 0))
                image.set_colorkey(colorkey, pygame.RLEACCEL)
                image = image.convert()
            elif self.convert_alpha:
                image = image.convert_alpha()
            else:
                image = image.convert()
            
            # Scale if requested
            if scale:
                image = pygame.transform.scale(image, scale)
            
            # Cache and return
            self._images[cache_key] = image
            self._stats['images_loaded'] += 1
            
            if self.debug:
                print(f"[ResourceManager] Loaded image: {filename}")
            
            return image
            
        except pygame.error as e:
            print(f"[ResourceManager] Failed to load image {filename}: {e}")
            # Return a placeholder surface
            placeholder = pygame.Surface((32, 32))
            placeholder.fill((255, 0, 255))  # Magenta for missing texture
            return placeholder
    
    def load_sound(self, filename: str) -> Optional[pygame.mixer.Sound]:
        """
        Load a sound effect with caching
        
        Args:
            filename: Path to sound file relative to base_path
        
        Returns:
            Loaded pygame Sound object, or None if loading fails
        """
        # Check cache
        if filename in self._sounds:
            self._stats['cache_hits'] += 1
            return self._sounds[filename]
        
        # Load sound
        self._stats['cache_misses'] += 1
        filepath = self.base_path / filename
        
        try:
            sound = pygame.mixer.Sound(str(filepath))
            self._sounds[filename] = sound
            self._stats['sounds_loaded'] += 1
            
            if self.debug:
                print(f"[ResourceManager] Loaded sound: {filename}")
            
            return sound
            
        except pygame.error as e:
            print(f"[ResourceManager] Failed to load sound {filename}: {e}")
            return None
    
    def load_font(self, name: Optional[str], size: int) -> pygame.font.Font:
        """
        Load a font with caching
        
        Args:
            name: Font filename relative to base_path, or None for default font
            size: Font size in pixels
        
        Returns:
            Loaded pygame Font object
        """
        cache_key = (name, size)
        
        # Check cache
        if cache_key in self._fonts:
            self._stats['cache_hits'] += 1
            return self._fonts[cache_key]
        
        # Load font
        self._stats['cache_misses'] += 1
        
        try:
            if name is None:
                font = pygame.font.Font(None, size)
            else:
                filepath = self.base_path / name
                font = pygame.font.Font(str(filepath), size)
            
            self._fonts[cache_key] = font
            self._stats['fonts_loaded'] += 1
            
            if self.debug:
                print(f"[ResourceManager] Loaded font: {name} at size {size}")
            
            return font
            
        except pygame.error as e:
            print(f"[ResourceManager] Failed to load font {name}: {e}")
            # Return default font
            font = pygame.font.Font(None, size)
            self._fonts[cache_key] = font
            return font
    
    def load_music(self, name: str, filename: str):
        """
        Register music file (music is not loaded into memory until played)
        
        Args:
            name: Identifier for this music track
            filename: Path to music file relative to base_path
        """
        filepath = self.base_path / filename
        self._music[name] = str(filepath)
        
        if self.debug:
            print(f"[ResourceManager] Registered music: {name} -> {filename}")
    
    def play_music(self, name: str, loops: int = -1, fade_ms: int = 0):
        """
        Play a registered music track
        
        Args:
            name: Identifier for music track
            loops: Number of times to loop (-1 for infinite)
            fade_ms: Fade in time in milliseconds
        """
        if name in self._music:
            try:
                pygame.mixer.music.load(self._music[name])
                if fade_ms > 0:
                    pygame.mixer.music.play(loops, fade_ms=fade_ms)
                else:
                    pygame.mixer.music.play(loops)
            except pygame.error as e:
                print(f"[ResourceManager] Failed to play music {name}: {e}")
        else:
            print(f"[ResourceManager] Music '{name}' not registered")
    
    def stop_music(self, fade_ms: int = 0):
        """
        Stop currently playing music
        
        Args:
            fade_ms: Fade out time in milliseconds
        """
        if fade_ms > 0:
            pygame.mixer.music.fadeout(fade_ms)
        else:
            pygame.mixer.music.stop()
    
    def get_image(self, filename: str) -> Optional[pygame.Surface]:
        """Get cached image without loading"""
        return self._images.get(filename)
    
    def get_sound(self, filename: str) -> Optional[pygame.mixer.Sound]:
        """Get cached sound without loading"""
        return self._sounds.get(filename)
    
    def clear_cache(self, resource_type: str = 'all'):
        """
        Clear resource cache
        
        Args:
            resource_type: 'images', 'sounds', 'fonts', 'music', or 'all'
        """
        if resource_type in ('images', 'all'):
            self._images.clear()
        if resource_type in ('sounds', 'all'):
            self._sounds.clear()
        if resource_type in ('fonts', 'all'):
            self._fonts.clear()
        if resource_type in ('music', 'all'):
            self._music.clear()
    
    def preload_resources(self, manifest: dict):
        """
        Preload resources from a manifest dictionary
        
        Args:
            manifest: Dictionary with keys 'images', 'sounds', 'fonts', 'music'
                     Each containing lists of resources to load
        
        Example:
            manifest = {
                'images': [
                    {'file': 'player.png', 'colorkey': -1},
                    {'file': 'enemy.png', 'scale': (64, 64)}
                ],
                'sounds': ['jump.wav', 'hit.wav'],
                'fonts': [
                    {'name': 'font.ttf', 'size': 32},
                    {'name': None, 'size': 16}
                ],
                'music': [
                    {'name': 'menu_theme', 'file': 'music/menu.ogg'},
                    {'name': 'battle_theme', 'file': 'music/battle.ogg'}
                ]
            }
        """
        if 'images' in manifest:
            for img in manifest['images']:
                if isinstance(img, str):
                    self.load_image(img)
                else:
                    self.load_image(
                        img['file'],
                        colorkey=img.get('colorkey'),
                        scale=img.get('scale')
                    )
        
        if 'sounds' in manifest:
            for sound in manifest['sounds']:
                self.load_sound(sound)
        
        if 'fonts' in manifest:
            for font in manifest['fonts']:
                self.load_font(font['name'], font['size'])
        
        if 'music' in manifest:
            for music in manifest['music']:
                self.load_music(music['name'], music['file'])
    
    def get_stats(self) -> dict:
        """Get resource manager statistics"""
        stats = self._stats.copy()
        stats['cached_images'] = len(self._images)
        stats['cached_sounds'] = len(self._sounds)
        stats['cached_fonts'] = len(self._fonts)
        stats['registered_music'] = len(self._music)
        
        # Calculate cache hit rate
        total_requests = stats['cache_hits'] + stats['cache_misses']
        if total_requests > 0:
            stats['cache_hit_rate'] = f"{(stats['cache_hits'] / total_requests) * 100:.1f}%"
        else:
            stats['cache_hit_rate'] = "0%"
        
        return stats
    
    def reset_stats(self):
        """Reset statistics counters"""
        self._stats = {
            'images_loaded': 0,
            'sounds_loaded': 0,
            'fonts_loaded': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }


# Global resource manager instance
_global_resource_manager = None


def get_resource_manager() -> ResourceManager:
    """Get the global resource manager instance (singleton pattern)"""
    global _global_resource_manager
    if _global_resource_manager is None:
        _global_resource_manager = ResourceManager()
    return _global_resource_manager


# Convenience functions
def load_image(filename: str, colorkey=None, scale: tuple = None) -> pygame.Surface:
    """Load an image using global resource manager"""
    return get_resource_manager().load_image(filename, colorkey, scale)


def load_sound(filename: str) -> Optional[pygame.mixer.Sound]:
    """Load a sound using global resource manager"""
    return get_resource_manager().load_sound(filename)


def load_font(name: Optional[str], size: int) -> pygame.font.Font:
    """Load a font using global resource manager"""
    return get_resource_manager().load_font(name, size)


def play_music(name: str, loops: int = -1, fade_ms: int = 0):
    """Play music using global resource manager"""
    get_resource_manager().play_music(name, loops, fade_ms)


def stop_music(fade_ms: int = 0):
    """Stop music using global resource manager"""
    get_resource_manager().stop_music(fade_ms)
