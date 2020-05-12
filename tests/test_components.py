# -*- coding: utf-8 -*-
import unittest

from universe import components


class MetadataComponentTestCase(unittest.TestCase):
    def test_simple(self):
        data = {'type': 'something'}
        component = components.MetadataComponent()
        self.assertEqual(component.serialize(data), data)

    def test_missing_required_field(self):
        data = {}
        component = components.MetadataComponent()
        with self.assertRaises(components.ValidationError):
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
