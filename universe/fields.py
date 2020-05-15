from . import exceptions


class Field:
    def __init__(self, required=True):
        self.required = required

    def validate(self, data):
        if self.required and self.name not in data:
            raise exceptions.ValidationError(f"{self.name!r} is required.")


class IntField(Field):
    def __init__(self, min=None, max=None, **kwargs):
        super().__init__(**kwargs)
        self.min = min
        self.max = max

    def validate(self, data):
        super().validate(data)
        if self.name not in data:
            return
        value = data[self.name]
        if not isinstance(value, int):
            raise exceptions.ValidationError(f"{self.name!r} must be an integer.")
        if self.min is not None and value < self.min:
            raise exceptions.ValidationError(f"{self.name!r} must be greater than or equal to {self.min}.")
        if self.max is not None and value > self.max:
            raise exceptions.ValidationError(f"{self.name!r} must be less than or equal to {self.max}.")


class ListField(Field):
    def validate(self, data):
        super().validate(data)
        if self.name not in data:
            return
        value = data[self.name]
        if not isinstance(value, list):
            raise exceptions.ValidationError(f"{self.name!r} must be a list.")


class CharField(Field):
    pass
