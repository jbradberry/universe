from __future__ import division
from decimal import Decimal
import random


class GameState(object):
    def __init__(self, state, updates):
        self.old = state
        self.updates = updates

        self.new = {}

    def generate(self):
        self.new_headers()
        self.merge_updates()
        self.process_movement()
        self.post_process()

        return self.new

    def new_headers(self):
        self.new.update(turn=self.old['turn'] + 1, width=self.old['width'])

    def merge_updates(self):
        indexed_actions = dict(
            (loc_id, dict(enumerate(action_list)))
            for loc_id, action_list in self.old['actions'].iteritems()
        )

        for action in self.updates:
            loc_id = action.pop('locatable_id')
            seq = action.pop('seq')
            indexed_actions.setdefault(loc_id, {})[seq] = action

        self.actions = dict(
            (loc_id, [action for seq, action in sorted(actions.iteritems())])
            for loc_id, actions in indexed_actions.iteritems()
        )

    def process_movement(self):
        movements = dict((loc_id, actions[0])
                         for loc_id, actions in self.actions.iteritems()
                         if actions)
        while movements:
            update = False
            for loc_id in list(movements.iterkeys()):
                move = movements[loc_id]
                if 'target_id' not in move:
                    self._do_move(loc_id, move)
                elif move['target_id'] not in movements:
                    self._do_move(loc_id, move)
                else:
                    continue

                update = True
                del movements[loc_id]

            if not update:
                loc_id = random.choice(movements.keys())
                self._do_move(loc_id, movements[loc_id])
                del movements[loc_id]

        # drop any waypoints that have been reached
        for loc_id, actions in self.actions.iteritems():
            move = actions[0]
            locatable = self.old['locatables'][loc_id]
            x, y, z = locatable['x'], locatable['y'], locatable['z']
            if 'target_id' in move:
                target = self.old['locatables'][move['target_id']]
                x_t, y_t, z_t = target['x'], target['y'], target['z']
            else:
                x_t, y_t, z_t = move['x_t'], move['y_t'], move['z_t']

            if (x, y, z) == (x_t, y_t, z_t):
                actions.pop(0)

        self.new['locatables'] = self.old['locatables']
        self.new['actions'] = self.actions

    def _do_move(self, loc_id, move):
        locatable = self.old['locatables'][loc_id]

        speed = move['speed'] ** 2
        x, y, z = locatable['x'], locatable['y'], locatable['z']
        if 'target_id' in move:
            target = self.old['locatables'][move['target_id']]
            x_t, y_t, z_t = target['x'], target['y'], target['z']
        else:
            x_t, y_t, z_t = move['x_t'], move['y_t'], move['z_t']

        dx, dy, dz = x_t - x, y_t - y, z_t - z
        D = Decimal(dx**2 + dy**2 + dz**2).sqrt()

        if D.to_integral_value() <= speed:
            x_new, y_new, z_new = x_t, y_t, z_t
        else:
            x_new = x + int((speed * dx / D).to_integral_value())
            y_new = y + int((speed * dy / D).to_integral_value())
            z_new = z + int((speed * dz / D).to_integral_value())

        locatable.update(x=x_new, y=y_new, z=z_new)

    def post_process(self):
        loc_ids = [
            loc_id for loc_id, actions in self.new['actions'].iteritems()
            if not actions
        ]

        for loc_id in loc_ids:
            del self.new['actions'][loc_id]
