# -*- coding: utf-8 -*-
import unittest

from universe import components, fields, engine, exceptions


class ComponentTestCase(unittest.TestCase):
    class SpecialComponent(components.Component):
        foo = fields.IntField(required=False)
        bar = fields.IntField(required=False)

        def validate(self, data):
            super().validate(data)
            if ('foo' in data) == ('bar' in data):
                raise exceptions.ValidationError("Only one of 'foo' or 'bar' can be set.")

        def validate_bar(self, data):
            if 'bar' in data and data['bar'] % 2 != 0:
                raise exceptions.ValidationError("'bar' must be even.")

    def test_invalid_type_foo(self):
        with self.assertRaises(exceptions.ValidationError) as e:
            self.SpecialComponent().validate({'foo': 'a'})
        self.assertEqual(str(e.exception), "'foo' must be an integer.")

    def test_invalid_type_bar(self):
        with self.assertRaises(exceptions.ValidationError) as e:
            self.SpecialComponent().validate({'bar': 'a'})
        self.assertEqual(str(e.exception), "'bar' must be an integer.")

    def test_valid_foo(self):
        self.assertIsNone(self.SpecialComponent().validate({'foo': 42}))

    def test_valid_bar(self):
        self.assertIsNone(self.SpecialComponent().validate({'bar': 42}))

    def test_custom_field_validation(self):
        with self.assertRaises(exceptions.ValidationError) as e:
            self.SpecialComponent().validate({'bar': 3})
        self.assertEqual(str(e.exception), "'bar' must be even.")

    def test_custom_component_validation(self):
        with self.assertRaises(exceptions.ValidationError) as e:
            self.SpecialComponent().validate({})
        self.assertEqual(str(e.exception), "Only one of 'foo' or 'bar' can be set.")

        with self.assertRaises(exceptions.ValidationError) as e:
            self.SpecialComponent().validate({'foo': 42, 'bar': 12})
        self.assertEqual(str(e.exception), "Only one of 'foo' or 'bar' can be set.")


class MetadataComponentTestCase(unittest.TestCase):
    def test_simple(self):
        data = {'type': 'something'}
        component = components.MetadataComponent()
        self.assertEqual(component.serialize(data), data)

    def test_missing_required_field(self):
        data = {}
        component = components.MetadataComponent()
        with self.assertRaises(exceptions.ValidationError):
            component.serialize(data)


class EnvironmentComponentTestCase(unittest.TestCase):
    def test_display_fields(self):
        data = {
            'gravity': 35,
            'temperature': 62,
            'radiation': 50,
        }
        component = components.EnvironmentComponent()
        self.assertEqual(component._display_gravity(data['gravity']), "0.536g")
        self.assertEqual(component._display_temperature(data['temperature']), "48°C")
        self.assertEqual(component._display_radiation(data['radiation']), "50mR")

    def test_component_display(self):
        data = {
            'gravity': 35,
            'temperature': 62,
            'radiation': 50,
        }
        component = components.EnvironmentComponent()
        self.assertEqual(
            component.display(data),
            {'gravity': "0.536g", 'temperature': "48°C", 'radiation': "50mR"}
        )

    def test_random(self):
        data = components.EnvironmentComponent.random()
        self.assertGreaterEqual(data['gravity'], 1)
        self.assertLessEqual(data['gravity'], 99)
        self.assertGreaterEqual(data['temperature'], 1)
        self.assertLessEqual(data['temperature'], 99)
        self.assertGreaterEqual(data['radiation'], 1)
        self.assertLessEqual(data['radiation'], 99)

        # no ValidationError is raised
        self.assertTrue(components.EnvironmentComponent().serialize(data))


class MineralConcentrationComponentTestCase(unittest.TestCase):
    def test_random(self):
        data = components.MineralConcentrationComponent.random()
        self.assertGreaterEqual(data['ironium_conc'], 1)
        self.assertLessEqual(data['ironium_conc'], 99)
        self.assertGreaterEqual(data['boranium_conc'], 1)
        self.assertLessEqual(data['boranium_conc'], 99)
        self.assertGreaterEqual(data['germanium_conc'], 1)
        self.assertLessEqual(data['germanium_conc'], 99)

        # no ValidationError is raised
        self.assertTrue(components.MineralConcentrationComponent().serialize(data))


class SpeciesComponentTestCase(unittest.TestCase):
    def test_immune(self):
        data = {
            'type': 'species',
            'name': 'Human',
            'plural_name': 'Humans',
            'growth_rate': 15,
            'gravity_immune': True,
            'temperature_immune': True,
            'radiation_immune': True,
        }
        component = components.SpeciesComponent()

        self.assertIsNone(component.validate(data))

    def test_immune_with_value(self):
        component = components.SpeciesComponent()

        for fname in ('gravity', 'temperature', 'radiation'):
            data = {
                'type': 'species',
                'name': 'Human',
                'plural_name': 'Humans',
                'growth_rate': 15,
                'gravity_immune': True,
                'temperature_immune': True,
                'radiation_immune': True,
            }
            data[f'{fname}_min'] = 30
            data[f'{fname}_max'] = 70

            with self.assertRaises(exceptions.ValidationError) as e:
                component.validate(data)

            self.assertEqual(
                str(e.exception),
                f"'{fname}_min' and '{fname}_max' may not be set if '{fname}_immune' is true."
            )

    def test_not_immune(self):
        data = {
            'type': 'species',
            'name': 'Human',
            'plural_name': 'Humans',
            'growth_rate': 15,
            'gravity_immune': False,
            'temperature_immune': False,
            'radiation_immune': False,
        }
        component = components.SpeciesComponent()

        with self.assertRaises(exceptions.ValidationError):
            component.validate(data)

    def test_not_immune_without_value(self):
        component = components.SpeciesComponent()

        for fname in ('gravity', 'temperature', 'radiation'):
            data = {
                'type': 'species',
                'name': 'Human',
                'plural_name': 'Humans',
                'growth_rate': 15,
                'gravity_min': 30,
                'gravity_max': 70,
                'gravity_immune': False,
                'temperature_min': 30,
                'temperature_max': 70,
                'temperature_immune': False,
                'radiation_min': 30,
                'radiation_max': 70,
                'radiation_immune': False,
            }
            data.pop(f'{fname}_min')
            data.pop(f'{fname}_max')

            with self.assertRaises(exceptions.ValidationError) as e:
                component.validate(data)

            self.assertEqual(
                str(e.exception),
                f"'{fname}_min' and '{fname}_max' must be set if '{fname}_immune' is false."
            )


class OwnershipComponentTestCase(unittest.TestCase):
    def setUp(self):
        self.manager = engine.Manager()
        self.manager._entity_registry = {
            'species': {
                'metadata': components.MetadataComponent(),
            },
            'planet': {
                'metadata': components.MetadataComponent(),
                'ownership': components.OwnershipComponent(),
            },
        }
        engine.Entity.register_manager(self.manager)

    def test_null_pointer(self):
        self.manager.register_entity(0, {'type': 'planet'})

        planet = self.manager.get_entity('metadata', 0)
        self.assertIsNone(planet.owner)

    def test_entity_reference(self):
        self.manager.register_entity(0, {'type': 'species'})
        self.manager.register_entity(1, {'type': 'planet', 'owner_id': 0})

        planet = self.manager.get_entity('metadata', 1)

        self.assertIsInstance(planet.owner, engine.Entity)
        self.assertEqual(planet.owner.serialize(), {'type': 'species'})
