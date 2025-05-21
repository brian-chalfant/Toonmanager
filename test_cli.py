import pytest
from unittest.mock import patch, MagicMock
import json
import os
from cli import (
    prompt_user,
    get_available_races,
    get_available_classes,
    get_subraces,
    interactive_create_character,
    interactive_load_character,
    interactive_delete_character,
    create_character,
    load_character,
    list_characters,
    delete_character,
    handle_pending_choices
)
from toon import Toon, CharacterError

@pytest.fixture
def mock_toon():
    """Create a mock Toon object for testing"""
    mock = MagicMock()
    # Set up properties as a regular dict instead of a MagicMock
    mock.properties = {}
    # Set up methods to actually modify the properties dict
    def set_subclass(class_name, subclass):
        mock.properties["subclass"] = {class_name: subclass}
    mock.set_subclass.side_effect = set_subclass
    
    def set_ability_score(ability, value):
        if "stats" not in mock.properties:
            mock.properties["stats"] = {}
        mock.properties["stats"][ability] = value
    mock.set_ability_score.side_effect = set_ability_score
    
    def add_skill(skill):
        if "skills" not in mock.properties:
            mock.properties["skills"] = {}
        mock.properties["skills"][skill.lower()] = True
    mock.add_skill.side_effect = add_skill
    
    def add_equipment(items):
        if "equipment" not in mock.properties:
            mock.properties["equipment"] = []
        for item in items:
            mock.properties["equipment"].append({"item": item})
    mock.add_equipment.side_effect = add_equipment
    
    def add_language(language):
        if "proficiencies" not in mock.properties:
            mock.properties["proficiencies"] = {"languages": []}
        if "languages" not in mock.properties["proficiencies"]:
            mock.properties["proficiencies"]["languages"] = []
        mock.properties["proficiencies"]["languages"].append(language)
    mock.add_language.side_effect = add_language
    
    return mock

@pytest.fixture
def sample_character_data():
    """Fixture providing sample character data"""
    return {
        'name': 'Test Character',
        'race': 'Elf',
        'subrace': 'High Elf',
        'level': 1,
        'classes': [{'name': 'Wizard', 'level': 1}],
        'stats': {
            'strength': 10,
            'dexterity': 15,
            'constitution': 12,
            'intelligence': 16,
            'wisdom': 13,
            'charisma': 11
        }
    }

def test_prompt_user_with_choices():
    """Test prompt_user function with choices"""
    with patch('builtins.input', return_value='1'):
        result = prompt_user("Select option", ["Option 1", "Option 2"])
        assert result == "Option 1"

def test_prompt_user_without_choices():
    """Test prompt_user function without choices"""
    with patch('builtins.input', return_value='test input'):
        result = prompt_user("Enter value")
        assert result == "test input"

def test_get_available_races(tmp_path):
    """Test getting available races from data directory"""
    # Create temporary race files
    race_dir = tmp_path / "data" / "races"
    race_dir.mkdir(parents=True)
    (race_dir / "elf.json").touch()
    (race_dir / "dwarf.json").touch()
    
    with patch('cli.os.path.join', return_value=str(race_dir)):
        races = get_available_races()
        assert set(races) == {'elf', 'dwarf'}

def test_get_available_classes(tmp_path):
    """Test getting available classes from data directory"""
    # Create temporary class files
    class_dir = tmp_path / "data" / "classes"
    class_dir.mkdir(parents=True)
    (class_dir / "wizard.json").touch()
    (class_dir / "fighter.json").touch()
    
    with patch('cli.os.path.join', return_value=str(class_dir)):
        classes = get_available_classes()
        assert set(classes) == {'wizard', 'fighter'}

def test_get_subraces():
    """Test getting subraces for a race"""
    mock_race_data = {
        'subraces': [
            {'name': 'High Elf'},
            {'name': 'Wood Elf'}
        ]
    }
    
    with patch('builtins.open', create=True) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_race_data)
        subraces = get_subraces('elf')
        assert subraces == ['High Elf', 'Wood Elf']

def test_list_characters(capsys):
    """Test listing characters"""
    mock_chars = [
        {
            'name': 'Test1',
            'race': 'Elf',
            'level': 1,
            'classes': ['Wizard 1'],
            'filename': 'test1.json',
            'last_modified': '2024-01-01'
        }
    ]
    
    with patch('cli.Toon.list_saved_characters', return_value=mock_chars):
        list_characters(None)
        captured = capsys.readouterr()
        assert 'Test1' in captured.out
        assert 'Elf' in captured.out
        assert 'Wizard 1' in captured.out

def test_delete_character(mock_toon):
    """Test character deletion"""
    args = MagicMock(filename='test_char')
    mock_toon.delete_save.return_value = True
    with patch('cli.Toon', return_value=mock_toon):
        delete_character(args)
        mock_toon.delete_save.assert_called_once_with('test_char')

def test_handle_subclass_choices(mock_toon):
    """Test handling of subclass choices"""
    # Set up mock pending choices for subclass selection
    mock_toon.properties["pending_choices"] = {
        "subclass_wizard": {
            "type": "subclass",
            "class": "Wizard",
            "description": "Choose a Wizard subclass",
            "options": ["Evocation", "Divination"]
        }
    }
    
    # Set up has_pending_choices to return True first, then False after choice is handled
    mock_toon.has_pending_choices.side_effect = [True, False]
    mock_toon.get_pending_choices.return_value = mock_toon.properties["pending_choices"]
    
    with patch('cli.prompt_user', return_value="Evocation"):
        handle_pending_choices(mock_toon)
        
        # Verify subclass was set
        assert mock_toon.properties.get("subclass", {}).get("Wizard") == "Evocation"
        # Verify pending choice was removed
        assert "subclass_wizard" not in mock_toon.properties["pending_choices"]
        # Verify has_pending_choices was called twice (once for initial check, once after handling)
        assert mock_toon.has_pending_choices.call_count == 2

def test_handle_ability_score_improvement_one_ability_plus_two(mock_toon):
    """Test handling of ability score improvement: one ability +2"""
    mock_toon.properties["pending_choices"] = {
        "class_fighter_level_4_asi": {
            "type": "ability_score_improvement",
            "count": 2,
            "options": ["strength", "dexterity", "constitution"],
            "description": "Choose ability scores to improve"
        }
    }
    mock_toon.properties["stats"] = {
        "strength": 15,
        "dexterity": 14,
        "constitution": 13
    }
    mock_toon.has_pending_choices.side_effect = [True, False]
    mock_toon.get_pending_choices.return_value = mock_toon.properties["pending_choices"]
    with patch('cli.prompt_user', side_effect=["One ability +2", "strength"]):
        handle_pending_choices(mock_toon)
        assert mock_toon.properties["stats"]["strength"] == 17
        assert "class_fighter_level_4_asi" not in mock_toon.properties["pending_choices"]
        assert mock_toon.has_pending_choices.call_count == 2

def test_handle_ability_score_improvement_two_abilities_plus_one(mock_toon):
    """Test handling of ability score improvement: two abilities +1"""
    mock_toon.properties["pending_choices"] = {
        "class_fighter_level_4_asi": {
            "type": "ability_score_improvement",
            "count": 2,
            "options": ["strength", "dexterity", "constitution"],
            "description": "Choose ability scores to improve"
        }
    }
    mock_toon.properties["stats"] = {
        "strength": 15,
        "dexterity": 14,
        "constitution": 13
    }
    mock_toon.has_pending_choices.side_effect = [True, False]
    mock_toon.get_pending_choices.return_value = mock_toon.properties["pending_choices"]
    with patch('cli.prompt_user', side_effect=["Two abilities +1", "dexterity", "constitution"]):
        handle_pending_choices(mock_toon)
        assert mock_toon.properties["stats"]["dexterity"] == 15
        assert mock_toon.properties["stats"]["constitution"] == 14
        assert "class_fighter_level_4_asi" not in mock_toon.properties["pending_choices"]
        assert mock_toon.has_pending_choices.call_count == 2

def test_handle_skill_choices(mock_toon):
    """Test handling of skill proficiency choices"""
    # Set up mock pending choices for skill selection
    mock_toon.properties["pending_choices"] = {
        "class_rogue_skills": {
            "type": "skill",
            "count": 2,
            "options": ["Stealth", "Sleight of Hand", "Acrobatics"],
            "description": "Choose skills from your class list"
        }
    }
    mock_toon.properties["skills"] = {
        "stealth": False,
        "sleight of hand": False,
        "acrobatics": False
    }
    mock_toon.has_pending_choices.side_effect = [True, False]
    mock_toon.get_pending_choices.return_value = mock_toon.properties["pending_choices"]
    
    with patch('cli.prompt_user', side_effect=["Stealth", "Sleight of Hand"]):
        handle_pending_choices(mock_toon)
        assert mock_toon.properties["skills"]["stealth"] is True
        assert mock_toon.properties["skills"]["sleight of hand"] is True
        assert "class_rogue_skills" not in mock_toon.properties["pending_choices"]
        assert mock_toon.has_pending_choices.call_count == 2

def test_handle_equipment_choices(mock_toon):
    """Test handling of equipment choices"""
    # Set up mock pending choices for equipment selection
    mock_toon.properties["pending_choices"] = {
        "class_fighter_equipment_0": {
            "type": "equipment",
            "count": 1,
            "options": [["Longsword", "Shield"], ["Battleaxe", "Handaxe"]],
            "description": "Choose starting equipment"
        }
    }
    mock_toon.properties["equipment"] = []
    mock_toon.has_pending_choices.side_effect = [True, False]
    mock_toon.get_pending_choices.return_value = mock_toon.properties["pending_choices"]
    
    with patch('cli.prompt_user', return_value="1"):  # Choose first package
        handle_pending_choices(mock_toon)
        assert len(mock_toon.properties["equipment"]) == 2
        assert any(item["item"] == "Longsword" for item in mock_toon.properties["equipment"])
        assert any(item["item"] == "Shield" for item in mock_toon.properties["equipment"])
        assert "class_fighter_equipment_0" not in mock_toon.properties["pending_choices"]
        assert mock_toon.has_pending_choices.call_count == 2

def test_handle_language_choices(mock_toon):
    """Test handling of language choices"""
    # Set up mock pending choices for language selection
    mock_toon.properties["pending_choices"] = {
        "languages": {
            "count": 2,
            "type": "choice",
            "description": "Choose languages"
        }
    }
    mock_toon.properties["proficiencies"] = {"languages": ["Common"]}
    mock_toon.has_pending_choices.side_effect = [True, False]
    mock_toon.get_pending_choices.return_value = mock_toon.properties["pending_choices"]
    
    with patch('cli.prompt_user', side_effect=["Elvish", "Dwarvish"]):
        handle_pending_choices(mock_toon)
        assert "Elvish" in mock_toon.properties["proficiencies"]["languages"]
        assert "Dwarvish" in mock_toon.properties["proficiencies"]["languages"]
        assert "languages" not in mock_toon.properties["pending_choices"]
        assert mock_toon.has_pending_choices.call_count == 2

def test_handle_race_ability_scores(mock_toon):
    """Test handling of ability score choices from race"""
    # Set up mock pending choices for racial ability scores
    mock_toon.properties["pending_choices"] = {
        "ability_scores": {
            "count": 2,
            "bonus": 1,
            "from": ["dexterity", "intelligence"],
            "description": "Choose ability scores to increase"
        }
    }
    mock_toon.properties["stats"] = {
        "dexterity": 14,
        "intelligence": 13
    }
    mock_toon.has_pending_choices.side_effect = [True, False]
    mock_toon.get_pending_choices.return_value = mock_toon.properties["pending_choices"]
    
    with patch('cli.prompt_user', side_effect=["dexterity", "intelligence"]):
        handle_pending_choices(mock_toon)
        assert mock_toon.properties["stats"]["dexterity"] == 15
        assert mock_toon.properties["stats"]["intelligence"] == 14
        assert "ability_scores" not in mock_toon.properties["pending_choices"]
        assert mock_toon.has_pending_choices.call_count == 2

def test_handle_multiple_choice_types(mock_toon):
    """Test handling multiple types of choices in sequence"""
    # Set up multiple pending choices
    mock_toon.properties["pending_choices"] = {
        "subclass_wizard": {
            "type": "subclass",
            "class": "Wizard",
            "description": "Choose a Wizard subclass",
            "options": ["Evocation", "Divination"]
        },
        "class_wizard_skills": {
            "type": "skill",
            "count": 2,
            "options": ["Arcana", "History", "Investigation"],
            "description": "Choose skills"
        }
    }
    mock_toon.properties["skills"] = {
        "arcana": False,
        "history": False,
        "investigation": False
    }
    # Set up has_pending_choices to return True twice (once for each choice) then False
    mock_toon.has_pending_choices.side_effect = [True, True, False]
    mock_toon.get_pending_choices.return_value = mock_toon.properties["pending_choices"]
    
    with patch('cli.prompt_user', side_effect=["Evocation", "Arcana", "History"]):
        handle_pending_choices(mock_toon)
        # Verify subclass was set
        assert mock_toon.properties.get("subclass", {}).get("Wizard") == "Evocation"
        # Verify skills were set
        assert mock_toon.properties["skills"]["arcana"] is True
        assert mock_toon.properties["skills"]["history"] is True
        # Verify all pending choices were handled
        assert not mock_toon.properties["pending_choices"]
        # Verify has_pending_choices was called three times (twice for initial checks, once after handling)
        assert mock_toon.has_pending_choices.call_count == 3
