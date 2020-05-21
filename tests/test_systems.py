import unittest

from universe import engine
from universe import systems


class PopulationTestCase(unittest.TestCase):
    def test_habitability_growth(self):
        state = {
            'turn': 2500,
            'width': 1000,
            'entities': [
                {
                    'pk': 0,
                    'type': 'species',
                    'name': 'Human',
                    'plural_name': 'Humans',
                    'growth_rate': 15,
                    'gravity_immune': True,
                    'temperature_immune': True,
                    'radiation_immune': True,
                },
                {
                    'pk': 1,
                    'type': 'planet',
                    'population': 1000,
                    'x': 480,
                    'y': 235,
                    'gravity': 50,
                    'temperature': 50,
                    'radiation': 50,
                    'ironium_conc': 50,
                    'boranium_conc': 50,
                    'germanium_conc': 50,
                    'owner_id': 0,
                },
            ]
        }

        S = engine.GameState(state, {})
        results = S.generate()

        self.assertEqual(len(results['entities']), 2)
        self.assertEqual(results['entities'][1]['owner_id'], 0)
        self.assertEqual(results['entities'][1]['population'], 1150)

    def test_crowding_growth(self):
        state = {
            'turn': 2500,
            'width': 1000,
            'entities': [
                {
                    'pk': 0,
                    'type': 'species',
                    'name': 'Human',
                    'plural_name': 'Humans',
                    'growth_rate': 15,
                    'gravity_immune': True,
                    'temperature_immune': True,
                    'radiation_immune': True,
                },
                {
                    'pk': 1,
                    'type': 'planet',
                    'population': 500_000,
                    'x': 480,
                    'y': 235,
                    'gravity': 50,
                    'temperature': 50,
                    'radiation': 50,
                    'ironium_conc': 50,
                    'boranium_conc': 50,
                    'germanium_conc': 50,
                    'owner_id': 0,
                },
            ]
        }

        S = engine.GameState(state, {})
        results = S.generate()

        self.assertEqual(len(results['entities']), 2)
        self.assertEqual(results['entities'][1]['owner_id'], 0)

        # At a population of 50% of capacity, the crowding factor
        # should be 4/9.  Effective growth rate should then be 6.67%.
        self.assertEqual(results['entities'][1]['population'], 533_333)

    def test_capacity_growth(self):
        state = {
            'turn': 2500,
            'width': 1000,
            'entities': [
                {
                    'pk': 0,
                    'type': 'species',
                    'name': 'Human',
                    'plural_name': 'Humans',
                    'growth_rate': 15,
                    'gravity_immune': False,
                    'temperature_immune': False,
                    'radiation_immune': False,
                    'gravity_min': 32,
                    'gravity_max': 86,
                    'temperature_min': 10,
                    'temperature_max': 64,
                    'radiation_min': 38,
                    'radiation_max': 90,
                },
                {
                    'pk': 1,
                    'type': 'planet',
                    'population': 1_000_000,
                    'x': 480,
                    'y': 235,
                    'gravity': 59,
                    'temperature': 37,
                    'radiation': 64,
                    'ironium_conc': 50,
                    'boranium_conc': 50,
                    'germanium_conc': 50,
                    'owner_id': 0,
                },
            ]
        }

        S = engine.GameState(state, {})
        results = S.generate()

        self.assertEqual(len(results['entities']), 2)
        self.assertEqual(results['entities'][1]['owner_id'], 0)
        self.assertEqual(results['entities'][1]['population'], 1_000_000)

    def test_overcrowding_growth(self):
        state = {
            'turn': 2500,
            'width': 1000,
            'entities': [
                {
                    'pk': 0,
                    'type': 'species',
                    'name': 'Human',
                    'plural_name': 'Humans',
                    'growth_rate': 15,
                    'gravity_immune': False,
                    'temperature_immune': False,
                    'radiation_immune': False,
                    'gravity_min': 32,
                    'gravity_max': 86,
                    'temperature_min': 10,
                    'temperature_max': 64,
                    'radiation_min': 38,
                    'radiation_max': 90,
                },
                {
                    'pk': 1,
                    'type': 'planet',
                    'population': 2_000_000,
                    'x': 480,
                    'y': 235,
                    'gravity': 59,
                    'temperature': 37,
                    'radiation': 64,
                    'ironium_conc': 50,
                    'boranium_conc': 50,
                    'germanium_conc': 50,
                    'owner_id': 0,
                },
            ]
        }

        S = engine.GameState(state, {})
        results = S.generate()

        self.assertEqual(len(results['entities']), 2)
        self.assertEqual(results['entities'][1]['owner_id'], 0)

        # At a population of 200% of capacity, the death rate should be 100 * 0.04% = 4.0%.
        self.assertEqual(results['entities'][1]['population'], 1_920_000)

    def test_uninhabitable_growth(self):
        state = {
            'turn': 2500,
            'width': 1000,
            'entities': [
                {
                    'pk': 0,
                    'type': 'species',
                    'name': 'Human',
                    'plural_name': 'Humans',
                    'growth_rate': 15,
                    'gravity_immune': False,
                    'temperature_immune': False,
                    'radiation_immune': False,
                    'gravity_min': 32,
                    'gravity_max': 86,
                    'temperature_min': 10,
                    'temperature_max': 64,
                    'radiation_min': 38,
                    'radiation_max': 90,
                },
                {
                    'pk': 1,
                    'type': 'planet',
                    'population': 100_000,
                    'x': 480,
                    'y': 235,
                    'gravity': 1,
                    'temperature': 84,
                    'radiation': 3,
                    'ironium_conc': 50,
                    'boranium_conc': 50,
                    'germanium_conc': 50,
                    'owner_id': 0,
                },
            ]
        }

        S = engine.GameState(state, {})
        results = S.generate()

        self.assertEqual(len(results['entities']), 2)
        self.assertEqual(results['entities'][1]['owner_id'], 0)

        # This planet should be at -45% habitable, so we should lose 4.5%.
        self.assertEqual(results['entities'][1]['population'], 95_500)

    def test_lose_ownership(self):
        state = {
            'turn': 2500,
            'width': 1000,
            'entities': [
                {
                    'pk': 0,
                    'type': 'species',
                    'name': 'Human',
                    'plural_name': 'Humans',
                    'growth_rate': 15,
                    'gravity_immune': True,
                    'temperature_immune': True,
                    'radiation_immune': True,
                },
                {
                    'pk': 1,
                    'type': 'planet',
                    'population': 0,
                    'x': 480,
                    'y': 235,
                    'gravity': 50,
                    'temperature': 50,
                    'radiation': 50,
                    'ironium_conc': 50,
                    'boranium_conc': 50,
                    'germanium_conc': 50,
                    'owner_id': 0,
                },
            ]
        }

        S = engine.GameState(state, {})
        results = S.generate()

        self.assertEqual(len(results['entities']), 2)
        self.assertNotIn('population', results['entities'][1])
        self.assertNotIn('owner_id', results['entities'][1])
