#!/usr/bin/env python3

from toon import Toon

# Test Standard Human
print('=== TESTING STANDARD HUMAN DEBUG ===')
toon1 = Toon()
toon1.set_name('Standard Human Test')

print('Initial state:')
print('  stats:', {k: v for k, v in toon1.properties['stats'].items()})
print('  base_stats:', {k: v for k, v in toon1.properties['base_stats'].items()})
print('  racial_bonuses:', {k: v for k, v in toon1.properties['racial_bonuses'].items()})

toon1.set_race('human', 'Standard')
print('\nAfter setting Standard Human race:')
print('  stats:', {k: v for k, v in toon1.properties['stats'].items()})
print('  base_stats:', {k: v for k, v in toon1.properties['base_stats'].items()})
print('  racial_bonuses:', {k: v for k, v in toon1.properties['racial_bonuses'].items()})

# Test Variant Human
print('\n=== TESTING VARIANT HUMAN DEBUG ===')
toon2 = Toon()
toon2.set_name('Variant Human Test')

print('Initial state:')
print('  stats:', {k: v for k, v in toon2.properties['stats'].items()})
print('  base_stats:', {k: v for k, v in toon2.properties['base_stats'].items()})
print('  racial_bonuses:', {k: v for k, v in toon2.properties['racial_bonuses'].items()})

toon2.set_race('human', 'Variant')
print('\nAfter setting Variant Human race:')
print('  stats:', {k: v for k, v in toon2.properties['stats'].items()})
print('  base_stats:', {k: v for k, v in toon2.properties['base_stats'].items()})
print('  racial_bonuses:', {k: v for k, v in toon2.properties['racial_bonuses'].items()})
print('  pending_choices:', list(toon2.properties.get('pending_choices', {}).keys())) 