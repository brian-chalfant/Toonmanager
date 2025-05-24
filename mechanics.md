# D&D 5E Class Mechanics Guide

This guide explains how to build custom `class.json` files using the standardized mechanics system for the D&D 5E Character Manager.

## Table of Contents

1. [Basic Class Structure](#basic-class-structure)
2. [Core Mechanic Types](#core-mechanic-types)
3. [Effect Types](#effect-types)
4. [Resource Management](#resource-management)
5. [Action Economy](#action-economy)
6. [Subclass Structure](#subclass-structure)
7. [Spellcasting Mechanics](#spellcasting-mechanics)
8. [Examples by Feature Type](#examples-by-feature-type)
9. [Best Practices](#best-practices)

## Basic Class Structure

Every class file must follow this basic structure:

```json
{
    "name": "Class Name",
    "description": "Brief description of the class",
    "hit_dice": "1d8",
    "primary_ability": ["main_stat"],
    "saving_throw_proficiencies": ["stat1", "stat2"],
    "armor_proficiencies": ["light armor", "medium armor"],
    "weapon_proficiencies": ["simple weapons"],
    "tool_proficiencies": [],
    "skill_proficiencies": {
        "choose": 2,
        "from": ["Skill1", "Skill2", "Skill3"]
    },
    "starting_equipment": {
        "choices": [
            {
                "choose": 1,
                "from": ["option1", "option2"]
            }
        ]
    },
    "features": {
        "1": [
            // Level 1 features
        ],
        "2": [
            // Level 2 features
        ]
        // ... continue for all 20 levels
    },
    "subclass_level": 3,
    "subclasses": [
        // Subclass definitions
    ],
    "version": "5E",
    "source": "PHB",
    "source_page": 70
}
```

## Core Mechanic Types

### 1. `passive`
For always-active features or simple effects.

```json
{
    "name": "Feature Name",
    "description": "Feature description",
    "mechanics": {
        "type": "passive",
        "effects": [
            {
                "type": "ac_bonus",
                "bonus": 1,
                "condition": "wearing_armor"
            }
        ]
    }
}
```

### 2. `resource`
For features with limited uses that recover on rest.

```json
{
    "name": "Limited Feature",
    "description": "Feature with limited uses",
    "mechanics": {
        "type": "resource",
        "action_type": "bonus_action",
        "uses": {
            "per_rest": "short",
            "amount": {
                "2": 2,
                "6": 3,
                "18": 4
            }
        },
        "effects": [
            {
                "type": "healing",
                "formula": "1d4 + charisma_modifier"
            }
        ]
    }
}
```

### 3. `choice`
For features that offer multiple options to choose from.

```json
{
    "name": "Fighting Style",
    "description": "Choose a fighting style",
    "mechanics": {
        "type": "choice",
        "choose": 1,
        "options": [
            {
                "name": "Option 1",
                "description": "First option",
                "effects": [
                    {
                        "type": "attack_roll_bonus",
                        "bonus": 2,
                        "weapon_type": "ranged"
                    }
                ]
            },
            {
                "name": "Option 2",
                "description": "Second option",
                "effects": [
                    {
                        "type": "ac_bonus",
                        "bonus": 1,
                        "condition": "wearing_armor"
                    }
                ]
            }
        ]
    }
}
```

### 4. `ability_score_improvement`
Standardized format for ASI features.

```json
{
    "name": "Ability Score Improvement",
    "description": "Increase ability scores",
    "mechanics": {
        "type": "ability_score_improvement",
        "options": [
            {
                "type": "single",
                "amount": 2
            },
            {
                "type": "double",
                "amount": 1
            }
        ],
        "max_score": 20
    }
}
```

### 5. `subclass_choice`
For subclass selection features.

```json
{
    "name": "Subclass Selection",
    "description": "Choose your path",
    "mechanics": {
        "type": "subclass_choice",
        "subclass_type": "tradition",
        "feature_levels": [2, 6, 10, 14]
    }
}
```

### 6. `passive_enhancement`
For features that improve existing abilities.

```json
{
    "name": "Improved Feature",
    "description": "Enhancement to existing feature",
    "mechanics": {
        "type": "passive_enhancement",
        "enhances": "Original Feature Name",
        "effect": {
            "type": "increase_uses",
            "new_amount": 3
        }
    }
}
```

### 7. `spellcasting`
For spellcasting abilities.

```json
{
    "name": "Spellcasting",
    "description": "Cast spells using ability",
    "mechanics": {
        "type": "spellcasting",
        "ability": "wisdom",
        "focus": ["holy symbol"],
        "preparation": "prepared",
        "ritual_casting": true,
        "spell_list": "cleric"
    }
}
```

## Effect Types

### Combat Effects

#### `damage_bonus`
```json
{
    "type": "damage_bonus",
    "bonus": 2,
    "weapon_type": "melee",
    "condition": "one_handed_no_other_weapons"
}
```

#### `attack_roll_bonus`
```json
{
    "type": "attack_roll_bonus",
    "bonus": 2,
    "weapon_type": "ranged"
}
```

#### `critical_hit_range`
```json
{
    "type": "critical_hit_range",
    "range": [19, 20]
}
```

#### `extra_attack`
```json
{
    "type": "extra_attack",
    "attacks": 2,
    "trigger": "attack_action"
}
```

### Defensive Effects

#### `ac_bonus`
```json
{
    "type": "ac_bonus",
    "bonus": 1,
    "condition": "wearing_armor"
}
```

#### `damage_resistance`
```json
{
    "type": "damage_resistance",
    "damage_types": ["bludgeoning", "piercing", "slashing"]
}
```

#### `saving_throw_bonus`
```json
{
    "type": "saving_throw_bonus",
    "bonus": "proficiency_bonus",
    "saves": ["wisdom", "charisma"]
}
```

### Utility Effects

#### `advantage`
```json
{
    "type": "advantage",
    "on": ["strength_checks", "strength_saves"]
}
```

#### `speed_increase`
```json
{
    "type": "speed_increase",
    "bonus": 10,
    "condition": "not_wearing_heavy_armor"
}
```

#### `healing`
```json
{
    "type": "healing",
    "formula": "1d10 + fighter_level"
}
```

### Skill and Proficiency Effects

#### `skill_proficiency`
```json
{
    "type": "skill_proficiency",
    "skills": ["Insight", "Medicine"]
}
```

#### `expertise`
```json
{
    "type": "expertise",
    "applies_to": "chosen_skills"
}
```

#### `tool_proficiency`
```json
{
    "type": "tool_proficiency",
    "tools": "thieves_tools"
}
```

## Resource Management

### Basic Resource Structure
```json
"uses": {
    "per_rest": "short",  // "short", "long", or "none"
    "amount": 2           // Fixed amount
}
```

### Scaling Resources
```json
"uses": {
    "per_rest": "long",
    "amount": {
        "1": 1,
        "6": 2,
        "18": 3
    }
}
```

### Formula-Based Resources
```json
"uses": {
    "per_rest": "long",
    "formula": "charisma_modifier",
    "minimum": 1
}
```

### Resource Recovery
```json
"recovery": {
    "type": "partial",
    "amount": "half_max_rounded_up",
    "rest_type": "short"
}
```

## Action Economy

### Action Types
- `"action"` - Full action
- `"bonus_action"` - Bonus action
- `"reaction"` - Reaction
- `"free"` - Free action/no action required
- `"1_minute"` - Takes 1 minute
- `"10_minutes"` - Takes 10 minutes
- `"1_hour"` - Takes 1 hour (rituals)

### Triggers and Conditions
```json
{
    "action_type": "reaction",
    "trigger": "hit_by_attack",
    "condition": "wearing_shield",
    "range": "5 feet"
}
```

### Frequency Limitations
```json
{
    "frequency": "once_per_turn",
    "restriction": "once_per_round"
}
```

## Subclass Structure

### Basic Subclass Format
```json
"subclasses": [
    {
        "name": "Subclass Name",
        "description": "Subclass description",
        "source": "PHB",
        "features": {
            "3": [
                {
                    "name": "Feature Name",
                    "description": "Feature description",
                    "mechanics": {
                        // Feature mechanics
                    }
                }
            ],
            "6": [
                // Level 6 features
            ]
        }
    }
]
```

### Feature Levels
Common subclass feature level patterns:
- **Casters (full)**: `[1, 6, 14, 18]`
- **Casters (half)**: `[3, 7, 15, 20]`
- **Martials**: `[3, 7, 10, 15, 18]`
- **Mixed**: `[2, 6, 10, 14]`

## Spellcasting Mechanics

### Full Caster
```json
{
    "type": "spellcasting",
    "ability": "wisdom",
    "focus": ["holy symbol"],
    "preparation": "prepared",
    "ritual_casting": true,
    "spell_list": "cleric"
}
```

### Half Caster
```json
{
    "type": "spellcasting",
    "ability": "charisma",
    "focus": ["holy symbol"],
    "preparation": "prepared",
    "ritual_casting": false,
    "spell_list": "paladin",
    "caster_level": "half"
}
```

### Unique Caster (Warlock)
```json
{
    "type": "spellcasting",
    "ability": "charisma",
    "focus": ["arcane focus"],
    "preparation": "known",
    "short_rest_recovery": true,
    "spell_slot_type": "pact_magic"
}
```

### Spellcasting Section
Include this section for spellcasters:

```json
"spellcasting": {
    "ability": "wisdom",
    "focus": ["holy symbol"],
    "spells_known": "prepared",
    "cantrips_known": {
        "1": 3,
        "4": 4,
        "10": 5
    },
    "spell_slots_per_level": {
        // Standard spell slot progression
    }
}
```

## Examples by Feature Type

### Limited Use Ability (Ki)
```json
{
    "name": "Ki",
    "description": "Harness your inner energy",
    "mechanics": {
        "type": "resource",
        "uses": {
            "per_rest": "short",
            "formula": "monk_level"
        },
        "abilities": [
            {
                "name": "Flurry of Blows",
                "description": "Make two unarmed strikes",
                "cost": 1,
                "action_type": "bonus_action",
                "trigger": "after_attack_action"
            }
        ]
    }
}
```

### Rage-like Feature
```json
{
    "name": "Rage",
    "description": "Enter a battle fury",
    "mechanics": {
        "type": "resource",
        "action_type": "bonus_action",
        "duration": {
            "value": 1,
            "unit": "minute"
        },
        "uses": {
            "per_rest": "long",
            "amount": {
                "1": 2,
                "3": 3,
                "6": 4
            }
        },
        "effects": [
            {
                "type": "damage_bonus",
                "bonus": {
                    "1": 2,
                    "9": 3,
                    "16": 4
                },
                "weapon_type": "strength_based"
            },
            {
                "type": "damage_resistance",
                "damage_types": ["bludgeoning", "piercing", "slashing"]
            }
        ],
        "conditions": [
            "Cannot cast spells",
            "Cannot be wearing heavy armor"
        ]
    }
}
```

### Channel Divinity
```json
{
    "name": "Channel Divinity",
    "description": "Channel divine energy",
    "mechanics": {
        "type": "resource",
        "uses": {
            "per_rest": "short",
            "amount": {
                "2": 1,
                "6": 2,
                "18": 3
            }
        },
        "effects": [
            {
                "name": "Turn Undead",
                "description": "Turn undead creatures",
                "action_type": "action",
                "range": "30 feet",
                "save_dc": "8 + proficiency + wisdom_modifier",
                "target": "undead_creatures"
            }
        ]
    }
}
```

### Metamagic-style Choices
```json
{
    "name": "Metamagic",
    "description": "Alter your spells",
    "mechanics": {
        "type": "choice",
        "choose": {
            "3": 2,
            "10": 1,
            "17": 1
        },
        "total": {
            "3": 2,
            "10": 3,
            "17": 4
        },
        "options": [
            {
                "name": "Careful Spell",
                "description": "Protect allies from spell effects",
                "cost": "1 sorcery point",
                "mechanics": {
                    "type": "spell_modification",
                    "effect": "exclude_allies_from_area"
                }
            }
        ]
    }
}
```

## Best Practices

### 1. Consistency
- Use the same mechanic types and effect names across similar features
- Follow the established patterns for resource management
- Maintain consistent naming conventions

### 2. Completeness
- Include mechanics for every feature that has game effects
- Don't leave features with just descriptions
- Add all necessary conditions and restrictions

### 3. Automation-Friendly
- Use specific, parseable formulas like `"1d10 + fighter_level"`
- Include all necessary information for calculations
- Specify action economy clearly

### 4. Level Progression
- Include features for all 20 levels
- Use passive enhancements for improvements to existing features
- Follow D&D 5E progression patterns

### 5. Subclass Integration
- Use array format for subclasses
- Include proper source attribution
- Follow established feature level patterns

### 6. Validation
- Ensure JSON syntax is valid
- Test that all referenced mechanics exist
- Verify mathematical formulas are correct

### 7. Documentation
- Include clear descriptions for all features
- Explain unusual mechanics in comments if needed
- Reference official sources when possible

## Common Patterns

### ASI Levels
Standard ASI levels: 4, 8, 12, 16, 19

### Resource Scaling
- Early game: 1-2 uses
- Mid game: 2-4 uses  
- Late game: 3-6 uses

### Damage Scaling
- Cantrips: Scale at levels 5, 11, 17
- Class features: Often scale at levels 5, 11, 17
- Resource dice: d6 → d8 → d10 → d12

### Subclass Features
- Usually 4-5 features total
- Spread across 4-5 levels
- Often include a "capstone" at high level

This guide provides the framework for creating custom classes that integrate seamlessly with the D&D 5E Character Manager's automation system. 