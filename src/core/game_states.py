"""
Game State Management System
Manages different game states (Menu, Playing, Paused, etc.) with clean transitions
"""

from enum import Enum
from abc import ABC, abstractmethod
import pygame


class GameStateType(Enum):
    """Enumeration of all possible game states"""
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    LEVEL_UP = "level_up"
    INVENTORY = "inventory"
    LOADING = "loading"
    VICTORY = "victory"
    SETTINGS = "settings"


class GameState(ABC):
    """
    Abstract base class for all game states
    Each state must implement enter, exit, update, draw, and handle_event methods
    """
    
    def __init__(self, game):
        self.game = game
        self.state_type = None
    
    @abstractmethod
    def enter(self):
        """Called when entering this state"""
        pass
    
    @abstractmethod
    def exit(self):
        """Called when exiting this state"""
        pass
    
    @abstractmethod
    def update(self, dt):
        """
        Update state logic
        Args:
            dt: Delta time in seconds
        """
        pass
    
    @abstractmethod
    def draw(self, screen):
        """
        Draw state visuals
        Args:
            screen: Pygame surface to draw on
        """
        pass
    
    @abstractmethod
    def handle_event(self, event):
        """
        Handle pygame events
        Args:
            event: Pygame event object
        Returns:
            True if event was handled, False otherwise
        """
        pass


class MenuState(GameState):
    """Main menu state"""
    
    def __init__(self, game):
        super().__init__(game)
        self.state_type = GameStateType.MENU
        self.font = None
        self.options = ["Start Game", "Settings", "Quit"]
        self.selected_option = 0
    
    def enter(self):
        self.font = pygame.font.Font(None, 64)
        pygame.mouse.set_visible(True)
    
    def exit(self):
        pass
    
    def update(self, dt):
        pass
    
    def draw(self, screen):
        screen.fill((20, 20, 40))
        
        # Title
        title = self.font.render("Hollow Platformer", True, (255, 255, 255))
        title_rect = title.get_rect(center=(screen.get_width() // 2, 150))
        screen.blit(title, title_rect)
        
        # Menu options
        for i, option in enumerate(self.options):
            color = (255, 215, 0) if i == self.selected_option else (200, 200, 200)
            text = self.font.render(option, True, color)
            text_rect = text.get_rect(center=(screen.get_width() // 2, 300 + i * 80))
            screen.blit(text, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
                return True
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
                return True
            elif event.key == pygame.K_RETURN:
                if self.selected_option == 0:  # Start Game
                    from src.core.events import publish, EventType
                    publish(EventType.GAME_STARTED)
                    return True
                elif self.selected_option == 1:  # Settings
                    # TODO: Implement settings
                    return True
                elif self.selected_option == 2:  # Quit
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                    return True
        return False


class PlayingState(GameState):
    """Main gameplay state"""
    
    def __init__(self, game):
        super().__init__(game)
        self.state_type = GameStateType.PLAYING
    
    def enter(self):
        pygame.mouse.set_visible(False)
        from src.core.events import publish, EventType
        publish(EventType.LEVEL_STARTED)
    
    def exit(self):
        pass
    
    def update(self, dt):
        # Game update logic happens here
        pass
    
    def draw(self, screen):
        # Game rendering happens here
        pass
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                from src.core.events import publish, EventType
                publish(EventType.GAME_PAUSED)
                return True
            elif event.key == pygame.K_TAB:
                # Open inventory
                return True
        return False


class PausedState(GameState):
    """Paused game state"""
    
    def __init__(self, game):
        super().__init__(game)
        self.state_type = GameStateType.PAUSED
        self.font = None
        self.options = ["Resume", "Settings", "Main Menu"]
        self.selected_option = 0
    
    def enter(self):
        self.font = pygame.font.Font(None, 64)
        pygame.mouse.set_visible(True)
    
    def exit(self):
        pygame.mouse.set_visible(False)
    
    def update(self, dt):
        # Don't update game logic while paused
        pass
    
    def draw(self, screen):
        # Draw dimmed game background
        overlay = pygame.Surface(screen.get_size())
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        
        # Paused text
        title = self.font.render("PAUSED", True, (255, 255, 255))
        title_rect = title.get_rect(center=(screen.get_width() // 2, 150))
        screen.blit(title, title_rect)
        
        # Menu options
        for i, option in enumerate(self.options):
            color = (255, 215, 0) if i == self.selected_option else (200, 200, 200)
            text = self.font.render(option, True, color)
            text_rect = text.get_rect(center=(screen.get_width() // 2, 300 + i * 80))
            screen.blit(text, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                from src.core.events import publish, EventType
                publish(EventType.GAME_RESUMED)
                return True
            elif event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
                return True
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
                return True
            elif event.key == pygame.K_RETURN:
                if self.selected_option == 0:  # Resume
                    from src.core.events import publish, EventType
                    publish(EventType.GAME_RESUMED)
                    return True
                elif self.selected_option == 1:  # Settings
                    # TODO: Implement settings
                    return True
                elif self.selected_option == 2:  # Main Menu
                    # TODO: Return to main menu
                    return True
        return False


class GameOverState(GameState):
    """Game over state"""
    
    def __init__(self, game):
        super().__init__(game)
        self.state_type = GameStateType.GAME_OVER
        self.font = None
        self.timer = 0
    
    def enter(self):
        self.font = pygame.font.Font(None, 72)
        self.timer = 0
        pygame.mouse.set_visible(True)
    
    def exit(self):
        pass
    
    def update(self, dt):
        self.timer += dt
    
    def draw(self, screen):
        screen.fill((20, 0, 0))
        
        # Game Over text with fade-in effect
        alpha = min(255, int(self.timer * 255))
        text = self.font.render("GAME OVER", True, (255, 50, 50))
        text.set_alpha(alpha)
        text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(text, text_rect)
        
        # Show continue prompt after delay
        if self.timer > 2:
            prompt = pygame.font.Font(None, 36).render("Press SPACE to continue", True, (200, 200, 200))
            prompt_rect = prompt.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 100))
            screen.blit(prompt, prompt_rect)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and self.timer > 2:
                # Return to menu or restart
                return True
        return False


class GameStateManager:
    """
    Manages game states and transitions between them
    """
    
    def __init__(self, game):
        self.game = game
        self.states = {}
        self.current_state = None
        self.previous_state = None
        
        # Register event listeners
        from src.core.events import subscribe, EventType
        subscribe(EventType.GAME_STARTED, self._on_game_started)
        subscribe(EventType.GAME_PAUSED, self._on_game_paused)
        subscribe(EventType.GAME_RESUMED, self._on_game_resumed)
        subscribe(EventType.GAME_OVER, self._on_game_over)
    
    def register_state(self, state: GameState):
        """Register a new state"""
        self.states[state.state_type] = state
    
    def change_state(self, state_type: GameStateType):
        """Change to a different state"""
        if state_type not in self.states:
            print(f"Warning: State {state_type} not registered!")
            return
        
        # Exit current state
        if self.current_state:
            self.current_state.exit()
            self.previous_state = self.current_state.state_type
        
        # Enter new state
        self.current_state = self.states[state_type]
        self.current_state.enter()
    
    def update(self, dt):
        """Update current state"""
        if self.current_state:
            self.current_state.update(dt)
    
    def draw(self, screen):
        """Draw current state"""
        if self.current_state:
            self.current_state.draw(screen)
    
    def handle_event(self, event):
        """Pass event to current state"""
        if self.current_state:
            return self.current_state.handle_event(event)
        return False
    
    def get_current_state_type(self) -> GameStateType:
        """Get the current state type"""
        return self.current_state.state_type if self.current_state else None
    
    # Event handlers
    def _on_game_started(self, event):
        """Handle game start event"""
        self.change_state(GameStateType.PLAYING)
    
    def _on_game_paused(self, event):
        """Handle game pause event"""
        self.change_state(GameStateType.PAUSED)
    
    def _on_game_resumed(self, event):
        """Handle game resume event"""
        self.change_state(GameStateType.PLAYING)
    
    def _on_game_over(self, event):
        """Handle game over event"""
        self.change_state(GameStateType.GAME_OVER)
