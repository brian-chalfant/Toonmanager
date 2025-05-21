import pytest
import os
import json
from background import Background
from toon import Toon, CharacterError

@pytest.fixture
def test_background_data():
    """Create a test background data file"""
    data = {
        "name": "Test Background",
        "description": "A background for testing",
        "feature": {
            "name": "Test Feature",
            "description": "A feature for testing"
        },
        "proficiency_grants": {
            "skills": ["Stealth", "Deception"],
            "languages": {
                "count": 1,
                "type": "choice",
                "description": "One language of your choice"
            },
            "tools": ["Thieves' Tools"]
        },
        "equipment_grants": {
            "fixed": [
                {
                    "item": "Test Item",
                    "quantity": 2,
                    "description": "A test item"
                }
            ],
            "currency": {
                "gold": 10,
                "silver": 5
            }
        },
        "personality": {
            "personality_traits": {
                "suggestions": [
                    "Trait 1",
                    "Trait 2"
                ],
                "count": 2,
                "type": "choice"
            },
            "ideals": {
                "suggestions": [
                    {
                        "ideal": "Test Ideal",
                        "alignment": "Neutral"
                    }
                ],
                "count": 1,
                "type": "choice"
            },
            "bonds": {
                "suggestions": ["Test Bond"],
                "count": 1,
                "type": "choice"
            },
            "flaws": {
                "suggestions": ["Test Flaw"],
                "count": 1,
                "type": "choice"
            }
        }
    }
    
    # Ensure backgrounds directory exists
    os.makedirs(os.path.join("data", "backgrounds"), exist_ok=True)
    
    # Write test background file
    with open(os.path.join("data", "backgrounds", "test.json"), "w") as f:
        json.dump(data, f, indent=2)
    
    yield data
    
    # Cleanup
    try:
        os.remove(os.path.join("data", "backgrounds", "test.json"))
    except:
        pass

@pytest.fixture
def test_character():
    """Create a test character"""
    character = Toon()
    character.set_name("Test Character")
    return character

def test_background_loading(test_background_data):
    """Test loading a background from file"""
    background = Background("test")
    assert background.name == "test"
    assert background.data == test_background_data

def test_background_invalid_name():
    """Test loading a non-existent background"""
    with pytest.raises(ValueError, match="Invalid background: nonexistent"):
        Background("nonexistent")

def test_apply_proficiencies(test_background_data, test_character):
    """Test applying proficiency grants to a character"""
    background = Background("test")
    background._apply_proficiencies(test_character)
    
    # Check skill proficiencies
    assert test_character.properties["skills"]["stealth"] is True
    assert test_character.properties["skills"]["deception"] is True
    
    # Check tool proficiencies
    assert "Thieves' Tools" in test_character.properties["proficiencies"]["tools"]
    
    # Check language choice is pending
    assert "languages" in test_character.properties["pending_choices"]
    assert test_character.properties["pending_choices"]["languages"]["count"] == 1

def test_apply_equipment(test_background_data, test_character):
    """Test applying equipment grants to a character"""
    background = Background("test")
    background._apply_equipment(test_character)
    
    # Check fixed equipment
    equipment = test_character.properties["equipment"]
    test_item = next((item for item in equipment if item["item"] == "Test Item"), None)
    assert test_item is not None
    assert test_item["quantity"] == 2
    
    # Check currency
    assert test_character.properties["currency"]["gold"] == 10
    assert test_character.properties["currency"]["silver"] == 5

def test_apply_feature(test_background_data, test_character):
    """Test applying background feature to a character"""
    background = Background("test")
    background._apply_feature(test_character)
    
    # Check feature was added
    features = test_character.properties["features"]
    test_feature = next((f for f in features if f["name"] == "Test Feature"), None)
    assert test_feature is not None
    assert test_feature["source"] == "Background: test"

def test_get_personality_options(test_background_data):
    """Test retrieving personality options"""
    background = Background("test")
    options = background.get_personality_options()
    
    assert "personality_traits" in options
    assert options["personality_traits"]["count"] == 2
    assert "ideals" in options
    assert options["ideals"]["suggestions"][0]["ideal"] == "Test Ideal"

def test_apply_to_character(test_background_data, test_character):
    """Test applying entire background to a character"""
    background = Background("test")
    background.apply_to_character(test_character)
    
    # Check background name was set
    assert test_character.properties["background"] == "test"
    
    # Check proficiencies were applied
    assert test_character.properties["skills"]["stealth"] is True
    assert "Thieves' Tools" in test_character.properties["proficiencies"]["tools"]
    
    # Check equipment was added
    assert any(item["item"] == "Test Item" for item in test_character.properties["equipment"])
    assert test_character.properties["currency"]["gold"] == 10
    
    # Check feature was added
    assert any(f["name"] == "Test Feature" for f in test_character.properties["features"])

def test_list_available_backgrounds(test_background_data):
    """Test listing available backgrounds"""
    backgrounds = Background.list_available_backgrounds()
    assert "test" in backgrounds

def test_background_equipment_stacking(test_background_data, test_character):
    """Test that equipment quantities stack properly"""
    # Add initial equipment
    test_character.properties["equipment"].append({
        "item": "Test Item",
        "quantity": 3,
        "description": "Existing item"
    })
    
    background = Background("test")
    background._apply_equipment(test_character)
    
    # Check that quantities were added together
    test_item = next(item for item in test_character.properties["equipment"] 
                    if item["item"] == "Test Item")
    assert test_item["quantity"] == 5  # 3 existing + 2 from background

def test_background_currency_stacking(test_background_data, test_character):
    """Test that currency amounts stack properly"""
    # Add initial currency
    test_character.properties["currency"] = {
        "gold": 5,
        "silver": 10,
        "copper": 3
    }
    
    background = Background("test")
    background._apply_equipment(test_character)
    
    # Check that currency was added correctly
    assert test_character.properties["currency"]["gold"] == 15  # 5 existing + 10 from background
    assert test_character.properties["currency"]["silver"] == 15  # 10 existing + 5 from background
    assert test_character.properties["currency"]["copper"] == 3  # unchanged

def test_apply_personality_choices(test_background_data, test_character):
    """Test applying personality choices to a character"""
    background = Background("test")
    background.apply_to_character(test_character)
    
    # Apply personality choices
    choices = {
        "traits": ["Trait 1", "Trait 2"],
        "ideal": "Test Ideal",
        "bond": "Test Bond",
        "flaw": "Test Flaw"
    }
    
    test_character._apply_personality_choices(background, choices)
    
    # Check that choices were applied
    assert test_character.properties["personality"]["traits"] == choices["traits"]
    assert test_character.properties["personality"]["ideals"] == [choices["ideal"]]
    assert test_character.properties["personality"]["bonds"] == [choices["bond"]]
    assert test_character.properties["personality"]["flaws"] == [choices["flaw"]]
    
    # Check that pending choices were removed
    assert "personality" not in test_character.properties["pending_choices"]

def test_invalid_personality_choices(test_background_data, test_character):
    """Test applying invalid personality choices"""
    background = Background("test")
    background.apply_to_character(test_character)
    
    # Try to apply wrong number of traits
    with pytest.raises(CharacterError, match="Must choose exactly 2 personality traits"):
        test_character._apply_personality_choices(background, {
            "traits": ["Trait 1"],  # Should be 2 traits
            "ideal": "Test Ideal",
            "bond": "Test Bond",
            "flaw": "Test Flaw"
        }) 