from decimal import Decimal
import random


class UpdateSystem:
    def process(self, manager):
        for _id, entity in manager.get_entities('queue').items():
            queue = entity.queue
            indexed_queue = dict(enumerate(queue))

            for action in manager.get_updates(_id):
                seq = action.pop('seq')
                indexed_queue[seq] = action

            entity.queue = [action for seq, action in sorted(indexed_queue.items())]


class MovementSystem:
    def process(self, manager):
        movements = {
            _id: entity
            for _id, entity in manager.get_entities('queue').items()
            if entity.queue
        }
        while movements:
            update = False
            for _id in list(movements.keys()):
                entity = movements[_id]
                move = entity.queue[0]
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
                self._do_move(manager, movements[_id], movements[_id].entity.queue[0])
                del movements[_id]

        # drop any waypoints that have been reached
        for _id, entity in manager.get_entities('queue').items():
            if not entity.queue:
                continue
            move = entity.queue[0]
            x, y = entity.x, entity.y
            if 'target_id' in move:
                target_entity = manager.get_entity('position', move['target_id'])
                x_t, y_t = target_entity.x, target_entity.y
            else:
                x_t, y_t = move['x_t'], move['y_t']

            if (x, y) == (x_t, y_t):
                entity.queue.pop(0)

    def _do_move(self, manager, entity, move):
        speed = move['warp'] ** 2
        x, y = entity.x, entity.y
        if 'target_id' in move:
            target_entity = manager.get_entity('position', move['target_id'])
            x_t, y_t = target_entity.x, target_entity.y
        else:
            x_t, y_t = move['x_t'], move['y_t']

        dx, dy = x_t - x, y_t - y
        D = Decimal(dx**2 + dy**2).sqrt()

        if D.to_integral_value() <= speed:
            x_new, y_new = x_t, y_t
        else:
            x_new = x + int((speed * dx / D).to_integral_value())
            y_new = y + int((speed * dy / D).to_integral_value())

        entity.x = x_new
        entity.y = y_new
