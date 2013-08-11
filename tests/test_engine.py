import unittest
from universe import engine


class MovementTestCase(unittest.TestCase):
    def test_empty_universe(self):
        state = {'turn': 2500, 'width': 1000, 'locatables': []}
        updates = []

        results = engine.generate(state, updates)
        self.assertIsNotNone(results)
        new_state, new_updates = results

        self.assertEqual(new_updates, [])
        self.assertEqual(new_state, {'turn': 2501, 'width': 1000, 'locatables': []})

    def test_one_stationary_object(self):
        state = {'turn': 2500, 'width': 1000,
                 'locatables': [{'id': 0, 'x': 456, 'y': 337, 'z': 441}]}
        updates = []

        results = engine.generate(state, updates)
        self.assertIsNotNone(results)
        new_state, new_updates = results

        self.assertEqual(new_updates, [])
        self.assertEqual(set(new_state.iterkeys()), set(['turn', 'width', 'locatables']))
        self.assertEqual(new_state['turn'], 2501)
        self.assertEqual(new_state['width'], 1000)
        self.assertEqual(new_state['locatables'], [{'id': 0, 'x': 456, 'y': 337, 'z': 441}])

    def test_one_object_single_turn_move(self):
        state = {'turn': 2500, 'width': 1000,
                 'locatables': [{'id': 0, 'x': 480, 'y': 235, 'z': 187}]}
        # actual speed is speed**2
        updates = [{'locatable_id': 0, 'seq': 1, 'x_t': 422, 'y_t': 210, 'z_t': 178, 'speed': 10}]

        results = engine.generate(state, updates)
        self.assertIsNotNone(results)
        new_state, new_updates = results

        self.assertEqual(new_updates, [])
        self.assertEqual(set(new_state.iterkeys()), set(['turn', 'width', 'locatables']))
        self.assertEqual(new_state['turn'], 2501)
        self.assertEqual(new_state['width'], 1000)
        self.assertEqual(len(new_state['locatables']), 1)
        self.assertEqual(new_state['locatables'], [{'id': 0, 'x': 422, 'y': 210, 'z': 178}])

    def test_multi_turn_single_move(self):
        state = {'turn': 2500, 'width': 1000,
                 'locatables': [{'id': 0, 'x': 480, 'y': 235, 'z': 187}]}
        # actual speed is speed**2
        updates = [{'locatable_id': 0, 'seq': 1, 'x_t': 168, 'y_t': 870, 'z_t': 390, 'speed': 10}]

        results = engine.generate(state, updates)
        self.assertIsNotNone(results)
        new_state, new_updates = results

        self.assertEqual(len(new_updates), 1)
        self.assertEqual(new_updates, updates)
        self.assertEqual(set(new_state.iterkeys()), set(['turn', 'width', 'locatables']))
        self.assertEqual(new_state['turn'], 2501)
        self.assertEqual(new_state['width'], 1000)
        self.assertEqual(len(new_state['locatables']), 1)
        self.assertEqual(new_state['locatables'], [{'id': 0, 'x': 438, 'y': 321, 'z': 215}])
