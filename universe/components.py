from . import fields


class MetaComponent(type):
    def __new__(cls, name, bases, attrs, **kwargs):
        super_new = super().__new__

        new_attrs = {}
        for name, f in attrs.items():
            if isinstance(f, fields.Field):
                new_attrs[name] = fields.Accessor(name, f)
            else:
                new_attrs[name] = f

        new_class = super_new(cls, name, bases, new_attrs, **kwargs)
        return new_class


class Component(metaclass=MetaComponent):
    pass


class PositionComponent(Component):
    x = fields.IntField()
    y = fields.IntField()
    warp = fields.IntField()
    x_prev = fields.IntField()
    y_prev = fields.IntField()


class QueueComponent(Component):
    queue = fields.ListField()
