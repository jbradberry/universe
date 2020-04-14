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
