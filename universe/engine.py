
def generate(state, updates):
    new_state = {'turn': state['turn'] + 1, 'width': state['width']}
    new_updates = {}

    new_state['locatables'] = tuple(
        locatable.copy() for locatable in state['locatables']
    )

    return new_state, new_updates
