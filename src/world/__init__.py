"""
World Package
Environmental systems: particles, platforms, camera, collectibles
"""

from .particles import Particle, DamageNumber
from .platform import Platform
from .camera import Camera, ParallaxLayer
from .collectibles import Coin
from .decorations import DecorativeElement

__all__ = ['Particle', 'DamageNumber', 'Platform', 'Camera', 'ParallaxLayer', 'Coin', 'DecorativeElement']

