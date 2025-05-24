#!/usr/bin/env python3
"""
Comprehensive test script to generate HTML character sheets for every combination
of race, class, and subclass to ensure all mechanics work properly.
"""

import os
import json
import traceback
from pathlib import Path
from toon import Toon
from logging_config import get_logger

logger = get_logger(__name__)

def get_available_races():
    """Get all available races and their subraces"""
    races_dir = Path("data/races")
    races = {}
    
    for race_file in races_dir.glob("*.json"):
        try:
            with open(race_file, 'r') as f:
                race_data = json.load(f)
            
            race_name = race_data["name"]
            races[race_name] = {
                "subraces": []
            }
            
            # Check for subraces
            if "subraces" in race_data:
                for subrace in race_data["subraces"]:
                    races[race_name]["subraces"].append(subrace["name"])
            
            # If no subraces, add None to represent the base race
            if not races[race_name]["subraces"]:
                races[race_name]["subraces"] = [None]
                
        except Exception as e:
            logger.error(f"Error loading race {race_file}: {e}")
            
    return races

def get_available_classes():
    """Get all available classes and their subclasses"""
    classes_dir = Path("data/classes")
    classes = {}
    
    for class_file in classes_dir.glob("*.json"):
        # Skip template file
        if class_file.name == "class_template.json":
            continue
            
        try:
            with open(class_file, 'r') as f:
                class_data = json.load(f)
            
            class_name = class_data["name"]
            classes[class_name] = {
                "subclasses": [],
                "subclass_level": class_data.get("subclass_level", 3)
            }
            
            # Check for subclasses
            if "subclasses" in class_data:
                for subclass in class_data["subclasses"]:
                    classes[class_name]["subclasses"].append(subclass["name"])
            
            # If no subclasses, add None
            if not classes[class_name]["subclasses"]:
                classes[class_name]["subclasses"] = [None]
                
        except Exception as e:
            logger.error(f"Error loading class {class_file}: {e}")
            
    return classes

def create_test_character(race_name, subrace_name, class_name, subclass_name, test_level=5):
    """Create a test character with the specified combinations"""
    try:
        # Create character
        toon = Toon()
        
        # Set basic info
        char_name = f"{race_name}"
        if subrace_name:
            char_name += f" {subrace_name}"
        char_name += f" {class_name}"
        if subclass_name:
            char_name += f" ({subclass_name})"
        
        toon.set_name(char_name)
        
        # Set race
        if subrace_name:
            toon.set_race(race_name.lower(), subrace_name)
        else:
            toon.set_race(race_name.lower())
        
        # Set ability scores (use standard array)
        toon.set_ability_scores({
            "strength": 15,
            "dexterity": 14,
            "constitution": 13,
            "intelligence": 12,
            "wisdom": 10,
            "charisma": 8
        })
        
        # Add class
        toon.add_class(class_name.lower(), test_level)
        
        # Set subclass if available and character is high enough level
        if subclass_name:
            subclass_level = 3  # Default subclass level
            if test_level >= subclass_level:
                toon.set_subclass(class_name.lower(), subclass_name)
        
        # Set a basic background
        toon.set_background("acolyte")
        
        return toon
        
    except Exception as e:
        logger.error(f"Error creating character {char_name}: {e}")
        logger.error(traceback.format_exc())
        return None

def generate_html_sheet(toon, output_dir):
    """Generate HTML character sheet and save to output directory"""
    try:
        # Generate HTML
        html_path = toon.export_character_sheet("html")
        
        # Move to our output directory
        if html_path and os.path.exists(html_path):
            filename = os.path.basename(html_path)
            new_path = os.path.join(output_dir, filename)
            
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Move file
            os.rename(html_path, new_path)
            return new_path
        
        return None
        
    except Exception as e:
        logger.error(f"Error generating HTML for {toon.get_name()}: {e}")
        logger.error(traceback.format_exc())
        return None

def main():
    """Main function to generate all combinations"""
    print("🧙‍♂️ Starting comprehensive character sheet generation test...")
    print("This will create HTML sheets for every race/class/subclass combination.\n")
    
    # Create output directory
    output_dir = "test_character_sheets"
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all available options
    print("📚 Loading available races and classes...")
    races = get_available_races()
    classes = get_available_classes()
    
    print(f"Found {len(races)} races with subraces:")
    for race, data in races.items():
        subrace_count = len([s for s in data["subraces"] if s is not None])
        print(f"  • {race} ({subrace_count} subraces)" if subrace_count > 0 else f"  • {race}")
    
    print(f"\nFound {len(classes)} classes with subclasses:")
    for class_name, data in classes.items():
        subclass_count = len([s for s in data["subclasses"] if s is not None])
        print(f"  • {class_name} ({subclass_count} subclasses)" if subclass_count > 0 else f"  • {class_name}")
    
    # Calculate total combinations
    total_combinations = 0
    for race_name, race_data in races.items():
        for class_name, class_data in classes.items():
            total_combinations += len(race_data["subraces"]) * len(class_data["subclasses"])
    
    print(f"\n🎲 Generating {total_combinations} character combinations...\n")
    
    # Track results
    successful = 0
    failed = 0
    failed_combinations = []
    
    # Generate all combinations
    combination_count = 0
    for race_name, race_data in races.items():
        for subrace_name in race_data["subraces"]:
            for class_name, class_data in classes.items():
                for subclass_name in class_data["subclasses"]:
                    combination_count += 1
                    
                    # Create combination string for display
                    combo_str = f"{race_name}"
                    if subrace_name:
                        combo_str += f" {subrace_name}"
                    combo_str += f" {class_name}"
                    if subclass_name:
                        combo_str += f" ({subclass_name})"
                    
                    print(f"[{combination_count}/{total_combinations}] {combo_str}...", end=" ")
                    
                    try:
                        # Create character
                        toon = create_test_character(
                            race_name, subrace_name, class_name, subclass_name
                        )
                        
                        if toon is None:
                            print("❌ Failed to create character")
                            failed += 1
                            failed_combinations.append(combo_str)
                            continue
                        
                        # Generate HTML
                        html_path = generate_html_sheet(toon, output_dir)
                        
                        if html_path:
                            print("✅ Success")
                            successful += 1
                        else:
                            print("❌ Failed to generate HTML")
                            failed += 1
                            failed_combinations.append(combo_str)
                            
                    except Exception as e:
                        print(f"❌ Error: {e}")
                        failed += 1
                        failed_combinations.append(combo_str)
                        logger.error(f"Error with combination {combo_str}: {e}")
    
    # Print summary
    print(f"\n📊 Generation Complete!")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📁 Output directory: {output_dir}")
    
    if failed_combinations:
        print(f"\n❌ Failed combinations:")
        for combo in failed_combinations:
            print(f"  • {combo}")
    
    # Check for any pending choices that might indicate incomplete data
    print(f"\n🔍 Checking for data completeness...")
    
    # Create a sample character to check for common issues
    try:
        test_toon = Toon()
        test_toon.set_name("Test Character")
        test_toon.set_race("human")
        test_toon.add_class("fighter", 3)
        
        if test_toon.has_pending_choices():
            print("⚠️  Note: Some characters may have pending choices that need to be resolved.")
            print("   This is normal for features that require player input.")
        else:
            print("✅ No obvious data structure issues detected.")
            
    except Exception as e:
        print(f"⚠️  Warning: Basic character creation test failed: {e}")
    
    print(f"\n🎉 Test complete! Check the '{output_dir}' directory for all generated character sheets.")
    
    if successful > 0:
        print("💡 Tip: Open any of the HTML files in a web browser to test the mechanics toggle functionality!")

if __name__ == "__main__":
    main() 