from collections import defaultdict
from decimal import Decimal

from . import utils


class UpdateSystem:
    def process(self, manager):
        queues = defaultdict(dict)
        for order in manager.get_entities('orders').values():
            queues[order.actor_id][order.seq] = order

        for data in manager._updates:
            action = data.pop('action')
            if action == 'create':
                if data['actor_id'] in queues and data['seq'] in queues[data['actor_id']]:
                    continue
                order = manager.register_entity(data)
                queues[order.actor_id][order.seq] = order
            elif action == 'reorder':
                if data['actor_id'] not in queues:
                    continue
                if data['seq1'] not in queues[data['actor_id']]:
                    continue
                if data['seq2'] not in queues[data['actor_id']]:
                    continue
                order1 = queues[data['actor_id']].pop(data['seq1'], None)
                order2 = queues[data['actor_id']].pop(data['seq2'], None)
                order1.seq, order2.seq = order2.seq, order1.seq
                queues[order1.actor_id][order1.seq] = order1
                queues[order2.actor_id][order2.seq] = order2
            elif action == 'update':
                if data['actor_id'] not in queues:
                    continue
                if data['seq'] not in queues[data['actor_id']]:
                    continue
                order = queues[data['actor_id']][data['seq']]
                for k, v in data.items():
                    setattr(order, k, v)
            elif action == 'delete':
                if data['actor_id'] not in queues:
                    continue
                if data['seq'] not in queues[data['actor_id']]:
                    continue
                manager.unregister_entity(queues[data['actor_id']][data['seq']])
                del queues[data['actor_id']][data['seq']]


class MovementSystem:
    N = 1000

    def _vector_to_target(self, move):
        speed = Decimal(move.warp ** 2) / self.N

        if move.target is not None:
            x_t, y_t = move.target.x, move.target.y
        else:
            x_t, y_t = move.x_t, move.y_t

        # Aim for the midpoint of the 1-light-year sector the goal is in.
        dx, dy = Decimal(x_t).to_integral_value() - move.actor.x, Decimal(y_t).to_integral_value() - move.actor.y

        D = Decimal(dx ** 2 + dy ** 2).sqrt()
        if D.to_integral_value() <= speed:
            move.actor.dx, move.actor.dy = dx, dy
        else:
            move.actor.dx, move.actor.dy = speed * dx / D, speed * dy / D

        # The naive prediction of the endpoint for this object
        remaining = self.N - self.step
        x_p = (move.actor.x + remaining * move.actor.dx).to_integral_value()
        y_p = (move.actor.y + remaining * move.actor.dy).to_integral_value()
        if not hasattr(move.actor, 'x_p'):
            move.actor.x_p, move.actor.y_p = x_p, y_p
        # If the projected endpoint is not stable, intercepting objects should just use Euler.
        if (move.actor.x_p, move.actor.y_p) != (x_p, y_p):
            move.actor.x_p, move.actor.y_p = None, None

    def _vector_to_projection(self, move):
        # Update the real vector of this object based on the (non-updated) observable vector of its target.
        if move.target is None:
            return

        # Only proceed with moving towards the target's projected endpoint if it is stable.
        if getattr(move.target, 'x_p', None) is None:
            return

        x_p, y_p = move.target.x_p, move.target.y_p
        dx, dy = x_p - move.actor.x, y_p - move.actor.y

        speed = Decimal(move.warp ** 2) / self.N
        D = Decimal(dx ** 2 + dy ** 2).sqrt()
        if D.to_integral_value() <= speed:
            move.actor.dx, move.actor.dy = dx, dy
        else:
            move.actor.dx, move.actor.dy = speed * dx / D, speed * dy / D

    def process(self, manager):
        movements = defaultdict(list)
        for move in manager.get_entities('movement_orders').values():
            movements[move.actor_id].append(move)

        movements = {_id: sorted(queue, key=lambda x: x.seq) for _id, queue in movements.items() if queue}

        for _id, entity in manager.get_entities('position').items():
            entity.x_prev, entity.y_prev = entity.x, entity.y

        for self.step in range(self.N):
            for queue in movements.values():
                self._vector_to_target(queue[0])

            for queue in movements.values():
                self._vector_to_projection(queue[0])

            for queue in movements.values():
                entity = queue[0].actor
                dx, dy = entity.dx or Decimal(0), entity.dy or Decimal(0)
                entity.x, entity.y = entity.x + dx, entity.y + dy

        for queue in movements.values():
            entity = queue[0].actor
            entity.x, entity.y = int(entity.x.to_integral_value()), int(entity.y.to_integral_value())

        # drop any waypoints that have been reached
        for queue in movements.values():
            move = queue[0]
            entity = move.actor
            x, y = entity.x, entity.y
            if move.target is not None:
                x_t, y_t = move.target.x, move.target.y
            else:
                x_t, y_t = move.x_t, move.y_t

            if (x, y) == (x_t, y_t):
                manager.unregister_entity(move)
                queue.pop(0)
                for i, order in enumerate(queue):
                    order.seq = i


class MiningSystem:
    def process(self, manager):
        for _id, entity in manager.get_entities('mineral_concentrations').items():
            species = manager.get_entity('species', entity.owner_id)
            if species is None:
                continue

            ir, bo, ge = utils.mining(species, entity)
            entity.ironium = (entity.ironium or 0) + ir
            entity.boranium = (entity.boranium or 0) + bo
            entity.germanium = (entity.germanium or 0) + ge


class PopulationGrowthSystem:
    def process(self, manager):
        for _id, entity in manager.get_entities('population').items():
            if entity.type == 'ship':
                continue
            species = manager.get_entity('species', entity.owner_id)
            if species is None:
                continue

            population = entity.population or 0
            growth_rate = Decimal(species.growth_rate) / 100
            habitability = Decimal(utils.planet_value(species, entity)) / 100
            capacity = 1_000_000 * habitability

            crowding, ratio = 1, 1
            if habitability >= 0:
                ratio = population / capacity
                if ratio > 4:
                    growth_rate = Decimal('-0.12')
                elif ratio > 1:
                    growth_rate = Decimal('-0.04') * (ratio - 1)
                elif ratio > 0.25:
                    crowding = 16 * (1 - ratio) ** 2 / 9
            else:
                # For red planets, you always lose 1/10 of the negative hab rating,
                # e.g. -45% is -4.5% per year.  See:
                # https://starsautohost.org/sahforum2/index.php?t=msg&th=5565&rid=0#msg_62828
                growth_rate = Decimal('0.10')

            population *= 1 + growth_rate * habitability * crowding
            entity.population = int(population.to_integral_value())
            if entity.population <= 0:
                del entity.population
                del entity.owner_id
