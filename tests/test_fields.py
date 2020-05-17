# -*- coding: utf-8 -*-
import unittest

from universe import fields, exceptions


class FieldTestCase(unittest.TestCase):
    def test_implicit(self):
        field = fields.Field()
        field.name = 'foo'

        with self.assertRaises(exceptions.ValidationError) as e:
            field.validate({})
        self.assertEqual(str(e.exception), "'foo' is required.")

    def test_not_required(self):
        field = fields.Field(required=False)
        field.name = 'foo'

        self.assertIsNone(field.validate({}))

    def test_explicit_required(self):
        field = fields.Field(required=True)
        field.name = 'foo'

        with self.assertRaises(exceptions.ValidationError) as e:
            field.validate({})
        self.assertEqual(str(e.exception), "'foo' is required.")


class BooleanFieldTestCase(unittest.TestCase):
    def test_implicit(self):
        field = fields.BooleanField()
        field.name = 'checkmark'

        with self.assertRaises(exceptions.ValidationError) as e:
            field.validate({})
        self.assertEqual(str(e.exception), "'checkmark' is required.")

    def test_bad_type(self):
        field = fields.BooleanField()
        field.name = 'checkmark'

        with self.assertRaises(exceptions.ValidationError) as e:
            field.validate({'checkmark': 'a'})
        self.assertEqual(str(e.exception), "'checkmark' must be a boolean.")

    def test_ok(self):
        field = fields.BooleanField()
        field.name = 'checkmark'

        self.assertIsNone(field.validate({'checkmark': True}))
        self.assertIsNone(field.validate({'checkmark': False}))


class IntFieldTestCase(unittest.TestCase):
    def test_not_required(self):
        field = fields.IntField(required=False)
        field.name = 'widgets'

        self.assertIsNone(field.validate({}))

    def test_explicit_required(self):
        field = fields.IntField(required=True)
        field.name = 'widgets'

        with self.assertRaises(exceptions.ValidationError) as e:
            field.validate({})
        self.assertEqual(str(e.exception), "'widgets' is required.")

    def test_bad_type(self):
        field = fields.IntField(required=True)
        field.name = 'widgets'

        with self.assertRaises(exceptions.ValidationError) as e:
            field.validate({'widgets': 'a'})
        self.assertEqual(str(e.exception), "'widgets' must be an integer.")

    def test_in_range(self):
        field = fields.IntField(min=0, max=100, required=True)
        field.name = 'widgets'

        self.assertIsNone(field.validate({'widgets': 42}))

    def test_under_min(self):
        field = fields.IntField(min=0, max=100, required=True)
        field.name = 'widgets'

        with self.assertRaises(exceptions.ValidationError) as e:
            field.validate({'widgets': -10})
        self.assertEqual(str(e.exception), "'widgets' must be greater than or equal to 0.")

    def test_over_max(self):
        field = fields.IntField(min=0, max=100, required=True)
        field.name = 'widgets'

        with self.assertRaises(exceptions.ValidationError) as e:
            field.validate({'widgets': 200})
        self.assertEqual(str(e.exception), "'widgets' must be less than or equal to 100.")


class ListFieldTestCase(unittest.TestCase):
    def test_not_required(self):
        field = fields.ListField(required=False)
        field.name = 'queue'

        self.assertIsNone(field.validate({}))

    def test_explicit_required(self):
        field = fields.ListField(required=True)
        field.name = 'queue'

        with self.assertRaises(exceptions.ValidationError) as e:
            field.validate({})
        self.assertEqual(str(e.exception), "'queue' is required.")

    def test_bad_type(self):
        field = fields.ListField(required=True)
        field.name = 'queue'

        with self.assertRaises(exceptions.ValidationError) as e:
            field.validate({'queue': 0})
        self.assertEqual(str(e.exception), "'queue' must be a list.")

    def test_empty_list_is_valid(self):
        field = fields.ListField(required=True)
        field.name = 'queue'

        self.assertIsNone(field.validate({'queue': []}))


class CharFieldTestCase(unittest.TestCase):
    def test_not_required(self):
        field = fields.CharField(required=False)
        field.name = 'name'

        self.assertIsNone(field.validate({}))

    def test_explicit_required(self):
        field = fields.CharField(required=True)
        field.name = 'name'

        with self.assertRaises(exceptions.ValidationError) as e:
            field.validate({})
        self.assertEqual(str(e.exception), "'name' is required.")

    def test_bad_type(self):
        field = fields.CharField(required=True)
        field.name = 'name'

        with self.assertRaises(exceptions.ValidationError) as e:
            field.validate({'name': 0})
        self.assertEqual(str(e.exception), "'name' must be a string.")

    def test_empty_string_is_valid(self):
        field = fields.CharField(required=True)
        field.name = 'name'

        self.assertIsNone(field.validate({'name': ""}))

    def test_valid_string(self):
        field = fields.CharField(required=True)
        field.name = 'name'

        self.assertIsNone(field.validate({'name': "Human"}))
