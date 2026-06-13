*This project has been created as part of the 42 curriculum by gcabecas, bclairot.*

# Pac-Man

A modern Python implementation of the classic Pac-Man arcade game.

## Description

Pac-Man is a recreation of the iconic arcade game originally released by Namco in 1980.

The objective of the game is to guide Pac-Man through procedurally generated mazes, collect all pacgums, avoid ghosts, and complete multiple levels while achieving the highest score possible.

This project was developed as part of the 42 curriculum with a strong focus on:

- Object-Oriented Programming
- Software Architecture
- Error Handling
- Configuration Management
- Project Management
- Third-party Package Integration
- Packaging and Deployment

## Features

- Procedurally generated mazes
- Multiple levels
- Four autonomous ghosts
- Pacgums and Super-Pacgums
- Persistent highscore system
- Main menu and pause menu
- Victory and Game Over screens
- Cheat mode for evaluation
- Configurable gameplay through JSON files
- Robust error handling

---

# Instructions

## Requirements

- Python 3.10+
- Pygame
- A-Maze-ing maze generator package

<!-- TODO @gcabecas faut recheck l'installation -->

## Installation

```bash
make install
```

Or manually:

```bash
uv sync
```

## Launch

```bash
make run
```

or

```bash
python3 pac-man.py config.json
```

## Debug

```bash
make debug
```

## Linting

```bash
make lint
```

Strict mode:

```bash
make lint-strict
```

## Clean caches

```bash
make clean
```

---

# Controls

| Action | Key |
|----------|----------|
| Move Up | ↑ |
| Move Down | ↓ |
| Move Left | ← |
| Move Right | → |
| Pause | P |
| Quit | ESC |
| Skip Level | 7 |
| Invicibility Cheat | 8 |
| Pause Timer | 9 |

---

# Configuration

The game is configured through a JSON file.

Comments beginning with `#` are ignored by the parser.

Example:

```json
{
    "highscore_filename": "highscores.json",
    "lives": 3,
    "points_per_pacgum": 10,
    "points_per_super_pacgum": 50,
    "points_per_ghost": 200,
    "seed": 42,
    "level_max_time": 90,
    "levels": [
        {
            "width": 20, 
            "height": 20
        }
    ]
}
```
## Supported Keys

| Key | Default |
|----------|----------|
| highscore_filename | highscores.json |
| lives | 3 |
| points_per_pacgum | 10 |
| points_per_super_pacgum | 50 |
| points_per_ghost | 200 |
| seed | 42 |
| level_max_time | 90 |
| levels | 10 generated levels |

## Invalid Configuration Handling

The application never crashes because of an invalid configuration.

When a value is:

- Missing
- Invalid
- Out of range

The game:

1. Logs a clear warning message.
2. Replaces the value with a safe default.
3. Continues execution.

Unknown keys are ignored.

---

# Highscore System

The game maintains a persistent Top 10 highscore list.

## Storage

Highscores are stored inside:

```text
highscores.json
```

## Validation

Player names:

- Maximum length: 10 characters
- Letters, digits and spaces only

Scores:

- Non-negative integers only

## Behaviour

At startup:

- Highscores are loaded from disk.

At game over or victory:

- The player enters a name.
- The score is inserted into the ranking.
- The file is updated.

Invalid or missing highscore files are automatically recreated.

### Why this implementation?

JSON was chosen because:

- Human-readable
- Easy to debug
- Easy to validate
- Portable
- No external database dependency

---

# Maze Generation

Maze generation is delegated entirely to the assigned A-Maze-ing package.

The project does not implement its own maze generator.

## Usage

The generator is imported and used during level creation.

Example:

```python
MazeGenerator(
    (width, height),
    perfect=False,
    seed=seed
)
```

## Design Choice

Using the external package allows:

- Reusability
- Separation of responsibilities
- Compliance with project requirements

If the generator raises an exception, the error is handled gracefully and the application remains stable.

---

# Gameplay

## Objective

Clear every pacgum from the maze while avoiding ghosts.

## Scoring

(Point are define in the config file this is an exemple)

| Event | Points |
|---------|---------|
| Pacgum | +10 |
| Super Pacgum | +50 |
| Ghost | +200 |

## Player

- Starts with 3 lives
- Respawns after losing a life
- Wins the level when all pacgums are eaten
- Wins the game after completing all levels

## Ghosts

Ghosts:

- Move autonomously
- Chase Pac-Man normally
- Flee while vulnerable
- Respawn after being eaten

## Levels

- Minimum 10 levels
- First level uses a fixed seed
- Following levels are randomly generated
- Timer applies to every level

---

# Cheat Mode

The cheat mode exists exclusively to facilitate project evaluation.

Available features:

- Invincibility
- Skip current level
- Pause timer

These tools allow evaluators to quickly test every game mechanic.

---

# User Interface

## Main Menu

- Start Game
- Highscores
- Instructions
- Exit

## HUD

Displayed during gameplay:

- Current score
- Lives remaining
- Current level
- Remaining time

## Pause Menu

- Resume
- Return to Main Menu

## End Screens

### Game Over

Displays:

- Final score
- Name entry

### Victory

Displays:

- Final score
- Congratulations message
- Name entry

---

# Implementation

The project follows an Object-Oriented architecture.

Main responsibilities are separated into dedicated modules:

- Game management
- Rendering
- Maze handling
- Entity logic
- Ghost AI
- Configuration loading
- Highscore management
- User interface

Design goals:

- Maintainability
- Testability
- Reusability
- Clear separation of concerns

---

## Project Management

Project management documents can be found in the `project_management/`
directory of the repository.

# General Software Architecture

```text
src/
│
├── config/
│   ├── __init__.py
│   ├── models.py
│   └── parser.py
│
├── entities/
│   ├── assets/
│   ├── __init__.py
│   ├── ghost.py
│   ├── ia.py
│   └── player.py
│
├── highscore/
│   ├── __init__.py
│   ├── models.py
│   └── parser.py
│
├── scenes/
│   ├── __init__.py
│   ├── base.py
│   ├── end_scene.py
│   ├── menu.py
│   └── play.py
│
├── __init__.py
├── build-entry.py
├── game.py
└── pac-man.py
```

## Architecture Overview

### Game

Controls game flow and state transitions.

### Entities

Contains game objects:

- Player
- Ghosts

### Config

Loads and validates configuration files.

---

# Project Management

Project management documentation can be found in:

```text
project_management/
```

This directory contains:

- Planning documents
- Kanban boards
- Progress tracking
- Risk analysis
- Team organization
- Testing reports
- Design decisions

The project followed an iterative development approach with continuous testing and regular code reviews.

---

# Resources

## Documentation

- Python Documentation
- Pygame Documentation
- Flake8 Documentation
- Mypy Documentation

## Articles

- Pac-Man Dossier (Namco History)
- Object-Oriented Design Principles
- Game Programming Patterns

## AI Usage

Artificial Intelligence tools were used to assist with:

- Documentation drafting
- README writing
- Error handling suggestions

No AI-generated code was used without review, testing, and understanding by project members.
