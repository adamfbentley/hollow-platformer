"""
Core systems package
"""

from src.core.events import (
    EventManager, 
    Event, 
    EventType,
    get_event_manager,
    subscribe,
    unsubscribe,
    publish,
    queue_event,
    process_events
)

from src.core.game_states import (
    GameState,
    GameStateType,
    GameStateManager,
    MenuState,
    PlayingState,
    PausedState,
    GameOverState
)

from src.core.resources import (
    ResourceManager,
    get_resource_manager,
    load_image,
    load_sound,
    load_font,
    play_music,
    stop_music
)

from src.core.config import (
    Config,
    KeybindingManager,
    get_config
)

__all__ = [
    # Events
    'EventManager', 'Event', 'EventType',
    'get_event_manager', 'subscribe', 'unsubscribe', 'publish', 'queue_event', 'process_events',
    # Game States
    'GameState', 'GameStateType', 'GameStateManager',
    'MenuState', 'PlayingState', 'PausedState', 'GameOverState',
    # Resources
    'ResourceManager', 'get_resource_manager',
    'load_image', 'load_sound', 'load_font', 'play_music', 'stop_music',
    # Config
    'Config', 'KeybindingManager', 'get_config'
]
