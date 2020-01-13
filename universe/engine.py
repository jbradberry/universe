from . import components, systems
from .orders import (Move, CargoTransfer, Scrap, BuildInstallation, Terraform,
                     BuildStation, BuildShip, LaunchMassPacket)


class Manager:
    def __init__(self):
        self._components = {}
        self._systems = []

        self._entity_registry = {}

    def register_system(self, system):
        self._systems.append(system)

    def register_entity_type(self, name, components):
        if name in self._entity_registry:
            raise ValueError("{} is already a registered entity type.".format(name))
        self._entity_registry[name] = components

    def get_components(self, _type):
        return self._components.get(_type, {})

    def get_component(self, _type, entity):
        return self._components.get(_type, {}).get(entity)

    def set_component(self, _type, entity, component):
        self._components.setdefault(_type, {})[entity] = component

    def process(self):
        for system_cls in self._systems:
            system = system_cls()
            system.process(self)

    def import_data(self, data, updates):
        self._components['position'] = {k: dict(v) for k, v in (data.get('locatables') or {}).items()}
        self._components['queue'] = {k: list(v) for k, v in (data.get('actions') or {}).items()}
        self._components['update'] = {k: list(v) for k, v in (updates or {}).items()}

    def export_data(self):
        data = {}
        data['locatables'] = {k: dict(v) for k, v in self._components['position'].items()}
        data['actions'] = {k: list(v) for k, v in self._components['queue'].items()}

        return data


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

        self.post_process()

        return self.new

    def new_headers(self):
        self.new.update(turn=self.old['turn'] + 1, width=self.old['width'])

    def post_process(self):
        loc_ids = [
            loc_id for loc_id, actions in self.new['actions'].items()
            if not actions
        ]

        for loc_id in loc_ids:
            del self.new['actions'][loc_id]
