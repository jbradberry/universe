from __future__ import division
from decimal import Decimal


def generate(state, updates):
    new_state = {'turn': state['turn'] + 1, 'width': state['width']}

    update_by_id_seq = dict(((update['locatable_id'], update['seq']), update)
                            for update in updates)

    update_by_id = {}
    for (loc_id, loc_seq), update in sorted(update_by_id_seq.iteritems()):
        update_by_id.setdefault(loc_id, []).append(update)

    new_locatables = []
    for locatable in state['locatables']:
        new_loc = locatable.copy()
        if new_loc['id'] in update_by_id:
            update = update_by_id[new_loc['id']][0]
            x, y, z = new_loc['x'], new_loc['y'], new_loc['z']
            x_t, y_t, z_t = update['x_t'], update['y_t'], update['z_t']
            # REVIEW: the warp-to-speed calculation should be a
            # function brought in by the ruleset or game config
            speed = update['speed'] ** 2

            dx = x_t - x
            dy = y_t - y
            dz = z_t - z
            D = Decimal(dx**2 + dy**2 + dz**2).sqrt()

            if D.to_integral_value() <= speed:
                x_new, y_new, z_new = x_t, y_t, z_t
                update_by_id[new_loc['id']].pop(0)
            else:
                x_new = x + int((speed * dx / D).to_integral_value())
                y_new = y + int((speed * dy / D).to_integral_value())
                z_new = z + int((speed * dz / D).to_integral_value())

            new_loc.update(x=x_new, y=y_new, z=z_new)
        new_locatables.append(new_loc)

    new_state['locatables'] = new_locatables

    new_updates = [update for loc_id, loc_updates in update_by_id.iteritems()
                   for update in loc_updates]

    return new_state, new_updates
