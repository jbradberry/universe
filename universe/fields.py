

class Field:
    pass


class IntField(Field):
    def __init__(self, min=None, max=None, required=True):
        self.min = min
        self.max = max
        self.required = required


class ListField(Field):
    pass


class CharField(Field):
    def __init__(self, required=True):
        self.required = required
