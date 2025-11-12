"""
Sound Manager for the game
Handles sound effect playback with spatial audio, volume control, and sound limiting
"""

import pygame
from typing import Dict, Optional, Tuple
import os

class SoundManager:
    """Manages sound effects with spatial audio and performance optimization"""
    
    def __init__(self, max_simultaneous_sounds: int = 32):
        """Initialize the sound manager
        
        Args:
            max_simultaneous_sounds: Maximum number of sounds playing at once
        """
        # Initialize pygame mixer if not already initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        # Set maximum simultaneous sounds
        pygame.mixer.set_num_channels(max_simultaneous_sounds)
        
        # Sound library - cache loaded sounds
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        
        # Volume controls (0.0 to 1.0)
        self.master_volume = 1.0
        self.sfx_volume = 0.7
        self.category_volumes = {
            'player': 1.0,
            'combat': 1.0,
            'enemy': 0.8,
            'ui': 0.9,
            'environment': 0.7,
            'ambient': 0.5
        }
        
        # Sound limiting - track last play time for each sound
        self.sound_cooldowns: Dict[str, int] = {}
        self.min_replay_delay = 50  # milliseconds
        
        # Spatial audio parameters
        self.listener_position = (0, 0)
        self.max_audio_distance = 800  # pixels
        self.stereo_width = 400  # pixels - distance for full left/right pan
    
    def load_sound(self, name: str, filepath: str) -> bool:
        """Load a sound file into memory
        
        Args:
            name: Identifier for the sound
            filepath: Path to the sound file
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            # Check if file exists
            if not os.path.exists(filepath):
                print(f"Sound file not found: {filepath}")
                return False
            
            # Load the sound
            sound = pygame.mixer.Sound(filepath)
            self.sounds[name] = sound
            return True
            
        except Exception as e:
            print(f"Error loading sound {name}: {e}")
            return False
    
    def play_sound(self, 
                   name: str, 
                   category: str = 'environment',
                   volume_override: Optional[float] = None,
                   position: Optional[Tuple[float, float]] = None,
                   loops: int = 0) -> Optional[pygame.mixer.Channel]:
        """Play a sound effect
        
        Args:
            name: Sound identifier (must be loaded first)
            category: Sound category for volume control
            volume_override: Override volume (0.0 to 1.0), None to use category volume
            position: World position for spatial audio (x, y), None for centered
            loops: Number of times to loop (-1 for infinite)
            
        Returns:
            The channel the sound is playing on, or None if not played
        """
        # Check if sound exists
        if name not in self.sounds:
            # Try to generate placeholder if in development
            self._generate_placeholder_sound(name)
            if name not in self.sounds:
                return None
        
        # Check cooldown to prevent sound spam
        current_time = pygame.time.get_ticks()
        if name in self.sound_cooldowns:
            if current_time - self.sound_cooldowns[name] < self.min_replay_delay:
                return None
        
        # Calculate final volume
        category_vol = self.category_volumes.get(category, 1.0)
        final_volume = self.master_volume * self.sfx_volume * category_vol
        
        if volume_override is not None:
            final_volume = self.master_volume * volume_override
        
        # Get the sound
        sound = self.sounds[name]
        
        # Find available channel
        channel = pygame.mixer.find_channel()
        if channel is None:
            return None
        
        # Apply spatial audio if position provided
        if position is not None:
            left_vol, right_vol = self._calculate_stereo_pan(position, final_volume)
            channel.set_volume(left_vol, right_vol)
        else:
            channel.set_volume(final_volume)
        
        # Play the sound
        channel.play(sound, loops=loops)
        
        # Update cooldown
        self.sound_cooldowns[name] = current_time
        
        return channel
    
    def play_sound_at(self, 
                     name: str,
                     world_x: float,
                     world_y: float,
                     category: str = 'environment') -> Optional[pygame.mixer.Channel]:
        """Convenience method to play sound at world position
        
        Args:
            name: Sound identifier
            world_x: World X coordinate
            world_y: World Y coordinate
            category: Sound category
            
        Returns:
            The channel the sound is playing on, or None if not played
        """
        return self.play_sound(name, category=category, position=(world_x, world_y))
    
    def _calculate_stereo_pan(self, 
                             sound_position: Tuple[float, float], 
                             base_volume: float) -> Tuple[float, float]:
        """Calculate stereo panning based on position relative to listener
        
        Args:
            sound_position: World position of sound (x, y)
            base_volume: Base volume before spatial adjustments
            
        Returns:
            Tuple of (left_volume, right_volume)
        """
        # Calculate distance from listener
        dx = sound_position[0] - self.listener_position[0]
        dy = sound_position[1] - self.listener_position[1]
        distance = (dx * dx + dy * dy) ** 0.5
        
        # Apply distance attenuation
        if distance > self.max_audio_distance:
            return (0.0, 0.0)
        
        distance_factor = 1.0 - (distance / self.max_audio_distance)
        attenuated_volume = base_volume * distance_factor
        
        # Calculate stereo pan
        # Positive dx = sound is to the right
        # Normalize to -1 (full left) to +1 (full right)
        pan = dx / self.stereo_width
        pan = max(-1.0, min(1.0, pan))  # Clamp to [-1, 1]
        
        # Convert pan to left/right volumes
        # pan = -1: left = 1.0, right = 0.0
        # pan =  0: left = 1.0, right = 1.0
        # pan = +1: left = 0.0, right = 1.0
        left_volume = attenuated_volume * (1.0 - max(0, pan))
        right_volume = attenuated_volume * (1.0 + min(0, pan))
        
        return (left_volume, right_volume)
    
    def set_listener_position(self, x: float, y: float):
        """Update the listener position (usually the camera/player position)
        
        Args:
            x: World X coordinate
            y: World Y coordinate
        """
        self.listener_position = (x, y)
    
    def set_master_volume(self, volume: float):
        """Set master volume for all sounds
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.master_volume = max(0.0, min(1.0, volume))
    
    def set_sfx_volume(self, volume: float):
        """Set volume for all sound effects
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.sfx_volume = max(0.0, min(1.0, volume))
    
    def set_category_volume(self, category: str, volume: float):
        """Set volume for a specific category
        
        Args:
            category: Category name
            volume: Volume level (0.0 to 1.0)
        """
        if category in self.category_volumes:
            self.category_volumes[category] = max(0.0, min(1.0, volume))
    
    def stop_all_sounds(self):
        """Stop all currently playing sounds"""
        pygame.mixer.stop()
    
    def stop_sound(self, name: str):
        """Stop a specific sound if it's playing
        
        Args:
            name: Sound identifier
        """
        if name in self.sounds:
            self.sounds[name].stop()
    
    def _generate_placeholder_sound(self, name: str):
        """Generate a simple placeholder sound for development
        
        Args:
            name: Sound identifier
        """
        try:
            # Create a simple beep sound
            sample_rate = 22050
            duration = 0.1  # seconds
            frequency = 440  # Hz (A4 note)
            
            # Generate sine wave
            import numpy as np
            samples = int(sample_rate * duration)
            wave = np.sin(2 * np.pi * frequency * np.linspace(0, duration, samples))
            
            # Apply fade out to prevent clicks
            fade_samples = int(samples * 0.1)
            for i in range(fade_samples):
                wave[samples - fade_samples + i] *= (fade_samples - i) / fade_samples
            
            # Convert to 16-bit PCM
            wave = (wave * 32767).astype(np.int16)
            
            # Create stereo sound
            stereo_wave = np.column_stack((wave, wave))
            
            # Create pygame sound from array
            sound = pygame.sndarray.make_sound(stereo_wave)
            self.sounds[name] = sound
            
            print(f"Generated placeholder sound: {name}")
            
        except Exception as e:
            print(f"Could not generate placeholder sound {name}: {e}")
    
    def preload_sounds(self, sound_list: Dict[str, str]):
        """Preload multiple sounds at once
        
        Args:
            sound_list: Dictionary of {name: filepath}
        """
        print(f"Preloading {len(sound_list)} sounds...")
        loaded = 0
        for name, filepath in sound_list.items():
            if self.load_sound(name, filepath):
                loaded += 1
        print(f"Loaded {loaded}/{len(sound_list)} sounds successfully")
    
    def get_sound_info(self) -> Dict:
        """Get information about loaded sounds and current state
        
        Returns:
            Dictionary with sound manager stats
        """
        return {
            'loaded_sounds': len(self.sounds),
            'master_volume': self.master_volume,
            'sfx_volume': self.sfx_volume,
            'active_channels': pygame.mixer.get_busy(),
            'listener_position': self.listener_position
        }
