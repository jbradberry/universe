

class Accessor:
    def __init__(self, name, field):
        self.name = name
        self.field = field

    def __get__(self, obj, type=None):
        print("getting {} from {}".format(self.name, obj))
        return obj.__dict__[self.name]

    def __set__(self, obj, value):
        print("setting {} on field {} for {}".format(value, self.name, obj))
        obj.__dict__[self.name] = value

    def __delete__(self, obj):
        print("clearing field {} on {}".format(self.name, obj))
        del obj.__dict__[self.name]


class Field:
    pass


class IntField(Field):
    pass


class ListField(Field):
    pass
