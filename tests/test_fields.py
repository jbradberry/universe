# -*- coding: utf-8 -*-
import unittest

from universe import fields, exceptions


class FieldTestCase(unittest.TestCase):
    def test_implicit(self):
        field = fields.Field()
        field.name = 'foo'

        with self.assertRaises(exceptions.ValidationError) as e:
            field.validate({})
        self.assertEqual(str(e.exception), "Field 'foo' is required.")

    def test_not_required(self):
        field = fields.Field(required=False)
        field.name = 'foo'

        self.assertIsNone(field.validate({}))

    def test_explicit_required(self):
        field = fields.Field(required=True)
        field.name = 'foo'

        with self.assertRaises(exceptions.ValidationError) as e:
            field.validate({})
        self.assertEqual(str(e.exception), "Field 'foo' is required.")
