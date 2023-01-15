import pygame
import math as m


def lead_shot(origin, target, proj_speed, distance=None):
    p = proj_speed
    x = target.x - origin.x
    y = target.y - origin.y
    h = m.cos(target.d) * target.speed
    v = m.sin(target.d) * target.speed

    a = h ** 2 + v ** 2 - p ** 2
    b = 2 * (h * x + v * y)
    c = x ** 2 + y ** 2

    try:
        t = (-1 * b - m.sqrt(-1 * b * b - 4 * a * c)) / (2 * a)

        d = m.atan2(y + v * t, x + h * t)
    except ValueError:
        if distance is None:
            distance = m.dist((origin.x, origin.y), (target.x, target.y))
        dx = (target.x + m.cos(target.d) * target.speed * distance / proj_speed - origin.x)
        dy = (target.y + m.sin(target.d) * target.speed * distance / proj_speed - origin.y)
        d = m.atan2(dy, dx)
    return d


class Projectile:
    def __init__(self, x, y, d, target, damage):
        self.x = x
        self.y = y
        self.start_x = self.x
        self.start_y = self.y
        self.d = d
        self.damage = damage
        self.target = target

        self.intended_range = m.dist((x, y), (target.x, target.y))

        self.active = True
        self.speed = 0

    def update(self, camera):
        self.x += m.cos(self.d) * self.speed * camera.dt
        self.y += m.sin(self.d) * self.speed * camera.dt

        if m.dist((self.x, self.y), (self.target.x, self.target.y)) < 20 and self.active and self.target.active:
            self.active = False
            self.deal_damage()

        elif m.dist((self.start_x, self.start_y), (self.x, self.y)) > self.intended_range + 40:
            self.active = False

        self.map_border_collisions(camera)

    def map_border_collisions(self, camera):
        if self.x > camera.width or self.x < 0 or self.y > camera.height or self.y < 0:
            self.active = False

    def deal_damage(self):
        pass


class Shell(Projectile):
    def __init__(self, x, y, d, target, damage=5, speed=2):
        super().__init__(x, y, d, target, damage)
        self.color = {2: (0, 0, 200), 1: (200, 0, 0)}[target.team]
        self.speed = speed
        self.hit_target = False

    def deal_damage(self):
        self.target.health -= self.damage
        self.hit_target = True

    def draw(self, camera):
        a = m.atan(1 / 2)
        size = 5
        points = [(self.x + m.cos(self.d) * size, self.y + m.sin(self.d) * size),
                  (self.x + m.cos(self.d - a + m.pi) * size, self.y + m.sin(self.d - a + m.pi) * size),
                  (self.x + m.cos(self.d + a + m.pi) * size, self.y + m.sin(self.d + a + m.pi) * size)]

        pygame.draw.circle(camera.foreground, self.color, (self.x - m.cos(self.d) * size, self.y - m.sin(self.d) * size), size - 2)
        pygame.draw.polygon(camera.foreground, (128, 128, 0), points)


class Bullet(Projectile):
    def __init__(self, x, y, d, target, damage=1):
        super().__init__(x, y, d, target, damage)
        self.speed = 5

    def deal_damage(self):
        self.target.squadron.health -= self.damage

    def draw(self, camera):
        pygame.draw.line(camera.foreground, (128, 128, 0), (self.x, self.y), (self.x, self.y), 5)
