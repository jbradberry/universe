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
        for field in self._fields.values():
            output.update(field.serialize(data))
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

    pk = fields.PrimaryKey()
    type = fields.CharField(required=True)


class PositionComponent(Component):
    _name = 'position'

    x = fields.IntField()
    y = fields.IntField()
    warp = fields.IntField(required=False)
    x_prev = fields.IntField(required=False)
    y_prev = fields.IntField(required=False)


class SpeciesComponent(Component):
    _name = 'species'

    name = fields.CharField(required=True)
    plural_name = fields.CharField(required=True)
    growth_rate = fields.IntField(required=True)


class SpeciesEnvironmentComponent(Component):
    _name = 'species_environment'

    gravity_min = fields.IntField(min=0, max=100, required=False)
    gravity_max = fields.IntField(min=0, max=100, required=False)
    gravity_immune = fields.BooleanField()

    temperature_min = fields.IntField(min=0, max=100, required=False)
    temperature_max = fields.IntField(min=0, max=100, required=False)
    temperature_immune = fields.BooleanField()

    radiation_min = fields.IntField(min=0, max=100, required=False)
    radiation_max = fields.IntField(min=0, max=100, required=False)
    radiation_immune = fields.BooleanField()

    def validate(self, data):
        super().validate(data)

        if data['gravity_immune']:
            if 'gravity_min' in data or 'gravity_max' in data:
                raise exceptions.ValidationError(
                    "'gravity_min' and 'gravity_max' may not be set if 'gravity_immune' is true.")
        else:
            if 'gravity_min' not in data or 'gravity_max' not in data:
                raise exceptions.ValidationError(
                    "'gravity_min' and 'gravity_max' must be set if 'gravity_immune' is false.")

        if data['temperature_immune']:
            if 'temperature_min' in data or 'temperature_max' in data:
                raise exceptions.ValidationError(
                    "'temperature_min' and 'temperature_max' may not be set if 'temperature_immune' is true.")
        else:
            if 'temperature_min' not in data or 'temperature_max' not in data:
                raise exceptions.ValidationError(
                    "'temperature_min' and 'temperature_max' must be set if 'temperature_immune' is false.")

        if data['radiation_immune']:
            if 'radiation_min' in data or 'radiation_max' in data:
                raise exceptions.ValidationError(
                    "'radiation_min' and 'radiation_max' may not be set if 'radiation_immune' is true.")
        else:
            if 'radiation_min' not in data or 'radiation_max' not in data:
                raise exceptions.ValidationError(
                    "'radiation_min' and 'radiation_max' must be set if 'radiation_immune' is false.")


class SpeciesProductionComponent(Component):
    _name = 'species_production'

    population_per_r = fields.IntField(min=700)

    minerals_per_m = fields.IntField(min=5, max=25)
    mines_cost_r = fields.IntField(min=2, max=15)
    mines_per_pop = fields.IntField(min=5, max=25)


class OwnershipComponent(Component):
    _name = 'ownership'

    owner = fields.Reference(types=['species'], required=False)


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


class OrderComponent(Component):
    _name = 'orders'

    actor = fields.Reference(types=['planet', 'ship'])
    seq = fields.IntField(min=0)


class MovementComponent(Component):
    _name = 'movement_orders'

    warp = fields.IntField(min=0)
    x_t = fields.IntField(required=False)
    y_t = fields.IntField(required=False)
    target = fields.Reference(types=['planet', 'ship'], required=False)

    def validate(self, data):
        super().validate(data)

        from .engine import Entity
        actor = Entity.manager.get_entity('metadata', data['actor_id'])
        if actor.type != 'ship':
            raise exceptions.ValidationError("The acting object must be a ship.")

        if data['actor_id'] == data.get('target_id'):
            raise exceptions.ValidationError("A ship cannot target itself for a movement order.")

        if (data.get('target_id') is None) == (data.get('x_t') is None or data.get('y_t') is None):
            raise exceptions.ValidationError("Either of 'target_id' or the target coordinates must be set.")
