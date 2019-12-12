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
        indexed_actions = {
            loc_id: dict(enumerate(action_list))
            for loc_id, action_list in self.old['actions'].items()
        }

        for action in self.updates:
            loc_id = action.pop('locatable_id')
            seq = action.pop('seq')
            indexed_actions.setdefault(loc_id, {})[seq] = action

        self.actions = {
            loc_id: [action for seq, action in sorted(actions.items())]
            for loc_id, actions in indexed_actions.items()
        }

    def process_movement(self):
        movements = {
            loc_id: actions[0]
            for loc_id, actions in self.actions.items()
            if actions
        }
        while movements:
            update = False
            for loc_id in list(movements.keys()):
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
                loc_id = random.choice(list(movements.keys()))
                self._do_move(loc_id, movements[loc_id])
                del movements[loc_id]

        # drop any waypoints that have been reached
        for loc_id, actions in self.actions.items():
            move = actions[0]
            locatable = self.old['locatables'][loc_id]
            x, y = locatable['x'], locatable['y']
            if 'target_id' in move:
                target = self.old['locatables'][move['target_id']]
                x_t, y_t = target['x'], target['y']
            else:
                x_t, y_t = move['x_t'], move['y_t']

            if (x, y) == (x_t, y_t):
                actions.pop(0)

        self.new['locatables'] = self.old['locatables']
        self.new['actions'] = self.actions

    def _do_move(self, loc_id, move):
        locatable = self.old['locatables'][loc_id]

        speed = move['speed'] ** 2
        x, y = locatable['x'], locatable['y']
        if 'target_id' in move:
            target = self.old['locatables'][move['target_id']]
            x_t, y_t = target['x'], target['y']
        else:
            x_t, y_t = move['x_t'], move['y_t']

        dx, dy = x_t - x, y_t - y
        D = Decimal(dx**2 + dy**2).sqrt()

        if D.to_integral_value() <= speed:
            x_new, y_new = x_t, y_t
        else:
            x_new = x + int((speed * dx / D).to_integral_value())
            y_new = y + int((speed * dy / D).to_integral_value())

        locatable.update(x=x_new, y=y_new)

    def post_process(self):
        loc_ids = [
            loc_id for loc_id, actions in self.new['actions'].items()
            if not actions
        ]

        for loc_id in loc_ids:
            del self.new['actions'][loc_id]
