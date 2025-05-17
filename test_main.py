import unittest
from file_functions import save_file, open_file, list_files, remove_file
from os import listdir, remove
from toon import Toon, DiceRoll, CharacterError
import json
import io
import sys
from logging_config import setup_logging, get_logger
import os

# Set up logging before tests
setup_logging()
logger = get_logger(__name__)

class SuppressOutput:
    """Context manager to suppress stdout/stderr output"""
    def __init__(self):
        self.stdout = None
        self.stderr = None

    def __enter__(self):
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self.stdout
        sys.stderr = self.stderr

class TestFileFunctions(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.test_data = {
            'name': 'test',
            'a': 1,
            'b': 2,
            'c': 3
        }
        self.test_dir = "testing/"
        self.output_suppressor = SuppressOutput()

    def test_save_file(self):
        """Test saving files with various data types and sizes"""
        test_cases = [
            (self.test_data, "basic_save"),
            ({}, "empty_save"),
            ({'nested': {'data': True}}, "nested_save")
        ]
        
        with self.output_suppressor:
            for data, filename in test_cases:
                with self.subTest(case=filename):
                    save_file(data, "test", filename)
                    self.assertTrue(f"{filename}.json" in [f for f in listdir(self.test_dir) if f.endswith("json")])
    
    def test_open_file(self):
        """Test opening files with various scenarios"""
        with self.output_suppressor:
            # Test normal open
            save_file(self.test_data, "test", "openfiletest")
            loaded_data = open_file("openfiletest", "test")
            self.assertEqual(loaded_data, self.test_data)
            
            # Test opening non-existent file
            with self.assertRaises(FileNotFoundError):
                open_file("nonexistent", "test")

    def test_list_files(self):
        """Test file listing with different extensions and directories"""
        with self.output_suppressor:
            # Test JSON files
            save_file(self.test_data, "test", "listfiletest")
            files = list_files("test", "json")
            self.assertTrue("listfiletest.json" in files)
            
            # Test empty directory
            empty_dir_files = list_files("test", "nonexistent")
            self.assertEqual(len(empty_dir_files), 0)

    def test_remove_file(self):
        """Test file removal with various scenarios"""
        with self.output_suppressor:
            # Test successful removal
            save_file(self.test_data, "test", "remove")
            self.assertTrue(remove_file("remove.json", "test"))
            
            # Test removing non-existent file
            self.assertFalse(remove_file("nonexistent.json", "test"))

    def tearDown(self):
        """Clean up test files"""
        with self.output_suppressor:
            try:
                for file in [f for f in listdir(self.test_dir) if f.endswith("json")]:
                    remove(f"{self.test_dir}{file}")
            except OSError as e:
                print(f"Cleanup error: {e}")
            return super().tearDown()
          
class TestDiceRoll(unittest.TestCase):
    """Test the DiceRoll utility class"""
    
    def test_basic_roll(self):
        """Test basic dice rolls"""
        # Test single die
        result = DiceRoll.roll("1d6")
        self.assertTrue(1 <= result <= 6)
        
        # Test multiple dice
        result = DiceRoll.roll("2d6")
        self.assertTrue(2 <= result <= 12)
        
        # Test with modifier
        result = DiceRoll.roll("1d6+2")
        self.assertTrue(3 <= result <= 8)
        
        # Test negative modifier
        result = DiceRoll.roll("1d6-1")
        self.assertTrue(0 <= result <= 5)

    def test_invalid_dice(self):
        """Test invalid dice notation"""
        with self.assertRaises(ValueError):
            DiceRoll.roll("invalid")
        with self.assertRaises(ValueError):
            DiceRoll.roll("d")
        with self.assertRaises(ValueError):
            DiceRoll.roll("1d")
        with self.assertRaises(ValueError):
            DiceRoll.roll("d20")

class TestToonConfig(unittest.TestCase):
    def setUp(self):
        """Set up test character"""
        self.toon = Toon()
        self.output_suppressor = SuppressOutput()

    def test_race_setup(self):
        """Test race selection and trait application"""
        with self.output_suppressor:
            # Test basic race selection
            self.toon.set_race("elf")
            self.assertEqual(self.toon.properties["race"], "Elf")
            self.assertEqual(self.toon.properties["speed"], 30)
            self.assertEqual(self.toon.properties["stats"]["dexterity"], 2)
            
            # Check racial traits
            trait_names = [t["name"] for t in self.toon.properties["traits"]]
            self.assertIn("Darkvision", trait_names)
            self.assertIn("Keen Senses", trait_names)
            self.assertIn("Fey Ancestry", trait_names)
            
            # Check languages
            self.assertIn("Common", self.toon.properties["proficiencies"]["languages"])
            self.assertIn("Elvish", self.toon.properties["proficiencies"]["languages"])

    def test_subrace_setup(self):
        """Test subrace selection and trait application"""
        with self.output_suppressor:
            self.toon.set_race("elf", "High Elf")
            
            # Check subrace ability score
            self.assertEqual(self.toon.properties["stats"]["intelligence"], 1)
            
            # Check subrace traits
            trait_names = [t["name"] for t in self.toon.properties["traits"]]
            self.assertIn("Elf Weapon Training", trait_names)
            self.assertIn("Cantrip", trait_names)
            
            # Check weapon proficiencies
            weapons = self.toon.properties["proficiencies"]["weapons"]
            self.assertIn("longsword", weapons)
            self.assertIn("shortbow", weapons)

    def test_class_setup(self):
        """Test class selection and feature application"""
        with self.output_suppressor:
            self.toon.add_class("wizard", 1)
            
            # Check basic class properties
            self.assertEqual(len(self.toon.properties["classes"]), 1)
            self.assertEqual(self.toon.properties["classes"][0]["name"], "Wizard")
            self.assertEqual(self.toon.properties["classes"][0]["level"], 1)
            
            # Check hit dice
            self.assertEqual(len(self.toon.properties["hit_dice"]), 1)
            self.assertEqual(self.toon.properties["hit_dice"][0], "1d6")
            
            # Check saving throws
            self.assertTrue(self.toon.properties["saving_throws"]["intelligence"])
            self.assertTrue(self.toon.properties["saving_throws"]["wisdom"])
            
            # Check weapon proficiencies
            weapons = self.toon.properties["proficiencies"]["weapons"]
            self.assertIn("dagger", weapons)
            self.assertIn("quarterstaff", weapons)
            
            # Check spellcasting
            self.assertEqual(self.toon.properties["spells"]["spellcasting_ability"], "intelligence")
            self.assertEqual(len(self.toon.properties["spells"]["cantrips"]), 3)
            self.assertEqual(self.toon.properties["spells"]["spell_slots"]["1"], 2)

    def test_multiclass(self):
        """Test multiclassing functionality"""
        with self.output_suppressor:
            # Add first class
            self.toon.add_class("wizard", 1)
            
            # Add second class
            self.toon.add_class("wizard", 2)
            
            # Check levels
            self.assertEqual(self.toon.properties["level"], 3)
            self.assertEqual(len(self.toon.properties["hit_dice"]), 3)
            
            # Check proficiency bonus scaling
            self.assertEqual(self.toon.properties["proficiency_bonus"], 2)

    def test_ability_scores(self):
        """Test ability score setting and calculations"""
        with self.output_suppressor:
            scores = {
                "strength": 15,
                "dexterity": 14,
                "constitution": 13,
                "intelligence": 12,
                "wisdom": 10,
                "charisma": 8
            }
            self.toon.set_ability_scores(scores)
            
            # Test ability modifiers
            self.assertEqual(self.toon.get_ability_modifier("strength"), 2)
            self.assertEqual(self.toon.get_ability_modifier("dexterity"), 2)
            self.assertEqual(self.toon.get_ability_modifier("wisdom"), 0)
            self.assertEqual(self.toon.get_ability_modifier("charisma"), -1)
            
            # Test dependent values
            self.assertEqual(self.toon.properties["initiative"], 2)
            self.assertEqual(self.toon.properties["armor_class"], 12)  # 10 + DEX mod

    def test_saving_throws(self):
        """Test saving throw calculations"""
        with self.output_suppressor:
            # Set up a character with some saving throw proficiencies
            self.toon.set_ability_scores({
                "strength": 15,
                "dexterity": 14,
                "constitution": 13,
                "intelligence": 12,
                "wisdom": 10,
                "charisma": 8
            })
            self.toon.add_class("wizard", 1)  # Gives INT and WIS saving throw proficiency
            
            # Test proficient saves
            self.assertEqual(self.toon.get_saving_throw_bonus("intelligence"), 3)  # +1 ability, +2 prof
            self.assertEqual(self.toon.get_saving_throw_bonus("wisdom"), 2)  # +0 ability, +2 prof
            
            # Test non-proficient saves
            self.assertEqual(self.toon.get_saving_throw_bonus("strength"), 2)  # +2 ability, no prof
            self.assertEqual(self.toon.get_saving_throw_bonus("charisma"), -1)  # -1 ability, no prof

    def test_validation(self):
        """Test input validation"""
        with self.output_suppressor:
            # Test invalid race
            with self.assertRaises(ValueError):
                self.toon.set_race("invalid_race")
            
            # Test invalid subrace
            with self.assertRaises(ValueError):
                self.toon.set_race("elf", "invalid_subrace")
            
            # Test invalid class
            with self.assertRaises(ValueError):
                self.toon.add_class("invalid_class", 1)
            
            # Test invalid level
            with self.assertRaises(ValueError):
                self.toon.add_class("wizard", 0)
            with self.assertRaises(ValueError):
                self.toon.add_class("wizard", 21)
            
            # Test invalid ability scores
            with self.assertRaises(ValueError):
                self.toon.set_ability_scores({"strength": 25})
            with self.assertRaises(ValueError):
                self.toon.set_ability_scores({"invalid_ability": 10})

    def tearDown(self):
        """Clean up test character"""
        self.toon = None

class TestCharacterManagement(unittest.TestCase):
    """Test character management features"""
    
    def setUp(self):
        """Set up test character"""
        self.output_suppressor = SuppressOutput()
        self.toon = Toon()
        self.toon.set_name("TestCharacter")
        self.toon.set_race("elf", "High Elf")
        self.toon.add_class("wizard", 1)
        self.toon.set_ability_scores({
            "strength": 10,
            "dexterity": 12,
            "constitution": 14,
            "intelligence": 16,
            "wisdom": 13,
            "charisma": 8
        })

    def test_save_load(self):
        """Test saving and loading characters"""
        with self.output_suppressor:
            # Test basic save
            filename = self.toon.save()
            self.assertTrue(filename.startswith("testcharacter_"))
            
            # Test load
            loaded_toon = Toon(load_from=filename)
            self.assertEqual(loaded_toon.get_name(), "TestCharacter")
            self.assertEqual(loaded_toon.properties["race"], "Elf")
            self.assertEqual(loaded_toon.properties["subrace"], "High Elf")
            
            # Clean up
            self.toon.delete_save(filename)

    def test_lightfoot_halfling_creation(self):
        """Test creating a Lightfoot Halfling character with racial traits"""
        with self.output_suppressor:
            halfling = Toon()
            halfling.set_name("Bilbo")
            halfling.set_race("halfling", "Lightfoot")
            halfling.set_ability_scores({
                "strength": 10,
                "dexterity": 16,  # Base 14 + 2 from Halfling
                "constitution": 12,
                "intelligence": 14,
                "wisdom": 13,
                "charisma": 15  # Base 14 + 1 from Lightfoot
            })
            halfling.add_class("rogue", 1)

            # Test racial ability score bonuses
            self.assertEqual(halfling.properties["stats"]["dexterity"], 16)
            self.assertEqual(halfling.properties["stats"]["charisma"], 15)

            # Test size and speed
            self.assertEqual(halfling.properties["size"]["category"], "Small")
            self.assertEqual(halfling.properties["speed"], 25)

            # Test languages
            self.assertTrue("Common" in halfling.properties["proficiencies"]["languages"])
            self.assertTrue("Halfling" in halfling.properties["proficiencies"]["languages"])

            # Test traits
            trait_names = [t["name"] for t in halfling.properties["traits"]]
            self.assertIn("Lucky", trait_names)
            self.assertIn("Brave", trait_names)
            self.assertIn("Halfling Nimbleness", trait_names)
            self.assertIn("Naturally Stealthy", trait_names)

    def test_mountain_dwarf_creation(self):
        """Test creating a Mountain Dwarf character with racial traits"""
        with self.output_suppressor:
            mountain_dwarf = Toon()
            mountain_dwarf.set_name("Thorin")
            mountain_dwarf.set_race("dwarf", "Mountain Dwarf")
            mountain_dwarf.set_ability_scores({
                "strength": 17,  # Base 15 + 2 from Mountain Dwarf
                "dexterity": 12,
                "constitution": 16,  # Base 14 + 2 from Dwarf
                "intelligence": 10,
                "wisdom": 13,
                "charisma": 8
            })
            mountain_dwarf.add_class("fighter", 1)

            # Test racial ability score bonuses
            self.assertEqual(mountain_dwarf.properties["stats"]["strength"], 17)
            self.assertEqual(mountain_dwarf.properties["stats"]["constitution"], 16)

            # Test speed (Dwarves have 25 ft. speed)
            self.assertEqual(mountain_dwarf.properties["speed"], 25)

            # Test weapon proficiencies from Dwarven Combat Training
            self.assertTrue("battleaxe" in mountain_dwarf.properties["proficiencies"]["weapons"])
            self.assertTrue("handaxe" in mountain_dwarf.properties["proficiencies"]["weapons"])
            self.assertTrue("light hammer" in mountain_dwarf.properties["proficiencies"]["weapons"])
            self.assertTrue("warhammer" in mountain_dwarf.properties["proficiencies"]["weapons"])

            # Test armor proficiencies from Mountain Dwarf
            self.assertTrue("light armor" in mountain_dwarf.properties["proficiencies"]["armor"])
            self.assertTrue("medium armor" in mountain_dwarf.properties["proficiencies"]["armor"])

            # Test languages
            self.assertTrue("Common" in mountain_dwarf.properties["proficiencies"]["languages"])
            self.assertTrue("Dwarvish" in mountain_dwarf.properties["proficiencies"]["languages"])

            # Test traits
            trait_names = [t["name"] for t in mountain_dwarf.properties["traits"]]
            self.assertIn("Darkvision", trait_names)
            self.assertIn("Dwarven Resilience", trait_names)
            self.assertIn("Stonecunning", trait_names)
            self.assertIn("Dwarven Combat Training", trait_names)
            self.assertIn("Dwarven Armor Training", trait_names)

    def test_wood_elf_creation(self):
        """Test creating a Wood Elf character with racial traits"""
        with self.output_suppressor:
            wood_elf = Toon()
            wood_elf.set_name("Legolas")
            wood_elf.set_race("elf", "Wood Elf")
            wood_elf.set_ability_scores({
                "strength": 12,
                "dexterity": 16,  # Base 14 + 2 from Elf
                "constitution": 13,
                "intelligence": 10,
                "wisdom": 15,  # Base 14 + 1 from Wood Elf
                "charisma": 11
            })
            wood_elf.add_class("ranger", 1)

            # Test racial ability score bonuses
            self.assertEqual(wood_elf.properties["stats"]["dexterity"], 16)
            self.assertEqual(wood_elf.properties["stats"]["wisdom"], 15)

            # Test speed (Wood Elf has 35 ft. speed)
            self.assertEqual(wood_elf.properties["speed"], 35)

            # Test weapon proficiencies
            self.assertTrue("longsword" in wood_elf.properties["proficiencies"]["weapons"])
            self.assertTrue("shortbow" in wood_elf.properties["proficiencies"]["weapons"])
            self.assertTrue("longbow" in wood_elf.properties["proficiencies"]["weapons"])

            # Test skill proficiencies
            self.assertTrue("perception" in wood_elf.properties["skills"])

    def test_list_characters(self):
        """Test listing saved characters"""
        with self.output_suppressor:
            # Save a character
            filename = self.toon.save()
            
            # List characters
            characters = Toon.list_saved_characters()
            self.assertTrue(len(characters) > 0)
            
            # Verify character info
            char_info = next(c for c in characters if c["filename"].startswith(filename))
            self.assertEqual(char_info["name"], "TestCharacter")
            self.assertEqual(char_info["race"], "Elf High Elf")
            self.assertEqual(char_info["level"], 1)
            self.assertEqual(char_info["classes"], ["Wizard 1"])
            
            # Clean up
            self.toon.delete_save(filename)

    def test_backup(self):
        """Test character backup functionality"""
        with self.output_suppressor:
            # Create backup
            backup_filename = self.toon.create_backup()
            self.assertTrue("backup" in backup_filename)
            
            # Verify backup can be loaded
            backup_toon = Toon(load_from=backup_filename)
            self.assertEqual(backup_toon.get_name(), "TestCharacter")
            
            # Clean up
            self.toon.delete_save(backup_filename)

    def test_export(self):
        """Test character sheet export"""
        with self.output_suppressor:
            # Test JSON export
            json_sheet = self.toon.export_character_sheet("json")
            self.assertTrue(isinstance(json_sheet, str))
            self.assertTrue("TestCharacter" in json_sheet)

            # Test text export
            text_sheet = self.toon.export_character_sheet("text")
            self.assertTrue("=== TestCharacter ===" in text_sheet)
            self.assertTrue("Race: Elf High Elf" in text_sheet)
            self.assertTrue("Classes: Wizard 1" in text_sheet)

            # Test HTML export
            html_file_path = self.toon.export_character_sheet("html")
            self.assertTrue(os.path.exists(html_file_path))
            with open(html_file_path, 'r') as f:
                html_content = f.read()
            self.assertTrue("<html>" in html_content)
            self.assertTrue("TestCharacter" in html_content)
            os.remove(html_file_path)  # Clean up the test file

    def test_metadata(self):
        """Test character metadata tracking"""
        with self.output_suppressor:
            # Save character
            filename = self.toon.save()
            
            # Load and check metadata
            loaded_toon = Toon(load_from=filename)
            metadata = loaded_toon.properties["metadata"]
            self.assertTrue("created_at" in metadata)
            self.assertTrue("last_modified" in metadata)
            self.assertEqual(metadata["version"], "1.0")
            self.assertEqual(metadata["save_count"], 1)
            
            # Clean up
            self.toon.delete_save(filename)

    def test_error_handling(self):
        """Test error handling in character management"""
        with self.output_suppressor:
            # Test invalid save (no name)
            unnamed_toon = Toon()
            with self.assertRaises(CharacterError):
                unnamed_toon.save()
            
            # Test loading non-existent character
            with self.assertRaises(CharacterError):
                Toon(load_from="nonexistent_character")
            
            # Test invalid export format
            with self.assertRaises(CharacterError):
                self.toon.export_character_sheet("invalid_format")

    def tearDown(self):
        """Clean up test files"""
        try:
            # Clean up any remaining test files
            for filename in list_files("characters", "json"):
                if "testcharacter" in filename.lower() or "backup" in filename.lower():
                    remove_file(filename, "characters")
        except Exception as e:
            print(f"Cleanup error: {e}")
        self.toon = None

if __name__ == '__main__':
    unittest.main(verbosity=2)  # Added verbosity for better test output