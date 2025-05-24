#!/usr/bin/env python3

import json

# Load the human race data to check what's in it
with open('data/races/human.json', 'r') as f:
    human_data = json.load(f)

print('Base human ability_scores:', human_data['ability_scores'])
print()
print('Variant subrace data:')
variant = next(sr for sr in human_data['subraces'] if sr['name'] == 'Variant')
print('  replaces:', variant.get('replaces', 'NOT FOUND'))
print('  ability_scores:', variant.get('ability_scores', 'NOT FOUND'))
print('  has choose:', 'choose' in variant.get('ability_scores', {})) 