

class Field:
    def __init__(self, required=True):
        self.required = required


class IntField(Field):
    def __init__(self, min=None, max=None, **kwargs):
        super().__init__(**kwargs)
        self.min = min
        self.max = max


class ListField(Field):
    pass


class CharField(Field):
    pass
