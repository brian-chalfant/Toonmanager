#!/usr/bin/env python3
"""
Test script to generate HTML character sheets for all subclasses of a specified class.
Takes a --c flag to specify the class, then generates one character per subclass using different races.

Usage:
  python test_class_subclasses.py --c barbarian
  python test_class_subclasses.py --c bard
  python test_class_subclasses.py --c fighter
"""

import argparse
import json
import os
import traceback
from pathlib import Path
from toon import Toon
from logging_config import get_logger

logger = get_logger(__name__)

def get_available_races():
    """Get all available races"""
    races_dir = Path("data/races")
    races = []
    
    for race_file in races_dir.glob("*.json"):
        try:
            with open(race_file, 'r') as f:
                race_data = json.load(f)
            races.append(race_data["name"].lower())
        except Exception as e:
            logger.warning(f"Could not load race {race_file}: {e}")
    
    return sorted(races)

def get_class_subclasses(class_name):
    """Get all subclasses for a given class"""
    class_file = Path(f"data/classes/{class_name.lower()}.json")
    
    if not class_file.exists():
        raise FileNotFoundError(f"Class file not found: {class_file}")
    
    try:
        with open(class_file, 'r') as f:
            class_data = json.load(f)
        
        subclasses = []
        if "subclasses" in class_data:
            for subclass in class_data["subclasses"]:
                subclasses.append(subclass["name"])
        
        return subclasses, class_data.get("subclass_level", 3)
    
    except Exception as e:
        raise Exception(f"Error loading class data: {e}")

def create_character(race, class_name, subclass, level):
    """Create a character with the given parameters"""
    try:
        toon = Toon()
        toon.set_name(f"{race.title()} {subclass.replace(' ', '')}")
        toon.set_race(race)
        toon.add_class(class_name, level)
        toon.set_subclass(class_name, subclass)
        toon.set_background("acolyte")  # Use consistent background
        
        return toon
    except Exception as e:
        logger.error(f"Error creating character {race} {class_name} {subclass}: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Generate character sheets for all subclasses of a class")
    parser.add_argument("--c", "--class", dest="class_name", required=True,
                       help="Class name to test (e.g., barbarian, bard, fighter)")
    parser.add_argument("--level", type=int, default=6,
                       help="Character level (default: 6)")
    parser.add_argument("--output-dir", default="test_output",
                       help="Output directory for HTML files")
    
    args = parser.parse_args()
    
    try:
        # Get available data
        races = get_available_races()
        subclasses, subclass_level = get_class_subclasses(args.class_name)
        
        if not races:
            print("❌ No races found!")
            return
        
        if not subclasses:
            print(f"❌ No subclasses found for {args.class_name}!")
            return
        
        # Create output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(exist_ok=True)
        
        print(f"🧙‍♂️ Testing {args.class_name.title()} class...")
        print(f"📋 Found {len(subclasses)} subclasses: {', '.join(subclasses)}")
        print(f"🏃‍♂️ Using {len(races)} races: {', '.join(races)}")
        print(f"📊 Character level: {args.level}")
        print(f"📁 Output directory: {output_dir}")
        print()
        
        successful = 0
        failed = 0
        
        # Create one character per subclass, cycling through races
        for i, subclass in enumerate(subclasses):
            race = races[i % len(races)]  # Cycle through races
            
            print(f"🔮 Creating {race.title()} {args.class_name.title()} ({subclass})...")
            
            try:
                # Create character
                toon = create_character(race, args.class_name, subclass, args.level)
                if not toon:
                    failed += 1
                    continue
                
                # Generate HTML (method returns the file path)
                html_path = toon.export_character_sheet('html')
                
                # Move to our desired location and rename
                import shutil
                filename = f"{race}_{args.class_name}_{subclass.replace(' ', '_').replace('/', '_')}.html"
                dest_path = output_dir / filename
                shutil.move(html_path, dest_path)
                html_path = dest_path
                
                print(f"  ✅ Generated: {html_path}")
                successful += 1
                
            except Exception as e:
                print(f"  ❌ Failed: {e}")
                logger.error(f"Failed to create {race} {args.class_name} {subclass}: {traceback.format_exc()}")
                failed += 1
        
        print()
        print("="*60)
        print(f"📊 SUMMARY")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"📁 Files in: {output_dir.absolute()}")
        
        if successful > 0:
            print()
            print("🔍 Generated files:")
            for html_file in sorted(output_dir.glob("*.html")):
                print(f"  - {html_file.name}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Script error: {traceback.format_exc()}")

if __name__ == "__main__":
    main() 