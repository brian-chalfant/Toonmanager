from logging_config import get_logger
import json
import os
from typing import Dict, List, Optional, Union
import random
from file_functions import save_file, open_file, list_files, remove_file
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from collections import defaultdict

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
            "skills": {},
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
            "spells": {
                "cantrips": [],
                "spells_known": [],
                "spell_slots": {},
                "spellcasting_ability": ""
            },
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
            filename: The filename to delete
            
        Returns:
            True if deletion was successful
        """
        try:
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
                if "skills" not in self.properties:
                    self.properties["skills"] = {}
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
            for ability, bonus in race_data["ability_scores"].items():
                self.properties["stats"][ability.lower()] += bonus
            
            # Add racial traits and apply their grants
            for trait in race_data["traits"]:
                self.properties["traits"].append(trait)
                if "grants" in trait:
                    self._apply_trait_grants(trait["grants"])
                self._apply_trait_modifies(trait)
            
            # Add languages
            self.properties["proficiencies"]["languages"].extend(race_data["languages"]["standard"])
            
            # Apply subrace if specified
            if subrace:
                self.properties["subrace"] = subrace
                subrace_data = next(sr for sr in race_data["subraces"] if sr["name"] == subrace)
                
                # Apply subrace ability scores
                for ability, bonus in subrace_data.get("ability_scores", {}).items():
                    self.properties["stats"][ability.lower()] += bonus
                
                # Add subrace traits and apply their grants
                for trait in subrace_data.get("traits", []):
                    self.properties["traits"].append(trait)
                    if "grants" in trait:
                        self._apply_trait_grants(trait["grants"])
                    self._apply_trait_modifies(trait)
                
            logger.info(f"Set race to {race}" + (f" ({subrace})" if subrace else ""))
            
        except Exception as e:
            logger.error(f"Failed to set race to {race}: {e}")
            raise

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
                # Add cantrips known
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
            
            # Create output filename based on character name
            output_path = os.path.join('characters', f"{self.properties['name'].replace(' ', '_')}_sheet.pdf")
            
            # Create a temporary FDF file with form field data
            field_data = {
                # Basic Information
                'CharacterName': self.properties['name'],
                'CharacterName 2': self.properties['name'],  # Character name on page 2
                'ClassLevel': ', '.join(f"{c['name']} {c['level']}" for c in self.properties['classes']),
                'Race ': f"{self.properties['race']} {self.properties.get('subrace', '')}".strip(),  # Note the space after 'Race'
                'Background': self.properties.get('background', ''),
                'Alignment': self.properties.get('alignment', ''),
                'XP': str(self.properties.get('experience', 0)),
                'ProfBonus': f"+{self.properties['proficiency_bonus']}",
                'Inspiration': '1' if self.properties.get('inspiration', False) else '0',
                
                # Ability scores and modifiers
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
                'CHamod': f"{self.get_ability_modifier('charisma'):+d}",
                
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
                'HPCurrent': str(self.properties['hit_points'].get('current', 0)),
                'HPTemp': str(self.properties['hit_points'].get('temporary', 0)),
            }

            # Format hit dice by consolidating identical dice
            hit_dice = self.properties.get('hit_dice', [])
            if hit_dice:
                hit_dice_counts = defaultdict(int)
                for die in hit_dice:
                    # Extract the die type (e.g., 'd10' from '1d10')
                    die_type = die.split('d')[1]
                    hit_dice_counts[die_type] += 1
                consolidated_hit_dice = []
                for die_type, count in hit_dice_counts.items():
                    consolidated_hit_dice.append(f"{count}d{die_type}")
                field_data['HD'] = ', '.join(consolidated_hit_dice)
                field_data['HDTotal'] = str(len(hit_dice))
            
            # Skills
            skill_bonuses = defaultdict(lambda: "+0")
            for skill, proficient in self.properties['skills'].items():
                # Determine ability modifier for skill
                ability = self._get_skill_ability(skill)
                bonus = self.get_ability_modifier(ability)
                if proficient:
                    bonus += self.properties['proficiency_bonus']
                skill_bonuses[skill] = f"{bonus:+d}"
            
            # Other proficiencies and languages
            field_data['ProficienciesLang'] = '\n'.join([
                'Languages: ' + ', '.join(self.properties['proficiencies']['languages']),
                'Armor: ' + ', '.join(self.properties['proficiencies']['armor']),
                'Weapons: ' + ', '.join(self.properties['proficiencies']['weapons']),
                'Tools: ' + ', '.join(self.properties['proficiencies']['tools'])
            ])
            
            # Features & Traits - Split between pages
            core_features = []
            additional_features = []

            # Sort features by importance/frequency of use
            for trait in self.properties.get('traits', []):
                if any(keyword in trait['name'].lower() for keyword in ['darkvision', 'resistance', 'proficiency', 'save', 'armor', 'weapon']):
                    core_features.append(f"{trait['name']}: {trait['description']}")
                else:
                    additional_features.append(f"{trait['name']}: {trait['description']}")

            for feature in self.properties.get('features', []):
                if any(keyword in feature['name'].lower() for keyword in ['spellcasting', 'attack', 'defense', 'proficiency', 'save']):
                    core_features.append(f"{feature['name']}: {feature['description']}")
                else:
                    additional_features.append(f"{feature['name']}: {feature['description']}")

            # Page 1: Core combat and frequently used features
            field_data['Features and Traits'] = '\n'.join([
                '=== Core Features ===',
                *core_features
            ])

            # Page 2: Additional features and detailed descriptions
            field_data['Feat+Traits'] = '\n'.join([
                '=== Additional Features ===',
                *additional_features
            ])
            
            # Add spellcasting information if the character has spellcasting ability
            if self.properties['spells']['spellcasting_ability']:
                ability = self.properties['spells']['spellcasting_ability']
                modifier = self.get_ability_modifier(ability)
                spell_save_dc = 8 + self.properties['proficiency_bonus'] + modifier
                spell_attack_bonus = modifier + self.properties['proficiency_bonus']
                
                # Get the spellcasting class
                spellcasting_class = next((c['name'] for c in self.properties['classes'] 
                                        if any('spellcasting' in f.get('name', '').lower() 
                                              for f in self.properties.get('features', []))), '')
                
                # Add spellcasting fields
                field_data.update({
                    'Spellcasting Class 2': spellcasting_class,
                    'SpellcastingAbility 2': ability.capitalize(),
                    'SpellSaveDC  2': str(spell_save_dc),
                    'SpellAtkBonus 2': f"+{spell_attack_bonus}"
                })
                
                # Add spell slots if any
                spell_slots = self.properties['spells']['spell_slots']
                if isinstance(spell_slots, dict):
                    # Get the spell slots from the character's spellcasting class data
                    for level, slots in spell_slots.items():
                        try:
                            level_num = int(level)
                            field_num = 18 + level_num  # Convert spell level to field number (19 for level 1, 20 for level 2, etc.)
                            
                            # Just show the total number in the first field
                            if slots > 0:
                                field_data[f'SlotsTotal {field_num}'] = str(slots)
                            
                            # Don't populate the SlotsRemaining field - let the user mark off used slots manually
                            
                        except (ValueError, TypeError) as e:
                            logger.warning(f"Failed to process spell slots for level {level}: {e}")
                            continue
            
            # Create a temporary file for the FDF data
            with tempfile.NamedTemporaryFile(mode='w', suffix='.fdf', delete=False) as fdf_file:
                fdf_file.write("%FDF-1.2\n")
                fdf_file.write("1 0 obj\n")
                fdf_file.write("<<\n")
                fdf_file.write("/FDF\n")
                fdf_file.write("<<\n")
                fdf_file.write("/Fields [\n")
                for field_name, value in field_data.items():
                    fdf_file.write("<<\n")
                    fdf_file.write(f"/T ({field_name})\n")
                    fdf_file.write(f"/V ({value})\n")
                    fdf_file.write(">>\n")
                fdf_file.write("]\n")
                fdf_file.write(">>\n")
                fdf_file.write("trailer\n")
                fdf_file.write("<<\n")
                fdf_file.write("/Root 1 0 R\n")
                fdf_file.write(">>\n")
                fdf_file.write("%%EOF\n")
                fdf_path = fdf_file.name
            
            # Use pdftk to fill the form
            subprocess.run([
                'pdftk',
                template_path,
                'fill_form',
                fdf_path,
                'output',
                output_path,
                'flatten'
            ], check=True)
            
            # Clean up the temporary FDF file
            os.unlink(fdf_path)
            
            logger.info(f"Successfully exported character sheet to {output_path}")
            return output_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to run pdftk: {e}")
            raise CharacterError(f"Failed to export PDF character sheet: {e}")
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
        ability = self._get_skill_ability(skill)
        bonus = self.get_ability_modifier(ability)
        if self.properties['skills'].get(skill, False):
            bonus += self.properties['proficiency_bonus']
        return bonus





