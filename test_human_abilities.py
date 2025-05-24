#!/usr/bin/env python3

from toon import Toon

# Test Standard Human
print('=== TESTING STANDARD HUMAN ===')
toon1 = Toon()
toon1.set_name('Standard Human Test')

# Check initial stats
print('Initial stats:', {k: v for k, v in toon1.properties['stats'].items()})

# Set race first
toon1.set_race('human', 'Standard')
print('After setting race:', {k: v for k, v in toon1.properties['stats'].items()})

# Then set ability scores
toon1.set_ability_scores({'strength': 10, 'dexterity': 10, 'constitution': 10, 'intelligence': 10, 'wisdom': 10, 'charisma': 10})
print('After setting abilities:', {k: v for k, v in toon1.properties['stats'].items()})
print('Expected: all should be 11 (10 base + 1 racial)')

# Test the opposite order too
print('\n=== TESTING REVERSE ORDER ===')
toon3 = Toon()
toon3.set_name('Test Reverse Order')

# Set abilities first 
toon3.set_ability_scores({'strength': 10, 'dexterity': 10, 'constitution': 10, 'intelligence': 10, 'wisdom': 10, 'charisma': 10})
print('After setting abilities first:', {k: v for k, v in toon3.properties['stats'].items()})

# Then set race
toon3.set_race('human', 'Standard')
print('After setting race second:', {k: v for k, v in toon3.properties['stats'].items()})
print('Expected: all should be 11 (10 base + 1 racial)')

# Test Variant Human
print('\n=== TESTING VARIANT HUMAN ===')
toon2 = Toon()
toon2.set_name('Variant Human Test')
toon2.set_race('human', 'Variant')
print('After setting variant race:', {k: v for k, v in toon2.properties['stats'].items()})
toon2.set_ability_scores({'strength': 10, 'dexterity': 10, 'constitution': 10, 'intelligence': 10, 'wisdom': 10, 'charisma': 10})
print('After setting abilities:', {k: v for k, v in toon2.properties['stats'].items()})
print('Expected: all should be 10 (base racial bonuses were replaced)')
print('Pending choices:', toon2.properties.get('pending_choices', {}))
print('Expected: should have pending choice for 2 ability scores') 