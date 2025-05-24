from logging_config import get_logger
import json
import os
from typing import Dict, List, Optional, Union
import random
from file_functions import save_file, open_file, list_files, remove_file
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from collections import defaultdict
from background import Background

logger = get_logger(__name__)

class CharacterError(Exception):
    """Custom exception for character-related errors"""
    pass

class DiceRoll:
    @staticmethod
    def roll(dice_str: str) -> int:
        """Roll dice based on standard D&D notation (e.g., '2d6+3')"""
        try:
            # Remove spaces
            dice_str = dice_str.replace(' ', '')
            
            # Handle modifiers
            if '+' in dice_str:
                dice_part, mod_part = dice_str.split('+')
                modifier = int(mod_part)
            elif '-' in dice_str:
                dice_part, mod_part = dice_str.split('-')
                modifier = -int(mod_part)
            else:
                dice_part = dice_str
                modifier = 0
            
            # Handle dice rolls
            if 'd' in dice_part:
                num_dice, sides = map(int, dice_part.split('d'))
                total = sum(random.randint(1, sides) for _ in range(num_dice))
                return total + modifier
            else:
                return int(dice_part) + modifier
        except Exception as e:
            logger.error(f"Failed to roll dice '{dice_str}': {e}")
            raise ValueError(f"Invalid dice notation: {dice_str}")

class Toon:
    def __init__(self, load_from: Optional[str] = None):
        """Initialize a new character or load an existing one
        
        Args:
            load_from: Optional filename to load character from
        """
        self.data_path = "data"
        self.save_path = "characters"
        
        # Ensure characters directory exists
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        
        if load_from:
            self._load_character(load_from)
            logger.info(f"Loaded character from {load_from}")
        else:
            logger.debug("Initializing new character")
            self._init_default_properties()

    def _init_default_properties(self):
        """Initialize default character properties"""
        self.properties = {
            "name": "",
            "race": "",
            "subrace": "",
            "background": "",
            "alignment": "",
            "experience": 0,
            "level": 0,
            "proficiency_bonus": 2,
            "inspiration": False,
            "stats": {
                "strength": 10,
                "dexterity": 10,
                "constitution": 10,
                "intelligence": 10,
                "wisdom": 10,
                "charisma": 10
            },
            "base_stats": {
                "strength": 10,
                "dexterity": 10,
                "constitution": 10,
                "intelligence": 10,
                "wisdom": 10,
                "charisma": 10
            },
            "racial_bonuses": {
                "strength": 0,
                "dexterity": 0,
                "constitution": 0,
                "intelligence": 0,
                "wisdom": 0,
                "charisma": 0
            },
            "saving_throws": {
                "strength": False,
                "dexterity": False,
                "constitution": False,
                "intelligence": False,
                "wisdom": False,
                "charisma": False
            },
            "skills": {
                "acrobatics": False,
                "animal handling": False,
                "arcana": False,
                "athletics": False,
                "deception": False,
                "history": False,
                "insight": False,
                "intimidation": False,
                "investigation": False,
                "medicine": False,
                "nature": False,
                "perception": False,
                "performance": False,
                "persuasion": False,
                "religion": False,
                "sleight of hand": False,
                "stealth": False,
                "survival": False
            },
            "armor_class": 10,
            "initiative": 0,
            "speed": 30,
            "hit_points": {
                "maximum": 0,
                "current": 0,
                "temporary": 0
            },
            "hit_dice": [],
            "death_saves": {
                "successes": 0,
                "failures": 0
            },
            "proficiencies": {
                "armor": [],
                "weapons": [],
                "tools": [],
                "languages": []
            },
            "traits": [],  # Add traits list
            "features": [],
            "subclass_features": {},  # Organized by level
            "spells": {
                "spellcasting_ability": None,
                "spell_save_dc": None,
                "spell_attack_bonus": None,
                "cantrips": [],
                "spells_known": [],
                "spell_slots": {}
            },
            "equipment": [],
            "currency": {
                "cp": 0,
                "sp": 0,
                "ep": 0,
                "gp": 0,
                "pp": 0
            },
            "personality": {
                "traits": [],
                "ideals": [],
                "bonds": [],
                "flaws": []
            },
            "classes": [],
            "pending_choices": {},
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat(),
                "version": "1.0",
                "save_count": 0  # Initialize save counter
            }
        }

    def save(self, filename: Optional[str] = None) -> str:
        """Save the character to a file
        
        Args:
            filename: Optional filename to save as. If not provided, uses character name
            
        Returns:
            The filename used for saving
        """
        try:
            # Update metadata
            self.properties["metadata"]["last_modified"] = datetime.now().isoformat()
            self.properties["metadata"]["save_count"] += 1
            
            # Generate filename if not provided
            if not filename:
                if not self.properties["name"]:
                    raise CharacterError("Character must have a name before saving")
                base_filename = self.properties["name"].lower().replace(" ", "_")
                filename = f"{base_filename}_{self.properties['metadata']['save_count']}"
            
            # Save the character
            save_file(self.properties, self.save_path, filename)
            logger.info(f"Saved character to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Failed to save character: {e}")
            raise CharacterError(f"Failed to save character: {e}")

    def _load_character(self, filename: str):
        """Load a character from a file"""
        try:
            data = open_file(filename, self.save_path)
            
            # Validate version compatibility
            if "metadata" not in data or "version" not in data["metadata"]:
                raise CharacterError("Invalid character file format")
            
            # Migrate old character files to new format
            if "base_stats" not in data:
                # Old format - assume current stats are base stats with no racial bonuses applied
                data["base_stats"] = data["stats"].copy()
                data["racial_bonuses"] = {
                    "strength": 0,
                    "dexterity": 0,
                    "constitution": 0,
                    "intelligence": 0,
                    "wisdom": 0,
                    "charisma": 0
                }
            
            self.properties = data
            logger.info(f"Loaded character {self.properties.get('name', 'unnamed')} from {filename}")
            
        except Exception as e:
            logger.error(f"Failed to load character from {filename}: {e}")
            raise CharacterError(f"Failed to load character: {e}")

    @staticmethod
    def list_saved_characters() -> List[Dict[str, str]]:
        """List all saved characters with their basic information
        
        Returns:
            List of dictionaries containing character information
        """
        try:
            characters = []
            for filename in list_files("characters", "json"):
                try:
                    data = open_file(filename.replace(".json", ""), "characters")
                    characters.append({
                        "filename": filename,
                        "name": data.get("name", "unnamed"),
                        "race": f"{data.get('race', '')} {data.get('subrace', '')}".strip(),
                        "level": data.get("level", 0),
                        "classes": [f"{c['name']} {c['level']}" for c in data.get("classes", [])],
                        "last_modified": data.get("metadata", {}).get("last_modified", "unknown")
                    })
                except Exception as e:
                    logger.warning(f"Skipping corrupted character file {filename}: {e}")
                    continue
            
            return sorted(characters, key=lambda x: x["last_modified"], reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to list characters: {e}")
            raise CharacterError(f"Failed to list characters: {e}")

    def delete_save(self, filename: str) -> bool:
        """Delete a saved character file
        
        Args:
            filename: The filename to delete (with or without .json extension)
            
        Returns:
            True if deletion was successful
        """
        try:
            # Remove .json extension if present, then add it back
            filename = filename.replace('.json', '')
            return remove_file(f"{filename}.json", self.save_path)
        except Exception as e:
            logger.error(f"Failed to delete character file {filename}: {e}")
            raise CharacterError(f"Failed to delete character: {e}")

    def export_character_sheet(self, format: str = "text") -> str:
        """Export character sheet in various formats
        
        Args:
            format: The format to export in ("text", "json", "html", "pdf")
            
        Returns:
            Formatted character sheet or path to generated file
        """
        try:
            if format == "pdf":
                return self._export_to_pdf()
            elif format == "json":
                return json.dumps(self.properties, indent=2)
            
            elif format == "text":
                # Create a text representation of the character sheet
                sheet = []
                sheet.append(f"=== {self.properties['name']} ===")
                sheet.append(f"Race: {self.properties['race']} {self.properties.get('subrace', '')}")
                sheet.append(f"Level: {self.properties['level']}")
                sheet.append(f"Classes: {', '.join(f'{c['name']} {c['level']}' for c in self.properties['classes'])}")
                
                sheet.append("\nAbility Scores:")
                for ability, score in self.properties["stats"].items():
                    modifier = self.get_ability_modifier(ability)
                    sheet.append(f"{ability.capitalize()}: {score} ({modifier:+d})")
                
                sheet.append("\nSaving Throws:")
                for ability in self.properties["saving_throws"]:
                    bonus = self.get_saving_throw_bonus(ability)
                    prof = "✓" if self.properties["saving_throws"][ability] else " "
                    sheet.append(f"{ability.capitalize()}: {bonus:+d} [{prof}]")
                
                sheet.append("\nProficiencies:")
                for prof_type, profs in self.properties["proficiencies"].items():
                    if profs:
                        sheet.append(f"{prof_type.capitalize()}: {', '.join(profs)}")
                
                return "\n".join(sheet)
            
            elif format == "html":
                # Set up Jinja2 environment
                env = Environment(
                    loader=FileSystemLoader('templates'),
                    autoescape=True
                )
                template = env.get_template('character_sheet.html')

                # Calculate derived values for the template (reuse PDF helpers)
                class_levels = {
                    c['name']: c['level'] 
                    for c in self.properties['classes']
                }
                modifiers = {
                    ability: f"{self.get_ability_modifier(ability):+d}"
                    for ability in self.properties['stats']
                }
                saving_throws = {
                    ability: {
                        'bonus': f"{self.get_saving_throw_bonus(ability):+d}",
                        'proficient': self.properties['saving_throws'][ability]
                    }
                    for ability in self.properties['saving_throws']
                }
                # DEBUG: Log the skills dict before rendering
                logger.debug(f"Skills dict before rendering: {self.properties['skills']}")
                
                # Change to include both bonus and proficiency status
                skill_data = {}
                for skill, proficient in self.properties['skills'].items():
                    skill_lc = skill.lower()
                    ability = self._get_skill_ability(skill_lc)
                    bonus = self.get_ability_modifier(ability)
                    if proficient:
                        bonus += self.properties['proficiency_bonus']
                    skill_data[skill_lc] = {
                        'bonus': f"{bonus:+d}",
                        'proficient': proficient
                    }
                # Format hit dice for display
                hit_dice_total, hit_dice_types = self._format_hit_dice_for_pdf()
                hit_dice_summary = f"{hit_dice_total} ({hit_dice_types})"
                
                # Organize features by source and level
                class_features = {}
                background_features = []
                other_features = []
                
                for feature in self.properties.get('features', []):
                    source = feature.get('source', '')
                    if source:
                        # Check if this is a background feature
                        if source.startswith('Background:'):
                            background_features.append(feature)
                            other_features.append(feature)  # Also add to other_features for template compatibility
                        else:
                            # Extract class name and level from source (e.g. "Barbarian 1")
                            parts = source.split()
                            if len(parts) == 2 and parts[1].isdigit():
                                class_name, level = parts[0], int(parts[1])
                                if level not in class_features:
                                    class_features[level] = []
                                class_features[level].append(feature)

                # Features and traits split
                combat_features_str, non_combat_features_str = self._format_features_for_pdf()
                
                # Parse features/traits for HTML (as lists)
                def parse_features_str(features_str):
                    # Split by double newlines, skip header
                    blocks = features_str.split('\\n\\n')[1:]
                    features = []
                    current_feature = None
                    
                    for block in blocks:
                        lines = block.strip().split('\\n')
                        if not lines or not lines[0]:
                            continue
                            
                        name = lines[0].strip()
                        if name:
                            # If we have a current feature, add it to the list
                            if current_feature:
                                features.append(current_feature)
                            
                            # Start a new feature
                            current_feature = {
                                'name': name,
                                'description': ''
                            }
                            
                            # Add remaining lines as description
                            if len(lines) > 1:
                                current_feature['description'] = '\\n'.join(lines[1:])
                    
                    # Add the last feature if we have one
                    if current_feature:
                        features.append(current_feature)
                        
                    return features
                    
                combat_features = parse_features_str(combat_features_str)
                non_combat_features = parse_features_str(non_combat_features_str)
                # Personality as lists
                personality = self.properties.get('personality', {})
                # Proficiencies
                proficiencies = self.properties['proficiencies']
                # Currency
                currency = self.properties.get('currency', {})
                # Passive Perception
                passive_perception = 10 + self.get_ability_modifier('wisdom')
                if self.properties['skills'].get('perception', False):
                    passive_perception += self.properties['proficiency_bonus']
                # Passive Investigation
                passive_investigation = 10 + self.get_ability_modifier('intelligence')
                if self.properties['skills'].get('investigation', False):
                    passive_investigation += self.properties['proficiency_bonus']
                # Passive Insight
                passive_insight = 10 + self.get_ability_modifier('wisdom')
                if self.properties['skills'].get('insight', False):
                    passive_insight += self.properties['proficiency_bonus']
                # Death saves
                death_saves = self.properties.get('death_saves', {'successes': 0, 'failures': 0})
                # Metadata
                metadata = self.properties.get('metadata', {})
                # Spellcasting
                spell_save_dc = None
                spell_attack_bonus = None
                spellcasting_data = None
                spell_ability = self.properties['spells']['spellcasting_ability']
                
                # Check if character has any spellcasting (racial or class)
                has_cantrips = bool(self.properties['spells'].get('cantrips', []))
                has_spells = bool(self.properties['spells'].get('spells_known', []))
                has_class_spellcasting = False
                try:
                    has_class_spellcasting = any(
                        'spellcasting' in self._load_data_file('classes', c['name']) 
                        for c in self.properties.get('classes', [])
                        if c['name']
                    )
                except:
                    pass
                
                if spell_ability or has_cantrips or has_spells or has_class_spellcasting:
                    # If we have spellcasting ability, calculate bonuses
                    if spell_ability:
                        modifier = self.get_ability_modifier(spell_ability)
                        spell_save_dc = 8 + self.properties['proficiency_bonus'] + modifier
                        spell_attack_bonus = modifier + self.properties['proficiency_bonus']
                    
                    # Get cantrips known and spell slots
                    cantrips_known = self._get_cantrips_known_for_level()
                    spell_slots = self._get_spell_slots_for_level()
                    
                    # For racial-only spellcasting, count actual cantrips
                    if not cantrips_known.get(self.properties['level'], 0) and has_cantrips:
                        cantrips_known[self.properties['level']] = len(self.properties['spells'].get('cantrips', []))
                    
                    # Construct spellcasting object for template
                    spellcasting_data = {
                        'ability': spell_ability or 'none',
                        'spell_attack_bonus': spell_attack_bonus,
                        'spell_save_dc': spell_save_dc,
                        'focus': self.properties['spells'].get('focus', []),
                        'cantrips_known': cantrips_known,
                        'spell_slots_per_level': spell_slots
                    }
                # Prepare template data
                template_data = {
                    'character': {
                        'name': self.properties['name'],
                        'race': f"{self.properties['race']} {self.properties.get('subrace', '')}".strip(),
                        'class_levels': class_levels,
                        'level': self.properties['level'],
                        'background': self.properties.get('background', ''),
                        'alignment': self.properties.get('alignment', ''),
                        'experience': self.properties.get('experience', 0),
                        'proficiency_bonus': self.properties['proficiency_bonus'],
                        'inspiration': self.properties.get('inspiration', False),
                        'stats': self.properties['stats'],
                        'modifiers': modifiers,
                        'saving_throws': saving_throws,
                        'skills': skill_data,
                        'armor_class': self.properties['armor_class'],
                        'initiative': self.properties['initiative'],
                        'speed': self.properties['speed'],
                        'hit_points': self.properties['hit_points'],
                        'hit_dice': hit_dice_summary,
                        'proficiencies': proficiencies,
                        'features': combat_features + non_combat_features,
                        'background_features': background_features,
                        'other_features': other_features,
                        'class_features': class_features,
                        'subclass_features': self.properties.get('subclass_features', {}),
                        'spells': self.properties['spells'],
                        'spellcasting': spellcasting_data,
                        'spell_save_dc': spell_save_dc,
                        'spell_attack_bonus': spell_attack_bonus,
                        'equipment': self.properties.get('equipment', []),
                        'currency': currency,
                        'personality': personality,
                        'death_saves': death_saves,
                        'passive_perception': passive_perception,
                        'passive_investigation': passive_investigation,
                        'passive_insight': passive_insight,
                        'metadata': metadata
                    }
                }
                
                # Render the template
                rendered_html = template.render(**template_data)
                
                # Save the rendered HTML to a file
                output_path = os.path.join(self.save_path, f"{self.properties['name'].replace(' ', '_')}_sheet.html")
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(rendered_html)
                
                return output_path
            
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"Failed to export character sheet: {e}")
            raise

    def _get_skill_ability(self, skill: str) -> str:
        """Get the ability score associated with a skill"""
        # D&D 5E skill to ability score mapping
        skill_abilities = {
            'acrobatics': 'dexterity',
            'animal handling': 'wisdom',
            'arcana': 'intelligence',
            'athletics': 'strength',
            'deception': 'charisma',
            'history': 'intelligence',
            'insight': 'wisdom',
            'intimidation': 'charisma',
            'investigation': 'intelligence',
            'medicine': 'wisdom',
            'nature': 'intelligence',
            'perception': 'wisdom',
            'performance': 'charisma',
            'persuasion': 'charisma',
            'religion': 'intelligence',
            'sleight of hand': 'dexterity',
            'stealth': 'dexterity',
            'survival': 'wisdom'
        }
        return skill_abilities.get(skill.lower(), 'intelligence')  # Default to INT if unknown

    def _get_cantrips_known_for_level(self) -> Dict[int, int]:
        """Get cantrips known progression based on current level and classes"""
        cantrips_known = {}
        current_level = self.properties.get('level', 1)
        
        # Count racial cantrips
        racial_cantrips = len([c for c in self.properties.get('spells', {}).get('cantrips', []) 
                              if c.get('source') == 'racial'])
        
        # Check each class for spellcasting
        class_cantrips_count = 0
        for class_info in self.properties.get('classes', []):
            class_name = class_info['name']
            try:
                class_data = self._load_data_file("classes", class_name)
                if 'spellcasting' in class_data and 'cantrips_known' in class_data['spellcasting']:
                    class_cantrips = class_data['spellcasting']['cantrips_known']
                    # Get the highest applicable level
                    for level in sorted(class_cantrips.keys(), key=int, reverse=True):
                        if int(level) <= current_level:
                            class_cantrips_count = class_cantrips[level]
                            break
            except:
                continue
        
        # Total cantrips is racial + class
        total_cantrips = racial_cantrips + class_cantrips_count
        cantrips_known[current_level] = total_cantrips
            
        return cantrips_known

    def _get_spell_slots_for_level(self) -> Dict[int, Dict[int, int]]:
        """Get spell slots progression based on current level and classes"""
        spell_slots = {}
        current_level = self.properties.get('level', 1)
        
        # Check each class for spellcasting
        for class_info in self.properties.get('classes', []):
            class_name = class_info['name']
            try:
                class_data = self._load_data_file("classes", class_name)
                if 'spellcasting' in class_data and 'spell_slots_per_level' in class_data['spellcasting']:
                    class_slots = class_data['spellcasting']['spell_slots_per_level']
                    # Get slots for current level
                    level_str = str(current_level)
                    if level_str in class_slots:
                        spell_slots[current_level] = class_slots[level_str]
                        break
            except:
                continue
        
        # If no class spellcasting found, return empty dict
        if not spell_slots:
            spell_slots[current_level] = {}
            
        return spell_slots

    def create_backup(self) -> str:
        """Create a backup of the character
        
        Returns:
            Filename of the backup
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{self.properties['name']}_backup_{timestamp}"
            return self.save(backup_name)
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            raise CharacterError(f"Failed to create backup: {e}")

    def set_name(self, name: str):
        """Set character name"""
        try:
            if not name:
                raise ValueError("Name cannot be empty")
            self.properties["name"] = name
            logger.info(f"Set character name to: {name}")
        except Exception as e:
            logger.error(f"Failed to set name: {e}")
            raise

    def get_name(self) -> str:
        """Get character name"""
        return self.properties["name"]

    def _load_data_file(self, category: str, name: str) -> Dict:
        """Load a data file from the appropriate category"""
        try:
            file_path = os.path.join(self.data_path, category, f"{name.lower()}.json")
            with open(file_path, 'r') as f:
                data = json.load(f)
            logger.debug(f"Loaded {category} data for {name}")
            return data
        except FileNotFoundError:
            logger.error(f"Data file not found: {file_path}")
            raise ValueError(f"No {category} data found for {name}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading {category} data for {name}: {e}")
            raise

    def _apply_trait_grants(self, grants: Dict):
        """Apply granted proficiencies and other benefits from traits"""
        try:
            # Apply skill proficiencies
            if "skill_proficiencies" in grants:
                for skill in grants["skill_proficiencies"]:
                    self.properties["skills"][skill.lower()] = True

            # Apply weapon proficiencies
            if "weapon_proficiencies" in grants:
                self.properties["proficiencies"]["weapons"].extend(grants["weapon_proficiencies"])

            # Apply armor proficiencies
            if "armor_proficiencies" in grants:
                self.properties["proficiencies"]["armor"].extend(grants["armor_proficiencies"])

            # Apply tool proficiencies
            if "tool_proficiencies" in grants:
                self.properties["proficiencies"]["tools"].extend(grants["tool_proficiencies"])

            # Remove any duplicates from proficiency lists
            for prof_type in ["weapons", "armor", "tools", "languages"]:
                self.properties["proficiencies"][prof_type] = list(set(self.properties["proficiencies"][prof_type]))

            logger.debug(f"Applied trait grants: {grants}")

        except Exception as e:
            logger.error(f"Failed to apply trait grants: {e}")
            raise

    def _apply_trait_modifies(self, trait: Dict):
        """Apply modifications from traits (like speed changes)"""
        try:
            if "modifies" in trait:
                for path, value in trait["modifies"].items():
                    # Handle dot notation for nested properties
                    parts = path.split('.')
                    target = self.properties
                    
                    # Special handling for trait modifications
                    if parts[0] == "traits":
                        # Find the trait to modify
                        trait_name = parts[1]
                        for t in self.properties["traits"]:
                            if t["name"] == trait_name:
                                # Modify the specified field
                                if len(parts) > 2:
                                    t[parts[2]] = value
                                break
                        continue
                    
                    # Handle regular nested dictionary paths
                    for part in parts[:-1]:
                        if part not in target:
                            target[part] = {}
                        target = target[part]
                    
                    # Set the final value
                    if isinstance(target, dict):
                        target[parts[-1]] = value
                    else:
                        # If we're trying to modify a non-dict value, set it in the parent
                        parent_parts = parts[:-1]
                        parent = self.properties
                        for part in parent_parts[:-1]:
                            parent = parent[part]
                        parent[parent_parts[-1]] = value
                    
                logger.debug(f"Applied trait modifications: {trait['modifies']}")
        except Exception as e:
            logger.error(f"Failed to apply trait modifications: {e}")
            raise

    def _apply_racial_spellcasting(self, spellcasting_data: Dict):
        """Apply racial spellcasting traits"""
        try:
            # Set spellcasting ability if not already set
            if "ability" in spellcasting_data and not self.properties["spells"]["spellcasting_ability"]:
                self.properties["spells"]["spellcasting_ability"] = spellcasting_data["ability"]
                logger.debug(f"Set racial spellcasting ability to {spellcasting_data['ability']}")
            
            # Handle innate spellcasting (like Drow Magic)
            if "innate" in spellcasting_data:
                for level, spell_data in spellcasting_data["innate"].items():
                    level_int = int(level)
                    
                    if isinstance(spell_data, list):
                        # Simple list of cantrips (level 1)
                        for spell_name in spell_data:
                            spell_entry = {
                                "name": spell_name,
                                "source": "racial",
                                "level": 0,  # Cantrips are level 0
                                "description": f"Racial cantrip from {spellcasting_data['ability']} spellcasting"
                            }
                            self.properties["spells"]["cantrips"].append(spell_entry)
                    
                    elif isinstance(spell_data, dict):
                        # Spells with usage restrictions
                        spells = spell_data.get("spells", [])
                        uses = spell_data.get("uses", {})
                        
                        for spell_name in spells:
                            spell_entry = {
                                "name": spell_name,
                                "source": "racial",
                                "level": 1,  # Default to 1st level for now
                                "uses": uses,
                                "description": f"Racial spell from {spellcasting_data['ability']} spellcasting"
                            }
                            self.properties["spells"]["spells_known"].append(spell_entry)
            
            # Handle spell choices (like High Elf cantrip)
            if "spells" in spellcasting_data:
                spell_choice = spellcasting_data["spells"]
                if spell_choice.get("type") == "choose":
                    count = spell_choice.get("count", 1)
                    spell_list = spell_choice.get("from", "")
                    
                    choice_key = f"racial_spells_{spell_list}"
                    self.properties["pending_choices"][choice_key] = {
                        "type": "cantrips" if "cantrip" in spell_list else "spells",
                        "count": count,
                        "from": spell_list,
                        "ability": spellcasting_data["ability"],
                        "description": f"Choose {count} {'cantrip' if 'cantrip' in spell_list else 'spell'}(s) from the {spell_list.replace('_', ' ')} list"
                    }
                    
        except Exception as e:
            logger.error(f"Failed to apply racial spellcasting: {e}")
            raise

    def set_race(self, race: str, subrace: Optional[str] = None):
        """Set character race and apply racial traits"""
        try:
            race_data = self._load_data_file("races", race)
            
            # Validate subrace if provided
            if subrace and subrace not in [sr["name"] for sr in race_data.get("subraces", [])]:
                raise ValueError(f"Invalid subrace {subrace} for race {race}")
            
            # Set basic race properties
            self.properties["race"] = race_data["name"]
            self.properties["speed"] = race_data["speed"]["walk"]
            self.properties["size"] = race_data["size"]
            
            # Reset racial bonuses (in case race is being changed)
            for ability in self.properties["racial_bonuses"]:
                self.properties["racial_bonuses"][ability] = 0
            
            # Apply racial ability score increases
            ability_scores = race_data["ability_scores"]
            if isinstance(ability_scores, dict) and "choose" not in ability_scores:
                for ability, bonus in ability_scores.items():
                    self.properties["racial_bonuses"][ability.lower()] += bonus
            elif isinstance(ability_scores, dict) and "choose" in ability_scores:
                # Store ability score choices in pending_choices
                self.properties["pending_choices"]["ability_scores"] = ability_scores["choose"]
            
            # Add racial traits and apply their grants
            for trait in race_data.get("traits", []):
                self.properties["traits"].append(trait)
                if "grants" in trait:
                    self._apply_trait_grants(trait["grants"])
                self._apply_trait_modifies(trait)
                
                # Handle racial spellcasting
                if "spellcasting" in trait:
                    self._apply_racial_spellcasting(trait["spellcasting"])
            
            # Add languages
            self.properties["proficiencies"]["languages"].extend(race_data["languages"]["standard"])
            if "bonus" in race_data["languages"]:
                bonus_languages = race_data["languages"]["bonus"]
                if bonus_languages.get("type") == "choose" or "count" in bonus_languages:
                    self.properties["pending_choices"]["languages"] = bonus_languages
            
            # Apply subrace if specified
            if subrace:
                self.properties["subrace"] = subrace
                subrace_data = next(sr for sr in race_data["subraces"] if sr["name"] == subrace)
                
                # Handle subrace ability scores
                if "ability_scores" in subrace_data:
                    if "replaces" in subrace_data and "ability_scores" in subrace_data["replaces"]:
                        # Reset base race ability scores if subrace replaces them
                        for ability in self.properties["racial_bonuses"]:
                            self.properties["racial_bonuses"][ability] -= race_data["ability_scores"].get(ability, 0)
                        # Apply subrace ability scores
                        if "choose" not in subrace_data["ability_scores"]:
                            for ability, bonus in subrace_data["ability_scores"].items():
                                self.properties["racial_bonuses"][ability.lower()] += bonus
                        else:
                            self.properties["pending_choices"]["ability_scores"] = subrace_data["ability_scores"]["choose"]
                    elif isinstance(subrace_data["ability_scores"], dict) and "choose" in subrace_data["ability_scores"]:
                        # Store ability score choices in pending_choices
                        self.properties["pending_choices"]["ability_scores"] = subrace_data["ability_scores"]["choose"]
                    else:
                        # Add subrace ability scores to base racial bonuses
                        for ability, bonus in subrace_data.get("ability_scores", {}).items():
                            self.properties["racial_bonuses"][ability.lower()] += bonus
                
                # Add subrace traits and apply their grants
                for trait in subrace_data.get("traits", []):
                    self.properties["traits"].append(trait)
                    if "grants" in trait:
                        if any("choose" in grant for grant in trait["grants"].values()):
                            # Store choices in pending_choices
                            choice_key = f"trait_{trait['name'].lower()}"
                            self.properties["pending_choices"][choice_key] = trait["grants"]
                        else:
                            self._apply_trait_grants(trait["grants"])
                    self._apply_trait_modifies(trait)
                    
                    # Handle racial spellcasting
                    if "spellcasting" in trait:
                        self._apply_racial_spellcasting(trait["spellcasting"])
            
            # Recalculate final stats with all bonuses
            self._recalculate_final_stats()
                
            logger.info(f"Set race to {race}" + (f" ({subrace})" if subrace else ""))
            
        except Exception as e:
            logger.error(f"Failed to set race to {race}: {e}")
            raise

    def _calculate_max_hp(self) -> int:
        """Calculate maximum hit points based on hit dice and Constitution modifier"""
        if not self.properties['classes']:
            return 0
            
        con_mod = self.get_ability_modifier('constitution')
        max_hp = 0
        
        # First class gets maximum hit points for first level
        first_class = self.properties['classes'][0]
        first_hit_die = int(self.properties['hit_dice'][0].split('d')[1])  # Get the die size (e.g., 10 from '1d10')
        max_hp = first_hit_die + con_mod  # First level gets maximum
        
        # Add average hit points for remaining levels
        remaining_hit_dice = self.properties['hit_dice'][1:]  # Skip first level
        for hit_die in remaining_hit_dice:
            die_size = int(hit_die.split('d')[1])
            max_hp += (die_size // 2 + 1) + con_mod  # Average roll is (die_size/2 + 0.5)
            
        return max_hp

    def get_available_subclasses(self, class_name: str) -> list:
        """Get available subclasses for a given class
        
        Args:
            class_name: Name of the class to get subclasses for
            
        Returns:
            List of available subclass names
        """
        try:
            class_data = self._load_data_file("classes", class_name)
            if "subclasses" in class_data:
                return [subclass["name"] for subclass in class_data["subclasses"]]
            return []
        except Exception as e:
            logger.error(f"Failed to get subclasses for {class_name}: {e}")
            return []

    def set_subclass(self, class_name: str, subclass_name: str):
        """Set a subclass for a class
        
        Args:
            class_name: Name of the class to set subclass for
            subclass_name: Name of the subclass to set
        """
        try:
            class_data = self._load_data_file("classes", class_name)
            if "subclasses" not in class_data:
                raise ValueError(f"Class {class_name} does not have subclasses")
            
            # Find the subclass in the class data
            subclass_data = None
            for subclass in class_data["subclasses"]:
                if subclass["name"].lower() == subclass_name.lower():
                    subclass_data = subclass
                    break
            
            if not subclass_data:
                raise ValueError(f"Subclass {subclass_name} not found for class {class_name}")
            
            # Find the class entry in the character's classes
            class_entry = None
            for c in self.properties["classes"]:
                if c["name"].lower() == class_name.lower():
                    class_entry = c
                    break
            
            if not class_entry:
                raise ValueError(f"Character does not have class {class_name}")
            
            # Check if character is high enough level for subclass
            subclass_level = class_data.get("subclass_level", 3)  # Default to level 3
            if class_entry["level"] < subclass_level:
                raise ValueError(f"Must be level {subclass_level} to select a subclass for {class_name}")
            
            # Set the subclass
            class_entry["subclass"] = subclass_name
            
            # Apply subclass features for current level
            if "features" in subclass_data:
                for level, features in subclass_data["features"].items():
                    level_int = int(level)
                    if level_int <= class_entry["level"]:
                        # Initialize the level in subclass_features if not present
                        if level_int not in self.properties["subclass_features"]:
                            self.properties["subclass_features"][level_int] = []
                            
                        for feature in features:
                            # All features should have mechanics in standardized format
                            mechanics = feature.get("mechanics", {})
                            if not mechanics:
                                # If no mechanics, just store the feature name and description
                                self.properties["subclass_features"][level_int].append({
                                    "name": feature.get("name", ""),
                                    "description": feature.get("description", ""),
                                    "source": f"{subclass_name} {level}"
                                })
                                continue
                                
                            mechanics_type = mechanics.get("type", "")
                            
                            # Handle ability score improvements
                            if mechanics_type == "ability_score_improvement":
                                choice_key = f"subclass_{class_name.lower()}_{level}_asi"
                                self.properties["pending_choices"][choice_key] = {
                                    "type": "ability_score_improvement",
                                    "count": mechanics.get("count", 2),  # Default to 2 increases
                                    "amount": mechanics.get("amount", 1),  # Default to +1 per increase
                                    "options": mechanics.get("options", list(self.properties["stats"].keys())),
                                    "description": feature.get("description", "Choose which ability scores to improve")
                                }
                            
                            # Handle expertise
                            elif mechanics_type == "expertise":
                                choice_key = f"subclass_{class_name.lower()}_{level}_expertise"
                                self.properties["pending_choices"][choice_key] = {
                                    "type": "expertise",
                                    "count": mechanics.get("count", 2),  # Default to 2 if not specified
                                    "options": mechanics.get("options", []),
                                    "description": "Choose skills to gain expertise in"
                                }
                            
                            # Handle spellcasting
                            elif mechanics_type == "spellcasting":
                                # Update spellcasting ability if provided
                                if "ability" in mechanics:
                                    self.properties["spells"]["spellcasting_ability"] = mechanics["ability"]
                                
                                # Update spellcasting focus if provided
                                if "focus" in mechanics:
                                    self.properties["spells"]["focus"] = mechanics["focus"]
                                
                                # Handle additional cantrips
                                if "cantrips_known" in mechanics:
                                    cantrips_count = mechanics["cantrips_known"].get(str(level), 0)
                                    if cantrips_count > 0:
                                        self.properties["spells"]["cantrips"].extend([{"name": "", "description": ""}] * cantrips_count)
                                        choice_key = f"subclass_{class_name.lower()}_{level}_cantrips"
                                        self.properties["pending_choices"][choice_key] = {
                                            "type": "cantrips",
                                            "count": cantrips_count,
                                            "class": class_name,
                                            "description": f"Choose {cantrips_count} additional cantrips from your {subclass_name} list"
                                        }
                                
                                # Handle additional spells known
                                if "spells_known" in mechanics:
                                    spells_known_count = mechanics["spells_known"].get(str(level), 0)
                                    if spells_known_count > 0:
                                        self.properties["spells"]["spells_known"].extend([{"name": "", "description": ""}] * spells_known_count)
                                        choice_key = f"subclass_{class_name.lower()}_{level}_spells"
                                        self.properties["pending_choices"][choice_key] = {
                                            "type": "spells",
                                            "count": spells_known_count,
                                            "class": class_name,
                                            "description": f"Choose {spells_known_count} additional spells from your {subclass_name} list"
                                        }
                                
                                # Handle additional spell slots
                                if "spell_slots" in mechanics:
                                    current_slots = self.properties["spells"]["spell_slots"]
                                    new_slots = mechanics["spell_slots"].get(str(level), {})
                                    # Merge the spell slots, taking the higher value for each level
                                    for slot_level, count in new_slots.items():
                                        if slot_level not in current_slots or current_slots[slot_level] < count:
                                            current_slots[slot_level] = count
                            
                            # Handle choice-based features
                            elif mechanics_type == "choice":
                                feature_copy = feature.copy()
                                feature_copy["source"] = f"{subclass_name} {level}"
                                
                                # Add detailed descriptions and mechanics for each option
                                if "options" in mechanics:
                                    for option in mechanics["options"]:
                                        if isinstance(option, dict) and "effects" in option:
                                            # Create a detailed description of the option's effects
                                            effect_descriptions = []
                                            for effect in option["effects"]:
                                                if effect["type"] == "advantage":
                                                    targets = effect.get("on", [])
                                                    if isinstance(targets, str):
                                                        targets = [targets]
                                                    effect_descriptions.append(f"Gain advantage on {', '.join(targets)} checks")
                                                elif effect["type"] == "resistance":
                                                    damage_types = effect.get("to", [])
                                                    if isinstance(damage_types, str):
                                                        damage_types = [damage_types]
                                                    effect_descriptions.append(f"Gain resistance to {', '.join(damage_types)} damage")
                                                elif effect["type"] == "grant_advantage":
                                                    target = effect.get("to", "")
                                                    conditions = effect.get("conditions", [])
                                                    desc = f"Grant advantage on {target}"
                                                    if conditions:
                                                        desc += f" when {', '.join(conditions)}"
                                                    effect_descriptions.append(desc)
                                            
                                            # Add the detailed description to the option
                                            if effect_descriptions:
                                                option["description"] = ". ".join(effect_descriptions)
                                
                                feature_copy["mechanics"] = mechanics
                                self.properties["subclass_features"][level_int].append(feature_copy)
                                
                                # Add to pending choices if this is a choice that needs to be made
                                if mechanics.get("choose", 0) > 0:
                                    choice_key = f"subclass_{class_name.lower()}_{level}_feature"
                                    self.properties["pending_choices"][choice_key] = {
                                        "type": "feature",
                                        "count": mechanics["choose"],
                                        "options": mechanics["options"],
                                        "description": feature.get("description", "Choose your feature option")
                                    }
                            
                            # Handle resource-based features
                            elif mechanics_type == "resource":
                                feature_copy = feature.copy()
                                feature_copy["source"] = f"{subclass_name} {level}"
                                feature_copy["mechanics"] = mechanics
                                self.properties["subclass_features"][level_int].append(feature_copy)
                            
                            # Handle passive features
                            elif mechanics_type == "passive":
                                feature_copy = feature.copy()
                                feature_copy["source"] = f"{subclass_name} {level}"
                                feature_copy["mechanics"] = mechanics
                                self.properties["subclass_features"][level_int].append(feature_copy)
                            
                            # Handle action features
                            elif mechanics_type == "action":
                                feature_copy = feature.copy()
                                feature_copy["source"] = f"{subclass_name} {level}"
                                feature_copy["mechanics"] = mechanics
                                self.properties["subclass_features"][level_int].append(feature_copy)
                            
                            # Handle all other features
                            else:
                                feature_copy = feature.copy()
                                feature_copy["source"] = f"{subclass_name} {level}"
                                feature_copy["mechanics"] = mechanics
                                self.properties["subclass_features"][level_int].append(feature_copy)
            
            logger.info(f"Set subclass {subclass_name} for {class_name}")
            
        except Exception as e:
            logger.error(f"Failed to set subclass {subclass_name} for {class_name}: {e}")
            raise

    def add_class(self, class_name: str, level: int):
        """Add a class to the character
        
        Args:
            class_name: Name of the class to add
            level: Level in the class
        """
        try:
            class_data = self._load_data_file("classes", class_name)
            
            # Add class to class list
            self.properties["classes"].append({
                "name": class_data["name"],
                "level": level
            })
            
            # Check if we need to select a subclass
            subclass_level = class_data.get("subclass_level", 3)  # Default to level 3 if not specified
            if level >= subclass_level and class_data.get("subclasses"):
                choice_key = f"subclass_{class_name.lower()}"
                self.properties["pending_choices"][choice_key] = {
                    "type": "subclass",
                    "class": class_data["name"],
                    "level": subclass_level,
                    "options": [subclass["name"] for subclass in class_data["subclasses"]],
                    "description": f"Choose a subclass for your {class_data['name']}"
                }
            
            # Update total level
            self.properties["level"] = sum(c["level"] for c in self.properties["classes"])
            
            # Add hit dice
            hit_die = class_data["hit_dice"]
            self.properties["hit_dice"].extend([hit_die] * level)
            
            # Add saving throw proficiencies
            for save in class_data["saving_throw_proficiencies"]:
                self.properties["saving_throws"][save.lower()] = True
            
            # Add armor proficiencies
            self.properties["proficiencies"]["armor"].extend(class_data["armor_proficiencies"])
            
            # Add weapon proficiencies
            self.properties["proficiencies"]["weapons"].extend(class_data["weapon_proficiencies"])
            
            # Add tool proficiencies
            self.properties["proficiencies"]["tools"].extend(class_data["tool_proficiencies"])
            
            # Add skill proficiencies
            if "skill_proficiencies" in class_data:
                if "choose" in class_data["skill_proficiencies"]:
                    choice_key = f"class_{class_name.lower()}_skills"
                    self.properties["pending_choices"][choice_key] = {
                        "type": "skill",
                        "count": class_data["skill_proficiencies"]["choose"],
                        "options": class_data["skill_proficiencies"]["from"],
                        "description": f"Choose {class_data['skill_proficiencies']['choose']} skills for your {class_data['name']}"
                    }
                else:
                    for skill in class_data["skill_proficiencies"]:
                        self.properties["skills"][skill.lower()] = True
            
            # Add equipment
            if "starting_equipment" in class_data:
                for item in class_data["starting_equipment"]:
                    if isinstance(item, dict):
                        # Handle equipment choices
                        choice_key = f"class_{class_name.lower()}_equipment_{len(self.properties['pending_choices'])}"
                        self.properties["pending_choices"][choice_key] = {
                            "type": "equipment",
                            "options": item["options"],
                            "description": item.get("description", "Choose your starting equipment")
                        }
                    else:
                        # Add fixed equipment
                        self.properties["equipment"].append({
                            "item": item,
                            "quantity": 1,
                            "description": ""
                        })
            
            # Handle class-level spellcasting
            if "spellcasting" in class_data:
                spellcasting_info = class_data["spellcasting"]
                
                # Set spellcasting ability if not already set
                if "ability" in spellcasting_info and not self.properties["spells"]["spellcasting_ability"]:
                    self.properties["spells"]["spellcasting_ability"] = spellcasting_info["ability"]
                
                # Set spellcasting focus
                if "focus" in spellcasting_info:
                    self.properties["spells"]["focus"] = spellcasting_info["focus"]
            
            # Add features
            if "features" in class_data:
                for level_str, features in class_data["features"].items():
                    feature_level = int(level_str)
                    if feature_level <= level:
                        for feature in features:
                            # All features should have mechanics in standardized format
                            mechanics = feature.get("mechanics", {})
                            if not mechanics:
                                # If no mechanics, just store the feature name and description
                                self.properties["features"].append({
                                    "name": feature.get("name", ""),
                                    "description": feature.get("description", ""),
                                    "source": f"{class_data['name']} {level_str}"
                                })
                                continue
                                
                            mechanics_type = mechanics.get("type", "")
                            
                            # Handle ability score improvements
                            if mechanics_type == "ability_score_improvement":
                                choice_key = f"class_{class_name.lower()}_{level_str}_asi"
                                self.properties["pending_choices"][choice_key] = {
                                    "type": "ability_score_improvement",
                                    "count": mechanics.get("count", 2),  # Default to 2 increases
                                    "amount": mechanics.get("amount", 1),  # Default to +1 per increase
                                    "options": mechanics.get("options", list(self.properties["stats"].keys())),
                                    "description": feature.get("description", "Choose which ability scores to improve")
                                }
                            
                            # Handle expertise
                            elif mechanics_type == "expertise":
                                choice_key = f"class_{class_name.lower()}_{level_str}_expertise"
                                self.properties["pending_choices"][choice_key] = {
                                    "type": "expertise",
                                    "count": mechanics.get("count", 2),  # Default to 2 if not specified
                                    "options": mechanics.get("options", []),
                                    "description": "Choose skills to gain expertise in"
                                }
                            
                            # Handle spellcasting
                            elif mechanics_type == "spellcasting":
                                # Update spellcasting ability if provided
                                if "ability" in mechanics:
                                    self.properties["spells"]["spellcasting_ability"] = mechanics["ability"]
                                
                                # Update spellcasting focus if provided
                                if "focus" in mechanics:
                                    self.properties["spells"]["focus"] = mechanics["focus"]
                                
                                # Handle additional cantrips
                                if "cantrips_known" in mechanics:
                                    cantrips_count = mechanics["cantrips_known"].get(str(level), 0)
                                    if cantrips_count > 0:
                                        self.properties["spells"]["cantrips"].extend([{"name": "", "description": ""}] * cantrips_count)
                                        choice_key = f"class_{class_name.lower()}_{level_str}_cantrips"
                                        self.properties["pending_choices"][choice_key] = {
                                            "type": "cantrips",
                                            "count": cantrips_count,
                                            "class": class_name,
                                            "description": f"Choose {cantrips_count} additional cantrips"
                                        }
                                
                                # Handle additional spells known
                                if "spells_known" in mechanics:
                                    spells_known_count = mechanics["spells_known"].get(str(level), 0)
                                    if spells_known_count > 0:
                                        self.properties["spells"]["spells_known"].extend([{"name": "", "description": ""}] * spells_known_count)
                                        choice_key = f"class_{class_name.lower()}_{level_str}_spells"
                                        self.properties["pending_choices"][choice_key] = {
                                            "type": "spells",
                                            "count": spells_known_count,
                                            "class": class_name,
                                            "description": f"Choose {spells_known_count} additional spells"
                                        }
                                
                                # Handle additional spell slots
                                if "spell_slots" in mechanics:
                                    current_slots = self.properties["spells"]["spell_slots"]
                                    new_slots = mechanics["spell_slots"].get(str(level), {})
                                    # Merge the spell slots, taking the higher value for each level
                                    for slot_level, count in new_slots.items():
                                        if slot_level not in current_slots or current_slots[slot_level] < count:
                                            current_slots[slot_level] = count
                            
                            # Handle resource-based features
                            elif mechanics_type == "resource":
                                feature_copy = feature.copy()
                                feature_copy["source"] = f"{class_data['name']} {level_str}"
                                feature_copy["mechanics"] = mechanics
                                self.properties["features"].append(feature_copy)
                            
                            # Handle passive features
                            elif mechanics_type == "passive":
                                feature_copy = feature.copy()
                                feature_copy["source"] = f"{class_data['name']} {level_str}"
                                feature_copy["mechanics"] = mechanics
                                self.properties["features"].append(feature_copy)
                            
                            # Handle action features
                            elif mechanics_type == "action":
                                feature_copy = feature.copy()
                                feature_copy["source"] = f"{class_data['name']} {level_str}"
                                feature_copy["mechanics"] = mechanics
                                self.properties["features"].append(feature_copy)
                            
                            # Handle all other features
                            else:
                                feature_copy = feature.copy()
                                feature_copy["source"] = f"{class_data['name']} {level_str}"
                                feature_copy["mechanics"] = mechanics
                                self.properties["features"].append(feature_copy)
            
            logger.info(f"Added class {class_name} at level {level}")
            
        except Exception as e:
            logger.error(f"Failed to add class {class_name}: {e}")
            raise

    def set_ability_scores(self, scores: Dict[str, int]):
        """Set base ability scores and update dependent values"""
        try:
            valid_abilities = {"strength", "dexterity", "constitution", 
                             "intelligence", "wisdom", "charisma"}
            
            # Validate scores
            if not all(8 <= score <= 20 for score in scores.values()):
                raise ValueError("Ability scores must be between 8 and 20")
            if not all(ability.lower() in valid_abilities for ability in scores):
                raise ValueError("Invalid ability score name")
            
            # Set base scores
            for ability, score in scores.items():
                self.properties["base_stats"][ability.lower()] = score
            
            # Recalculate final stats with all bonuses
            self._recalculate_final_stats()
            
            # Update dependent values
            self._update_dependent_values()
            
            logger.info(f"Set ability scores: {scores}")
            
        except Exception as e:
            logger.error(f"Failed to set ability scores: {e}")
            raise

    def _recalculate_final_stats(self):
        """Recalculate final stats from base stats plus all bonuses"""
        for ability in self.properties["base_stats"]:
            base = self.properties["base_stats"][ability]
            racial = self.properties["racial_bonuses"][ability]
            # In the future, we can add other bonus types here (feats, magic items, etc.)
            self.properties["stats"][ability] = base + racial

    def _update_dependent_values(self):
        """Update values that depend on ability scores"""
        # Update initiative (DEX modifier)
        self.properties["initiative"] = (self.properties["stats"]["dexterity"] - 10) // 2
        
        # Update unarmored AC (10 + DEX modifier)
        self.properties["armor_class"] = 10 + (self.properties["stats"]["dexterity"] - 10) // 2

        # Update maximum hit points (affected by Constitution modifier)
        self.properties["hit_points"]["maximum"] = self._calculate_max_hp()

    def get_ability_modifier(self, ability: str) -> int:
        """Calculate ability modifier"""
        score = self.properties["stats"].get(ability.lower())
        if score is None:
            raise ValueError(f"Invalid ability: {ability}")
        return (score - 10) // 2

    def get_saving_throw_bonus(self, ability: str) -> int:
        """Calculate saving throw bonus"""
        modifier = self.get_ability_modifier(ability)
        if self.properties["saving_throws"].get(ability.lower()):
            modifier += self.properties["proficiency_bonus"]
        return modifier

    def _get_pdf_field_names(self, pdf_path: str) -> dict:
        """Get all form field names from a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary of field names and their types
        """
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(pdf_path, strict=False)
            fields = {}
            
            if '/AcroForm' in reader.trailer['/Root']:
                form = reader.trailer['/Root']['/AcroForm']
                field_objects = form.get('/Fields', [])
                for field in field_objects:
                    field_obj = field.get_object()
                    field_name = field_obj.get('/T')
                    field_type = field_obj.get('/FT')
                    fields[field_name] = field_type
                    logger.debug(f"Found field: {field_name} of type {field_type}")
            
            return fields
        except Exception as e:
            logger.error(f"Failed to get PDF field names: {e}")
            return {}

    def _export_to_pdf(self) -> str:
        """Export character data to a fillable PDF character sheet
        
        Returns:
            Path to the generated PDF file
        """
        try:
            import os
            import subprocess
            import tempfile
            from collections import defaultdict
            
            # Path to the blank character sheet template
            template_path = os.path.join('templates', '5E_CharacterSheet_Fillable.pdf')
            if not os.path.exists(template_path):
                raise CharacterError(f"PDF template not found at {template_path}")
            
            # Calculate hit dice values
            hit_dice_total, hit_dice_types = self._format_hit_dice_for_pdf()
            
            # Format features and traits
            combat_text, non_combat_text = self._format_features_for_pdf()
            
            # Create output filename based on character name
            output_path = os.path.join('characters', f"{self.properties['name'].replace(' ', '_')}_sheet.pdf")
            
            # Create a temporary FDF file with form field data
            field_data = {
                # Basic Information
                'CharacterName': self.properties['name'],
                'CharacterName 2': self.properties['name'],  # Character name on page 2
                'ClassLevel': ', '.join(f"{c['name']} {c['level']}" for c in self.properties['classes']),
                'Race ': f"{self.properties['race']} {self.properties.get('subrace', '')}".strip(),  # Note the space after 'Race'
                'Background': self.properties.get('background', '').capitalize(),  # Capitalize background
                'Alignment': self.properties.get('alignment', ''),
                'XP': str(self.properties.get('experience', 0)),
                'ProfBonus': f"+{self.properties['proficiency_bonus']}",
                'Inspiration': '1' if self.properties.get('inspiration', False) else '0',
                
                # Hit Dice
                'HDTotal': hit_dice_total,
                'HD': hit_dice_types,
                
                # Features and Traits
                'Features and Traits': combat_text,
                'Feat+Traits': non_combat_text,

                # Handle spellcasting classes
                'Spellcasting Class 2': '',  # Initialize secondary spellcasting fields
                'SpellcastingAbility 2': '',
                'SpellSaveDC  2': '',  # Note: two spaces in field name
                'SpellAtkBonus 2': '',

                # Personality
                'PersonalityTraits ': '\\n'.join(self.properties.get('personality', {}).get('traits', [])),  # Note the space after field name
                'Ideals': '\\n'.join(self.properties.get('personality', {}).get('ideals', [])),
                'Bonds': '\\n'.join(self.properties.get('personality', {}).get('bonds', [])),
                'Flaws': '\\n'.join(self.properties.get('personality', {}).get('flaws', [])),
                
                # Proficiencies & Languages
                'ProficienciesLang': (
                    'LANGUAGES:\\n' + 
                    ', '.join(self.properties['proficiencies']['languages']) + 
                    '\\n\\n' +
                    'ARMOR PROFICIENCIES:\\n' + 
                    ', '.join(self.properties['proficiencies']['armor']) + 
                    '\\n\\n' +
                    'WEAPON PROFICIENCIES:\\n' + 
                    ', '.join(self.properties['proficiencies']['weapons']) + 
                    '\\n\\n' +
                    'TOOL PROFICIENCIES:\\n' + 
                    ', '.join(self.properties['proficiencies']['tools'])
                )
            }

            # Calculate Passive Perception (10 + Wisdom modifier + proficiency if proficient)
            passive_perception = 10 + self.get_ability_modifier('wisdom')
            if self.properties['skills'].get('perception', False):
                passive_perception += self.properties['proficiency_bonus']
            # Passive Investigation
            passive_investigation = 10 + self.get_ability_modifier('intelligence')
            if self.properties['skills'].get('investigation', False):
                passive_investigation += self.properties['proficiency_bonus']
            # Passive Insight
            passive_insight = 10 + self.get_ability_modifier('wisdom')
            if self.properties['skills'].get('insight', False):
                passive_insight += self.properties['proficiency_bonus']
            field_data['Passive'] = str(passive_perception)

            # Ability scores and modifiers
            field_data.update({
                'STR': str(self.properties['stats']['strength']),
                'STRmod': f"{self.get_ability_modifier('strength'):+d}",
                'DEX': str(self.properties['stats']['dexterity']),
                'DEXmod': f"{self.get_ability_modifier('dexterity'):+d}",
                'CON': str(self.properties['stats']['constitution']),
                'CONmod': f"{self.get_ability_modifier('constitution'):+d}",
                'INT': str(self.properties['stats']['intelligence']),
                'INTmod': f"{self.get_ability_modifier('intelligence'):+d}",
                'WIS': str(self.properties['stats']['wisdom']),
                'WISmod': f"{self.get_ability_modifier('wisdom'):+d}",
                'CHA': str(self.properties['stats']['charisma']),
                'CHAmod': f"{self.get_ability_modifier('charisma'):+d}",
                
                # Saving throws
                'ST Strength': f"{self.get_saving_throw_bonus('strength'):+d}",
                'ST Dexterity': f"{self.get_saving_throw_bonus('dexterity'):+d}",
                'ST Constitution': f"{self.get_saving_throw_bonus('constitution'):+d}",
                'ST Intelligence': f"{self.get_saving_throw_bonus('intelligence'):+d}",
                'ST Wisdom': f"{self.get_saving_throw_bonus('wisdom'):+d}",
                'ST Charisma': f"{self.get_saving_throw_bonus('charisma'):+d}",
                
                # Combat stats
                'AC': str(self.properties.get('armor_class', 10)),
                'Initiative': f"{self.get_ability_modifier('dexterity'):+d}",
                'Speed': str(self.properties.get('speed', 30)),
                'HPMax': str(self.properties['hit_points'].get('maximum', 0)),
                'HPCurrent': '',
                'HPTemp': '',
                
                # Skills
                'Acrobatics': f"{self._get_skill_bonus('acrobatics'):+d}",
                'Animal': f"{self._get_skill_bonus('animal handling'):+d}",
                'Arcana': f"{self._get_skill_bonus('arcana'):+d}",
                'Athletics': f"{self._get_skill_bonus('athletics'):+d}",
                'Deception ': f"{self._get_skill_bonus('deception'):+d}",  # Note: space after name matches PDF field
                'History ': f"{self._get_skill_bonus('history'):+d}",  # Note: space after name matches PDF field
                'Insight': f"{self._get_skill_bonus('insight'):+d}",
                'Intimidation': f"{self._get_skill_bonus('intimidation'):+d}",
                'Investigation ': f"{self._get_skill_bonus('investigation'):+d}",  # Note: space after name matches PDF field
                'Medicine': f"{self._get_skill_bonus('medicine'):+d}",
                'Nature': f"{self._get_skill_bonus('nature'):+d}",
                'Perception ': f"{self._get_skill_bonus('perception'):+d}",  # Note: space after name matches PDF field
                'Performance': f"{self._get_skill_bonus('performance'):+d}",
                'Persuasion': f"{self._get_skill_bonus('persuasion'):+d}",
                'Religion': f"{self._get_skill_bonus('religion'):+d}",
                'SleightofHand': f"{self._get_skill_bonus('sleight of hand'):+d}",
                'Stealth ': f"{self._get_skill_bonus('stealth'):+d}",  # Note: space after name matches PDF field
                'Survival': f"{self._get_skill_bonus('survival'):+d}",
                
                # Skill proficiency checkboxes - using exact PDF field names
                'Check Box 23': 'Yes' if self.properties['skills'].get('acrobatics', False) else 'Off',
                'Check Box 24': 'Yes' if self.properties['skills'].get('animal handling', False) else 'Off',
                'Check Box 25': 'Yes' if self.properties['skills'].get('arcana', False) else 'Off',
                'Check Box 26': 'Yes' if self.properties['skills'].get('athletics', False) else 'Off',
                'Check Box 27': 'Yes' if self.properties['skills'].get('deception', False) else 'Off',
                'Check Box 28': 'Yes' if self.properties['skills'].get('history', False) else 'Off',
                'Check Box 29': 'Yes' if self.properties['skills'].get('insight', False) else 'Off',
                'Check Box 30': 'Yes' if self.properties['skills'].get('intimidation', False) else 'Off',
                'Check Box 31': 'Yes' if self.properties['skills'].get('investigation', False) else 'Off',
                'Check Box 32': 'Yes' if self.properties['skills'].get('medicine', False) else 'Off',
                'Check Box 33': 'Yes' if self.properties['skills'].get('nature', False) else 'Off',
                'Check Box 34': 'Yes' if self.properties['skills'].get('perception', False) else 'Off',
                'Check Box 35': 'Yes' if self.properties['skills'].get('performance', False) else 'Off',
                'Check Box 36': 'Yes' if self.properties['skills'].get('persuasion', False) else 'Off',
                'Check Box 37': 'Yes' if self.properties['skills'].get('religion', False) else 'Off',
                'Check Box 38': 'Yes' if self.properties['skills'].get('sleight of hand', False) else 'Off',
                'Check Box 39': 'Yes' if self.properties['skills'].get('stealth', False) else 'Off',
                'Check Box 40': 'Yes' if self.properties['skills'].get('survival', False) else 'Off',
                
                # Saving throw proficiency checkboxes
                'Check Box 11': 'Yes' if self.properties['saving_throws']['strength'] else 'Off',
                'Check Box 18': 'Yes' if self.properties['saving_throws']['dexterity'] else 'Off',
                'Check Box 19': 'Yes' if self.properties['saving_throws']['constitution'] else 'Off',
                'Check Box 20': 'Yes' if self.properties['saving_throws']['intelligence'] else 'Off',
                'Check Box 21': 'Yes' if self.properties['saving_throws']['wisdom'] else 'Off',
                'Check Box 22': 'Yes' if self.properties['saving_throws']['charisma'] else 'Off',
            })
                
            # Calculate spellcasting values if applicable
            spellcasting_classes = []
            for class_info in self.properties['classes']:
                class_data = self._load_data_file('classes', class_info['name'])
                if 'spellcasting' in class_data:
                    spellcasting_classes.append({
                        'name': class_info['name'],
                        'ability': class_data['spellcasting']['ability'],
                        'level': class_info['level']
                    })

            # Handle up to two spellcasting classes
            if len(spellcasting_classes) >= 1:
                primary = spellcasting_classes[0]
                ability = primary['ability']
                modifier = self.get_ability_modifier(ability)
                field_data.update({
                    'Spellcasting Class': primary['name'],
                    'SpellcastingAbility': ability.upper()[:3],  # First three letters capitalized
                    'SpellSaveDC': str(8 + self.properties['proficiency_bonus'] + modifier),
                    'SpellAtkBonus': f"+{modifier + self.properties['proficiency_bonus']}"
                })

            if len(spellcasting_classes) >= 2:
                secondary = spellcasting_classes[1]
                ability = secondary['ability']
                modifier = self.get_ability_modifier(ability)
                field_data.update({
                    'Spellcasting Class 2': secondary['name'],
                    'SpellcastingAbility 2': ability.upper()[:3],  # First three letters capitalized
                    'SpellSaveDC  2': str(8 + self.properties['proficiency_bonus'] + modifier),  # Note: two spaces in field name
                    'SpellAtkBonus 2': f"+{modifier + self.properties['proficiency_bonus']}"
                })
                
            # Save the FDF file
            fdf_path = os.path.join(tempfile.gettempdir(), f"{self.properties['name'].replace(' ', '_')}_sheet.fdf")
            
            # Ensure temp directory exists and is writable
            temp_dir = os.path.dirname(fdf_path)
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            try:
                with open(fdf_path, 'w', encoding='utf-8') as f:
                    f.write("%FDF-1.2\n")
                    f.write("1 0 obj\n")
                    f.write("<<\n")
                    f.write("/FDF\n")
                    f.write("<<\n")
                    f.write("/Fields [\n")
                    
                    for field_name, value in field_data.items():
                        # Convert value to string and handle newlines
                        value_str = str(value)
                        
                        # Replace literal \n with actual newlines, then escape for FDF
                        if '\\n' in value_str:
                            value_str = value_str.replace('\\n', '\n')
                        
                        # Properly escape special characters for FDF
                        value_str = value_str.replace('\\', '\\\\')
                        value_str = value_str.replace('(', '\\(')
                        value_str = value_str.replace(')', '\\)')
                        value_str = value_str.replace('\n', '\\r')  # Use \r for newlines in FDF
                        
                        # Write field entry
                        f.write("<<\n")
                        f.write(f"/T ({field_name})\n")
                        f.write(f"/V ({value_str})\n")
                        f.write(">>\n")
                    
                    f.write("]\n")
                    f.write(">>\n")
                    f.write(">>\n")  # Close the first dictionary
                    f.write("endobj\n")
                    f.write("trailer\n")
                    f.write("<<\n")
                    f.write("/Root 1 0 R\n")
                    f.write(">>\n")
                    f.write("%%EOF\n")
                    
                    # Ensure file is properly flushed and synced
                    f.flush()
                    os.fsync(f.fileno())
                
                # Verify the file exists and has content
                if not os.path.exists(fdf_path) or os.path.getsize(fdf_path) == 0:
                    raise CharacterError("Failed to create FDF file")
                
                # Run pdftk with error output capture
                try:
                    result = subprocess.run([
                        'pdftk',
                        template_path,
                        'fill_form',
                        fdf_path,
                        'output',
                        output_path,
                        'flatten'
                    ], capture_output=True, text=True, check=True)
                    
                    # Clean up the temporary FDF file
                    try:
                        os.unlink(fdf_path)
                    except Exception as e:
                        logger.warning(f"Failed to clean up FDF file: {e}")
                    
                    return output_path
                    
                except subprocess.CalledProcessError as e:
                    logger.error(f"pdftk stderr: {e.stderr}")
                    logger.error(f"pdftk stdout: {e.stdout}")
                    raise CharacterError(f"pdftk failed: {e.stderr}")
                    
            except Exception as e:
                logger.error(f"Failed to create or write FDF file: {e}")
                raise CharacterError(f"Failed to create FDF file: {e}")
        except Exception as e:
            logger.error(f"Failed to export PDF character sheet: {e}")
            raise CharacterError(f"Failed to export PDF character sheet: {e}")

    def _get_skill_bonus(self, skill: str) -> int:
        """Calculate total bonus for a skill
        
        Args:
            skill: The skill name
            
        Returns:
            Total skill bonus including ability modifier and proficiency
        """
        skill = skill.lower()  # Normalize skill name
        ability = self._get_skill_ability(skill)
        bonus = self.get_ability_modifier(ability)
        if self.properties['skills'].get(skill, False):
            bonus += self.properties['proficiency_bonus']
        return bonus

    def set_background(self, background_name: str, personality_choices: Optional[Dict] = None) -> None:
        """Set the character's background and apply its benefits
        
        Args:
            background_name: Name of the background to apply
            personality_choices: Optional dictionary containing chosen personality elements
                               Format: {
                                   "traits": List[str],
                                   "ideal": str,
                                   "bond": str,
                                   "flaw": str
                               }
        """
        try:
            # Load and apply background
            background = Background(background_name)
            background.apply_to_character(self)
            
            # Apply personality choices if provided
            if personality_choices:
                self._apply_personality_choices(background, personality_choices)
            else:
                # Store background personality options for later selection
                self.properties["pending_choices"]["personality"] = background.get_personality_options()
            
            logger.info(f"Set background to {background_name}")
            
        except Exception as e:
            logger.error(f"Failed to set background {background_name}: {e}")
            raise CharacterError(f"Failed to set background: {e}")
    
    def _apply_personality_choices(self, background: Background, choices: Dict) -> None:
        """Apply chosen personality elements from background
        
        Args:
            background: Background object
            choices: Dictionary of personality choices
        """
        try:
            personality_options = background.get_personality_options()
            
            # Validate and apply personality traits
            if "traits" in choices:
                if len(choices["traits"]) != personality_options["personality_traits"]["count"]:
                    raise CharacterError(f"Must choose exactly {personality_options['personality_traits']['count']} personality traits")
                self.properties["personality"]["traits"] = choices["traits"]
            
            # Apply ideal
            if "ideal" in choices:
                self.properties["personality"]["ideals"] = [choices["ideal"]]
            
            # Apply bond
            if "bond" in choices:
                self.properties["personality"]["bonds"] = [choices["bond"]]
            
            # Apply flaw
            if "flaw" in choices:
                self.properties["personality"]["flaws"] = [choices["flaw"]]
            
            # Remove pending personality choices if all are applied
            if "personality" in self.properties["pending_choices"]:
                del self.properties["pending_choices"]["personality"]
            
        except Exception as e:
            logger.error(f"Failed to apply personality choices: {e}")
            raise CharacterError(f"Failed to apply personality choices: {e}")

    def get_available_backgrounds(self) -> List[str]:
        """Get list of available backgrounds
        
        Returns:
            List of background names
        """
        return Background.list_available_backgrounds()

    def has_pending_choices(self) -> bool:
        """Check if character has pending choices to make
        
        Returns:
            True if there are pending choices, False otherwise
        """
        return bool(self.properties.get("pending_choices", {}))

    def get_pending_choices(self) -> Dict:
        """Get pending choices that need to be made
        
        Returns:
            Dictionary of pending choices
        """
        return self.properties.get("pending_choices", {})

    def _is_roleplay_feature(self, feature: Dict) -> bool:
        """Determine if a feature is roleplay-focused rather than mechanical
        
        Args:
            feature: Feature dictionary containing name and description
            
        Returns:
            True if the feature is roleplay-focused, False if mechanical
        """
        # Skip ability score improvements - they should be handled as choices
        if "Ability Score" in feature.get('name', ''):
            return False
            
        # List of keywords that suggest mechanical features
        mechanical_keywords = [
            "proficiency",
            "attack",
            "damage",
            "armor class",
            "hit points",
            "saving throw",
            "spell",
            "combat",
            "initiative",
            "resistance",
            "immunity",
            "bonus action",
            "reaction"
        ]
        
        # Check if feature is explicitly marked
        if feature.get('roleplay', False):
            return True
        if feature.get('mechanical', True):
            return False
            
        # Check feature name and description for mechanical keywords
        text = (feature.get('name', '') + ' ' + feature.get('description', '')).lower()
        
        # If it contains mechanical keywords, it's not a roleplay feature
        if any(keyword in text for keyword in mechanical_keywords):
            return False
            
        # By default, if it's not clearly mechanical, put it in roleplay
        return True

    def _handle_ability_score_improvement(self, feature: Dict):
        """Handle ability score improvement as a choice rather than a feature
        
        Args:
            feature: The ability score improvement feature
        """
        if "choose" not in self.properties["pending_choices"]:
            self.properties["pending_choices"]["choose"] = []
            
        self.properties["pending_choices"]["choose"].append({
            "type": "ability_score_improvement",
            "count": 2,  # Standard ASI allows two +1s or one +2
            "options": list(self.properties["stats"].keys()),
            "description": feature.get('description', 'Choose which ability scores to improve')
        })

    def _format_hit_dice_for_pdf(self) -> tuple[str, str]:
        """Format hit dice for PDF display with usage tracking
        
        Returns:
            Tuple containing:
            - String formatted as "n" for single die type or "n/m" for multiple die types
            - String formatted as "1dn" for single die type or "1dn, 1dm" for multiple
        """
        hit_dice_counts = defaultdict(int)
        for die in self.properties['hit_dice']:
            die_type = die.split('d')[1]  # Extract the die type (e.g., '10' from '1d10')
            hit_dice_counts[die_type] += 1
        
        # Sort by die size (d4, d6, d8, etc.)
        sorted_dice = sorted(hit_dice_counts.items(), key=lambda x: int(x[0]))
        
        if len(sorted_dice) == 1:
            # Single die type
            die_type, count = sorted_dice[0]
            return str(count), f"1d{die_type}"
        else:
            # Multiple die types
            total_str = "/".join(str(count) for _, count in sorted_dice)
            dice_types_str = ", ".join(f"1d{die_type}" for die_type, _ in sorted_dice)
            return total_str, dice_types_str

    def _categorize_feature(self, feature: Dict) -> str:
        """Categorize a feature as 'combat' or 'non_combat'
        
        Args:
            feature: Feature dictionary containing name and description
            
        Returns:
            'combat' or 'non_combat'
        """
        # Handle string features
        if isinstance(feature, str):
            return 'non_combat'
            
        # Check mechanics first
        mechanics = feature.get('mechanics', {})
        if mechanics:
            mechanics_type = mechanics.get('type', '')
            
            # Features with these mechanics types are always combat
            if mechanics_type in ['action', 'reaction', 'bonus_action']:
                return 'combat'
                
            # Features with damage, attack rolls, or saves are combat
            if any(k in mechanics for k in ['damage', 'attack', 'save']):
                return 'combat'
                
            # Resource-based features need more analysis
            if mechanics_type == 'resource':
                # If the resource is used for combat abilities, it's combat
                if any(k in mechanics for k in ['damage', 'attack', 'save', 'healing']):
                    return 'combat'
                # If it's clearly non-combat (like tool proficiencies), mark as such
                if any(k in mechanics for k in ['skill', 'tool', 'social']):
                    return 'non_combat'
        
        # Combat-related keywords that strongly indicate a combat feature
        combat_keywords = [
            "attack roll", "damage", "hit points", "AC", "armor class",
            "initiative", "reaction", "bonus action", "weapon",
            "resistance", "immunity", "spell attack", "combat",
            "defense", "shield", "dodge", "critical", "temporary hp",
            "martial", "maneuver", "rage", "smite", "sneak attack",
            "fighting style", "proficiency with", "disadvantage on attack",
            "advantage on attack"
        ]
        
        # Non-combat keywords that strongly indicate a non-combat feature
        non_combat_keywords = [
            "skill", "social", "interact", "craft", "create",
            "explore", "investigate", "survival", "culture",
            "background", "knowledge", "profession", "lifestyle",
            "residence", "ceremony", "meditation", "study",
            "tracking", "recall information", "familiar with",
            "environment", "healing", "care", "temple", "shrine"
        ]

        # Special case names that are always combat
        combat_names = {
            "fighting style", "martial", "weapon training", "armor training",
            "divine smite", "sneak attack", "rage", "martial arts",
            "extra attack", "unarmored defense", "defensive tactics"
        }

        # Special case names that are always non-combat
        non_combat_names = {
            "darkvision", "superior darkvision", "keen senses", "trance",
            "shelter of the faithful", "natural explorer", "favored enemy",
            "languages", "tool proficiency", "skill proficiency"
        }

        name = feature.get('name', '').lower()
        
        # Check special case names first
        if any(combat_name in name for combat_name in combat_names):
            return 'combat'
        if any(non_combat_name in name for non_combat_name in non_combat_names):
            return 'non_combat'
        
        # Combine name and description for text analysis
        text = (name + ' ' + feature.get('description', '')).lower()
        
        # Count keyword matches
        combat_matches = sum(1 for keyword in combat_keywords if keyword in text)
        non_combat_matches = sum(1 for keyword in non_combat_keywords if keyword in text)
        
        # Special case handling for spells and magic
        if "spell" in text or "magic" in text or "casting" in text:
            # Look for combat spell indicators
            combat_spell_indicators = ["damage", "attack", "hit", "defense", "weapon"]
            if any(indicator in text for indicator in combat_spell_indicators):
                return 'combat'
            # Look for utility spell indicators
            utility_spell_indicators = ["utility", "light", "illusion", "communication", "travel"]
            if any(indicator in text for indicator in utility_spell_indicators):
                return 'non_combat'
            # If unclear, default to combat for spellcasting features
            return 'combat'
        
        # If there are more combat matches, it's a combat feature
        if combat_matches > non_combat_matches:
            return 'combat'
        # If there are more non-combat matches, it's a non-combat feature
        if non_combat_matches > combat_matches:
            return 'non_combat'
        
        # Default case: if unclear, put in non-combat for less clutter in combat section
        return 'non_combat'

    def _format_features_for_pdf(self) -> tuple[str, str]:
        """Format features for both PDF sections
        
        Returns:
            Tuple of (combat_features_text, non_combat_features_text)
        """
        combat_features = []
        non_combat_features = []
        
        # Track features by name to avoid duplicates
        seen_features = set()
        
        # First process traits
        for trait in self.properties.get('traits', []):
            # Handle string traits
            if isinstance(trait, str):
                if trait not in seen_features:
                    seen_features.add(trait)
                    non_combat_features.append({'name': trait, 'description': ''})
                continue
                
            name = trait.get('name', '').strip()
            if name and name not in seen_features:
                seen_features.add(name)
                category = self._categorize_feature(trait)
                if category == 'combat':
                    combat_features.append(trait)
                else:
                    non_combat_features.append(trait)
        
        # Then process features
        for feature in self.properties.get('features', []):
            # Handle string features
            if isinstance(feature, str):
                if feature not in seen_features:
                    seen_features.add(feature)
                    non_combat_features.append({'name': feature, 'description': ''})
                continue
                
            name = feature.get('name', '').strip()
            if name and name not in seen_features:
                seen_features.add(name)
                mechanics = feature.get('mechanics', {})
                
                # Determine category based on mechanics type
                if mechanics:
                    mechanics_type = mechanics.get('type', '')
                    if mechanics_type in ['action', 'reaction', 'bonus_action'] or 'damage' in mechanics:
                        category = 'combat'
                    elif mechanics_type in ['passive', 'resource'] and not any(k in mechanics for k in ['damage', 'attack', 'save']):
                        category = 'non_combat'
                    else:
                        category = self._categorize_feature(feature)
                else:
                    category = self._categorize_feature(feature)
                
                # Format mechanics information
                if mechanics:
                    mechanics_text = []
                    mechanics_type = mechanics.get('type', '')
                    
                    # Action type
                    if mechanics_type in ['action', 'reaction', 'bonus_action']:
                        mechanics_text.append(f"Action Type: {mechanics_type.replace('_', ' ').title()}")
                    
                    # Resource usage
                    if 'resource' in mechanics:
                        resource = mechanics['resource']
                        if isinstance(resource, dict):
                            mechanics_text.append(f"Resource: {resource.get('name', 'Unknown')}")
                            if 'max' in resource:
                                mechanics_text.append(f"Uses: {resource['max']} per {resource.get('recovery', 'long rest')}")
                        else:
                            mechanics_text.append(f"Resource: {resource}")
                    
                    # Range
                    if 'range' in mechanics:
                        range_info = mechanics['range']
                        if isinstance(range_info, dict):
                            mechanics_text.append(f"Range: {range_info.get('normal', '—')} ft.")
                            if 'long' in range_info:
                                mechanics_text.append(f"Long Range: {range_info['long']} ft.")
                        else:
                            mechanics_text.append(f"Range: {range_info}")
                    
                    # Duration
                    if 'duration' in mechanics:
                        duration = mechanics['duration']
                        if isinstance(duration, dict):
                            mechanics_text.append(f"Duration: {duration.get('amount', '1')} {duration.get('unit', 'round')}")
                        else:
                            mechanics_text.append(f"Duration: {duration}")
                    
                    # Damage
                    if 'damage' in mechanics:
                        damage = mechanics['damage']
                        if isinstance(damage, dict):
                            damage_text = []
                            for damage_type, dice in damage.items():
                                if isinstance(dice, dict):
                                    damage_text.append(f"{dice.get('dice', '1d6')} {damage_type}")
                                else:
                                    damage_text.append(f"{dice} {damage_type}")
                            mechanics_text.append(f"Damage: {', '.join(damage_text)}")
                        else:
                            mechanics_text.append(f"Damage: {damage}")
                    
                    # Saving throw
                    if 'save' in mechanics:
                        save = mechanics['save']
                        if isinstance(save, dict):
                            mechanics_text.append(f"Save: {save.get('type', 'Unknown')} DC {save.get('dc', 'Unknown')}")
                            if 'effect' in save:
                                mechanics_text.append(f"Save Effect: {save['effect']}")
                        else:
                            mechanics_text.append(f"Save: {save}")
                    
                    # Add mechanics text to feature description
                    if mechanics_text:
                        feature = feature.copy()
                        feature['description'] = feature.get('description', '') + '\\n' + '\\n'.join(mechanics_text)
                
                if category == 'combat':
                    combat_features.append(feature)
                else:
                    non_combat_features.append(feature)
        
        # Sort features by level/importance if available, then by name
        def sort_key(x):
            if isinstance(x, str):
                return (0, x.lower())
            source = x.get('source', '')
            if source:
                try:
                    level = int(source.split()[-1])
                    return (level, x.get('name', '').lower())
                except (ValueError, IndexError):
                    pass
            return (0, x.get('name', '').lower())
        
        combat_features.sort(key=sort_key)
        non_combat_features.sort(key=sort_key)
        
        # Format combat features
        combat_text = ["COMBAT FEATURES AND TRAITS:", ""]  # Add header
        for feature in combat_features:
            if isinstance(feature, str):
                combat_text.append(feature.upper())
                combat_text.append("")  # blank line for spacing
            else:
                source = feature.get('source', '')
                name = feature['name'].upper()
                if source:
                    name = f"{name} ({source})"
                combat_text.append(name)
                combat_text.append(feature.get('description', 'No description available'))
                combat_text.append("")  # blank line for spacing
        
        # Format non-combat features
        non_combat_text = ["NON-COMBAT FEATURES AND TRAITS:", ""]  # Add header
        for feature in non_combat_features:
            if isinstance(feature, str):
                non_combat_text.append(feature.upper())
                non_combat_text.append("")  # blank line for spacing
            else:
                source = feature.get('source', '')
                name = feature['name'].upper()
                if source:
                    name = f"{name} ({source})"
                non_combat_text.append(name)
                non_combat_text.append(feature.get('description', 'No description available'))
                non_combat_text.append("")  # blank line for spacing
        
        # Join with newlines and escape for PDF
        combat_str = '\\n'.join(combat_text)
        non_combat_str = '\\n'.join(non_combat_text)
        
        return (combat_str, non_combat_str)





