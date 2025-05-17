# ToonManager

ToonManager is a Python-based character management system designed for creating, managing, and exporting character sheets for tabletop role-playing games.

## Features

- Character creation and management
- Ability score management
- Race and class selection
- Character sheet export to PDF and HTML formats
- Logging system for debugging and tracking
- Command-line interface for interactive character management

## Project Structure

```
ToonManager/
├── characters/          # Directory for storing character data
├── data/               # Static data files
├── logs/               # Application logs
├── templates/          # HTML/PDF templates for character sheets
├── cli.py             # Command-line interface implementation
├── file_functions.py   # File handling utilities
├── logging_config.py   # Logging configuration
├── main.py            # Main application entry point
├── requirements.txt    # Project dependencies
├── test_cli.py        # CLI tests
├── test_main.py       # Main functionality tests
└── toon.py            # Core character class implementation
```

## Requirements

- Python 3.x
- PyPDF2 >= 3.0.0
- Jinja2 >= 3.0.0

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ToonManager.git
cd ToonManager
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

Run the CLI for interactive character management:
```bash
python cli.py
```

### Programmatic Usage

```python
from toon import Toon

# Create a new character
character = Toon()

# Set basic information
character.set_name("Character Name")
character.set_race("race")

# Set ability scores
character.set_ability_scores({
    "strength": 10,
    "dexterity": 14,
    "constitution": 12,
    "intelligence": 18,
    "wisdom": 16,
    "charisma": 14
})

# Add class levels
character.add_class("class_name", level)

# Export character sheet
character.export_character_sheet(format="pdf")  # or format="html"
```

## Testing

Run the test suite:
```bash
python -m pytest
```

## Logging

Logs are stored in the `logs/` directory. The logging system is configured in `logging_config.py` and provides detailed information about application operations and errors.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here] 