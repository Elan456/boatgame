import pygame
import random

red = (255, 0, 0)
orange = (255, 95, 31)
blue = (0, 0, 255)


class Effect:
    size: float

    def __init__(self, x, y):
        self.active = True
        self.x = x
        self.y = y

        self.size = .5  # The size will increase over time


class Explosion(Effect):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.sets = random.randint(2, 5)
        self.max_size = random.randint(10, 30)

    # noinspection PyTypeChecker
    def update(self, camera):
        self.size += 1
        self.size *= 1.2
        pygame.draw.circle(camera.midground, red, (self.x, self.y), self.size, 2)
        pygame.draw.circle(camera.midground, orange, (self.x, self.y), max(0, self.size - 2), 2)
        if self.size > self.max_size:
            self.sets -= 1
            self.size = .5
            self.max_size = random.randint(10, 30)
        if self.sets == 0:
            self.active = False


class Splash(Effect):
    def __init__(self, x, y):
        super().__init__(x, y)

    def update(self, camera):
        self.size += 1
        self.size *= 1.2
        pygame.draw.circle(camera.midground, blue, (self.x, self.y), self.size, 2)
        if self.size > 10:
            self.active = False
