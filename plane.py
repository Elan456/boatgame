import pygame
import random
import math as m
from status_bar import draw_bar
from projectile import *

size = 10


class Squadron:
    def __init__(self, origin_boat, speed, team, plane_count, target_boat, fuel, hpp, turn_rate, global_projs):
        self.global_projs = global_projs
        self.turn_rate = turn_rate
        self.distance_target_boat = None
        self.origin_boat = origin_boat
        self.plane_count = plane_count
        self.planes = []
        self.target_boat = target_boat
        self.fuel = fuel
        self.max_fuel = fuel
        self.orbit_direction = 1
        self.team = team
        self.speed = speed
        self.hp = hpp

        self.max_health = plane_count * hpp  # hpp is health per plane
        self.health = self.max_health

        self.active = True

        self.mode = "ftb"  # Fly to boat
        self.x, self.y = origin_boat.x + m.cos(origin_boat.d) * 10, origin_boat.y + m.sin(origin_boat.d) * 10

        self.dd = m.atan2(target_boat.y - self.y, target_boat.x - self.x)
        self.d = origin_boat.d

        self.generate_inital_planes()

    # ABSTRACT
    def new_plane(self, fd, fr):
        pass

    def generate_inital_planes(self):
        ppc = 1  # Planes per circle
        fd = 0  # Formation direction
        fr = 0  # Formation radius
        cc = 0
        for c in range(self.plane_count):
            if cc % ppc == 0:
                fr += 30
                ppc += 5
                cc = 0
            cc += 1

            fd += 2 * m.pi / ppc
            self.planes.append(self.new_plane(fd, fr))

    def ftb(self):  # Fly to boat, calculates the angle
        # Adjusting course to make sure we continue towards the targeted boat
        lead_x = self.target_boat.x + m.cos(self.target_boat.d) * self.target_boat.speed * 100
        lead_y = self.target_boat.y + m.sin(self.target_boat.d) * self.target_boat.speed * 100
        if self.distance_target_boat > 100:  # Lead the boat when it's far away
            self.dd = m.atan2(lead_y - self.y, lead_x - self.x)
        else:
            self.dd = m.atan2(self.target_boat.y - self.y, self.target_boat.x - self.x)

    def orbit(self):  # Flying around the target boat, if the distance becomes too great, ftb is activated
        self.dd += self.turn_rate / 3 * self.orbit_direction

        if m.dist((self.x, self.y), (self.target_boat.x, self.target_boat.y)) > 100:
            self.mode = "ftb"
        if not self.target_boat.active:
            self.mode = "rtb"  # Return to base if the boat you are meant to orbit is dead
            # Manuevring the planes back to the target boat if they orbit too far

    def rtb(self):
        # Desired x and y
        dx = self.origin_boat.x + m.cos(self.origin_boat.d) * -100
        dy = self.origin_boat.y + m.sin(self.origin_boat.d) * -100
        self.dd = m.atan2(dy - self.y,
                          dx - self.x)
        # Checking if they have reached their home boat yet
        if m.dist((self.x, self.y), (dx, dy)) < 10:
            self.mode = "landing"  # Marks coming in for landing

    def landing(self):

        # Desired x and y
        dx = self.origin_boat.x
        dy = self.origin_boat.y
        self.dd = m.atan2(dy - self.y,
                          dx - self.x)
        # Checking if they have reached their home boat yet
        if m.dist((self.x, self.y), (dx, dy)) < 10:
            self.mode = "done"  # Marks coming in for landing

    def purge_planes(self):
        # Removing planes based on damage taken
        while self.health < self.hp * (len(self.planes) - 1) and len(self.planes) > 0:
            self.planes.pop(random.randint(0, len(self.planes) - 1))

        if len(self.planes) < 1:
            self.mode = "done"
            self.active = False

    def general_update(self, camera):
        self.distance_target_boat = m.dist((self.x, self.y), (self.target_boat.x, self.target_boat.y))
        self.fuel -= 1 * camera.dt
        self.purge_planes()
        if len(self.planes) > 0:
            self.calc_position()
            if self.mode != "dgft" and self.mode != "bomb":  # Do not move the squadron as one unit during a dogfight
                self.move_squadron(camera)
                self.turn_towards_dd()
            if self.fuel < 0 and self.mode != "landing":  # Out of fuel time to return to the carrier they came from
                self.mode = "rtb"

            if self.mode == "rtb" or self.mode == "landing":  # Return to home carrier
                if not self.origin_boat.active:  # Checking if the carrier exists
                    self.mode = "done"  # Die if not
                    self.active = False
                else:
                    if self.mode == "rtb":
                        self.rtb()
                    else:
                        self.landing()

            elif self.mode == "ftb":  # Fly to targeted boat
                if not self.target_boat.active:  # Return if your target is already dead
                    self.mode = "rtb"
                self.ftb()

            elif self.mode == "orbit":
                self.orbit()

    def calc_position(self):
        self.x = 0
        self.y = 0
        for p in self.planes:  # Recalculating the x and y of the squadron
            # Calculating the average position of our planes to know where the 'squadron' generally is
            self.x += p.x
            self.y += p.y

        self.x /= len(self.planes)
        self.y /= len(self.planes)

    def move_squadron(self, camera):
        for p in self.planes:  # Recalculating the x and y of the squadron
            p.formation_update(camera, self.x, self.y, self.d)

    def turn_towards_dd(self):
        # Turning the squadron towards their desired direction
        if m.cos(self.dd) * m.sin(self.d) > m.sin(self.dd) * m.cos(self.d):
            self.d -= self.turn_rate
        else:
            self.d += self.turn_rate

    def draw(self, camera):
        for p in self.planes:
            p.draw(camera)
        pygame.draw.circle(camera.foreground, (128, 128, 0), (self.x, self.y), 2, 1)
        draw_bar(camera.foreground, self.x, self.y - 40, self.fuel, self.max_fuel, (204, 102, 0))
        self.draw_health_bar(camera.foreground)

    def draw_health_bar(self, surface):
        draw_bar(surface, self.x, self.y - 50, self.health, self.max_health, (255, 0, 0))


class BomberSquadron(Squadron):
    def __init__(self, origin_boat, speed, team, plane_count, target_boat, bomb_damage, fuel, hpp, turn_rate,
                 global_projs):
        self.bomb_damage = bomb_damage
        super().__init__(origin_boat, speed, team, plane_count, target_boat, fuel, hpp, turn_rate, global_projs)

    def update(self, camera):
        self.general_update(camera)  # Update for things that apply to both fighters and bombers squadrons

        if self.mode == "ftb":
            if m.dist((self.x, self.y), (self.target_boat.x, self.target_boat.y)) < self.speed * 200:
                self.mode = "bomb"

        elif self.mode == "bomb":
            done_bombing = True  # Until proven false
            for p in self.planes:
                p.bombing_update(camera)
                if p.active and p.has_bomb:  # Does this plane still need to use their bomb?
                    done_bombing = False
            if done_bombing:
                self.mode = "rtb"

        elif self.mode == "rtb":
            if m.dist((self.x, self.y), (self.origin_boat.x, self.origin_boat.y)) < 10:
                self.mode = "done"

    def new_plane(self, fd, fr):
        sx = m.cos(fd) * fr
        sy = m.sin(fd) * fr
        return Bomber(self.x + sx, self.y + sy, sx, sy, self.d, self.speed, self.team, self.bomb_damage, self.turn_rate,
                      self, self.target_boat, self.global_projs)


class FighterSquadron(Squadron):
    def __init__(self, origin_boat, speed, team, plane_count, target_boat, power, fuel, hpp, turn_rate,
                 global_squadrons, global_projs):
        self.power = power
        self.global_squadrons = global_squadrons
        self.target_squadron = None
        self.old_mode = None
        super().__init__(origin_boat, speed, team, plane_count, target_boat, fuel, hpp, turn_rate, global_projs)

    def update(self, camera):
        self.general_update(camera)
        if self.distance_target_boat < 10 and self.mode == "ftb":
            self.mode = "orbit"

        nearest = None
        distance = 200
        for s in self.global_squadrons:
            if s != self and s.team != self.team:
                for p in s.planes:
                    new_distance = m.dist((self.x, self.y), (p.x, p.y))
                    if new_distance < distance:
                        distance = new_distance
                        nearest = s
        if nearest is not None:
            # nearest is the closest enemy squadron
            self.target_squadron = nearest
            if self.mode != "dgft":
                self.old_mode = self.mode  # Saving the old mode so it can be returned to after the fight
            self.mode = "dgft"  # Dog fight
            for p in self.planes:  # Telling all my planes to target this squadron
                p.target_squadron = self.target_squadron
                p.shoot()
                p.dogfight_update(camera)
        elif self.mode == "dgft":  # No nearby targets, leave dgft mode
            self.mode = self.old_mode  # return to the previous mode before the dogfight

    def new_plane(self, fd, fr):
        sx = m.cos(fd) * fr
        sy = m.sin(fd) * fr
        return Fighter(self.x + sx, self.y + sy, sx, sy, self.d, self.speed, self.team, self.power, self.turn_rate,
                       self, self.target_boat, self.global_projs)


class Plane:
    def __init__(self, x, y, sx, sy, d, speed, team, damage, turn_rate, squadron, target_boat, global_projs):
        self.sy = sy
        self.sx = sx
        self.turn_rate = turn_rate
        self.damage = damage
        self.global_projs = global_projs
        self.x = x
        self.y = y
        self.d = d
        self.dd = self.d  # desired direction
        self.speed = speed
        self.team = team
        self.target_boat = target_boat
        self.active = True
        self.squadron = squadron

        if team == 1:
            self.color = (0, 0, 255)
        else:
            self.color = (255, 0, 0)

    def move(self, camera):
        self.x += m.cos(self.d) * self.speed * camera.dt
        self.y += m.sin(self.d) * self.speed * camera.dt

    def turn(self, camera):
        if m.cos(self.dd) * m.sin(self.d) > m.sin(self.dd) * m.cos(self.d):
            self.d -= self.turn_rate * camera.dt
        else:
            self.d += self.turn_rate * camera.dt

    def formation_update(self, camera, squad_x, squad_y, squad_d):
        # Getting desired x and y values
        dx = squad_x + m.cos(squad_d) * 50 + self.sx
        dy = squad_y + m.sin(squad_d) * 50 + self.sy

        self.dd = m.atan2(dy - self.y, dx - self.x)
        self.turn(camera)
        self.move(camera)


class Fighter(Plane):
    """
    Fighers passively defend the boat they are assigned to
    The player middle clicks on an aircraft carrier, then on another friendly boat to assign fighter to defend that boat
    """

    def __init__(self, x, y, sx, sy, d, speed, team, damage, turn_rate, squadron, target_boat, global_projs):
        super().__init__(x, y, sx, sy, d, speed, team, damage, turn_rate, squadron, target_boat, global_projs)
        self.target_squadron = None  # Must be assigned later
        self.target_plane = None
        self.shoot_tick = 0

    def shoot(self):
        if self.shoot_tick > 0:
            self.shoot_tick -= 1
        else:
            nearest = None
            distance = float("inf")
            for p in self.target_squadron.planes:
                new_distance = m.dist((self.x, self.y), (p.x, p.y))
                if new_distance < distance:
                    nearest = p
                    distance = new_distance
            self.target_plane = nearest
            self.shoot_tick += random.randint(1, 5)
            self.global_projs.append(Bullet(self.x, self.y, self.d, self.target_plane, self.damage))
        # Shoot at the closest plane in the target squadron

    def draw(self, camera):
        a = m.atan(1 / 2)
        points = [(self.x + m.cos(self.d) * size, self.y + m.sin(self.d) * size),
                  (self.x + m.cos(self.d - a + m.pi) * size, self.y + m.sin(self.d - a + m.pi) * size),
                  (self.x + m.cos(self.d + a + m.pi) * size, self.y + m.sin(self.d + a + m.pi) * size)]

        pygame.draw.polygon(camera.foreground, self.color, points, 1)

    def dogfight_update(self, camera):
        self.dd = lead_shot(self, self.target_plane, 5)
        # Turning the plane towards their desired direction
        self.turn(camera)

        self.move(camera)


class Bomber(Plane):
    """
    Bombers, when spawned must be given a target boat to attack
    They will go, drop bombs, and return
    Some will get shot down by AA fire or enemy fighter planes
    The ones that return will be rearmed and can be used again
    While a an aircraft carrier is selected, middle clicking on an enemy boat will send a fighter plane squdron
    """

    def __init__(self, x, y, sx, sy, d, speed, team, damage, turn_rate, squadron, target_boat, global_projs):
        super().__init__(x, y, sx, sy, d, speed, team, damage, turn_rate, squadron, target_boat, global_projs)
        self.has_bomb = True  # Will turn false after dropping the bomb

    def drop_bomb(self):
        if self.has_bomb:
            self.has_bomb = False  # To prevent dropping two bombs
            new_bomb = Bomb(self.x, self.y, self.dd, self.target_boat, self.damage, self.speed / 2)
            self.global_projs.append(new_bomb)

    def bombing_update(self, camera):
        distance = m.dist((self.x, self.y), (self.target_boat.x + m.cos(self.target_boat.d) * 10,
                                             self.target_boat.y + m.sin(self.target_boat.d) * 10))
        if distance < self.speed / 2 * 40:
            self.drop_bomb()
        self.dd = lead_shot(self, self.target_boat, self.speed)

        self.turn(camera)
        self.move(camera)

    def draw(self, camera):
        a = m.atan(1 / 1.5)
        points = [(self.x + m.cos(self.d) * size, self.y + m.sin(self.d) * size),
                  (self.x + m.cos(self.d - a + m.pi) * size, self.y + m.sin(self.d - a + m.pi) * size),
                  (self.x - m.cos(self.d) * size * 1.5, self.y - m.sin(self.d) * size * 1.5),
                  (self.x + m.cos(self.d + a + m.pi) * size, self.y + m.sin(self.d + a + m.pi) * size)]

        pygame.draw.polygon(camera.foreground, self.color, points, 1)
