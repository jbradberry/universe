import weakref

from . import components, systems, exceptions
from .orders import (Move, CargoTransfer, Scrap, BuildInstallation, Terraform,
                     BuildStation, BuildShip, LaunchMassPacket)


class Entity:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self._components = Entity.manager._entity_registry[kwargs['type']]

    def __getattr__(self, name):
        for component in self.__dict__.get('_components', {}).values():
            for field in component._fields.values():
                if name == field.data_name:
                    return self.__dict__.get(name)
                if name == field.name:
                    return field.from_data(self.__dict__)
        try:
            return self.__dict__[name]
        except KeyError:
            raise AttributeError(f"{self.__class__.__name__!r} object has no attribute {name!r}")

    def __setattr__(self, name, value):
        for component in self.__dict__.get('_components', {}).values():
            for field in component._fields.values():
                if name in (field.data_name, field.name):
                    try:
                        self.__dict__[field.data_name] = field.to_data(value)
                    except exceptions.empty:
                        self.__dict__.pop(field.data_name, None)
                    return
        self.__dict__[name] = value

    def __delattr__(self, name):
        for component in self.__dict__.get('_components', {}).values():
            for field in component._fields.values():
                if name in (field.data_name, field.name):
                    self.__dict__.pop(field.data_name)
                    return
        del self.__dict__[name]

    def __contains__(self, key):
        return key in self._components

    def validate(self):
        for component in self._components.values():
            component.validate(self.__dict__)

    def serialize(self):
        data = {}
        for _type, component in self._components.items():
            data.update(component.serialize(self.__dict__))
        return data

    @classmethod
    def register_manager(cls, manager):
        cls.manager = weakref.proxy(manager)


class Manager:
    def __init__(self):
        self._seq = 0
        self._components = {}
        self._systems = []
        self._updates = {}

        self._entity_registry = {}

    def register_system(self, system):
        self._systems.append(system)

    def register_entity_type(self, name, _components):
        if name in self._entity_registry:
            raise ValueError("{} is already a registered entity type.".format(name))
        _components.append(components.MetadataComponent())
        self._entity_registry[name] = {component._name: component for component in _components}

    def get_updates(self, _id):
        return self._updates.get(_id, [])

    def get_entities(self, _type):
        return self._components.get(_type, {})

    def get_entity(self, _type, _id):
        return self._components.get(_type, {}).get(_id)

    def set_entity(self, _type, entity):
        self._components.setdefault(_type, {})[entity.pk] = entity

    def register_entity(self, entity):
        if not isinstance(entity, Entity):
            entity = Entity(**entity)
        if entity.pk is None:
            entity.pk = self._seq
            self._seq += 1
        for component in entity._components:
            self.set_entity(component, entity)

    def process(self):
        for system_cls in self._systems:
            system = system_cls()
            system.process(self)

    def import_data(self, data, updates):
        if 'seq' in data:
            self._seq = data['seq']
        for entity in (data.get('entities') or ()):
            self.register_entity(entity)
        for entity in self.get_entities('metadata').values():
            entity.validate()
        self._updates = updates

    def export_data(self):
        return {
            'seq': self._seq,
            'entities': [entity.serialize() for entity in self.get_entities('metadata').values()]
        }


class GameState:
    def __init__(self, state, updates):
        self.old = state
        self.updates = updates

        self.manager = Manager()
        self.manager.register_system(systems.UpdateSystem)
        self.manager.register_system(systems.MovementSystem)
        self.manager.register_system(systems.PopulationGrowthSystem)

        self.manager.register_entity_type('ship', [
            components.PositionComponent(),
            components.QueueComponent([Move, CargoTransfer, Scrap,]),
            components.OwnershipComponent(),
            components.PopulationComponent(),
            components.MineralInventoryComponent(),
        ])
        self.manager.register_entity_type('planet', [
            components.PositionComponent(),
            components.EnvironmentComponent(),
            components.MineralConcentrationComponent(),
            components.MineralInventoryComponent(),
            components.QueueComponent([
                BuildInstallation, Terraform, BuildStation, BuildShip, LaunchMassPacket,
            ]),
            components.OwnershipComponent(),
            components.PopulationComponent(),
        ])
        self.manager.register_entity_type('species', [
            components.SpeciesComponent(),
        ])
        Entity.register_manager(self.manager)

        self.new = {}

    def generate(self):
        self.new_headers()

        self.manager.import_data(self.old, self.updates)
        self.manager.process()
        self.new.update(self.manager.export_data())

        return self.new

    def new_headers(self):
        self.new.update(turn=self.old['turn'] + 1, width=self.old['width'])
