

class Field:
    pass


class IntField(Field):
    def __init__(self, required=True):
        self.required = required


class ListField(Field):
    pass


class CharField(Field):
    def __init__(self, required=True):
        self.required = required
