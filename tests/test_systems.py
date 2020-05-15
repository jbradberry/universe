import unittest

from universe import engine
from universe import systems


class PopulationTestCase(unittest.TestCase):
    def test_population_growth(self):
        state = {
            'turn': 2500,
            'width': 1000,
            'entities': {
                0: {
                    'type': 'species',
                    'name': 'Human',
                    'plural_name': 'Humans',
                    'growth_rate': 15,
                    'gravity_immune': True,
                    'temperature_immune': True,
                    'radiation_immune': True,
                },
                1: {
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
                    'queue': [],
                },
            }
        }

        S = engine.GameState(state, {})
        results = S.generate()

        self.assertEqual(
            results,
            {
                'turn': 2501,
                'width': 1000,
                'entities': {
                    0: {
                        'type': 'species',
                        'name': 'Human',
                        'plural_name': 'Humans',
                        'growth_rate': 15,
                        'gravity_immune': True,
                        'temperature_immune': True,
                        'radiation_immune': True,
                    },
                    1: {
                        'type': 'planet',
                        'population': 1150,
                        'x': 480,
                        'x_prev': 480,
                        'y': 235,
                        'y_prev': 235,
                        'gravity': 50,
                        'temperature': 50,
                        'radiation': 50,
                        'ironium_conc': 50,
                        'boranium_conc': 50,
                        'germanium_conc': 50,
                        'owner_id': 0,
                        'queue': [],
                    },
                }
            }
        )

    def test_lose_ownership(self):
        state = {
            'turn': 2500,
            'width': 1000,
            'entities': {
                0: {
                    'type': 'species',
                    'name': 'Human',
                    'plural_name': 'Humans',
                    'growth_rate': 15,
                    'gravity_immune': True,
                    'temperature_immune': True,
                    'radiation_immune': True,
                },
                1: {
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
                    'queue': [],
                },
            }
        }

        S = engine.GameState(state, {})
        results = S.generate()

        self.assertEqual(len(results['entities']), 2)
        self.assertNotIn('population', results['entities'][1])
        self.assertNotIn('owner_id', results['entities'][1])
