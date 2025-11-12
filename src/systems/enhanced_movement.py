"""
Enhanced Movement Controller
Implements tight, responsive movement inspired by Celeste and Hollow Knight
"""

import pygame
import math

class EnhancedMovementController:
    """Polished movement system with industry-standard feel"""
    
    def __init__(self, player):
        self.player = player
        
        # Movement parameters (tuned for tight control)
        self.ground_accel = 2.5  # Faster ground acceleration (Celeste: 10)
        self.ground_decel = 3.5  # Even faster deceleration for snappy stops
        self.air_accel = 1.8     # Good air control (Celeste: 6.5)
        self.air_decel = 2.0     # Air braking
        self.max_run_speed = 6.0
        self.max_fall_speed = 12.0
        self.fast_fall_speed = 16.0  # Holding down
        
        # Jump parameters (Celeste-inspired)
        self.jump_speed = -12.0
        self.jump_cut_multiplier = 0.5  # Jump height control
        self.variable_jump_time = 10  # Frames to apply extra jump force
        self.jump_grace_time = 6  # Coyote time frames
        self.jump_buffer_time = 6  # Jump buffer frames
        
        # Gravity (Celeste uses different gravity for rise/fall)
        self.gravity = 0.6
        self.gravity_multiplier_rising = 0.8  # Floatier going up
        self.gravity_multiplier_falling = 1.2  # Snappier coming down
        self.gravity_max_fall_multiplier = 1.5  # Terminal velocity boost
        
        # Dash parameters
        self.dash_speed = 12.0
        self.dash_time = 10  # Frames
        self.dash_cooldown = 20  # Frames
        self.dash_end_speed_mult = 0.6  # Preserve momentum after dash
        
        # Wall slide
        self.wall_slide_speed = 2.0
        self.wall_jump_h_speed = 8.0
        self.wall_jump_v_speed = -11.0
        self.wall_jump_force_time = 8  # Frames of forced horizontal movement
        
        # State tracking
        self.jump_grace_timer = 0
        self.jump_buffer_timer = 0
        self.variable_jump_timer = 0
        self.was_on_ground = False
        self.wall_jump_force_timer = 0
        self.wall_jump_direction = 0
        
    def update(self, keys, platforms):
        """Update movement with enhanced feel"""
        player = self.player
        
        # Update timers
        if self.jump_grace_timer > 0:
            self.jump_grace_timer -= 1
        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= 1
        if self.variable_jump_timer > 0:
            self.variable_jump_timer -= 1
        if self.wall_jump_force_timer > 0:
            self.wall_jump_force_timer -= 1
        
        # Coyote time - grace period after leaving ground
        if player.on_ground and not self.was_on_ground:
            self.jump_grace_timer = self.jump_grace_time
        self.was_on_ground = player.on_ground
        
        # Handle dash
        if player.is_dashing:
            self._handle_dash()
            return
        
        # Horizontal movement
        self._handle_horizontal_movement(keys)
        
        # Jump input
        self._handle_jump_input(keys)
        
        # Apply gravity
        self._apply_enhanced_gravity()
        
        # Wall slide
        if player.on_wall and not player.on_ground and player.velocity_y > 0:
            player.velocity_y = min(player.velocity_y, self.wall_slide_speed)
        
        # Clamp velocities
        player.velocity_x = max(-self.max_run_speed, min(self.max_run_speed, player.velocity_x))
        
        # Fast fall (holding down)
        max_fall = self.fast_fall_speed if keys[pygame.K_DOWN] or keys[pygame.K_s] else self.max_fall_speed
        player.velocity_y = min(player.velocity_y, max_fall)
    
    def _handle_horizontal_movement(self, keys):
        """Tight horizontal movement with proper acceleration"""
        player = self.player
        
        # Get input direction
        move_input = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_input = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_input = 1
        
        # Wall jump force overrides input temporarily
        if self.wall_jump_force_timer > 0:
            target_speed = self.wall_jump_direction * self.wall_jump_h_speed
            player.velocity_x = target_speed
            return
        
        # Choose acceleration based on ground state
        if player.on_ground:
            accel = self.ground_accel if move_input != 0 else self.ground_decel
        else:
            accel = self.air_accel if move_input != 0 else self.air_decel
        
        # Apply acceleration
        if move_input != 0:
            # Accelerating
            target_speed = move_input * self.max_run_speed
            player.velocity_x = self._approach(player.velocity_x, target_speed, accel)
            player.facing_right = (move_input > 0)
        else:
            # Decelerating
            player.velocity_x = self._approach(player.velocity_x, 0, accel)
    
    def _handle_jump_input(self, keys):
        """Handle jump with proper buffering and variable height"""
        player = self.player
        jump_key = keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]
        
        # Jump pressed
        if jump_key and not player.jump_held:
            player.jump_held = True
            self.jump_buffer_timer = self.jump_buffer_time
        
        # Jump released - cut jump short for variable height
        if not jump_key and player.jump_held:
            player.jump_held = False
            self.variable_jump_timer = 0
            # Cut jump velocity for lower jump
            if player.velocity_y < 0:
                player.velocity_y *= self.jump_cut_multiplier
        
        # Try to jump if buffered
        if self.jump_buffer_timer > 0:
            jump_performed = False
            
            # Wall jump
            if player.on_wall and not player.on_ground:
                self._perform_wall_jump()
                jump_performed = True
            # Ground/coyote jump
            elif player.on_ground or self.jump_grace_timer > 0:
                self._perform_jump()
                jump_performed = True
            # Double jump
            elif player.jumps_available > 0:
                self._perform_double_jump()
                jump_performed = True
            
            if jump_performed:
                self.jump_buffer_timer = 0
        
        # Variable jump height - hold for higher jump
        if player.jump_held and self.variable_jump_timer > 0 and player.velocity_y < 0:
            # Apply extra upward force while holding jump
            extra_force = abs(self.jump_speed) * 0.08
            player.velocity_y -= extra_force
    
    def _perform_jump(self):
        """Execute ground/coyote jump"""
        player = self.player
        player.velocity_y = self.jump_speed
        player.jumps_available = player.max_jumps - 1
        self.jump_grace_timer = 0
        self.variable_jump_timer = self.variable_jump_time
        player.spawn_particles('jump', 8)
        if player.sound_manager:
            player.sound_manager.play_sound('player_jump', category='player')
    
    def _perform_double_jump(self):
        """Execute double jump"""
        player = self.player
        player.velocity_y = self.jump_speed * 0.95  # Slightly weaker
        player.jumps_available -= 1
        self.variable_jump_timer = self.variable_jump_time
        player.spawn_particles('jump', 10)
        if player.sound_manager:
            player.sound_manager.play_sound('player_jump', category='player')
    
    def _perform_wall_jump(self):
        """Execute wall jump with forced horizontal movement"""
        player = self.player
        player.velocity_y = self.wall_jump_v_speed
        self.wall_jump_direction = -player.wall_side
        player.velocity_x = self.wall_jump_direction * self.wall_jump_h_speed
        self.wall_jump_force_timer = self.wall_jump_force_time
        player.on_wall = False
        player.jumps_available = player.max_jumps - 1
        self.variable_jump_timer = self.variable_jump_time
        player.spawn_particles('jump', 6)
        if player.sound_manager:
            player.sound_manager.play_sound('player_jump', category='player')
    
    def _apply_enhanced_gravity(self):
        """Apply gravity with rise/fall asymmetry like Celeste"""
        player = self.player
        
        # Different gravity for rising vs falling
        if player.velocity_y < 0:
            # Rising - floatier
            gravity = self.gravity * self.gravity_multiplier_rising
        elif player.velocity_y > 3:
            # Fast falling - snappier
            gravity = self.gravity * self.gravity_multiplier_falling
        else:
            # Apex of jump - normal
            gravity = self.gravity
        
        player.velocity_y += gravity
    
    def _handle_dash(self):
        """Handle dash with proper momentum preservation"""
        player = self.player
        player.dash_timer -= 1
        
        # Maintain dash speed
        player.velocity_x = player.dash_direction * self.dash_speed
        player.velocity_y = 0  # No gravity during dash
        
        # Spawn trail
        player.spawn_particles('dash', 2)
        
        # End dash
        if player.dash_timer <= 0:
            player.is_dashing = False
            # Preserve some momentum
            player.velocity_x *= self.dash_end_speed_mult
    
    def try_dash(self):
        """Attempt to start a dash"""
        player = self.player
        if player.can_dash and not player.is_dashing:
            player.is_dashing = True
            player.dash_timer = self.dash_time
            player.can_dash = False
            player.dash_cooldown = self.dash_cooldown
            player.dash_direction = 1 if player.facing_right else -1
            if player.sound_manager:
                player.sound_manager.play_sound('player_dash', category='player')
            return True
        return False
    
    @staticmethod
    def _approach(current, target, increment):
        """Move current value towards target by increment (utility function from Celeste)"""
        if current < target:
            return min(current + increment, target)
        else:
            return max(current - increment, target)
