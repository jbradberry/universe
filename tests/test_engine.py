import unittest
from universe import engine


class MovementTestCase(unittest.TestCase):
    def test_empty_universe(self):
        state = {'turn': 2500, 'width': 1000, 'locatables': {}, 'actions': {}}
        updates = []

        S = engine.GameState(state, updates)
        results = S.generate()

        self.assertIsNotNone(results)
        self.assertEqual(results,
                         {'turn': 2501, 'width': 1000, 'locatables': {}, 'actions': {}})

    def test_one_stationary_object(self):
        state = {'turn': 2500, 'width': 1000,
                 'locatables': {0: {'x': 456, 'y': 337, 'z': 441}},
                 'actions': {}}
        updates = []

        S = engine.GameState(state, updates)
        results = S.generate()

        self.assertIsNotNone(results)
        self.assertEqual(set(results.iterkeys()), set(['turn', 'width', 'locatables', 'actions']))
        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(results['locatables'], {0: {'x': 456, 'y': 337, 'z': 441}})
        self.assertEqual(results['actions'], {})

    def test_one_object_single_turn_move(self):
        state = {'turn': 2500, 'width': 1000,
                 'locatables': {0: {'x': 480, 'y': 235, 'z': 187}},
                 'actions': {}}
        # actual speed is speed**2
        updates = [{'locatable_id': 0, 'seq': 0, 'x_t': 422, 'y_t': 210, 'z_t': 178, 'speed': 10}]

        S = engine.GameState(state, updates)
        results = S.generate()

        self.assertIsNotNone(results)
        self.assertEqual(set(results.iterkeys()), set(['turn', 'width', 'locatables', 'actions']))
        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(len(results['locatables']), 1)
        self.assertEqual(results['locatables'], {0: {'x': 422, 'y': 210, 'z': 178}})
        self.assertEqual(results['actions'], {})

    def test_multi_turn_single_move(self):
        state = {'turn': 2500, 'width': 1000,
                 'locatables': {0: {'x': 480, 'y': 235, 'z': 187}},
                 'actions': {}}
        # actual speed is speed**2
        updates = [{'locatable_id': 0, 'seq': 0, 'x_t': 168, 'y_t': 870, 'z_t': 390, 'speed': 10}]

        S = engine.GameState(state, updates)
        results = S.generate()

        self.assertIsNotNone(results)
        self.assertEqual(set(results.iterkeys()), set(['turn', 'width', 'locatables', 'actions']))
        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(len(results['locatables']), 1)
        self.assertEqual(results['locatables'], {0: {'x': 438, 'y': 321, 'z': 215}})
        self.assertEqual(results['actions'],
                         {0: [{'x_t': 168, 'y_t': 870, 'z_t': 390, 'speed': 10}]})
