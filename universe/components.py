from . import fields


class ValidationError(Exception):
    pass


class MetaComponent(type):
    def __new__(cls, name, bases, attrs, **kwargs):
        super_new = super().__new__

        new_attrs = {'_fields': {}}
        for name, f in attrs.items():
            if isinstance(f, fields.Field):
                new_attrs['_fields'][name] = f
            else:
                new_attrs[name] = f

        new_class = super_new(cls, name, bases, new_attrs, **kwargs)
        return new_class


class Component(metaclass=MetaComponent):
    def serialize(self, data):
        output = {}
        for name, field in self._fields.items():
            if name in data:
                output[name] = data[name]
            elif getattr(field, 'required', True):
                raise ValidationError(f"{name} is required.")
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
