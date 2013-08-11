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

    def test_one_stationary_object(self):
        state = {'turn': 2500, 'width': 1000,
                 'locatables': ({'x': 456, 'y': 337, 'z': 441},)}
        updates = {}

        results = engine.generate(state, updates)
        self.assertIsNotNone(results)
        new_state, new_updates = results

        self.assertEqual(new_updates, {})
        self.assertEqual(set(new_state.iterkeys()), set(['turn', 'width', 'locatables']))
        self.assertEqual(new_state['turn'], 2501)
        self.assertEqual(new_state['width'], 1000)
        self.assertEqual(new_state['locatables'], ({'x': 456, 'y': 337, 'z': 441},))
