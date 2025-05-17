#!/usr/bin/env python3

import argparse
from toon import Toon, CharacterError
from background import Background
from logging_config import setup_logging, get_logger
import json
import sys
import os
from typing import Dict, Optional

logger = get_logger(__name__)

def prompt_user(prompt: str, choices: Optional[list] = None) -> str:
    """Prompt user for input, optionally with numbered choices"""
    while True:
        if choices:
            print("\n" + prompt)
            for i, choice in enumerate(choices, 1):
                print(f"{i}. {choice}")
            try:
                choice = int(input("\nEnter number: "))
                if 1 <= choice <= len(choices):
                    return choices[choice - 1]
            except ValueError:
                pass
            print("Invalid choice, please try again")
        else:
            value = input(prompt + ": ").strip()
            if value:
                return value
            print("Value cannot be empty, please try again")

def get_available_races() -> list:
    """Get list of available races from data directory"""
    races = []
    race_dir = os.path.join("data", "races")
    for file in os.listdir(race_dir):
        if file.endswith(".json"):
            races.append(file[:-5])  # Remove .json extension
    return races

def get_available_classes() -> list:
    """Get list of available classes from data directory"""
    classes = []
    class_dir = os.path.join("data", "classes")
    for file in os.listdir(class_dir):
        if file.endswith(".json"):
            classes.append(file[:-5])  # Remove .json extension
    return classes

def get_subraces(race: str) -> list:
    """Get available subraces for a given race"""
    try:
        with open(os.path.join("data", "races", f"{race}.json")) as f:
            race_data = json.load(f)
            return [subrace["name"] for subrace in race_data.get("subraces", [])]
    except Exception:
        return []

def get_available_backgrounds() -> list:
    """Get list of available backgrounds from data directory"""
    try:
        return Background.list_available_backgrounds()
    except Exception as e:
        logger.error(f"Failed to get backgrounds: {e}")
        return []

def prompt_personality_choices(background: Background) -> Dict:
    """Prompt user for personality choices for a background
    
    Args:
        background: The background to get choices for
        
    Returns:
        Dictionary of personality choices
    """
    options = background.get_personality_options()
    choices = {}
    
    # Get personality traits
    print("\nSelect personality traits:")
    trait_count = options["personality_traits"]["count"]
    traits = options["personality_traits"]["suggestions"]
    choices["traits"] = []
    for i in range(trait_count):
        trait = prompt_user(f"Select trait {i+1}/{trait_count}", traits)
        choices["traits"].append(trait)
    
    # Get ideal
    print("\nSelect an ideal:")
    ideals = [f"{i['ideal']} ({i['alignment']})" for i in options["ideals"]["suggestions"]]
    ideal = prompt_user("Select ideal", ideals)
    choices["ideal"] = ideal.split(" (")[0]  # Remove alignment from choice
    
    # Get bond
    print("\nSelect a bond:")
    bonds = options["bonds"]["suggestions"]
    choices["bond"] = prompt_user("Select bond", bonds)
    
    # Get flaw
    print("\nSelect a flaw:")
    flaws = options["flaws"]["suggestions"]
    choices["flaw"] = prompt_user("Select flaw", flaws)
    
    return choices

def interactive_create_character():
    """Interactive character creation"""
    try:
        toon = Toon()
        
        # Get character name
        name = prompt_user("Enter character name")
        toon.set_name(name)
        
        # Select race
        races = get_available_races()
        race = prompt_user("Select race", races)
        
        # Select subrace if available
        subraces = get_subraces(race)
        subrace = None
        if subraces:
            subrace = prompt_user("Select subrace", subraces)
        
        toon.set_race(race, subrace)
        
        # Handle pending choices from race selection
        pending = toon.get_pending_choices()
        if "ability_scores" in pending:
            print("\nChoose ability scores to increase:")
            ability_choice = pending["ability_scores"]
            chosen_abilities = []
            for i in range(ability_choice["count"]):
                available = [a for a in ability_choice["from"] if a not in chosen_abilities]
                ability = prompt_user(f"Select ability {i+1}/{ability_choice['count']} to increase by {ability_choice['bonus']}", available)
                chosen_abilities.append(ability)
                toon.properties["stats"][ability.lower()] += ability_choice["bonus"]
            # Remove the pending choice once handled
            del toon.properties["pending_choices"]["ability_scores"]
        
        # Handle skill proficiency choice for Variant Human
        if any(trait.get("name") == "Skills" for trait in toon.properties.get("traits", [])):
            skill_choices = [
                "acrobatics", "animal handling", "arcana", "athletics",
                "deception", "history", "insight", "intimidation",
                "investigation", "medicine", "nature", "perception",
                "performance", "persuasion", "religion", "sleight of hand",
                "stealth", "survival"
            ]
            skill = prompt_user("Choose a skill proficiency", skill_choices)
            if "skills" not in toon.properties:
                toon.properties["skills"] = {}
            toon.properties["skills"][skill] = True
        
        # Handle feat choice for Variant Human
        if any(trait.get("name") == "Feat" for trait in toon.properties.get("traits", [])):
            print("\nNote: Feat selection will be implemented in a future update")
            # TODO: Implement feat selection once feat data is available
        
        # Set ability scores
        print("\nEnter ability scores (8-20):")
        abilities = {}
        for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            while True:
                try:
                    score = int(prompt_user(f"Enter {ability}"))
                    if 8 <= score <= 20:
                        abilities[ability] = score
                        break
                    print("Score must be between 8 and 20")
                except ValueError:
                    print("Please enter a valid number")
        
        toon.set_ability_scores(abilities)
        
        # Select class and level
        classes = get_available_classes()
        class_name = prompt_user("Select class", classes)
        
        while True:
            try:
                level = int(prompt_user("Enter level (1-20)"))
                if 1 <= level <= 20:
                    break
                print("Level must be between 1 and 20")
            except ValueError:
                print("Please enter a valid number")
        
        toon.add_class(class_name, level)
        
        # Select background
        backgrounds = get_available_backgrounds()
        if backgrounds:
            background_name = prompt_user("Select background", backgrounds)
            background = Background(background_name)
            
            # Get personality choices
            print("\nSelect personality traits, ideals, bonds, and flaws:")
            choices = prompt_personality_choices(background)
            
            # Apply background with choices
            toon.set_background(background_name, choices)
            
            # Handle any pending choices (like languages)
            pending = toon.get_pending_choices()
            if "languages" in pending:
                print("\nSelect languages:")
                languages = ["Common", "Dwarvish", "Elvish", "Giant", "Gnomish", "Goblin", 
                           "Halfling", "Orc", "Abyssal", "Celestial", "Draconic", 
                           "Deep Speech", "Infernal", "Primordial", "Sylvan", "Undercommon"]
                lang_count = pending["languages"]["count"]
                chosen_languages = []
                for i in range(lang_count):
                    lang = prompt_user(f"Select language {i+1}/{lang_count}", 
                                     [l for l in languages if l not in chosen_languages])
                    chosen_languages.append(lang)
                    toon.properties["proficiencies"]["languages"].extend(chosen_languages)
        
        # Save the character
        filename = toon.save()
        print(f"Character saved as: {filename}")
        
        # Export options with improved error handling
        while True:
            export_format = prompt_user(
                "Select export format (or press Enter to skip)",
                ["text", "json", "html", "pdf"]
            )
            
            if not export_format:
                break
                
            try:
                output = toon.export_character_sheet(format=export_format)
                print(f"\nCharacter sheet exported in {export_format} format")
                if export_format == "text":
                    print("\n" + output)
                elif export_format == "pdf":
                    print(f"\nPDF file saved as: {output}")
                break
            except Exception as e:
                logger.error(f"Failed to export as {export_format}: {e}")
                print(f"\nFailed to export as {export_format}. Error: {str(e)}")
                retry = prompt_user("Would you like to try a different format? (y/n)").lower()
                if retry != 'y':
                    break
        
    except CharacterError as e:
        logger.error(f"Failed to create character: {e}")
        sys.exit(1)

def interactive_load_character():
    """Interactive character loading and modification"""
    try:
        # List available characters
        characters = Toon.list_saved_characters()
        if not characters:
            print("No saved characters found")
            return
        
        # Create list of character names with their filenames
        char_choices = [f"{char['name']} ({char['filename']})" for char in characters]
        choice = prompt_user("Select character to load", char_choices)
        # Extract filename without .json extension
        filename = choice.split("(")[-1].rstrip(")").replace(".json", "")
        
        toon = Toon(load_from=filename)
        print(f"\nLoaded character: {toon.get_name()}")
        
        # Ask about modifications
        if prompt_user("Add a class level? (y/n)").lower().startswith('y'):
            classes = get_available_classes()
            class_name = prompt_user("Select class", classes)
            
            while True:
                try:
                    level = int(prompt_user("Enter level (1-20)"))
                    if 1 <= level <= 20:
                        break
                    print("Level must be between 1 and 20")
                except ValueError:
                    print("Please enter a valid number")
            
            toon.add_class(class_name, level)
            toon.save()
            print("Character updated and saved")
        
        # Export options
        export_format = prompt_user(
            "Select export format (or press Enter to skip)",
            ["text", "json", "html", "pdf"]
        )
        
        if export_format:
            output = toon.export_character_sheet(format=export_format)
            print(f"\nCharacter sheet exported in {export_format} format")
            if export_format == "text":
                print("\n" + output)
            
    except CharacterError as e:
        logger.error(f"Failed to load character: {e}")
        sys.exit(1)

def interactive_delete_character():
    """Interactive character deletion"""
    try:
        # List available characters
        characters = Toon.list_saved_characters()
        if not characters:
            print("No saved characters found")
            return
        
        # Create list of character names with their filenames
        char_choices = [f"{char['name']} ({char['filename']})" for char in characters]
        choice = prompt_user("Select character to delete", char_choices)
        filename = choice.split("(")[-1].rstrip(")")
        
        if prompt_user(f"Are you sure you want to delete {filename}? (y/n)").lower().startswith('y'):
            toon = Toon()
            if toon.delete_save(filename):
                print(f"Character {filename} deleted successfully")
            else:
                print(f"Character {filename} not found")
            
    except CharacterError as e:
        logger.error(f"Failed to delete character: {e}")
        sys.exit(1)

def create_character(args):
    """Create a new character with the specified attributes"""
    try:
        toon = Toon()
        toon.set_name(args.name)
        toon.set_race(args.race, args.subrace)
        
        # Handle pending choices from race selection
        pending = toon.get_pending_choices()
        if "ability_scores" in pending:
            print("\nChoose ability scores to increase:")
            ability_choice = pending["ability_scores"]
            chosen_abilities = []
            for i in range(ability_choice["count"]):
                available = [a for a in ability_choice["from"] if a not in chosen_abilities]
                ability = prompt_user(f"Select ability {i+1}/{ability_choice['count']} to increase by {ability_choice['bonus']}", available)
                chosen_abilities.append(ability)
                toon.properties["stats"][ability.lower()] += ability_choice["bonus"]
            # Remove the pending choice once handled
            del toon.properties["pending_choices"]["ability_scores"]
        
        # Handle skill proficiency choice for Variant Human
        if any(trait.get("name") == "Skills" for trait in toon.properties.get("traits", [])):
            skill_choices = [
                "acrobatics", "animal handling", "arcana", "athletics",
                "deception", "history", "insight", "intimidation",
                "investigation", "medicine", "nature", "perception",
                "performance", "persuasion", "religion", "sleight of hand",
                "stealth", "survival"
            ]
            skill = prompt_user("Choose a skill proficiency", skill_choices)
            if "skills" not in toon.properties:
                toon.properties["skills"] = {}
            toon.properties["skills"][skill] = True
        
        # Handle feat choice for Variant Human
        if any(trait.get("name") == "Feat" for trait in toon.properties.get("traits", [])):
            print("\nNote: Feat selection will be implemented in a future update")
            # TODO: Implement feat selection once feat data is available
        
        # Set ability scores if provided
        if args.abilities:
            try:
                scores = json.loads(args.abilities)
                toon.set_ability_scores(scores)
            except json.JSONDecodeError:
                logger.error("Invalid ability scores format. Use JSON format, e.g., '{\"strength\": 15, \"dexterity\": 14}'")
                sys.exit(1)
        
        # Add class if provided
        if args.class_name and args.level:
            toon.add_class(args.class_name, args.level)
        
        # Add background if provided
        if args.background:
            try:
                # If personality choices provided, parse them
                if args.personality:
                    try:
                        choices = json.loads(args.personality)
                        toon.set_background(args.background, choices)
                    except json.JSONDecodeError:
                        logger.error("Invalid personality choices format. Use JSON format.")
                        sys.exit(1)
                else:
                    # Apply background without personality choices
                    toon.set_background(args.background)
                    logger.warning("No personality choices provided. Use interactive mode or --personality to set them.")
            except Exception as e:
                logger.error(f"Failed to apply background: {e}")
                sys.exit(1)
        
        # Save the character
        filename = toon.save()
        print(f"Character saved as: {filename}")
        
        # Export with improved error handling
        if args.export:
            try:
                output = toon.export_character_sheet(format=args.export)
                print(f"Character sheet exported in {args.export} format")
                if args.export == "text":
                    print(output)
                elif args.export == "pdf":
                    print(f"PDF file saved as: {output}")
            except Exception as e:
                logger.error(f"Failed to export as {args.export}: {e}")
                print(f"Failed to export character sheet. Error: {str(e)}")
                print("You can try exporting in a different format using the interactive mode (-i)")
        
    except CharacterError as e:
        logger.error(f"Failed to create character: {e}")
        sys.exit(1)

def load_character(args):
    """Load and optionally modify an existing character"""
    try:
        toon = Toon(load_from=args.filename)
        
        # Apply modifications if any
        if args.class_name and args.level:
            toon.add_class(args.class_name, args.level)
            toon.save()
        
        # Export if requested
        if args.export:
            output = toon.export_character_sheet(format=args.export)
            print(f"Character sheet exported in {args.export} format")
            if args.export == "text":
                print(output)
            
    except CharacterError as e:
        logger.error(f"Failed to load character: {e}")
        sys.exit(1)

def list_characters(args):
    """List all saved characters"""
    try:
        characters = Toon.list_saved_characters()
        print("\nSaved Characters:")
        print("================")
        for char in characters:
            print(f"\nName: {char['name']}")
            print(f"Race: {char['race']}")
            print(f"Level: {char['level']}")
            print(f"Classes: {', '.join(char['classes'])}")
            print(f"File: {char['filename']}")
            print(f"Last Modified: {char['last_modified']}")
    except CharacterError as e:
        logger.error(f"Failed to list characters: {e}")
        sys.exit(1)

def delete_character(args):
    """Delete a saved character"""
    try:
        toon = Toon()
        if toon.delete_save(args.filename):
            print(f"Character {args.filename} deleted successfully")
        else:
            print(f"Character {args.filename} not found")
    except CharacterError as e:
        logger.error(f"Failed to delete character: {e}")
        sys.exit(1)

def interactive_mode():
    """Run the program in interactive mode"""
    while True:
        choice = prompt_user(
            "Select action",
            ["Create new character", "Load character", "List characters", "Delete character", "Exit"]
        )
        
        if choice == "Create new character":
            interactive_create_character()
        elif choice == "Load character":
            interactive_load_character()
        elif choice == "List characters":
            list_characters(None)
        elif choice == "Delete character":
            interactive_delete_character()
        elif choice == "Exit":
            break
        
        input("\nPress Enter to continue...")

def main():
    """Main CLI entry point"""
    setup_logging()
    
    parser = argparse.ArgumentParser(description="D&D 5E Character Manager")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Create character command
    create_parser = subparsers.add_parser("create", help="Create a new character")
    create_parser.add_argument("name", help="Character name")
    create_parser.add_argument("race", help="Character race (e.g., elf, dwarf)")
    create_parser.add_argument("--subrace", help="Character subrace (e.g., High Elf, Mountain Dwarf)")
    create_parser.add_argument("--class-name", help="Character class (e.g., wizard, fighter)")
    create_parser.add_argument("--level", type=int, help="Class level (1-20)")
    create_parser.add_argument("--abilities", help="Ability scores in JSON format (e.g., '{\"strength\": 15}')")
    create_parser.add_argument("--background", help="Character background (e.g., acolyte, criminal)")
    create_parser.add_argument("--personality", help="Personality choices in JSON format (e.g., '{\"traits\": [\"trait1\", \"trait2\"], \"ideal\": \"ideal1\", \"bond\": \"bond1\", \"flaw\": \"flaw1\"}')")
    create_parser.add_argument("--export", choices=["text", "json", "html", "pdf"], 
                             help="Export character sheet format (Note: PDF export requires pdftk to be installed)")
    
    # Load character command
    load_parser = subparsers.add_parser("load", help="Load an existing character")
    load_parser.add_argument("filename", help="Character file to load")
    load_parser.add_argument("--class-name", help="Add a class to the character")
    load_parser.add_argument("--level", type=int, help="Level for the added class")
    load_parser.add_argument("--export", choices=["text", "json", "html", "pdf"], help="Export character sheet format")
    
    # List characters command
    list_parser = subparsers.add_parser("list", help="List all saved characters")
    
    # Delete character command
    delete_parser = subparsers.add_parser("delete", help="Delete a saved character")
    delete_parser.add_argument("filename", help="Character file to delete")
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
    elif args.command == "create":
        create_character(args)
    elif args.command == "load":
        load_character(args)
    elif args.command == "list":
        list_characters(args)
    elif args.command == "delete":
        delete_character(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main() 