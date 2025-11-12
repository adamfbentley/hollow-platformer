"""
Configuration System
Manages game settings, balance values, and keybindings from JSON/YAML files
Supports hot-reloading for rapid development iteration
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
import pygame


class Config:
    """
    Configuration manager with hot-reload support
    Loads settings from JSON files and provides easy access
    """
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self._configs: Dict[str, dict] = {}
        self._file_timestamps: Dict[str, float] = {}
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(exist_ok=True)
        
        # Hot-reload settings
        self.hot_reload_enabled = True
        self.hot_reload_check_interval = 1.0  # seconds
        self._time_since_check = 0
        
        # Debug mode
        self.debug = False
    
    def load(self, name: str, filename: str = None):
        """
        Load a configuration file
        
        Args:
            name: Identifier for this config
            filename: JSON file to load (defaults to name.json)
        """
        if filename is None:
            filename = f"{name}.json"
        
        filepath = self.config_dir / filename
        
        try:
            with open(filepath, 'r') as f:
                config_data = json.load(f)
                self._configs[name] = config_data
                self._file_timestamps[name] = os.path.getmtime(filepath)
                
                if self.debug:
                    print(f"[Config] Loaded config '{name}' from {filename}")
                
                return config_data
                
        except FileNotFoundError:
            print(f"[Config] Config file not found: {filepath}")
            print(f"[Config] Creating default config...")
            # Create default config
            default = self._create_default_config(name)
            self.save(name, default, filename)
            return default
            
        except json.JSONDecodeError as e:
            print(f"[Config] Error parsing JSON in {filepath}: {e}")
            return {}
    
    def save(self, name: str, data: dict, filename: str = None):
        """
        Save a configuration file
        
        Args:
            name: Identifier for this config
            data: Dictionary to save
            filename: JSON file to save to (defaults to name.json)
        """
        if filename is None:
            filename = f"{name}.json"
        
        filepath = self.config_dir / filename
        
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
                self._configs[name] = data
                self._file_timestamps[name] = os.path.getmtime(filepath)
                
                if self.debug:
                    print(f"[Config] Saved config '{name}' to {filename}")
                
        except Exception as e:
            print(f"[Config] Error saving config to {filepath}: {e}")
    
    def get(self, name: str, key: str = None, default: Any = None) -> Any:
        """
        Get a configuration value
        
        Args:
            name: Config identifier
            key: Dot-separated path to value (e.g., "player.health.max")
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        if name not in self._configs:
            if self.debug:
                print(f"[Config] Config '{name}' not loaded, attempting to load...")
            self.load(name)
        
        if name not in self._configs:
            return default
        
        if key is None:
            return self._configs[name]
        
        # Navigate nested keys
        value = self._configs[name]
        for part in key.split('.'):
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        
        return value
    
    def set(self, name: str, key: str, value: Any):
        """
        Set a configuration value (does not auto-save)
        
        Args:
            name: Config identifier
            key: Dot-separated path to value
            value: Value to set
        """
        if name not in self._configs:
            self._configs[name] = {}
        
        # Navigate and set nested keys
        config = self._configs[name]
        parts = key.split('.')
        
        for part in parts[:-1]:
            if part not in config:
                config[part] = {}
            config = config[part]
        
        config[parts[-1]] = value
    
    def reload(self, name: str):
        """Force reload a configuration file"""
        if name in self._configs:
            filename = f"{name}.json"
            self.load(name, filename)
    
    def check_hot_reload(self, dt: float):
        """
        Check for file changes and reload if needed
        
        Args:
            dt: Delta time in seconds
        """
        if not self.hot_reload_enabled:
            return
        
        self._time_since_check += dt
        
        if self._time_since_check >= self.hot_reload_check_interval:
            self._time_since_check = 0
            
            for name in list(self._configs.keys()):
                filename = f"{name}.json"
                filepath = self.config_dir / filename
                
                try:
                    current_mtime = os.path.getmtime(filepath)
                    if current_mtime > self._file_timestamps.get(name, 0):
                        if self.debug:
                            print(f"[Config] Hot-reloading config '{name}'")
                        self.reload(name)
                except FileNotFoundError:
                    pass
    
    def _create_default_config(self, name: str) -> dict:
        """Create default configuration based on name"""
        defaults = {
            'game': {
                'title': 'Hollow Platformer',
                'version': '0.1.0',
                'screen': {
                    'width': 1920,
                    'height': 1080,
                    'fullscreen': True,
                    'fps': 60
                },
                'audio': {
                    'master_volume': 1.0,
                    'music_volume': 0.7,
                    'sfx_volume': 0.8
                }
            },
            'balance': {
                'player': {
                    'base_health': 100,
                    'base_damage': 10,
                    'move_speed': 5,
                    'jump_strength': -13.5,
                    'dash_speed': 18
                },
                'combat': {
                    'crit_chance': 0.05,
                    'crit_multiplier': 1.5,
                    'hitstun_frames': 12
                },
                'xp': {
                    'level_curve': 1.5,
                    'base_xp': 100,
                    'points_per_level': 5
                }
            },
            'keybindings': {
                'move_left': pygame.K_a,
                'move_right': pygame.K_d,
                'jump': pygame.K_SPACE,
                'dash': pygame.K_LSHIFT,
                'attack': 1,  # Mouse button
                'interact': pygame.K_e,
                'inventory': pygame.K_TAB,
                'pause': pygame.K_ESCAPE
            }
        }
        
        return defaults.get(name, {})
    
    def get_all(self) -> Dict[str, dict]:
        """Get all loaded configurations"""
        return self._configs.copy()
    
    def clear(self):
        """Clear all loaded configurations"""
        self._configs.clear()
        self._file_timestamps.clear()


class KeybindingManager:
    """
    Manages keyboard and mouse bindings
    Allows rebinding controls and checking pressed keys by action name
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.bindings = {}
        self.load_bindings()
    
    def load_bindings(self):
        """Load keybindings from config"""
        self.bindings = self.config.get('keybindings', default={
            'move_left': pygame.K_a,
            'move_right': pygame.K_d,
            'jump': pygame.K_SPACE,
            'dash': pygame.K_LSHIFT,
            'attack': 1,  # Mouse button
            'interact': pygame.K_e,
            'inventory': pygame.K_TAB,
            'pause': pygame.K_ESCAPE
        })
    
    def save_bindings(self):
        """Save keybindings to config"""
        for action, key in self.bindings.items():
            self.config.set('keybindings', action, key)
        self.config.save('keybindings')
    
    def is_action_pressed(self, action: str) -> bool:
        """
        Check if an action's key is currently pressed
        
        Args:
            action: Action name (e.g., 'jump', 'attack')
        
        Returns:
            True if the bound key is pressed
        """
        if action not in self.bindings:
            return False
        
        key = self.bindings[action]
        
        # Check if it's a keyboard key
        if isinstance(key, int) and key < 1000:
            keys = pygame.key.get_pressed()
            return keys[key]
        
        # Check if it's a mouse button (values like 1, 2, 3)
        # Note: Mouse buttons need to be checked differently
        return False
    
    def is_action_just_pressed(self, action: str, event: pygame.event.Event) -> bool:
        """
        Check if an action was just pressed this frame
        
        Args:
            action: Action name
            event: Pygame event to check
        
        Returns:
            True if this event matches the action
        """
        if action not in self.bindings:
            return False
        
        key = self.bindings[action]
        
        # Keyboard event
        if event.type == pygame.KEYDOWN and event.key == key:
            return True
        
        # Mouse button event
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == key:
            return True
        
        return False
    
    def rebind(self, action: str, new_key: int):
        """
        Rebind an action to a new key
        
        Args:
            action: Action name
            new_key: New pygame key constant or mouse button
        """
        self.bindings[action] = new_key
    
    def get_key_name(self, action: str) -> str:
        """Get human-readable name of key bound to action"""
        if action not in self.bindings:
            return "Unbound"
        
        key = self.bindings[action]
        
        # Mouse button
        if key in [1, 2, 3, 4, 5]:
            button_names = {1: "Left Click", 2: "Middle Click", 3: "Right Click", 
                          4: "Mouse 4", 5: "Mouse 5"}
            return button_names.get(key, f"Mouse {key}")
        
        # Keyboard key
        return pygame.key.name(key).upper()


# Global config instance
_global_config = None


def get_config() -> Config:
    """Get the global config instance (singleton pattern)"""
    global _global_config
    if _global_config is None:
        _global_config = Config()
        # Load default configs
        _global_config.load('game')
        _global_config.load('balance')
        _global_config.load('keybindings')
    return _global_config
