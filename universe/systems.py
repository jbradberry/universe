from decimal import Decimal


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
    N = 1000

    def _vector_to_target(self, entity, manager):
        move = entity.queue[0]
        speed = Decimal(move['warp'] ** 2) / self.N

        if 'target_id' in move:
            target_entity = manager.get_entity('position', move['target_id'])
            x_t, y_t = target_entity.x, target_entity.y
        else:
            x_t, y_t = move['x_t'], move['y_t']

        # Aim for the midpoint of the 1-light-year sector the goal is in.
        dx, dy = Decimal(x_t).to_integral_value() - entity.x, Decimal(y_t).to_integral_value() - entity.y

        D = Decimal(dx ** 2 + dy ** 2).sqrt()
        if D.to_integral_value() <= speed:
            entity.dx, entity.dy = dx, dy
        else:
            entity.dx, entity.dy = speed * dx / D, speed * dy / D

        # The naive prediction of the endpoint for this object
        remaining = self.N - self.step
        x_p = (entity.x + remaining * entity.dx).to_integral_value()
        y_p = (entity.y + remaining * entity.dy).to_integral_value()
        if 'x_p' not in entity.__dict__:
            entity.x_p, entity.y_p = x_p, y_p
        # If the projected endpoint is not stable, intercepting objects should just use Euler.
        if (entity.x_p, entity.y_p) != (x_p, y_p):
            entity.x_p, entity.y_p = None, None

    def _vector_to_projection(self, entity, manager):
        # Update the real vector of this object based on the (non-updated) observable vector of its target.
        move = entity.queue[0]
        if 'target_id' not in move:
            return

        target_entity = manager.get_entity('position', move['target_id'])
        # Only proceed with moving towards the target's projected endpoint if it is stable.
        if target_entity.x_p is None:
            return

        x_p, y_p = target_entity.x_p, target_entity.y_p
        dx, dy = x_p - entity.x, y_p - entity.y

        speed = Decimal(move['warp'] ** 2) / self.N
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
                dx, dy = entity.dx or Decimal(0), entity.dy or Decimal(0)
                entity.x, entity.y = entity.x + dx, entity.y + dy

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


class PopulationGrowth:
    def process(self, manager):
        for _id, entity in manager.get_entities('population').items():
            population = entity.population
            if entity.type == 'ship':
                continue
            species = manager.get_entity('species', entity.owner_id)
            if species is None:
                continue
            growth_rate = 1 + Decimal(species.growth_rate) / 100
            population *= growth_rate
            entity.population = population.to_integral_value()
