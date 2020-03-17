from decimal import Decimal
import random


class UpdateSystem:
    def process(self, manager):
        for _id, entity in manager.get_entities('queue').items():
            queue = entity._data['queue']
            indexed_queue = dict(enumerate(queue))

            for action in manager.get_updates(_id):
                seq = action.pop('seq')
                indexed_queue[seq] = action

            entity._data['queue'] = [action for seq, action in sorted(indexed_queue.items())]


class MovementSystem:
    def process(self, manager):
        movements = {
            _id: entity
            for _id, entity in manager.get_entities('queue').items()
            if entity._data['queue']
        }
        while movements:
            update = False
            for _id in list(movements.keys()):
                entity = movements[_id]
                move = entity._data['queue'][0]
                if 'target_id' not in move:
                    self._do_move(manager, entity, move)
                elif move['target_id'] not in movements:
                    self._do_move(manager, entity, move)
                else:
                    continue

                update = True
                del movements[_id]

            if not update:
                _id = random.choice(list(movements.keys()))
                self._do_move(manager, movements[_id], movements[_id]._data['queue'][0])
                del movements[_id]

        # drop any waypoints that have been reached
        for _id, entity in manager.get_entities('queue').items():
            if not entity._data['queue']:
                continue
            move = entity._data['queue'][0]
            x, y = entity._data['x'], entity._data['y']
            if 'target_id' in move:
                target_entity = manager.get_entity('position', move['target_id'])
                x_t, y_t = target_entity._data['x'], target_entity._data['y']
            else:
                x_t, y_t = move['x_t'], move['y_t']

            if (x, y) == (x_t, y_t):
                entity._data['queue'].pop(0)

    def _do_move(self, manager, entity, move):
        speed = move['warp'] ** 2
        x, y = entity._data['x'], entity._data['y']
        if 'target_id' in move:
            target_entity = manager.get_entity('position', move['target_id'])
            x_t, y_t = target_entity._data['x'], target_entity._data['y']
        else:
            x_t, y_t = move['x_t'], move['y_t']

        dx, dy = x_t - x, y_t - y
        D = Decimal(dx**2 + dy**2).sqrt()

        if D.to_integral_value() <= speed:
            x_new, y_new = x_t, y_t
        else:
            x_new = x + int((speed * dx / D).to_integral_value())
            y_new = y + int((speed * dy / D).to_integral_value())

        entity._data.update(x=x_new, y=y_new)
