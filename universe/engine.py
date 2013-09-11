from __future__ import division
from decimal import Decimal


class GameState(object):
    def __init__(self, state, updates):
        self.old = state
        self.updates = updates

        self.new = {}

    def generate(self):
        self.new_headers()
        self.merge_updates()
        self.process_movement()

        return self.new

    def new_headers(self):
        self.new.update(turn=self.old['turn'] + 1, width=self.old['width'])

    def merge_updates(self):
        # deduplicate and index by locatable_id + sequence number
        indexed_actions = dict(
            ((loc_id, action['seq']), action)
            for loc_id, action in self.old['actions'].iteritems()
        )

        indexed_actions.update(
            ((action['locatable_id'], action['seq']), action)
            for action in self.updates
        )

        self.actions = {}
        for (loc_id, loc_seq), action in sorted(indexed_actions.iteritems()):
            self.actions.setdefault(loc_id, []).append(action)

    def process_movement(self):
        locatables = []
        for locatable in self.old['locatables']:
            new_loc = locatable.copy()
            if new_loc['id'] in self.actions:
                action = self.actions[new_loc['id']][0]

                x, y, z = new_loc['x'], new_loc['y'], new_loc['z']
                x_t, y_t, z_t = action['x_t'], action['y_t'], action['z_t']
                speed = action['speed'] ** 2

                dx, dy, dz = x_t - x, y_t - y, z_t - z
                D = Decimal(dx**2 + dy**2 + dz**2).sqrt()

                if D.to_integral_value() <= speed:
                    x_new, y_new, z_new = x_t, y_t, z_t
                    self.actions[new_loc['id']].pop(0)
                    if not self.actions[new_loc['id']]:
                        del self.actions[new_loc['id']]
                else:
                    x_new = x + int((speed * dx / D).to_integral_value())
                    y_new = y + int((speed * dy / D).to_integral_value())
                    z_new = z + int((speed * dz / D).to_integral_value())

                new_loc.update(x=x_new, y=y_new, z=z_new)

            locatables.append(new_loc)

        self.new['locatables'] = locatables
        self.new['actions'] = self.actions
