"""
Music Manager for the game
Handles background music with dynamic transitions, crossfading, and state-based playback
"""

import pygame
from typing import Dict, Optional, List
from enum import Enum
import os

class MusicState(Enum):
    """Enum for different music states"""
    MENU = "menu"
    EXPLORATION = "exploration"
    COMBAT = "combat"
    BOSS = "boss"
    VICTORY = "victory"
    DEFEAT = "defeat"
    AMBIENT = "ambient"

class MusicManager:
    """Manages background music with dynamic transitions and crossfading"""
    
    def __init__(self):
        """Initialize the music manager"""
        # Initialize pygame mixer music module if not already initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        # Music library - track file paths
        self.music_tracks: Dict[str, str] = {}
        
        # Current state tracking
        self.current_state = MusicState.MENU
        self.current_track: Optional[str] = None
        self.previous_state = MusicState.MENU
        
        # State to track mapping
        self.state_tracks: Dict[MusicState, List[str]] = {
            MusicState.MENU: [],
            MusicState.EXPLORATION: [],
            MusicState.COMBAT: [],
            MusicState.BOSS: [],
            MusicState.VICTORY: [],
            MusicState.DEFEAT: [],
            MusicState.AMBIENT: []
        }
        
        # Volume controls
        self.master_volume = 1.0
        self.music_volume = 0.5
        self._update_pygame_volume()
        
        # Combat music tracking
        self.combat_timer = 0
        self.combat_timeout = 5000  # ms - time after combat ends before returning to exploration
        self.in_combat = False
        
        # Boss music tracking
        self.boss_active = False
        self.boss_track: Optional[str] = None
        
        # Crossfade settings
        self.crossfade_duration = 2000  # milliseconds
        self.is_crossfading = False
        self.crossfade_timer = 0
        
        # Track position saving for seamless transitions
        self.saved_positions: Dict[str, float] = {}
    
    def load_music(self, name: str, filepath: str, states: List[MusicState] = None):
        """Load a music track and associate it with music states
        
        Args:
            name: Identifier for the track
            filepath: Path to the music file
            states: List of MusicStates this track can play during
        """
        if not os.path.exists(filepath):
            print(f"Music file not found: {filepath}")
            return False
        
        # Store the track
        self.music_tracks[name] = filepath
        
        # Associate with states
        if states:
            for state in states:
                if state in self.state_tracks:
                    self.state_tracks[state].append(name)
        
        print(f"Loaded music track: {name}")
        return True
    
    def play_music(self, track_name: str, loops: int = -1, fade_in: int = 0):
        """Play a specific music track
        
        Args:
            track_name: Name of the track to play
            loops: Number of times to loop (-1 for infinite)
            fade_in: Fade in duration in milliseconds
        """
        if track_name not in self.music_tracks:
            print(f"Music track not found: {track_name}")
            return
        
        # Stop current music
        if self.current_track == track_name:
            return  # Already playing
        
        # Save current position if needed
        if self.current_track:
            try:
                pos = pygame.mixer.music.get_pos() / 1000.0  # Convert to seconds
                self.saved_positions[self.current_track] = pos
            except:
                pass
        
        # Load and play new track
        filepath = self.music_tracks[track_name]
        try:
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play(loops=loops, fade_ms=fade_in)
            self.current_track = track_name
            self._update_pygame_volume()
        except Exception as e:
            print(f"Error playing music track {track_name}: {e}")
    
    def stop_music(self, fade_out: int = 0):
        """Stop the currently playing music
        
        Args:
            fade_out: Fade out duration in milliseconds
        """
        if fade_out > 0:
            pygame.mixer.music.fadeout(fade_out)
        else:
            pygame.mixer.music.stop()
        self.current_track = None
    
    def set_music_state(self, state: MusicState, force: bool = False):
        """Set the music state and transition tracks if needed
        
        Args:
            state: The new music state
            force: Force track change even if state is the same
        """
        # Handle boss music specially
        if state == MusicState.BOSS:
            self._handle_boss_music()
            return
        
        # Handle victory/defeat as one-shots
        if state in [MusicState.VICTORY, MusicState.DEFEAT]:
            self._play_state_music(state, loops=0)
            return
        
        # Don't change if already in this state (unless forced)
        if self.current_state == state and not force:
            return
        
        self.previous_state = self.current_state
        self.current_state = state
        
        # Select appropriate track for new state
        self._play_state_music(state)
    
    def _play_state_music(self, state: MusicState, loops: int = -1):
        """Play music for a specific state
        
        Args:
            state: The music state
            loops: Number of loops (-1 for infinite)
        """
        # Get available tracks for this state
        available_tracks = self.state_tracks.get(state, [])
        
        if not available_tracks:
            print(f"No music tracks available for state: {state}")
            # Generate placeholder silence
            return
        
        # For now, just play the first available track
        # TODO: Add track rotation/selection logic
        track_name = available_tracks[0]
        
        # Crossfade to new track
        self.play_music(track_name, loops=loops, fade_in=self.crossfade_duration)
    
    def _handle_boss_music(self):
        """Handle boss music activation"""
        if not self.boss_track:
            # Try to find a boss track
            boss_tracks = self.state_tracks.get(MusicState.BOSS, [])
            if boss_tracks:
                self.boss_track = boss_tracks[0]
        
        if self.boss_track:
            self.boss_active = True
            self.current_state = MusicState.BOSS
            self.play_music(self.boss_track, fade_in=500)
    
    def start_combat(self):
        """Signal that combat has started"""
        if not self.in_combat and self.current_state != MusicState.BOSS:
            self.in_combat = True
            self.combat_timer = pygame.time.get_ticks()
            self.set_music_state(MusicState.COMBAT)
    
    def end_combat(self):
        """Signal that combat has ended (with timeout)"""
        self.combat_timer = pygame.time.get_ticks()
    
    def start_boss_fight(self, boss_track: Optional[str] = None):
        """Start boss fight music
        
        Args:
            boss_track: Optional specific boss track to play
        """
        if boss_track:
            self.boss_track = boss_track
        self.set_music_state(MusicState.BOSS)
    
    def end_boss_fight(self, victory: bool = True):
        """End boss fight and play victory/defeat
        
        Args:
            victory: True if player won, False if player lost
        """
        self.boss_active = False
        self.boss_track = None
        
        if victory:
            self.set_music_state(MusicState.VICTORY)
            # Schedule return to exploration after victory music
        else:
            self.set_music_state(MusicState.DEFEAT)
    
    def update(self):
        """Update music manager - call every frame"""
        # Handle combat timeout
        if self.in_combat and self.current_state == MusicState.COMBAT:
            current_time = pygame.time.get_ticks()
            if current_time - self.combat_timer > self.combat_timeout:
                # Combat ended, return to exploration
                self.in_combat = False
                self.set_music_state(MusicState.EXPLORATION)
        
        # Check if victory/defeat music finished
        if self.current_state in [MusicState.VICTORY, MusicState.DEFEAT]:
            if not pygame.mixer.music.get_busy():
                # Music finished, return to exploration
                self.set_music_state(MusicState.EXPLORATION)
    
    def set_master_volume(self, volume: float):
        """Set master volume
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.master_volume = max(0.0, min(1.0, volume))
        self._update_pygame_volume()
    
    def set_music_volume(self, volume: float):
        """Set music volume
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.music_volume = max(0.0, min(1.0, volume))
        self._update_pygame_volume()
    
    def _update_pygame_volume(self):
        """Update pygame mixer music volume based on current settings"""
        final_volume = self.master_volume * self.music_volume
        pygame.mixer.music.set_volume(final_volume)
    
    def pause(self):
        """Pause the current music"""
        pygame.mixer.music.pause()
    
    def unpause(self):
        """Unpause the current music"""
        pygame.mixer.music.unpause()
    
    def is_playing(self) -> bool:
        """Check if music is currently playing
        
        Returns:
            True if music is playing
        """
        return pygame.mixer.music.get_busy()
    
    def preload_music(self, music_list: Dict[str, tuple]):
        """Preload multiple music tracks at once
        
        Args:
            music_list: Dictionary of {name: (filepath, [states])}
        """
        print(f"Preloading {len(music_list)} music tracks...")
        loaded = 0
        for name, (filepath, states) in music_list.items():
            if self.load_music(name, filepath, states):
                loaded += 1
        print(f"Loaded {loaded}/{len(music_list)} music tracks successfully")
    
    def get_music_info(self) -> Dict:
        """Get information about music manager state
        
        Returns:
            Dictionary with music manager stats
        """
        return {
            'current_state': self.current_state.value,
            'current_track': self.current_track,
            'is_playing': self.is_playing(),
            'in_combat': self.in_combat,
            'boss_active': self.boss_active,
            'master_volume': self.master_volume,
            'music_volume': self.music_volume,
            'loaded_tracks': len(self.music_tracks)
        }
