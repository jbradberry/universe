import unittest

from universe import engine


class MovementTestCase(unittest.TestCase):
    def test_empty_universe(self):
        state = {'turn': 2500, 'width': 1000, 'locatables': {}, 'actions': {}}
        updates = {}

        S = engine.GameState(state, updates)
        results = S.generate()

        self.assertEqual(results,
                         {'turn': 2501, 'width': 1000, 'locatables': {}, 'actions': {}})

    def test_one_stationary_object(self):
        state = {'turn': 2500, 'width': 1000,
                 'locatables': {0: {'x': 456, 'y': 337}},
                 'actions': {}}
        updates = {}

        S = engine.GameState(state, updates)
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(results['locatables'], {0: {'x': 456, 'y': 337}})
        self.assertEqual(results['actions'], {})

    def test_one_object_single_turn_move(self):
        state = {'turn': 2500, 'width': 1000,
                 'locatables': {0: {'x': 480, 'y': 235}},
                 'actions': {}}
        # actual speed is warp**2
        updates = {0: [{'seq': 0, 'x_t': 422, 'y_t': 210, 'warp': 10}]}

        S = engine.GameState(state, updates)
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(results['locatables'], {0: {'x': 422, 'y': 210}})
        self.assertEqual(results['actions'], {})

    def test_multi_turn_single_move(self):
        state = {'turn': 2500, 'width': 1000,
                 'locatables': {0: {'x': 480, 'y': 235}},
                 'actions': {}}
        # actual speed is warp**2
        updates = {0: [{'seq': 0, 'x_t': 168, 'y_t': 870, 'warp': 10}]}

        S = engine.GameState(state, updates)
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(results['locatables'], {0: {'x': 436, 'y': 325}})
        self.assertEqual(results['actions'],
                         {0: [{'x_t': 168, 'y_t': 870, 'warp': 10}]})

    def test_previously_queued_move(self):
        state = {'turn': 2500, 'width': 1000,
                 'locatables': {0: {'x': 480, 'y': 235}},
                 'actions': {0: [{'x_t': 422, 'y_t': 210, 'warp': 10}]}}
        updates = {}

        S = engine.GameState(state, updates)
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(results['locatables'], {0: {'x': 422, 'y': 210}})
        self.assertEqual(results['actions'], {})

    def test_replace_queued_move(self):
        state = {'turn': 2500, 'width': 1000,
                 'locatables': {0: {'x': 480, 'y': 235}},
                 'actions': {0: [{'x_t': 637, 'y_t': 786, 'warp': 8}]}}
        updates = {0: [{'seq': 0, 'x_t': 422, 'y_t': 210, 'warp': 10}]}

        S = engine.GameState(state, updates)
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(results['locatables'], {0: {'x': 422, 'y': 210}})
        self.assertEqual(results['actions'], {})

    def test_add_to_queued_moves(self):
        state = {'turn': 2500, 'width': 1000,
                 'locatables': {0: {'x': 480, 'y': 235}},
                 'actions': {0: [{'x_t': 422, 'y_t': 210, 'warp': 10}]}}
        updates = {0: [{'seq': 1, 'x_t': 637, 'y_t': 786, 'warp': 8}]}

        S = engine.GameState(state, updates)
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(results['locatables'], {0: {'x': 422, 'y': 210}})
        self.assertEqual(results['actions'], {0: [{'x_t': 637, 'y_t': 786, 'warp': 8}]})

    def test_target_stationary_object(self):
        state = {'turn': 2500, 'width': 1000,
                 'locatables': {0: {'x': 480, 'y': 235},
                                1: {'x': 460, 'y': 215}},
                 'actions': {0: [{'target_id': 1, 'warp': 10}]}}
        updates = {}

        S = engine.GameState(state, updates)
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(results['locatables'], {0: {'x': 460, 'y': 215},
                                                 1: {'x': 460, 'y': 215}})
        self.assertEqual(results['actions'], {})

    def test_target_moving_object(self):
        state = {'turn': 2500, 'width': 1000,
                 'locatables': {0: {'x': 480, 'y': 235},
                                1: {'x': 460, 'y': 215}},
                 'actions': {0: [{'target_id': 1, 'warp': 10}],
                             1: [{'x_t': 465, 'y_t': 220, 'warp': 10}]}}
        updates = {}

        S = engine.GameState(state, updates)
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(results['locatables'], {0: {'x': 465, 'y': 220},
                                                 1: {'x': 465, 'y': 220}})
        self.assertEqual(results['actions'], {})

    def test_mutual_intercept(self):
        state = {'turn': 2500, 'width': 1000,
                 'locatables': {0: {'x': 480, 'y': 235},
                                1: {'x': 460, 'y': 215}},
                 'actions': {0: [{'target_id': 1, 'warp': 10}],
                             1: [{'target_id': 0, 'warp': 10}]}}
        updates = {}

        S = engine.GameState(state, updates)
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(len(results['locatables']), 2)
        self.assertEqual(results['locatables'][0], results['locatables'][1])
        self.assertTrue(results['locatables'][0] == {'x': 480, 'y': 235} or
                        results['locatables'][0] == {'x': 460, 'y': 215})
        self.assertEqual(results['actions'], {})

    def test_three_way_cycle_intercept(self):
        state = {'turn': 2500, 'width': 1000,
                 'locatables': {0: {'x': 480, 'y': 235},
                                1: {'x': 460, 'y': 215},
                                2: {'x': 500, 'y': 205}},
                 'actions': {0: [{'target_id': 1, 'warp': 10}],
                             1: [{'target_id': 2, 'warp': 10}],
                             2: [{'target_id': 0, 'warp': 10}]}}
        updates = {}

        S = engine.GameState(state, updates)
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(len(results['locatables']), 3)
        self.assertEqual(results['locatables'][0], results['locatables'][1])
        self.assertEqual(results['locatables'][0], results['locatables'][2])
        self.assertTrue(results['locatables'][0] == {'x': 480, 'y': 235} or
                        results['locatables'][0] == {'x': 460, 'y': 215} or
                        results['locatables'][0] == {'x': 500, 'y': 205})
        self.assertEqual(results['actions'], {})

    def test_four_way_cycle_intercept(self):
        # ensures that the early-move deadlock breaker doesn't drop
        # its waypoint when it fails to end the turn at the same
        # location as its target.
        state = {'turn': 2500, 'width': 1000,
                 'locatables': {0: {'x': 500, 'y': 500},
                                1: {'x': 600, 'y': 500},
                                2: {'x': 600, 'y': 600},
                                3: {'x': 500, 'y': 600}},
                 'actions': {0: [{'target_id': 1, 'warp': 10}],
                             1: [{'target_id': 2, 'warp': 10}],
                             2: [{'target_id': 3, 'warp': 10}],
                             3: [{'target_id': 0, 'warp': 10}]}}
        updates = {}

        S = engine.GameState(state, updates)
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(len(results['locatables']), 4)
        coordinates = [(x['x'], x['y'])
                       for loc_id, x in sorted(results['locatables'].items())]
        self.assertEqual(len(set(coordinates)), 2)
        self.assertEqual(len(results['actions']), 2)
        k1, k2 = results['actions'].keys()
        self.assertNotEqual(results['locatables'][k1], results['locatables'][k2])
        self.assertTrue(results['actions'][k1][0]['target_id'] == k2 or
                        results['actions'][k2][0]['target_id'] == k1)
