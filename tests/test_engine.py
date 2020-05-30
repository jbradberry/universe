import unittest

from universe import engine, exceptions


class EntityTestCase(unittest.TestCase):
    def test_invalid_ownership(self):
        state = {
            'turn': 2500, 'width': 1000, 'seq': 2,
            'entities': [
                {
                    'pk': 1,
                    'type': 'planet',
                    'x': 300,
                    'y': 600,
                    'gravity': 27,
                    'temperature': 36,
                    'radiation': 45,
                    'ironium_conc': 67,
                    'boranium_conc': 78,
                    'germanium_conc': 82,
                    'ironium': 20,
                    'boranium': 30,
                    'germanium': 40,
                    'owner_id': 0,  # Not an entity in the pool.
                    'population': 1000,
                }
            ]
        }

        with self.assertRaises(exceptions.ValidationError) as e:
            S = engine.GameState(state, {})

        self.assertEqual(str(e.exception), "'owner_id' is not an existing entity.")


class PersistenceTestCase(unittest.TestCase):
    def test_empty_universe(self):
        state = {'turn': 2500, 'width': 1000, 'entities': []}

        S = engine.GameState(state, {})
        results = S.generate()

        self.assertEqual(results,
                         {'turn': 2501, 'width': 1000, 'seq': 0, 'entities': []})

    def test_planet(self):
        state = {
            'turn': 2500, 'width': 1000, 'seq': 2,
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
                    'population_per_r': 1000,
                    'minerals_per_m': 10,
                    'mines_cost_r': 5,
                    'mines_per_pop': 10,
                },
                {
                    'pk': 1,
                    'type': 'planet',
                    'x': 300,
                    'y': 600,
                    'gravity': 27,
                    'temperature': 36,
                    'radiation': 45,
                    'ironium_conc': 67,
                    'boranium_conc': 78,
                    'germanium_conc': 82,
                    'ironium': 20,
                    'boranium': 30,
                    'germanium': 40,
                    'owner_id': 0,
                    'population': 1000,
                }
            ]
        }

        S = engine.GameState(state, {})
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(len(results['entities']), 2)
        planet = next(E for E in results['entities'] if E['pk'] == 1)
        self.assertEqual(planet['type'], 'planet')
        self.assertEqual(planet['x'], 300)
        self.assertEqual(planet['y'], 600)
        self.assertEqual(planet['gravity'], 27)
        self.assertEqual(planet['temperature'], 36)
        self.assertEqual(planet['radiation'], 45)
        self.assertEqual(planet['ironium_conc'], 67)
        self.assertEqual(planet['boranium_conc'], 78)
        self.assertEqual(planet['germanium_conc'], 82)
        self.assertEqual(planet['ironium'], 20)
        self.assertEqual(planet['boranium'], 30)
        self.assertEqual(planet['germanium'], 40)
        self.assertEqual(planet['owner_id'], 0)
        self.assertGreater(planet['population'], 0)

    def test_ship(self):
        state = {
            'turn': 2500, 'width': 1000, 'seq': 2,
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
                    'population_per_r': 1000,
                    'minerals_per_m': 10,
                    'mines_cost_r': 5,
                    'mines_per_pop': 10,
                },
                {
                    'pk': 1,
                    'type': 'ship',
                    'x': 300,
                    'y': 600,
                    'ironium': 20,
                    'boranium': 30,
                    'germanium': 40,
                    'owner_id': 0,
                    'population': 1000,
                }
            ]
        }

        S = engine.GameState(state, {})
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(len(results['entities']), 2)
        ship = next(E for E in results['entities'] if E['pk'] == 1)
        self.assertEqual(ship['type'], 'ship')
        self.assertEqual(ship['x'], 300)
        self.assertEqual(ship['y'], 600)
        self.assertEqual(ship['ironium'], 20)
        self.assertEqual(ship['boranium'], 30)
        self.assertEqual(ship['germanium'], 40)
        self.assertEqual(ship['owner_id'], 0)
        self.assertGreater(ship['population'], 0)

    def test_species(self):
        state = {
            'turn': 2500, 'width': 1000, 'seq': 1,
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
                    'population_per_r': 1000,
                    'minerals_per_m': 10,
                    'mines_cost_r': 5,
                    'mines_per_pop': 10,
                },
            ]
        }

        S = engine.GameState(state, {})
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(len(results['entities']), 1)
        species = next(E for E in results['entities'] if E['pk'] == 0)
        self.assertEqual(species['type'], 'species')
        self.assertEqual(species['name'], 'Human')
        self.assertEqual(species['plural_name'], 'Humans')
        self.assertEqual(species['growth_rate'], 15)
        self.assertEqual(species['gravity_immune'], True)
        self.assertEqual(species['temperature_immune'], True)
        self.assertEqual(species['radiation_immune'], True)
        self.assertEqual(species['population_per_r'], 1000)
        self.assertEqual(species['minerals_per_m'], 10)
        self.assertEqual(species['mines_cost_r'], 5)
        self.assertEqual(species['mines_per_pop'], 10)


class MovementTestCase(unittest.TestCase):
    def test_one_stationary_object(self):
        state = {'turn': 2500, 'width': 1000, 'seq': 1,
                 'entities': [{'pk': 0, 'type': 'ship', 'x': 456, 'y': 337}]}

        S = engine.GameState(state, {})
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(
            results['entities'],
            [{'pk': 0, 'type': 'ship', 'x': 456, 'x_prev': 456, 'y': 337, 'y_prev': 337}]
        )

    def test_one_object_single_turn_move(self):
        state = {
            'turn': 2500, 'width': 1000, 'seq': 1,
            'entities': [
                {'pk': 0, 'type': 'ship', 'x': 480, 'y': 235},
                {'pk': 1, 'type': 'movement_order', 'actor_id': 0, 'seq': 0, 'x_t': 422, 'y_t': 210, 'warp': 10}
            ]
        }
        # actual speed is warp**2

        S = engine.GameState(state, {})
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(
            results['entities'],
            [{'pk': 0, 'type': 'ship', 'x': 422, 'x_prev': 480, 'y': 210, 'y_prev': 235}]
        )

    def test_multi_turn_single_move(self):
        state = {
            'turn': 2500, 'width': 1000, 'seq': 1,
            'entities': [
                {'pk': 0, 'type': 'ship', 'x': 480, 'y': 235},
                {'pk': 1, 'type': 'movement_order', 'actor_id': 0, 'seq': 0, 'x_t': 168, 'y_t': 870, 'warp': 10}
            ]
        }
        # actual speed is warp**2

        S = engine.GameState(state, {})
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(
            results['entities'],
            [{'pk': 0, 'type': 'ship', 'x': 436, 'x_prev': 480, 'y': 325, 'y_prev': 235},
             {'pk': 1, 'type': 'movement_order', 'actor_id': 0, 'seq': 0, 'x_t': 168, 'y_t': 870, 'warp': 10}]
        )

    def test_slow_motion(self):
        state = {
            'turn': 2500, 'width': 1000, 'seq': 2,
            'entities': [
                {'pk': 0, 'type': 'ship', 'x': 500, 'y': 500},
                {'pk': 1, 'type': 'movement_order', 'actor_id': 0, 'seq': 0, 'x_t': 501, 'y_t': 500, 'warp': 1},
            ]
        }

        S = engine.GameState(state, {})
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(
            results['entities'],
            [{'pk': 0, 'type': 'ship', 'x': 501, 'x_prev': 500, 'y': 500, 'y_prev': 500}]
        )

    def test_target_stationary_object(self):
        state = {
            'turn': 2500, 'width': 1000, 'seq': 3,
            'entities': [
                {'pk': 0, 'type': 'ship', 'x': 480, 'y': 235},
                {'pk': 1, 'type': 'ship', 'x': 460, 'y': 215},
                {'pk': 2, 'type': 'movement_order', 'actor_id': 0, 'seq': 0, 'target_id': 1, 'warp': 10},
            ]
        }

        S = engine.GameState(state, {})
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(
            results['entities'],
            [{'pk': 0, 'type': 'ship', 'x': 460, 'x_prev': 480, 'y': 215, 'y_prev': 235},
             {'pk': 1, 'type': 'ship', 'x': 460, 'x_prev': 460, 'y': 215, 'y_prev': 215}]
        )

    def test_target_moving_object(self):
        state = {
            'turn': 2500, 'width': 1000, 'seq': 4,
            'entities': [
                {'pk': 0, 'type': 'ship', 'x': 480, 'y': 235},
                {'pk': 1, 'type': 'ship', 'x': 460, 'y': 215},
                {'pk': 2, 'type': 'movement_order', 'actor_id': 0, 'seq': 0, 'target_id': 1, 'warp': 10},
                {'pk': 3, 'type': 'movement_order', 'actor_id': 1, 'seq': 0, 'x_t': 465, 'y_t': 220, 'warp': 10},
            ]
        }

        S = engine.GameState(state, {})
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(
            results['entities'],
            [{'pk': 0, 'type': 'ship', 'x': 465, 'x_prev': 480, 'y': 220, 'y_prev': 235},
             {'pk': 1, 'type': 'ship', 'x': 465, 'x_prev': 460, 'y': 220, 'y_prev': 215}]
        )

    def test_target_can_barely_reach(self):
        state = {
            'turn': 2500, 'width': 1000, 'seq': 4,
            'entities': [
                {'pk': 0, 'type': 'ship', 'x': 560, 'y': 315},
                {'pk': 1, 'type': 'ship', 'x': 460, 'y': 215},
                {'pk': 2, 'type': 'movement_order', 'actor_id': 0, 'seq': 0, 'target_id': 1, 'warp': 10},
                {'pk': 3, 'type': 'movement_order', 'actor_id': 1, 'seq': 0, 'x_t': 660, 'y_t': 215, 'warp': 10},
            ]
        }
        S = engine.GameState(state, {})
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(
            results['entities'],
            [{'pk': 0, 'type': 'ship', 'x': 560, 'x_prev': 560, 'y': 215, 'y_prev': 315},
             {'pk': 1, 'type': 'ship', 'x': 560, 'x_prev': 460, 'y': 215, 'y_prev': 215},
             {'pk': 3, 'type': 'movement_order', 'actor_id': 1, 'seq': 0, 'x_t': 660, 'y_t': 215, 'warp': 10}]
        )

    def test_target_stops_short(self):
        state = {
            'turn': 2500, 'width': 1000, 'seq': 4,
            'entities': [
                {'pk': 0, 'type': 'ship', 'x': 560, 'y': 315},
                {'pk': 1, 'type': 'ship', 'x': 460, 'y': 215},
                {'pk': 2, 'type': 'movement_order', 'actor_id': 0, 'seq': 0, 'target_id': 1, 'warp': 10},
                {'pk': 3, 'type': 'movement_order', 'actor_id': 1, 'seq': 0, 'x_t': 510, 'y_t': 215, 'warp': 10},
            ]
        }
        S = engine.GameState(state, {})
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        # Ship 0 should have moved directly north for the first 50 ticks, then northwest for the remainder
        # i.e. roughly 35 lightyears in each direction
        self.assertEqual(
            results['entities'],
            [{'pk': 0, 'type': 'ship', 'x': 524, 'x_prev': 560, 'y': 230, 'y_prev': 315},
             {'pk': 1, 'type': 'ship', 'x': 510, 'x_prev': 460, 'y': 215, 'y_prev': 215},
             {'pk': 2, 'type': 'movement_order', 'actor_id': 0, 'seq': 0, 'target_id': 1, 'warp': 10}]
        )

    def test_mutual_intercept(self):
        state = {
            'turn': 2500, 'width': 1000, 'seq': 4,
            'entities': [
                {'pk': 0, 'type': 'ship', 'x': 480, 'y': 235},
                {'pk': 1, 'type': 'ship', 'x': 460, 'y': 215},
                {'pk': 2, 'type': 'movement_order', 'actor_id': 0, 'seq': 0, 'target_id': 1, 'warp': 10},
                {'pk': 3, 'type': 'movement_order', 'actor_id': 1, 'seq': 0, 'target_id': 0, 'warp': 10},
            ]
        }

        S = engine.GameState(state, {})
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(len(results['entities']), 2)
        coordinates = {(entity['x'], entity['y']) for entity in results['entities']}
        self.assertEqual(coordinates, {(470, 225)})

    def test_three_way_cycle_intercept(self):
        state = {
            'turn': 2500, 'width': 1000, 'seq': 6,
            'entities': [
                {'pk': 0, 'type': 'ship', 'x': 480, 'y': 235},
                {'pk': 1, 'type': 'ship', 'x': 460, 'y': 215},
                {'pk': 2, 'type': 'ship', 'x': 500, 'y': 205},
                {'pk': 3, 'type': 'movement_order', 'actor_id': 0, 'seq': 0, 'target_id': 1, 'warp': 10},
                {'pk': 4, 'type': 'movement_order', 'actor_id': 1, 'seq': 0, 'target_id': 2, 'warp': 10},
                {'pk': 5, 'type': 'movement_order', 'actor_id': 2, 'seq': 0, 'target_id': 0, 'warp': 10},
            ]
        }

        S = engine.GameState(state, {})
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(len(results['entities']), 3)
        coordinates = {(entity['x'], entity['y']) for entity in results['entities']}
        self.assertEqual(coordinates, {(480, 217)})

    def test_four_way_cycle_intercept(self):
        state = {
            'turn': 2500, 'width': 1000, 'seq': 8,
            'entities': [
                {'pk': 0, 'type': 'ship', 'x': 500, 'y': 500},
                {'pk': 1, 'type': 'ship', 'x': 600, 'y': 500},
                {'pk': 2, 'type': 'ship', 'x': 600, 'y': 600},
                {'pk': 3, 'type': 'ship', 'x': 500, 'y': 600},
                {'pk': 4, 'type': 'movement_order', 'actor_id': 0, 'seq': 0, 'target_id': 1, 'warp': 10},
                {'pk': 5, 'type': 'movement_order', 'actor_id': 1, 'seq': 0, 'target_id': 2, 'warp': 10},
                {'pk': 6, 'type': 'movement_order', 'actor_id': 2, 'seq': 0, 'target_id': 3, 'warp': 10},
                {'pk': 7, 'type': 'movement_order', 'actor_id': 3, 'seq': 0, 'target_id': 0, 'warp': 10},
            ]
        }

        S = engine.GameState(state, {})
        results = S.generate()

        self.assertEqual(results['turn'], 2501)
        self.assertEqual(results['width'], 1000)
        self.assertEqual(len(results['entities']), 4)
        coordinates = {(entity['x'], entity['y']) for entity in results['entities']}
        self.assertEqual(coordinates, {(550, 550)})
