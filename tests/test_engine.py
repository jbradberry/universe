import unittest
from universe import engine


class MovementTestCase(unittest.TestCase):
    def test_empty_universe(self):
        state = {'turn': 2500, 'width': 1000, 'locatables': ()}
        updates = {}

        results = engine.generate(state, updates)
        self.assertIsNotNone(results)
        new_state, new_updates = results

        self.assertEqual(new_updates, {})
        self.assertEqual(new_state, {'turn': 2501, 'width': 1000, 'locatables': ()})
