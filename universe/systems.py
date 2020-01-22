from decimal import Decimal
import random


class UpdateSystem:
    def process(self, manager):
        for entity, queue in manager.get_components('queue').items():
            indexed_queue = dict(enumerate(queue))

            for action in manager.get_updates(entity):
                seq = action.pop('seq')
                indexed_queue[seq] = action

            manager.set_component('queue', entity, [action for seq, action in sorted(indexed_queue.items())])


class MovementSystem:
    def process(self, manager):
        movements = {
            entity: actions[0]
            for entity, actions in manager.get_components('queue').items()
            if actions
        }
        while movements:
            update = False
            for entity in list(movements.keys()):
                move = movements[entity]
                if 'target_id' not in move:
                    self._do_move(manager, entity, move)
                elif move['target_id'] not in movements:
                    self._do_move(manager, entity, move)
                else:
                    continue

                update = True
                del movements[entity]

            if not update:
                entity = random.choice(list(movements.keys()))
                self._do_move(manager, entity, movements[entity])
                del movements[entity]

        # drop any waypoints that have been reached
        for entity, actions in manager.get_components('queue').items():
            if not actions:
                continue
            move = actions[0]
            position = manager.get_component('position', entity)
            x, y = position['x'], position['y']
            if 'target_id' in move:
                target = manager.get_component('position', move['target_id'])
                x_t, y_t = target['x'], target['y']
            else:
                x_t, y_t = move['x_t'], move['y_t']

            if (x, y) == (x_t, y_t):
                actions.pop(0)
                manager.set_component('queue', entity, actions)

    def _do_move(self, manager, entity, move):
        position = manager.get_component('position', entity)
        speed = move['warp'] ** 2
        x, y = position['x'], position['y']
        if 'target_id' in move:
            target = manager.get_component('position', move['target_id'])
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

        position.update(x=x_new, y=y_new)
        manager.set_component('position', entity, position)
