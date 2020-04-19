import unittest

from universe import engine


class MovementTestCase(unittest.TestCase):
    def test_empty_universe(self):
        state = {'turn': 2500, 'width': 1000, 'entities': {}}
        updates = {}

        S = engine.GameState(state, updates)
        results = S.generate()

        self.assertEqual(results,
                         {'turn': 2501, 'width': 1000, 'entities': {}})

    def test_one_stationary_object(self):
        state = {'turn': 2500, 'width': 1000,
                 'entities': {0: {'type': 'ship', 'x': 456, 'y': 337, 'queue': []}}}
        updates = {}

        S = engine.GameState(state, updates)
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(
            results['entities'],
            {0: {'type': 'ship', 'x': 456, 'x_prev': 456, 'y': 337, 'y_prev': 337, 'queue': []}}
        )

    def test_one_object_single_turn_move(self):
        state = {'turn': 2500, 'width': 1000,
                 'entities': {0: {'type': 'ship', 'x': 480, 'y': 235, 'queue': []}}}
        # actual speed is warp**2
        updates = {0: [{'seq': 0, 'x_t': 422, 'y_t': 210, 'warp': 10}]}

        S = engine.GameState(state, updates)
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(
            results['entities'],
            {0: {'type': 'ship', 'x': 422, 'x_prev': 480, 'y': 210, 'y_prev': 235, 'queue': []}}
        )

    def test_multi_turn_single_move(self):
        state = {'turn': 2500, 'width': 1000,
                 'entities': {0: {'type': 'ship', 'x': 480, 'y': 235, 'queue': []}}}
        # actual speed is warp**2
        updates = {0: [{'seq': 0, 'x_t': 168, 'y_t': 870, 'warp': 10}]}

        S = engine.GameState(state, updates)
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(
            results['entities'],
            {0: {'type': 'ship', 'x': 436, 'x_prev': 480, 'y': 325, 'y_prev': 235,
                 'queue': [{'x_t': 168, 'y_t': 870, 'warp': 10}]}}
        )

    def test_previously_queued_move(self):
        state = {'turn': 2500, 'width': 1000,
                 'entities': {
                     0: {'type': 'ship', 'x': 480, 'y': 235, 'queue': [{'x_t': 422, 'y_t': 210, 'warp': 10}]}}}
        updates = {}

        S = engine.GameState(state, updates)
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(
            results['entities'],
            {0: {'type': 'ship', 'x': 422, 'x_prev': 480, 'y': 210, 'y_prev': 235, 'queue': []}}
        )

    def test_replace_queued_move(self):
        state = {'turn': 2500, 'width': 1000,
                 'entities': {
                     0: {'type': 'ship', 'x': 480, 'y': 235, 'queue': [{'x_t': 637, 'y_t': 786, 'warp': 8}]}}}
        updates = {0: [{'seq': 0, 'x_t': 422, 'y_t': 210, 'warp': 10}]}

        S = engine.GameState(state, updates)
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(
            results['entities'],
            {0: {'type': 'ship', 'x': 422, 'x_prev': 480, 'y': 210, 'y_prev': 235, 'queue': []}}
        )

    def test_add_to_queued_moves(self):
        state = {'turn': 2500, 'width': 1000,
                 'entities': {
                     0: {'type': 'ship', 'x': 480, 'y': 235, 'queue': [{'x_t': 422, 'y_t': 210, 'warp': 10}]}}}
        updates = {0: [{'seq': 1, 'x_t': 637, 'y_t': 786, 'warp': 8}]}

        S = engine.GameState(state, updates)
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(
            results['entities'],
            {0: {'type': 'ship', 'x': 422, 'x_prev': 480, 'y': 210, 'y_prev': 235,
                 'queue': [{'x_t': 637, 'y_t': 786, 'warp': 8}]}}
        )

    def test_slow_motion(self):
        state = {
            'turn': 2500, 'width': 1000,
            'entities': {0: {'type': 'ship', 'x': 500, 'y': 500, 'queue': [{'x_t': 501, 'y_t': 500, 'warp': 1}]}}
        }

        S = engine.GameState(state, {})
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(
            results['entities'],
            {0: {'type': 'ship', 'x': 501, 'x_prev': 500, 'y': 500, 'y_prev': 500, 'queue': []}}
        )

    def test_target_stationary_object(self):
        state = {'turn': 2500, 'width': 1000,
                 'entities': {0: {'type': 'ship', 'x': 480, 'y': 235, 'queue': [{'target_id': 1, 'warp': 10}]},
                              1: {'type': 'ship', 'x': 460, 'y': 215, 'queue': []}}}
        updates = {}

        S = engine.GameState(state, updates)
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(
            results['entities'],
            {0: {'type': 'ship', 'x': 460, 'x_prev': 480, 'y': 215, 'y_prev': 235, 'queue': []},
             1: {'type': 'ship', 'x': 460, 'x_prev': 460, 'y': 215, 'y_prev': 215, 'queue': []}}
        )

    def test_target_moving_object(self):
        state = {
            'turn': 2500, 'width': 1000,
            'entities': {0: {'type': 'ship', 'x': 480, 'y': 235, 'queue': [{'target_id': 1, 'warp': 10}]},
                         1: {'type': 'ship', 'x': 460, 'y': 215, 'queue': [{'x_t': 465, 'y_t': 220, 'warp': 10}]}}
        }
        updates = {}

        S = engine.GameState(state, updates)
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(
            results['entities'],
            {0: {'type': 'ship', 'x': 465, 'x_prev': 480, 'y': 220, 'y_prev': 235, 'queue': []},
             1: {'type': 'ship', 'x': 465, 'x_prev': 460, 'y': 220, 'y_prev': 215, 'queue': []}}
        )

    def test_target_can_barely_reach(self):
        state = {
            'turn': 2500, 'width': 1000,
            'entities': {0: {'type': 'ship', 'x': 560, 'y': 315, 'queue': [{'target_id': 1, 'warp': 10}]},
                         1: {'type': 'ship', 'x': 460, 'y': 215, 'queue': [{'x_t': 660, 'y_t': 215, 'warp': 10}]}}
        }
        S = engine.GameState(state, {})
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(
            results['entities'],
            {0: {'type': 'ship', 'x': 560, 'x_prev': 560, 'y': 215, 'y_prev': 315, 'queue': []},
             1: {'type': 'ship', 'x': 560, 'x_prev': 460, 'y': 215, 'y_prev': 215,
                 'queue': [{'x_t': 660, 'y_t': 215, 'warp': 10}]}}
        )

    def test_target_stops_short(self):
        state = {
            'turn': 2500, 'width': 1000,
            'entities': {0: {'type': 'ship', 'x': 560, 'y': 315, 'queue': [{'target_id': 1, 'warp': 10}]},
                         1: {'type': 'ship', 'x': 460, 'y': 215, 'queue': [{'x_t': 510, 'y_t': 215, 'warp': 10}]}}
        }
        S = engine.GameState(state, {})
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        # Ship 0 should have moved directly north for the first 50 ticks, then northwest for the remainder
        # i.e. roughly 35 lightyears in each direction
        self.assertEqual(
            results['entities'],
            {0: {'type': 'ship', 'x': 525, 'x_prev': 560, 'y': 230, 'y_prev': 315,
                 'queue': [{'target_id': 1, 'warp': 10}]},
             1: {'type': 'ship', 'x': 510, 'x_prev': 460, 'y': 215, 'y_prev': 215, 'queue': []}}
        )

    def test_mutual_intercept(self):
        state = {'turn': 2500, 'width': 1000,
                 'entities': {0: {'type': 'ship', 'x': 480, 'y': 235, 'queue': [{'target_id': 1, 'warp': 10}]},
                              1: {'type': 'ship', 'x': 460, 'y': 215, 'queue': [{'target_id': 0, 'warp': 10}]}}}
        updates = {}

        S = engine.GameState(state, updates)
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(len(results['entities']), 2)
        self.assertEqual(results['entities'][0]['x'], results['entities'][1]['x'])
        self.assertEqual(results['entities'][0]['y'], results['entities'][1]['y'])
        self.assertEqual(results['entities'][0]['queue'], [])
        self.assertEqual(results['entities'][1]['queue'], [])

    def test_three_way_cycle_intercept(self):
        state = {'turn': 2500, 'width': 1000,
                 'entities': {0: {'type': 'ship', 'x': 480, 'y': 235, 'queue': [{'target_id': 1, 'warp': 10}]},
                              1: {'type': 'ship', 'x': 460, 'y': 215, 'queue': [{'target_id': 2, 'warp': 10}]},
                              2: {'type': 'ship', 'x': 500, 'y': 205, 'queue': [{'target_id': 0, 'warp': 10}]}}}
        updates = {}

        S = engine.GameState(state, updates)
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(len(results['entities']), 3)

        self.assertEqual({(entity['x'], entity['y']) for entity in results['entities'].values()},
                         {(480, 219)})
        self.assertTrue(all(not entity['queue'] for entity in results['entities'].values()))

    def test_four_way_cycle_intercept(self):
        state = {'turn': 2500, 'width': 1000,
                 'entities': {0: {'type': 'ship', 'x': 500, 'y': 500, 'queue': [{'target_id': 1, 'warp': 10}]},
                              1: {'type': 'ship', 'x': 600, 'y': 500, 'queue': [{'target_id': 2, 'warp': 10}]},
                              2: {'type': 'ship', 'x': 600, 'y': 600, 'queue': [{'target_id': 3, 'warp': 10}]},
                              3: {'type': 'ship', 'x': 500, 'y': 600, 'queue': [{'target_id': 0, 'warp': 10}]}}}
        updates = {}

        S = engine.GameState(state, updates)
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(len(results['entities']), 4)
        coordinates = {(entity['x'], entity['y']) for entity in results['entities'].values()}
        self.assertEqual(len(coordinates), 1)
        self.assertTrue(all(not entity['queue'] for entity in results['entities'].values()))
