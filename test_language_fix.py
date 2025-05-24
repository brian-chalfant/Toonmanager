#!/usr/bin/env python3

from toon import Toon
import json

# Create a new character
char = Toon()
char.set_name('Test Human Ranger')

print("=== Testing Language Choice Merging ===")

# Set race (should give 1 language choice from human)
char.set_race('human', 'Standard')
print("\nAfter setting human race:")
print("Languages in proficiencies:", char.properties['proficiencies']['languages'])
print("Pending language choices:", char.properties.get('pending_choices', {}).get('languages', 'None'))

# Add class
char.add_class('ranger', 1)
print("\nAfter adding ranger class:")
print("Pending language choices:", char.properties.get('pending_choices', {}).get('languages', 'None'))

# Set background (acolyte gives 2 more language choices)
char.set_background('acolyte')
print("\nAfter setting acolyte background:")
print("Languages in proficiencies:", char.properties['proficiencies']['languages'])
print("Pending language choices:", char.properties.get('pending_choices', {}).get('languages', 'None'))

# Print all pending choices
print("\nAll pending choices:")
print(json.dumps(char.properties.get('pending_choices', {}), indent=2)) 