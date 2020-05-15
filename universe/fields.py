from . import exceptions


class Field:
    def __init__(self, required=True):
        self.required = required

    def validate(self, data):
        if self.required and self.name not in data:
            raise exceptions.ValidationError(f"Field {self.name!r} is required.")


class IntField(Field):
    def __init__(self, min=None, max=None, **kwargs):
        super().__init__(**kwargs)
        self.min = min
        self.max = max


class ListField(Field):
    pass


class CharField(Field):
    pass
