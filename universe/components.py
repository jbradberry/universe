import math
import random

from . import fields, exceptions


class MetaComponent(type):
    def __new__(cls, name, bases, attrs, **kwargs):
        super_new = super().__new__

        new_attrs = {'_fields': {}}
        for name, f in attrs.items():
            if isinstance(f, fields.Field):
                new_attrs['_fields'][name] = f
                f.name = name
            else:
                new_attrs[name] = f

        new_class = super_new(cls, name, bases, new_attrs, **kwargs)
        return new_class


class Component(metaclass=MetaComponent):
    def validate(self, data):
        for name, field in self._fields.items():
            field.validate(data)
            if hasattr(self, f'validate_{name}'):
                getattr(self, f'validate_{name}')(data)

    def serialize(self, data):
        output = {}
        self.validate(data)
        for name, field in self._fields.items():
            if name in data:
                output[name] = data[name]
        return output

    def display(self, data):
        output = {}
        self.validate(data)
        for name, field in self._fields.items():
            if name in data:
                value = data[name]
                if hasattr(self, f'_display_{name}'):
                    value = getattr(self, f'_display_{name}')(value)
                else:
                    value = str(value)
                output[name] = value
        return output


class MetadataComponent(Component):
    _name = 'metadata'

    type = fields.CharField(required=True)


class PositionComponent(Component):
    _name = 'position'

    x = fields.IntField()
    y = fields.IntField()
    warp = fields.IntField(required=False)
    x_prev = fields.IntField(required=False)
    y_prev = fields.IntField(required=False)


class QueueComponent(Component):
    _name = 'queue'

    queue = fields.ListField()

    def __init__(self, order_types):
        self._order_types = order_types


class SpeciesComponent(Component):
    _name = 'species'

    name = fields.CharField(required=True)
    plural_name = fields.CharField(required=True)
    growth_rate = fields.IntField(required=True)


class OwnershipComponent(Component):
    _name = 'ownership'

    owner_id = fields.IntField(required=False)


class PopulationComponent(Component):
    _name = 'population'

    population = fields.IntField(required=False)


class EnvironmentComponent(Component):
    _name = 'environment'

    gravity = fields.IntField(min=0, max=100)
    temperature = fields.IntField(min=0, max=100)
    radiation = fields.IntField(min=0, max=100)

    def _display_gravity(self, value):
        gravity = math.pow(2, 6. * value / 100 - 3)
        return f"{gravity:0.3f}g"

    def _display_temperature(self, value):
        temp = 4 * value - 200
        return f"{temp}\u00b0C"

    def _display_radiation(self, value):
        return f"{value}mR"

    @classmethod
    def random(cls):
        # Random weights taken from http://stars.arglos.net/articles/hm-charts.html

        weights = list(range(1, 10)) + [10] * 81 + list(reversed(range(1, 10)))
        return {
            'gravity': random.choices(list(range(1, 100)), weights=weights)[0],
            'temperature': random.choices(list(range(1, 100)), weights=weights)[0],
            'radiation': random.randint(1, 99),
        }


class MineralConcentrationComponent(Component):
    _name = 'mineral_concentrations'

    ironium_conc = fields.IntField(min=0, max=100)
    boranium_conc = fields.IntField(min=0, max=100)
    germanium_conc = fields.IntField(min=0, max=100)

    @classmethod
    def random(cls):
        return {
            'ironium_conc': random.randint(1, 99),
            'boranium_conc': random.randint(1, 99),
            'germanium_conc': random.randint(1, 99),
        }


class MineralInventoryComponent(Component):
    _name = 'minerals'

    ironium = fields.IntField(min=0, required=False)
    boranium = fields.IntField(min=0, required=False)
    germanium = fields.IntField(min=0, required=False)
