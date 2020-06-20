from decimal import Decimal
import math


def planet_value(species, planet):
    # Algorithm taken from https://starsautohost.org/sahforum2/index.php?t=rview&th=2299&rid=0

    value, red, ideal = 0, 0, 10000
    for env in ('gravity', 'temperature', 'radiation'):
        if getattr(species, f'{env}_immune'):
            value += 10000
        else:
            radius = (getattr(species, f'{env}_max') - getattr(species, f'{env}_min')) // 2
            center = (getattr(species, f'{env}_min') + getattr(species, f'{env}_max')) // 2
            delta = abs(center - getattr(planet, env))

            if delta <= radius:  # rating is in the green
                value += (100 - 100 * delta // radius) ** 2
                margin = 2 * delta - radius
                if margin > 0:  # planet is in the first or fourth quartile for this rating
                    ideal *= radius * 2 - margin
                    ideal //= radius * 2
            else:  # rating is in the red
                red += min(delta - radius, 15)  # lethality rating cannot be over 15.

    if red != 0:
        return -red
    return int(int(math.sqrt(value / 3) + 0.9) * ideal / 10000)


def production(species, planet):
    population = Decimal(planet.population or 0)

    return int(population / species.population_per_r)


def mining(species, planet):
    population = Decimal(planet.population or 0)
    mines = planet.mines or 0
    can_operate = int(population / 10_000) * species.mines_per_pop

    mines = Decimal(min(mines, can_operate))
    capacity = int(mines * species.minerals_per_m / 10)
    ir = Decimal(planet.ironium_conc) / 100
    bo = Decimal(planet.boranium_conc) / 100
    ga = Decimal(planet.germanium_conc) / 100

    return (int(ir * capacity), int(bo * capacity), int(ga * capacity))
