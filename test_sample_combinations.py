#!/usr/bin/env python3
"""
Quick test script to generate a sample of character combinations.
Useful for rapid testing without generating hundreds of character sheets.
"""

from toon import Toon
import os

def create_sample_characters():
    """Create a sample of interesting character combinations"""
    
    # Sample combinations to test various mechanics
    combinations = [
        # Race, Subrace, Class, Subclass, Level
        ("Human", None, "Fighter", "Champion", 5),
        ("Elf", "High Elf", "Wizard", None, 3),
        ("Dwarf", "Mountain Dwarf", "Barbarian", "Path of the Berserker", 6),
        ("Halfling", "Lightfoot", "Rogue", None, 4),
        ("Dwarf", "Hill Dwarf", "Bard", "College of Glamour", 6),
        ("Elf", "Wood Elf", "Ranger", None, 3),
        ("Dwarf", "Hill Dwarf", "Cleric", None, 4),
        ("Human", None, "Barbarian", "Path of the Storm Herald", 7),
        ("Human", None, "Barbarian", "Path of the Zealot", 8),
        ("Human", None, "Barbarian", "Path of the Beast", 6),
    ]
    
    output_dir = "sample_character_sheets"
    os.makedirs(output_dir, exist_ok=True)
    
    print("🧙‍♂️ Creating sample character combinations...\n")
    
    successful = 0
    failed = 0
    
    for i, (race, subrace, class_name, subclass, level) in enumerate(combinations, 1):
        try:
            # Create character name
            char_name = f"{race}"
            if subrace:
                char_name += f" {subrace}"
            char_name += f" {class_name}"
            if subclass:
                char_name += f" ({subclass})"
            
            print(f"[{i}/{len(combinations)}] Creating {char_name}...", end=" ")
            
            # Create character
            toon = Toon()
            toon.set_name(char_name)
            
            # Set race
            if subrace:
                toon.set_race(race.lower(), subrace)
            else:
                toon.set_race(race.lower())
            
            # Set ability scores
            toon.set_ability_scores({
                "strength": 15,
                "dexterity": 14,
                "constitution": 13,
                "intelligence": 12,
                "wisdom": 10,
                "charisma": 8
            })
            
            # Add class
            toon.add_class(class_name.lower(), level)
            
            # Set subclass if available
            if subclass and level >= 3:
                toon.set_subclass(class_name.lower(), subclass)
            
            # Set background
            toon.set_background("acolyte")
            
            # Generate HTML
            html_path = toon.export_character_sheet("html")
            
            if html_path and os.path.exists(html_path):
                # Move to output directory
                filename = os.path.basename(html_path)
                new_path = os.path.join(output_dir, filename)
                os.rename(html_path, new_path)
                print("✅")
                successful += 1
            else:
                print("❌ Failed to generate HTML")
                failed += 1
                
        except Exception as e:
            print(f"❌ Error: {e}")
            failed += 1
    
    print(f"\n📊 Sample Generation Complete!")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📁 Output directory: {output_dir}")
    print(f"\n💡 Open any HTML file in a web browser to test the mechanics toggle!")

if __name__ == "__main__":
    create_sample_characters() 