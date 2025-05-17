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
    delete_character
)
from toon import Toon, CharacterError

@pytest.fixture
def mock_toon():
    """Fixture to create a mock Toon instance"""
    with patch('cli.Toon') as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        yield mock_instance

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

@pytest.mark.parametrize('command,args,expected_calls', [
    (
        'create',
        MagicMock(
            name='TestChar',
            race='Elf',
            subrace='High Elf',
            class_name='Wizard',
            level=1,
            abilities='{"strength": 10}',
            background=None,
            personality=None,
            export='text'
        ),
        ['set_name', 'set_race', 'set_ability_scores', 'add_class', 'save', 'export_character_sheet']
    ),
    (
        'load',
        MagicMock(
            filename='test_char',
            class_name='Fighter',
            level=2,
            export='text'
        ),
        ['add_class', 'save', 'export_character_sheet']
    )
])
def test_character_commands(mock_toon, command, args, expected_calls):
    """Test character creation and loading commands"""
    with patch('cli.sys.exit') as mock_exit:
        if command == 'create':
            create_character(args)
        else:
            load_character(args)
        
        # Verify the expected method calls were made
        for method in expected_calls:
            assert getattr(mock_toon, method).called
        
        # Verify sys.exit was not called
        mock_exit.assert_not_called()

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
    
    delete_character(args)
    mock_toon.delete_save.assert_called_once_with('test_char')

@pytest.mark.parametrize('user_inputs,expected_calls', [
    (
        [
            'TestChar',  # name
            'Elf',      # race
            'High Elf', # subrace
            '10',       # strength
            '15',       # dexterity
            '12',       # constitution
            '16',       # intelligence
            '13',       # wisdom
            '11',       # charisma
            'Wizard',   # class
            '1',        # level
            'acolyte',  # background
            'Trait 1',  # first personality trait
            'Trait 2',  # second personality trait
            'Ideal 1',  # ideal
            'Bond 1',   # bond
            'Flaw 1',   # flaw
            '',        # skip export
            'Exit'     # exit
        ],
        ['set_name', 'set_race', 'set_ability_scores', 'add_class', 'set_background', 'save']
    )
])
def test_interactive_create_character(mock_toon, user_inputs, expected_calls):
    """Test interactive character creation"""
    with patch('cli.prompt_user') as mock_prompt, \
         patch('cli.Background') as mock_background, \
         patch('cli.get_available_backgrounds', return_value=['acolyte']), \
         patch('cli.get_subraces', return_value=['High Elf']), \
         patch('cli.get_available_races', return_value=['Elf']), \
         patch('cli.get_available_classes', return_value=['Wizard']):
        mock_prompt.side_effect = user_inputs
        
        # Mock background data
        mock_bg_instance = MagicMock()
        mock_bg_instance.get_personality_options.return_value = {
            'personality_traits': {'count': 2, 'suggestions': ['Trait 1', 'Trait 2']},
            'ideals': {'suggestions': [{'ideal': 'Ideal 1', 'alignment': 'Good'}]},
            'bonds': {'suggestions': ['Bond 1']},
            'flaws': {'suggestions': ['Flaw 1']}
        }
        mock_background.return_value = mock_bg_instance
        
        # Mock save to return a filename
        mock_toon.save.return_value = 'test_char.json'
        
        interactive_create_character()
        
        # Verify character creation steps
        for method in expected_calls:
            assert getattr(mock_toon, method).called

def test_interactive_load_character(mock_toon):
    """Test interactive character loading"""
    mock_chars = [{'name': 'Test1', 'filename': 'test1.json'}]
    
    with patch('cli.Toon.list_saved_characters', return_value=mock_chars), \
         patch('cli.prompt_user') as mock_prompt:
        
        mock_prompt.side_effect = ['Test1 (test1.json)', 'n', '']
        interactive_load_character()
        
        # Verify character was loaded
        assert mock_toon.get_name.called

def test_interactive_delete_character(mock_toon):
    """Test interactive character deletion"""
    mock_chars = [{'name': 'Test1', 'filename': 'test1.json'}]
    
    with patch('cli.Toon.list_saved_characters', return_value=mock_chars), \
         patch('cli.prompt_user') as mock_prompt:
        
        mock_prompt.side_effect = ['Test1 (test1.json)', 'y']
        interactive_delete_character()
        
        # Verify deletion was attempted
        assert mock_toon.delete_save.called

def test_error_handling():
    """Test error handling in CLI functions"""
    with patch('cli.Toon') as mock_toon:
        mock_toon.side_effect = CharacterError("Test error")
        with pytest.raises(SystemExit) as exc_info:
            create_character(MagicMock(name='Test', race='Invalid'))
        assert exc_info.value.code == 1

def test_error_handling_without_exit():
    """Test error handling without system exit"""
    with patch('cli.Toon') as mock_toon, \
         patch('cli.sys.exit') as mock_exit:
        mock_toon.side_effect = CharacterError("Test error")
        create_character(MagicMock(name='Test', race='Invalid'))
        mock_exit.assert_called_once_with(1)

def test_invalid_ability_scores():
    """Test handling of invalid ability scores JSON"""
    with patch('cli.Toon') as mock_toon, \
         patch('cli.sys.exit') as mock_exit:
        args = MagicMock(
            name='Test',
            race='Elf',
            subrace=None,
            abilities='invalid json',
            class_name=None,
            level=None,
            background=None,
            personality=None,
            export=None
        )
        
        create_character(args)
        
        # Verify sys.exit was called once with error code 1
        mock_exit.assert_called_once_with(1)
        
        # Verify no background-related calls were made
        mock_toon_instance = mock_toon.return_value
        assert not mock_toon_instance.set_background.called

@pytest.mark.parametrize('export_format,expected_output', [
    ('text', """=== Test Character ===
Race: Elf High Elf
Level: 1
Classes: Wizard 1

Ability Scores:
Strength: 10 (+0)
Dexterity: 15 (+2)
Constitution: 12 (+1)
Intelligence: 16 (+3)
Wisdom: 13 (+1)
Charisma: 11 (+0)"""),
    ('json', '{"name": "Test Character", "race": "Elf", "subrace": "High Elf", "level": 1}'),
    ('html', '<!DOCTYPE html>\n<html>\n<head>\n    <title>Test Character - Character Sheet</title>'),
    ('pdf', 'characters/Test_Character_sheet.pdf')
])
def test_character_export(mock_toon, sample_character_data, export_format, expected_output):
    """Test character export in different formats"""
    # Mock the export_character_sheet method to return format-specific output
    mock_toon.export_character_sheet.return_value = expected_output
    
    # Create args with export format
    args = MagicMock(
        name=sample_character_data['name'],
        race=sample_character_data['race'],
        subrace=sample_character_data['subrace'],
        class_name='Wizard',
        level=1,
        abilities=json.dumps(sample_character_data['stats']),
        background=None,
        personality=None,
        export=export_format
    )
    
    # Capture stdout to verify output
    with patch('builtins.print') as mock_print, \
         patch('cli.sys.exit') as mock_exit:
        create_character(args)
        
        # Verify character was created and exported
        mock_toon.set_name.assert_called_with(args.name)
        mock_toon.set_race.assert_called_with(args.race, args.subrace)
        mock_toon.add_class.assert_called_with(args.class_name, args.level)
        mock_toon.export_character_sheet.assert_called_with(format=export_format)
        
        # Verify sys.exit was not called
        mock_exit.assert_not_called()

def test_export_error_handling(mock_toon):
    """Test error handling during export"""
    # Mock export to raise an error
    mock_toon.export_character_sheet.side_effect = CharacterError("Export failed")
    
    args = MagicMock(
        name='Test',
        race='Elf',
        subrace=None,
        class_name='Wizard',
        level=1,
        abilities='{"strength": 10}',
        export='html'
    )
    
    with patch('cli.sys.exit') as mock_exit:
        create_character(args)
        mock_exit.assert_called_once_with(1)

def test_interactive_export(mock_toon):
    """Test interactive export functionality"""
    # Mock user inputs for character creation and export
    user_inputs = [
        'TestChar',  # name
        'Elf',      # race
        'High Elf', # subrace
        '10',       # strength
        '15',       # dexterity
        '12',       # constitution
        '16',       # intelligence
        '13',       # wisdom
        '11',       # charisma
        'Wizard',   # class
        '1',        # level
        'acolyte',  # background
        'Trait 1',  # first personality trait
        'Trait 2',  # second personality trait
        'Ideal 1',  # ideal
        'Bond 1',   # bond
        'Flaw 1',   # flaw
        'text',     # export format
        ''         # skip further exports
    ]
    
    with patch('cli.prompt_user') as mock_prompt, \
         patch('cli.sys.exit') as mock_exit, \
         patch('cli.Background') as mock_background, \
         patch('cli.get_available_backgrounds', return_value=['acolyte']), \
         patch('cli.get_subraces', return_value=['High Elf']), \
         patch('cli.get_available_races', return_value=['Elf']), \
         patch('cli.get_available_classes', return_value=['Wizard']):
        mock_prompt.side_effect = user_inputs
        mock_toon.export_character_sheet.return_value = '=== Test Character ==='
        mock_toon.save.return_value = 'test_char.json'
        
        # Mock background data
        mock_bg_instance = MagicMock()
        mock_bg_instance.get_personality_options.return_value = {
            'personality_traits': {'count': 2, 'suggestions': ['Trait 1', 'Trait 2']},
            'ideals': {'suggestions': [{'ideal': 'Ideal 1', 'alignment': 'Good'}]},
            'bonds': {'suggestions': ['Bond 1']},
            'flaws': {'suggestions': ['Flaw 1']}
        }
        mock_background.return_value = mock_bg_instance
        
        interactive_create_character()
        
        # Verify character was created with correct attributes
        mock_toon.set_name.assert_called_with('TestChar')
        mock_toon.set_race.assert_called_with('Elf', 'High Elf')
        mock_toon.add_class.assert_called_with('Wizard', 1)
        mock_toon.set_background.assert_called_with('acolyte', {
            'traits': ['Trait 1', 'Trait 2'],
            'ideal': 'Ideal 1',
            'bond': 'Bond 1',
            'flaw': 'Flaw 1'
        })
        mock_toon.save.assert_called()
        mock_toon.export_character_sheet.assert_called_with(format='text')
        
        # Verify sys.exit was not called
        mock_exit.assert_not_called() 