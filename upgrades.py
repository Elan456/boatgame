import math as m

class Upgrade:
    def __init__(self, min, max):
        self.min = min
        self.max = max
        self.k = (1 / (1 - 6)) * m.log((min / max))
        self.a = self.min * (m.e ** (-1 * self.k * 1))

    def get_value(self, stage):
        """
        Get what the value of this upgrade should be depending on what stage this upgrade is at. (1 to 5)
        """
        return self.a * m.e ** (self.k * stage)


class Upgrades:
    pass


class Boat(Upgrades):
    turn_rate = Upgrade(.005, .1)


class AbstractCarrier(Boat):
    health = Upgrade(400, 10000)
    speed = Upgrade(.2, 1.5)
    bomber_count = Upgrade(3, 32)
    bomber_squad_size = Upgrade(1, 17)
    fighter_count = Upgrade(2, 32)
    fighter_squad_size = Upgrade(1, 8)
    aa_power = Upgrade(.5, 8)


class AbstractDestroyer(Boat):
    health = Upgrade(200, 5000)
    speed = Upgrade(.3, 2)
    aa_power = Upgrade(.3, 4)
    gun_damage = Upgrade(50, 1000)
    gun_range = Upgrade(100, 600)
    gun_fire_rate = Upgrade(.001, .1)
    shell_speed = Upgrade(1.5, 10)


class Plane(Upgrades):
    pass


class AbstractBomber(Plane):
    damage = Upgrade(100, 2500)
    health = Upgrade(40, 500)
    speed = Upgrade(1, 4)
    turn_rate = Upgrade(.02, .17)
    fuel = Upgrade(200, 5000)


class AbstractFighter(Plane):
    damage = Upgrade(1, 100)
    health = Upgrade(20, 300)
    speed = Upgrade(1.1, 4.1)
    turn_rate = Upgrade(.03, .17)
    fuel = Upgrade(200, 3000)


wrapper = {"AbstractCarrier": AbstractCarrier,
           "AbstractDestroyer": AbstractDestroyer,
           "AbstractBomber": AbstractBomber,
           "AbstractFighter": AbstractFighter}


def get_class(name):
    return wrapper[name]
