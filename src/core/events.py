"""
Event System for Game
Provides decoupled communication between game components using publish-subscribe pattern
"""

from typing import Callable, Dict, List, Any
from collections import defaultdict


class Event:
    """Base class for all game events"""
    def __init__(self, event_type: str, **data):
        self.type = event_type
        self.data = data
    
    def __repr__(self):
        return f"Event({self.type}, {self.data})"


# Common game events
class EventType:
    """Predefined event types for common game events"""
    
    # Player events
    PLAYER_DAMAGED = "player_damaged"
    PLAYER_DIED = "player_died"
    PLAYER_HEALED = "player_healed"
    PLAYER_LEVELED_UP = "player_leveled_up"
    PLAYER_GAINED_XP = "player_gained_xp"
    PLAYER_RESPAWNED = "player_respawned"
    
    # Combat events
    ENEMY_DAMAGED = "enemy_damaged"
    ENEMY_DIED = "enemy_died"
    ATTACK_STARTED = "attack_started"
    ATTACK_HIT = "attack_hit"
    CRITICAL_HIT = "critical_hit"
    COMBO_INCREASED = "combo_increased"
    COMBO_BROKEN = "combo_broken"
    
    # Item/Inventory events
    ITEM_COLLECTED = "item_collected"
    ITEM_EQUIPPED = "item_equipped"
    ITEM_UNEQUIPPED = "item_unequipped"
    ITEM_USED = "item_used"
    ITEM_DROPPED = "item_dropped"
    INVENTORY_FULL = "inventory_full"
    
    # World events
    COIN_COLLECTED = "coin_collected"
    CHECKPOINT_REACHED = "checkpoint_reached"
    AREA_ENTERED = "area_entered"
    AREA_EXITED = "area_exited"
    DOOR_OPENED = "door_opened"
    SWITCH_ACTIVATED = "switch_activated"
    
    # UI events
    MENU_OPENED = "menu_opened"
    MENU_CLOSED = "menu_closed"
    BUTTON_CLICKED = "button_clicked"
    OPTION_CHANGED = "option_changed"
    
    # Game state events
    GAME_STARTED = "game_started"
    GAME_PAUSED = "game_paused"
    GAME_RESUMED = "game_resumed"
    GAME_OVER = "game_over"
    LEVEL_STARTED = "level_started"
    LEVEL_COMPLETED = "level_completed"
    
    # Audio events
    PLAY_SOUND = "play_sound"
    PLAY_MUSIC = "play_music"
    STOP_MUSIC = "stop_music"
    
    # Screen effects
    SCREEN_SHAKE = "screen_shake"
    HIT_FREEZE = "hit_freeze"
    SLOW_MOTION = "slow_motion"
    FLASH_SCREEN = "flash_screen"


class EventManager:
    """
    Central event manager using publish-subscribe pattern
    Allows decoupled communication between game systems
    """
    
    def __init__(self):
        # Dictionary of event_type -> list of callback functions
        self._listeners: Dict[str, List[Callable]] = defaultdict(list)
        
        # Event queue for delayed processing
        self._event_queue: List[Event] = []
        
        # Track statistics
        self._stats = {
            'events_fired': 0,
            'events_queued': 0,
            'listeners_registered': 0
        }
        
        # Debug mode
        self.debug = False
    
    def subscribe(self, event_type: str, callback: Callable):
        """
        Subscribe to an event type
        
        Args:
            event_type: The type of event to listen for
            callback: Function to call when event fires (receives Event object)
        """
        if callback not in self._listeners[event_type]:
            self._listeners[event_type].append(callback)
            self._stats['listeners_registered'] += 1
            
            if self.debug:
                print(f"[EventManager] Registered listener for '{event_type}'")
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """
        Unsubscribe from an event type
        
        Args:
            event_type: The event type to stop listening to
            callback: The callback function to remove
        """
        if callback in self._listeners[event_type]:
            self._listeners[event_type].remove(callback)
            
            if self.debug:
                print(f"[EventManager] Unregistered listener for '{event_type}'")
    
    def publish(self, event_type: str, **data):
        """
        Publish an event immediately
        
        Args:
            event_type: Type of event
            **data: Event data as keyword arguments
        """
        event = Event(event_type, **data)
        self._fire_event(event)
    
    def publish_event(self, event: Event):
        """
        Publish an Event object immediately
        
        Args:
            event: The Event object to publish
        """
        self._fire_event(event)
    
    def queue_event(self, event_type: str, **data):
        """
        Queue an event for later processing
        Useful when you want to defer event handling
        
        Args:
            event_type: Type of event
            **data: Event data as keyword arguments
        """
        event = Event(event_type, **data)
        self._event_queue.append(event)
        self._stats['events_queued'] += 1
        
        if self.debug:
            print(f"[EventManager] Queued event: {event}")
    
    def process_queued_events(self):
        """Process all queued events"""
        while self._event_queue:
            event = self._event_queue.pop(0)
            self._fire_event(event)
    
    def _fire_event(self, event: Event):
        """Internal method to fire an event to all listeners"""
        self._stats['events_fired'] += 1
        
        if self.debug:
            print(f"[EventManager] Firing event: {event}")
        
        # Call all registered listeners for this event type
        for callback in self._listeners[event.type]:
            try:
                callback(event)
            except Exception as e:
                print(f"[EventManager] Error in event listener for '{event.type}': {e}")
    
    def clear_listeners(self, event_type: str = None):
        """
        Clear all listeners for a specific event type, or all listeners
        
        Args:
            event_type: Specific event type to clear, or None to clear all
        """
        if event_type:
            self._listeners[event_type].clear()
        else:
            self._listeners.clear()
    
    def get_listener_count(self, event_type: str = None) -> int:
        """Get count of registered listeners"""
        if event_type:
            return len(self._listeners.get(event_type, []))
        else:
            return sum(len(listeners) for listeners in self._listeners.values())
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event manager statistics"""
        stats = self._stats.copy()
        stats['active_listeners'] = self.get_listener_count()
        stats['queued_events'] = len(self._event_queue)
        return stats
    
    def reset_stats(self):
        """Reset statistics counters"""
        self._stats = {
            'events_fired': 0,
            'events_queued': 0,
            'listeners_registered': 0
        }


# Global event manager instance
_global_event_manager = None


def get_event_manager() -> EventManager:
    """Get the global event manager instance (singleton pattern)"""
    global _global_event_manager
    if _global_event_manager is None:
        _global_event_manager = EventManager()
    return _global_event_manager


# Convenience functions for common operations
def subscribe(event_type: str, callback: Callable):
    """Subscribe to an event (uses global event manager)"""
    get_event_manager().subscribe(event_type, callback)


def unsubscribe(event_type: str, callback: Callable):
    """Unsubscribe from an event (uses global event manager)"""
    get_event_manager().unsubscribe(event_type, callback)


def publish(event_type: str, **data):
    """Publish an event (uses global event manager)"""
    get_event_manager().publish(event_type, **data)


def queue_event(event_type: str, **data):
    """Queue an event (uses global event manager)"""
    get_event_manager().queue_event(event_type, **data)


def process_events():
    """Process queued events (uses global event manager)"""
    get_event_manager().process_queued_events()
