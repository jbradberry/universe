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
    N = 100

    def _vector_to_target(self, entity, manager):
        move = entity.queue[0]
        speed = Decimal(move['warp'] ** 2) / self.N

        if 'target_id' in move:
            target_entity = manager.get_entity('position', move['target_id'])
            x_t, y_t = target_entity.x, target_entity.y
        else:
            x_t, y_t = move['x_t'], move['y_t']

        dx, dy = x_t - entity.x, y_t - entity.y

        D = Decimal(dx ** 2 + dy ** 2).sqrt()
        if D.to_integral_value() <= speed:
            entity.dx, entity.dy = dx, dy
        else:
            entity.dx, entity.dy = speed * dx / D, speed * dy / D

    def _vector_to_projection(self, entity, manager):
        move = entity.queue[0]
        if 'target_id' not in move:
            return

        speed = Decimal(move['warp'] ** 2) / self.N
        target_entity = manager.get_entity('position', move['target_id'])
        x_t, y_t = target_entity.x, target_entity.y
        dx_t, dy_t = target_entity.dx or 0, target_entity.dy or 0

        remaining = self.N - self.step
        x_p, y_p = x_t + remaining * dx_t, y_t + remaining * dy_t

        dx, dy = x_p - entity.x, y_p - entity.y

        D = Decimal(dx ** 2 + dy ** 2).sqrt()
        if D.to_integral_value() <= speed:
            entity.dx, entity.dy = dx, dy
        else:
            entity.dx, entity.dy = speed * dx / D, speed * dy / D

    def process(self, manager):
        movements = {
            _id: entity
            for _id, entity in manager.get_entities('queue').items()
            if entity.queue
        }

        for _id, entity in manager.get_entities('position').items():
            entity.x_prev, entity.y_prev = entity.x, entity.y

        for self.step in range(self.N):
            for entity in movements.values():
                self._vector_to_target(entity, manager)

            for entity in movements.values():
                self._vector_to_projection(entity, manager)

            for entity in movements.values():
                entity.x, entity.y = entity.x + entity.dx, entity.y + entity.dy

        for _id, entity in movements.items():
            entity.x, entity.y = int(entity.x.to_integral_value()), int(entity.y.to_integral_value())

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
