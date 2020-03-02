from . import components, systems
from .orders import (Move, CargoTransfer, Scrap, BuildInstallation, Terraform,
                     BuildStation, BuildShip, LaunchMassPacket)


class Entity:
    def __init__(self, registry, data):
        self._data = data
        self._components = registry[data['type']]

    def __contains__(self, key):
        return key in self._components

    def serialize(self):
        data = {}
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

    def register_entity_type(self, name, components):
        if name in self._entity_registry:
            raise ValueError("{} is already a registered entity type.".format(name))
        self._entity_registry[name] = {component.name: component for component in components}

    def get_updates(self, _id):
        return self._updates.get(_id, [])

    def get_components(self, _type):
        return self._components.get(_type, {})

    def get_component(self, _type, _id):
        return self._components.get(_type, {}).get(_id)

    def set_component(self, _type, _id, entity):
        self._components.setdefault(_type, {})[_id] = entity

    def process(self):
        for system_cls in self._systems:
            system = system_cls()
            system.process(self)

    def import_data(self, data, updates):
        entities = {_id: Entity(self._entity_registry, entity) for _id, entity in (data.get('entities') or {}).items()}

        self._components['position'] = {_id: entity for _id, entity in entities.items() if 'position' in entity}
        self._components['queue'] = {_id: entity for _id, entity in entities.items() if 'queue' in entity}
        self._updates = updates

    def export_data(self):
        data = {}
        data.update((_id, entity) for _id, entity in self._components['position'].items())
        data.update((_id, entity) for _id, entity in self._components['queue'].items())

        return {'entities': {_id: entity.serialize() for _id, entity in data.items()}}


class GameState:
    def __init__(self, state, updates):
        self.old = state
        self.updates = updates

        self.manager = Manager()
        self.manager.register_system(systems.UpdateSystem)
        self.manager.register_system(systems.MovementSystem)

        self.manager.register_entity_type('ship', [
            components.PositionComponent(),
            components.QueueComponent([Move, CargoTransfer, Scrap]),
        ])
        self.manager.register_entity_type('planet', [
            components.PositionComponent(),
            components.QueueComponent([
                BuildInstallation, Terraform, BuildStation, BuildShip, LaunchMassPacket,
            ]),
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
