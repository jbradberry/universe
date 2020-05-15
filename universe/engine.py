from . import components, systems
from .orders import (Move, CargoTransfer, Scrap, BuildInstallation, Terraform,
                     BuildStation, BuildShip, LaunchMassPacket)


class Entity:
    def __init__(self, registry, data):
        self._data = data
        self._components = registry[data['type']]

        for _type, component in self._components.items():
            component.validate(data)

    def __getattr__(self, name):
        for component in self.__dict__.get('_components', {}).values():
            if name in component._fields:
                return self.__dict__['_data'].get(name)
        try:
            return self.__dict__[name]
        except KeyError:
            raise AttributeError(f"{self.__class__.__name__!r} object has no attribute {name!r}")

    def __setattr__(self, name, value):
        for component in self.__dict__.get('_components', {}).values():
            if name in component._fields:
                self.__dict__['_data'][name] = value
        self.__dict__[name] = value

    def __delattr__(self, name):
        for component in self.__dict__.get('_components', {}).values():
            if name in component._fields:
                del self.__dict__['_data'][name]
        del self.__dict__[name]

    def __contains__(self, key):
        return key in self._components

    def serialize(self):
        data = {'type': self._data['type']}
        for _type, component in self._components.items():
            data.update(component.serialize(self._data))
        return data


class Manager:
    def __init__(self):
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

    def set_entity(self, _type, _id, entity):
        self._components.setdefault(_type, {})[_id] = entity

    def register_entity(self, _id, entity):
        entity_obj = Entity(self._entity_registry, entity)
        for component in entity_obj._components:
            self._components.setdefault(component, {})[_id] = entity_obj

    def process(self):
        for system_cls in self._systems:
            system = system_cls()
            system.process(self)

    def import_data(self, data, updates):
        for _id, entity in (data.get('entities') or {}).items():
            self.register_entity(_id, entity)
        self._updates = updates

    def export_data(self):
        data = {_id: entity for _id, entity in self._components.get('metadata', {}).items()}

        return {'entities': {_id: entity.serialize() for _id, entity in data.items()}}


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

        self.new = {}

    def generate(self):
        self.new_headers()

        self.manager.import_data(self.old, self.updates)
        self.manager.process()
        self.new.update(self.manager.export_data())

        return self.new

    def new_headers(self):
        self.new.update(turn=self.old['turn'] + 1, width=self.old['width'])
