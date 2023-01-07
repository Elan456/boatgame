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

size = 20
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
        self.money = 100  # How much money the player has

    def add_new_carrier(self):

        self.boats.append(AbstractCarrier())
        self.entities = [self.bombers, self.fighters] + self.boats
        self.carrier_count += 1

    def add_new_destroyer(self):
        self.boats.append(AbstractDestroyer())
        self.entities = [self.bombers, self.fighters] + self.boats
        self.destroyer_count += 1


class AbstractEntity:
    def __init__(self, health, speed, turn_rate):
        self.health = health
        self.speed = speed
        self.turn_rate = turn_rate
        self.upgrade_counts = {"health": 0,
                               "speed": 0,
                               "turn_rate": 0,
                               "aa_power": 0,
                               "bomber_count": 0,
                               "bomber_squad_size": 0,
                               "fighter_count": 0,
                               "fighter_squad_size": 0,
                               "gun_damage": 0,
                               "gun_range": 0,
                               "gun_fire_rate": 0,
                               "fuel": 0,
                               "damage": 0}
        self.x = 0
        self.y = 0


class AbstractBoat(AbstractEntity):
    def __init__(self, health, speed, turn_rate, aa_power):
        super().__init__(health, speed, turn_rate)
        self.aa_power = aa_power


class AbstractCarrier(AbstractBoat):
    def __init__(self, health=1000, speed=.2, turn_rate=.005, aa_power=.5,
                 bomber_count=3, bomber_squad_size=1, fighter_count=2, fighter_squad_size=1):
        super().__init__(health, speed, turn_rate, aa_power)
        self.fighter_squad_size = fighter_squad_size
        self.fighter_count = fighter_count
        self.bomber_squad_size = bomber_squad_size
        self.bomber_count = bomber_count

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
        pgt.text(surface, (x - 25, y - 65), str(self.bomber_count), (128, 128, 0), 15, "right")
        pgt.text(surface, (x + 14, y - 65), str(self.fighter_count), (128, 128, 128), 15, "right")


class AbstractDestroyer(AbstractBoat):
    def __init__(self, health=200, speed=.3, turn_rate=.01, aa_power=.2, gun_damage=1, gun_range=50, gun_fire_rate=.001):
        super().__init__(health, speed, turn_rate, aa_power)
        self.gun_fire_rate = gun_fire_rate
        self.gun_range = gun_range
        self.gun_damage = gun_damage

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
    def __init__(self, health, speed, turn_rate, fuel, damage):
        super().__init__(health, speed, turn_rate)
        self.fuel = fuel
        self.damage = damage


class AbstractBomber(AbstractPlane):
    def __init__(self, health=20, speed=.5, turn_rate=.02, fuel=200, damage=1):
        super().__init__(health, speed, turn_rate, fuel, damage)

    def draw(self, camera):
        x = self.x
        y = self.y
        a = m.atan(1 / 1.5)
        d = m.pi / 2
        points = [(x + m.cos(d) * size, y + m.sin(d) * size),
                  (x + m.cos(d - a + m.pi) * size, y + m.sin(d - a + m.pi) * size),
                  (x - m.cos(d) * size * 1.5, y - m.sin(d) * size * 1.5),
                  (x + m.cos(d + a + m.pi) * size, y + m.sin(d + a + m.pi) * size)]

        pygame.draw.polygon(camera.ui, blue, points, 1)


class AbstractFighter(AbstractPlane):
    def __init__(self, health=10, speed=.6, turn_rate=.03, fuel=300, damage=1):
        super().__init__(health, speed, turn_rate, fuel, damage)

    def draw(self, camera):
        x = self.x
        y = self.y
        a = m.atan(1 / 2)
        d = m.pi / 2
        points = [(x + m.cos(d) * size, y + m.sin(d) * size),
                  (x + m.cos(d - a + m.pi) * size, y + m.sin(d - a + m.pi) * size),
                  (x + m.cos(d + a + m.pi) * size, y + m.sin(d + a + m.pi) * size)]

        pygame.draw.polygon(camera.ui, blue, points, 1)
