#!/usr/bin/env python3

from toon import Toon
from logging_config import setup_logging

def test_bard():
    # Initialize logging
    setup_logging()
    
    # Create a new character
    character = Toon()
    
    # Set basic character information
    character.set_name("Test Bard")
    character.set_race("human")
    
    # Set ability scores
    character.set_ability_scores({
        "strength": 10,
        "dexterity": 14,
        "constitution": 14,
        "intelligence": 12,
        "wisdom": 13,
        "charisma": 16
    })
    
    # Add bard class levels
    character.add_class("bard", 5)
    
    # Set subclass manually if needed
    if hasattr(character, 'set_subclass'):
        character.set_subclass("bard", "College of Creation")
    
    # Export to HTML
    try:
        html = character.export_character_sheet(format="html")
        with open("test_bard_output.html", "w") as f:
            f.write(html)
        print("Character sheet exported to test_bard_output.html")
    except Exception as e:
        print(f"Failed to export: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_bard() 