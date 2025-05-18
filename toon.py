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
            "classes": [],
            "level": 0,
            "background": "",
            "alignment": "",
            "experience": 0,
            "inspiration": False,
            "stats": {
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
            "proficiency_bonus": 2,
            "armor_class": 10,
            "initiative": 0,
            "speed": 0,
            "size": {
                "category": "Medium",
                "height": {
                    "base": "5'0\"",
                    "modifier": "2d4"
                },
                "weight": {
                    "base": 100,
                    "modifier": "2d4"
                }
            },
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
            "features": [],
            "traits": [],
            "equipment": [],
            "currency": {
                "platinum": 0,
                "gold": 0,
                "electrum": 0,
                "silver": 0,
                "copper": 0
            },
            "spells": {
                "cantrips": [],
                "spells_known": [],
                "spell_slots": {},
                "spellcasting_ability": ""
            },
            "personality": {
                "traits": [],
                "ideals": [],
                "bonds": [],
                "flaws": []
            },
            "pending_choices": {},
            # Add metadata for character management
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat(),
                "version": "1.0",
                "save_count": 0
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
            
            # Here we could add version migration logic if needed
            
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
                
                # Calculate derived values for the template
                class_levels = ", ".join(f"{c['name']} {c['level']}" for c in self.properties['classes'])
                
                # Calculate ability modifiers
                modifiers = {
                    ability: f"{self.get_ability_modifier(ability):+d}"
                    for ability in self.properties['stats']
                }
                
                # Calculate saving throw bonuses
                saving_throws = {
                    ability: {
                        'bonus': f"{self.get_saving_throw_bonus(ability):+d}",
                        'proficient': self.properties['saving_throws'][ability]
                    }
                    for ability in self.properties['saving_throws']
                }
                
                # Calculate skill bonuses
                skill_bonuses = defaultdict(lambda: "+0")
                for skill, proficient in self.properties['skills'].items():
                    # Determine ability modifier for skill
                    ability = self._get_skill_ability(skill)
                    bonus = self.get_ability_modifier(ability)
                    if proficient:
                        bonus += self.properties['proficiency_bonus']
                    skill_bonuses[skill] = f"{bonus:+d}"
                
                # Format hit dice
                hit_dice_counts = defaultdict(int)
                for die in self.properties['hit_dice']:
                    # Extract the die type (e.g., 'd10' from '1d10')
                    die_type = die.split('d')[1]
                    hit_dice_counts[die_type] += 1
                consolidated_hit_dice = []
                for die_type, count in hit_dice_counts.items():
                    consolidated_hit_dice.append(f"{count}d{die_type}")
                hit_dice_summary = ', '.join(consolidated_hit_dice)
                
                # Calculate spellcasting values if applicable
                spell_save_dc = None
                spell_attack_bonus = None
                if self.properties['spells']['spellcasting_ability']:
                    ability = self.properties['spells']['spellcasting_ability']
                    modifier = self.get_ability_modifier(ability)
                    spell_save_dc = 8 + self.properties['proficiency_bonus'] + modifier
                    spell_attack_bonus = modifier + self.properties['proficiency_bonus']
                
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
                        'skills': skill_bonuses,
                        'armor_class': self.properties['armor_class'],
                        'initiative': self.properties['initiative'],
                        'speed': self.properties['speed'],
                        'hit_points': self.properties['hit_points'],
                        'hit_dice': hit_dice_summary,
                        'proficiencies': self.properties['proficiencies'],
                        'features': self.properties['features'],
                        'traits': self.properties['traits'],
                        'equipment': self.properties['equipment'],
                        'spells': {
                            'ability': self.properties['spells']['spellcasting_ability'],
                            'save_dc': spell_save_dc,
                            'attack_bonus': spell_attack_bonus,
                            'cantrips': self.properties['spells']['cantrips'],
                            'spells_known': self.properties['spells']['spells_known'],
                            'spell_slots': self.properties['spells']['spell_slots']
                        }
                    }
                }
                
                # Render the template
                html = template.render(**template_data)
                
                # Save the HTML file
                output_path = os.path.join('characters', f"{self.properties['name'].replace(' ', '_')}_sheet.html")
                with open(output_path, 'w') as f:
                    f.write(html)
                
                return output_path
            
            else:
                raise CharacterError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Failed to export character sheet: {e}")
            raise CharacterError(f"Failed to export character sheet: {e}")

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
            
            # Apply ability score increases
            ability_scores = race_data["ability_scores"]
            if isinstance(ability_scores, dict) and "choose" not in ability_scores:
                for ability, bonus in ability_scores.items():
                    self.properties["stats"][ability.lower()] += bonus
            elif isinstance(ability_scores, dict) and "choose" in ability_scores:
                # Store ability score choices in pending_choices
                self.properties["pending_choices"]["ability_scores"] = ability_scores["choose"]
            
            # Add racial traits and apply their grants
            for trait in race_data.get("traits", []):
                self.properties["traits"].append(trait)
                if "grants" in trait:
                    self._apply_trait_grants(trait["grants"])
                self._apply_trait_modifies(trait)
            
            # Add languages
            self.properties["proficiencies"]["languages"].extend(race_data["languages"]["standard"])
            if "bonus" in race_data["languages"]:
                if "choose" in race_data["languages"]["bonus"]:
                    self.properties["pending_choices"]["languages"] = race_data["languages"]["bonus"]
            
            # Apply subrace if specified
            if subrace:
                self.properties["subrace"] = subrace
                subrace_data = next(sr for sr in race_data["subraces"] if sr["name"] == subrace)
                
                # Handle subrace ability scores
                if "ability_scores" in subrace_data:
                    if isinstance(subrace_data["ability_scores"], dict) and "choose" in subrace_data["ability_scores"]:
                        # Store ability score choices in pending_choices
                        self.properties["pending_choices"]["ability_scores"] = subrace_data["ability_scores"]["choose"]
                    elif "replaces" in subrace_data and "ability_scores" in subrace_data["replaces"]:
                        # Reset base race ability scores if subrace replaces them
                        for ability in self.properties["stats"]:
                            self.properties["stats"][ability] -= race_data["ability_scores"].get(ability, 0)
                        # Apply subrace ability scores
                        if "choose" not in subrace_data["ability_scores"]:
                            for ability, bonus in subrace_data["ability_scores"].items():
                                self.properties["stats"][ability.lower()] += bonus
                        else:
                            self.properties["pending_choices"]["ability_scores"] = subrace_data["ability_scores"]["choose"]
                    else:
                        # Add subrace ability scores to base scores
                        for ability, bonus in subrace_data.get("ability_scores", {}).items():
                            self.properties["stats"][ability.lower()] += bonus
                
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

    def add_class(self, class_name: str, level: int):
        """Add a class level to the character"""
        try:
            if level < 1 or level > 20:
                raise ValueError("Level must be between 1 and 20")
                
            class_data = self._load_data_file("classes", class_name)
            
            # Create new class entry
            new_class = {
                "name": class_data["name"],
                "level": level,
                "subclass": None
            }
            
            # Add hit dice
            hit_dice = class_data["hit_dice"]
            self.properties["hit_dice"].extend([hit_dice] * level)
            
            # Add saving throw proficiencies (only if this is the first class)
            if not self.properties["classes"]:
                for save in class_data["saving_throw_proficiencies"]:
                    self.properties["saving_throws"][save.lower()] = True
            
            # Add weapon and armor proficiencies
            self.properties["proficiencies"]["weapons"].extend(class_data["weapon_proficiencies"])
            self.properties["proficiencies"]["armor"].extend(class_data["armor_proficiencies"])
            
            # Add class features
            for level_num in range(1, level + 1):
                if str(level_num) in class_data["features"]:
                    self.properties["features"].extend(class_data["features"][str(level_num)])
            
            # Update spellcasting if applicable
            if "spellcasting" in class_data:
                self.properties["spells"]["spellcasting_ability"] = class_data["spellcasting"]["ability"]
                # Add cantrips known if the class has them
                if "cantrips_known" in class_data["spellcasting"]:
                    for level_req, count in class_data["spellcasting"]["cantrips_known"].items():
                        if level >= int(level_req):
                            self.properties["spells"]["cantrips"] = [""] * count
                # Add spell slots
                for level_req, slots in class_data["spellcasting"]["spell_slots_per_level"].items():
                    if level >= int(level_req):
                        self.properties["spells"]["spell_slots"].update(slots)
            
            # Add the class to the character
            self.properties["classes"].append(new_class)
            self.properties["level"] = sum(c["level"] for c in self.properties["classes"])
            
            # Update proficiency bonus
            self.properties["proficiency_bonus"] = 2 + ((self.properties["level"] - 1) // 4)
            
            # Update maximum hit points
            self.properties["hit_points"]["maximum"] = self._calculate_max_hp()
            
            logger.info(f"Added class {class_name} (level {level})")
            
        except Exception as e:
            logger.error(f"Failed to add class {class_name}: {e}")
            raise

    def set_ability_scores(self, scores: Dict[str, int]):
        """Set ability scores and update dependent values"""
        try:
            valid_abilities = {"strength", "dexterity", "constitution", 
                             "intelligence", "wisdom", "charisma"}
            
            # Validate scores
            if not all(8 <= score <= 20 for score in scores.values()):
                raise ValueError("Ability scores must be between 8 and 20")
            if not all(ability.lower() in valid_abilities for ability in scores):
                raise ValueError("Invalid ability score name")
            
            # Set scores
            for ability, score in scores.items():
                self.properties["stats"][ability.lower()] = score
            
            # Update dependent values
            self._update_dependent_values()
            
            logger.info(f"Set ability scores: {scores}")
            
        except Exception as e:
            logger.error(f"Failed to set ability scores: {e}")
            raise

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
                passive_perception += 2 + ((self.properties['level'] - 1) // 4)  # Proficiency bonus calculation
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
            "divine smite", "sneak attack", "rage", "martial arts"
        }

        # Special case names that are always non-combat
        non_combat_names = {
            "darkvision", "superior darkvision", "keen senses", "trance",
            "shelter of the faithful", "natural explorer", "favored enemy",
            "languages"
        }
        
        # Check if feature is explicitly marked
        if feature.get('combat', False):
            return 'combat'
        if feature.get('non_combat', False):
            return 'non_combat'

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
            name = feature.get('name', '').strip()
            if name and name not in seen_features:
                seen_features.add(name)
                category = self._categorize_feature(feature)
                if category == 'combat':
                    combat_features.append(feature)
                else:
                    non_combat_features.append(feature)
        
        # Sort features by level/importance if available, then by name
        def sort_key(x):
            return (x.get('level', 0), x.get('name', '').lower())
        
        combat_features.sort(key=sort_key)
        non_combat_features.sort(key=sort_key)
        
        # Format combat features
        combat_text = ["COMBAT FEATURES AND TRAITS:", ""]  # Add header
        for feature in combat_features:
            combat_text.append(f"{feature['name'].upper()}")
            combat_text.append(feature.get('description', 'No description available'))
            if 'usage' in feature:
                combat_text.append(f"Usage: {feature['usage']}")
            combat_text.append("")  # blank line for spacing
        
        # Format non-combat features
        non_combat_text = ["NON-COMBAT FEATURES AND TRAITS:", ""]  # Add header
        for feature in non_combat_features:
            non_combat_text.append(f"{feature['name'].upper()}")
            non_combat_text.append(feature.get('description', 'No description available'))
            if 'usage' in feature:
                non_combat_text.append(f"Usage: {feature['usage']}")
            non_combat_text.append("")  # blank line for spacing
        
        # Join with newlines and escape for PDF
        combat_str = '\\n'.join(combat_text)
        non_combat_str = '\\n'.join(non_combat_text)
        
        return (combat_str, non_combat_str)





