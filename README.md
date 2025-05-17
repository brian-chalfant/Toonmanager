# D&D 5E Character Generator (ToonManager)

A comprehensive character generator for D&D 5E with support for the upcoming 2025 expansion.

## Project Overview

ToonManager is designed to be a flexible and extensible character generator that supports both current D&D 5E rules and will be adaptable for the 2025 expansion. The system will handle character creation, leveling, and management with a focus on maintainability and easy updates for new content.

## Core Features

### 1. Character Creation
- **Race Selection**
  - Core races from Player's Handbook
  - Support for subraces
  - Racial traits and abilities
  - Prepared for 2025 changes to race mechanics

- **Class System**
  - All standard classes
  - Subclass support
  - Multi-classing capabilities
  - Level progression tracking
  - Class features and abilities

- **Ability Scores**
  - Multiple generation methods:
    - Standard Array
    - Point Buy
    - Rolling methods (3d6, 4d6 drop lowest)
  - Racial bonuses
  - Ability score improvements

- **Background System**
  - Standard backgrounds
  - Custom background support
  - Background features
  - Skill proficiencies
  - Starting equipment

### 2. Character Management
- **Equipment**
  - Inventory management
  - Currency tracking
  - Encumbrance rules
  - Magic items

- **Spellcasting**
  - Spell slots tracking
  - Known/Prepared spells
  - Spell components
  - Ritual casting

- **Character Progression**
  - Experience points tracking
  - Level-up assistance
  - Feat selection
  - ASI management

### 3. Technical Features
- **Data Storage**
  - Character data persistence
  - Import/Export functionality
  - Character backups

- **Rules Engine**
  - Flexible rules implementation
  - Easy updates for 2025 changes
  - House rules support

- **User Interface**
  - Character sheet display
  - Interactive character creation
  - Digital dice rolling
  - Character export to PDF

## Project Structure

```
ToonManager/
├── data/                 # JSON/YAML files for game data
│   ├── races/
│   ├── classes/
│   ├── spells/
│   └── equipment/
├── src/
│   ├── character/       # Character-related classes
│   ├── rules/          # Rules implementation
│   ├── dice/           # Dice rolling mechanics
│   └── ui/             # User interface components
├── tests/              # Test suite
└── docs/               # Documentation
```

## Development Phases

1. **Phase 1: Core Character Creation**
   - Basic character creation flow
   - Race and class implementation
   - Ability score generation
   - Basic rule implementation

2. **Phase 2: Character Management**
   - Equipment system
   - Spellcasting
   - Character progression
   - Data persistence

3. **Phase 3: User Interface**
   - Character creation interface
   - Character sheet display
   - Digital dice implementation
   - Export functionality

4. **Phase 4: 2025 Expansion**
   - Updates for new rules
   - Additional content
   - Migration tools for existing characters

## Technical Requirements

- Python 3.8+
- JSON for data storage
- SQLite for character persistence
- GUI framework (TBD)

## Contributing

Guidelines for contributing to the project will be added as the project develops.

## License

TBD

## Notes for 2025 Expansion

- Monitor official announcements for rule changes
- Design systems to be flexible for future modifications
- Plan for backward compatibility
- Consider migration tools for existing characters 