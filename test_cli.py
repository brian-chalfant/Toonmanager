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
    if command == 'create':
        create_character(args)
    else:
        load_character(args)
    
    # Verify the expected method calls were made
    for method in expected_calls:
        assert getattr(mock_toon, method).called

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
        ['TestChar', 'Elf', 'High Elf', '10', '15', '12', '16', '13', '11', 'Wizard', '1', '', 'Exit'],
        ['set_name', 'set_race', 'set_ability_scores', 'add_class', 'save']
    )
])
def test_interactive_create_character(mock_toon, user_inputs, expected_calls):
    """Test interactive character creation"""
    with patch('cli.prompt_user') as mock_prompt:
        mock_prompt.side_effect = user_inputs
        
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
            export=None
        )
        create_character(args)
        mock_exit.assert_called_once_with(1)

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
        export=export_format
    )
    
    # Capture stdout to verify output
    with patch('builtins.print') as mock_print:
        create_character(args)
        
        # Verify export was called with correct format
        mock_toon.export_character_sheet.assert_called_once_with(format=export_format)
        
        # Verify output was printed
        mock_print.assert_any_call(f"Character sheet exported in {export_format} format")
        if export_format == 'text':
            mock_print.assert_any_call(expected_output)

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
        'html',     # export format
    ]
    
    with patch('cli.prompt_user') as mock_prompt:
        mock_prompt.side_effect = user_inputs
        
        # Mock the export output
        mock_toon.export_character_sheet.return_value = '<!DOCTYPE html>'
        
        interactive_create_character()
        
        # Verify export was called with html format
        mock_toon.export_character_sheet.assert_called_once_with(format='html') 