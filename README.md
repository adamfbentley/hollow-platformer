# Hollow Platformer

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Pygame](https://img.shields.io/badge/pygame-2.5+-green.svg)](https://www.pygame.org/)

A 2D action platformer game built with Python and Pygame, featuring combat mechanics, enemy AI, and boss battles.

## Overview

Hollow Platformer is a side-scrolling action game I built to learn game development and software architecture. The player navigates through levels, fights various enemies, and faces challenging boss encounters. The project showcases object-oriented design, event-driven programming, and real-time game physics.

## Features

- **Player Combat System**: Multiple attack types including melee, dash, and special abilities
- **Enemy AI**: Different enemy types with unique behaviors (patrolling, ranged attacks, shield mechanics)
- **Boss Battles**: Multi-phase boss fights with attack patterns
- **Level Progression**: Player stats, experience system, and leveling
- **Game Systems**: Inventory, particle effects, parallax scrolling, collision detection
- **UI Elements**: Combat HUD, menus, level-up screen

## Requirements

```
pygame>=2.5.0
```

## Installation

```bash
git clone https://github.com/adamfbentley/hollow-platformer.git
cd hollow-platformer
pip install -r requirements.txt
```

## Usage

Run the game:
```bash
python main.py
```

### Controls

- **Arrow Keys**: Move left/right
- **Space**: Jump
- **Z**: Primary attack
- **X**: Dash attack
- **C**: Special ability
- **ESC**: Pause menu

## Project Structure

```
hollow-platformer/
├── main.py                      # Game entry point
├── src/
│   ├── core/                    # Core systems (constants, spatial partition)
│   ├── entities/                # Player and enemy classes
│   │   ├── player.py
│   │   └── enemies/             # Enemy AI implementations
│   ├── systems/                 # Game systems (combat, stats, inventory)
│   ├── ui/                      # User interface components
│   └── world/                   # World elements (platforms, camera, particles)
├── data/                        # Game assets (not included)
└── README.md
```

## Technical Highlights

- **Modular Architecture**: Clean separation between entities, systems, and UI
- **Spatial Partitioning**: Efficient collision detection using quadtree
- **Event System**: Decoupled event handling for game actions
- **Object Pooling**: Performance optimization for particles and effects
- **State Management**: FSM for player and enemy states

## Development

This project was built as a learning exercise to explore:
- Game engine architecture
- Real-time physics and collision
- AI behavior patterns
- Performance optimization techniques
- Object-oriented design principles

## Notes

This is a personal learning project. The game is playable but assets (sprites, sounds) are not included in the repository due to licensing.

## License

MIT
