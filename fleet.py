"""
The fleet system is for storing the player's boats and their upgrades for usage across levels
All of the abstract boat classes are called abstract because they are not actually equipped with methods to fight in battle.
The real boats can be found in the boat.py file.
The abstract boats are only used to store upgrade values. When an actual battle begins, a real boat will be spawned in correlation
to each abstract boat using the abstract boat's values.
"""

import math as m
import pygame
import pgt
import upgrades
import random

size = 40
psize = 10
blue = (0, 0, 255)


class Fleet:
    def __init__(self):
        self.boats = [AbstractDestroyer()]
        self.carrier_count = sum([1 if isinstance(v, AbstractCarrier) else 0 for v in self.boats])
        self.destroyer_count = sum([1 if isinstance(v, AbstractDestroyer) else 0 for v in self.boats])

        self.bombers = AbstractBomber()
        self.fighters = AbstractFighter()
        self.entities = [self.bombers, self.fighters] + self.boats
        self.fx = 0
        self.fy = 0
        self.bx = 0
        self.by = 0

        self.level = 1  # What level does the player need to beat next
        self.money = 10  # How much money the player has

    def add_new_carrier(self):
        self.boats.append(AbstractCarrier())
        self.entities = [self.bombers, self.fighters] + self.boats
        self.carrier_count += 1

    def add_new_destroyer(self):
        self.boats.append(AbstractDestroyer())
        self.entities = [self.bombers, self.fighters] + self.boats
        self.destroyer_count += 1


class AbstractEntity:
    def __init__(self):
        self.upgrade_list = ["health",
                             "speed",
                             "turn_rate",
                             "aa_power",
                             "bomber_count",
                             "bomber_squad_size",
                             "fighter_count",
                             "fighter_squad_size",
                             "gun_damage",
                             "gun_range",
                             "gun_fire_rate",
                             "shell_speed",
                             "fuel",
                             "damage"]

        self.upgrade_stage = {}
        for u in self.upgrade_list:
            self.upgrade_stage[u] = 1  # Starting all upgrades at 1
        for u in self.upgrade_list:
            self.set_upgrade_value_from_stage(u)

        self.number_of_upgrades = len(self.upgrade_stage)
        self.x = 0
        self.y = 0

    def random_upgrade(self):
        """
        Upgrades one of the upgrades randomly, used for infinite mode, sometimes the upgrade is not applicable, so what
        """
        self.upgrade(random.choice(self.upgrade_list))

    def set_upgrade_value_from_stage(self, name):
        try:
            self.__setattr__(name,
                             getattr(upgrades.get_class(self.__class__.__name__), name).get_value(
                                 self.upgrade_stage[name]))
        except AttributeError:
            pass

    def upgrade(self, name):
        if self.upgrade_stage[name] < 6:
            self.upgrade_stage[name] += 1

            self.set_upgrade_value_from_stage(name)


class AbstractBoat(AbstractEntity):
    def __init__(self):
        super().__init__()


class AbstractCarrier(AbstractBoat):
    def __init__(self):
        super().__init__()

    def draw(self, camera):
        x = self.x
        y = self.y
        surface = camera.ui
        d = m.pi / 2
        a = m.atan(1 / 2)
        points = [(x + m.cos(d - a) * size, y + m.sin(d - a) * size),
                  (x + m.cos(d) * size * 1.7, y + m.sin(d) * size * 1.7),
                  (x + m.cos(d + a - .4) * size, y + m.sin(d + a - .4) * size),
                  (x + m.cos(d + a) * size, y + m.sin(d + a) * size),
                  (x + m.cos(d - a + m.pi) * size, y + m.sin(d - a + m.pi) * size),
                  (x + m.cos(d + a + m.pi) * size, y + m.sin(d + a + m.pi) * size)]
        pygame.draw.polygon(surface, blue, points, 1)
        pgt.text(surface, (x - 25, y - 65), str(m.ceil(self.bomber_count)), (128, 128, 0), 15, "right")
        pgt.text(surface, (x + 14, y - 65), str(m.ceil(self.fighter_count)), (128, 128, 128), 15, "right")


class AbstractDestroyer(AbstractBoat):
    def __init__(self):
        super().__init__()

    def draw(self, camera):
        x = self.x
        y = self.y

        surface = camera.ui
        d = m.pi / 2
        a = m.atan(1 / 3)
        dsize = size * .7
        points = [(x + m.cos(d - a) * dsize, y + m.sin(d - a) * dsize),  # Top left
                  (x + m.cos(d) * dsize * 1.7, y + m.sin(d) * dsize * 1.7),  # Tip of triangle
                  (x + m.cos(d + a) * dsize, y + m.sin(d + a) * dsize),  # Top right
                  (x + m.cos(d - a + m.pi) * dsize, y + m.sin(d - a + m.pi) * dsize),
                  (x + m.cos(d + m.pi) * dsize * 1.2, y + m.sin(d + m.pi) * dsize * 1.2),
                  (x + m.cos(d + a + m.pi) * dsize, y + m.sin(d + a + m.pi) * dsize)]

        pygame.draw.polygon(surface, blue, points, 1)


class AbstractPlane(AbstractEntity):
    def __init__(self):
        super().__init__()


class AbstractBomber(AbstractPlane):
    def __init__(self, health=20, speed=.5, turn_rate=.02, fuel=200, damage=1):
        super().__init__()

    def draw(self, camera):
        x = self.x
        y = self.y
        a = m.atan(1 / 1.5)
        d = m.pi / 2
        points = [(x + m.cos(d) * psize, y + m.sin(d) * psize),
                  (x + m.cos(d - a + m.pi) * psize, y + m.sin(d - a + m.pi) * psize),
                  (x - m.cos(d) * psize * 1.5, y - m.sin(d) * psize * 1.5),
                  (x + m.cos(d + a + m.pi) * psize, y + m.sin(d + a + m.pi) * psize)]

        pygame.draw.polygon(camera.ui, blue, points, 1)


class AbstractFighter(AbstractPlane):
    def __init__(self):
        super().__init__()

    def draw(self, camera):
        x = self.x
        y = self.y
        a = m.atan(1 / 2)
        d = m.pi / 2
        points = [(x + m.cos(d) * psize, y + m.sin(d) * psize),
                  (x + m.cos(d - a + m.pi) * psize, y + m.sin(d - a + m.pi) * psize),
                  (x + m.cos(d + a + m.pi) * psize, y + m.sin(d + a + m.pi) * psize)]

        pygame.draw.polygon(camera.ui, blue, points, 1)
