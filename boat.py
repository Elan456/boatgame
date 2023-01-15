import pygame
import math as m
from plane import *
from status_bar import draw_bar
from projectile import *
import random
import pgt

pi = m.pi

size = 20
shell_speed = 5


class Boat:
    def __init__(self, x, y, boats, squadrons, projs, d=0, speed=.25, turn_rate=.01, team=1, max_health=100, aa_power=0, aa_range=100):
        self.max_health = max_health
        self.health = max_health  # Start with max health
        self.turn_rate = turn_rate
        self.x = x
        self.y = y
        self.d = d
        self.speed = speed
        self.team = team

        self.aa_power = aa_power
        self.aa_range = aa_range
        self.aa_tick = 0

        self.active = True

        self.global_boats = boats
        self.global_squadrons = squadrons
        self.global_projs = projs

        if team == 1:
            self.color = (0, 0, 255)
        else:
            self.color = (255, 0, 0)
        self.selected = False
        self.waypoints = []

    def shoot_at_planes(self):
        # Finding the closest enemy squadron
        c_squad = None
        cd = float("inf")
        for s in self.global_squadrons:
            if s.team != self.team:
                distance = m.dist((s.x, s.y), (self.x, self.y))
                if distance < cd:
                    cd = distance
                    c_squad = s

        self.aa_tick += random.choice([0, 0, 0, 0, 0, 1, 2])
        if cd < self.aa_range and len(c_squad.planes) > 0:
            targeted_plane = c_squad.planes[self.aa_tick % len(c_squad.planes)]
            self.global_projs.append(Bullet(self.x, self.y, lead_shot(self, targeted_plane, 5, cd), targeted_plane, damage=self.aa_power))

    def follow_waypoints(self, camera):
        wx = self.waypoints[0][0]
        wy = self.waypoints[0][1]
        dtw = m.atan2(wy - self.y, wx - self.x)
        distance = m.sqrt((wx - self.x) ** 2 + (wy - self.y) ** 2)
        inverse = 1
        # Checking if the waypoint is too close at too harsh of an angle
        if distance < size * 5 and m.sqrt((m.cos(self.d) - m.cos(dtw)) ** 2) + ((m.sin(self.d) - m.sin(dtw)) ** 2) >= 2:
            inverse = -1
        if m.cos(dtw) * m.sin(self.d) > m.sin(dtw) * m.cos(self.d):  # Deciding which way to turn to face the point
            self.d -= self.turn_rate * inverse * camera.dt
        else:
            self.d += self.turn_rate * inverse * camera.dt
        if distance < size:
            self.waypoints.pop(0)

    def map_border_collisions(self, camera):
        if self.x > camera.width - 10 - size:
            self.x = camera.width - 10 - size
        elif self.x < 10 + size:
            self.x = 10 + size
        if self.y > camera.height - 10 - size:
            self.y = camera.height - 10 - size
        elif self.y < 10 + size:
            self.y = 10 + size

    def avoid_overlap(self, camera):  # Guides ships away from each other
        for b in self.global_boats:
            if b != self:
                distance = m.dist((self.x, self.y), (b.x, b.y))
                if distance < size * 2:
                    dtw = m.atan2(b.y - self.y, b.x - self.x)
                    if m.cos(dtw) * m.sin(self.d) > m.sin(dtw) * m.cos(self.d):
                        self.d += self.turn_rate * 2 * camera.dt
                    else:
                        self.d -= self.turn_rate * 2 * camera.dt
                    break

    def pos_update(self, camera):
        self.avoid_overlap(camera)
        self.x += m.cos(self.d) * self.speed * camera.dt
        self.y += m.sin(self.d) * self.speed * camera.dt
        self.map_border_collisions(camera)

    def draw_health_bar(self, surface):
        draw_bar(surface, self.x, self.y - 50, self.health, self.max_health, (255, 0, 0))


class Carrier(Boat):
    def __init__(self, x=0, y=0, boats=None, squadrons=None, projs=None, d=0, speed=.25, turn_rate=.01, team=1, max_health=100, aa_power=2, bomber_speed=1, bombers_per_squadron=8, bomb_damage=5,
                 bomber_fuel=1000, bomber_health=100, bomber_turn_rate=.02, fighter_speed=1, fighters_per_squadron=3, fighter_power=5, fighter_fuel=1000, fighter_health=50, fighter_turn_rate=.03, fighters=12, bombers=24):
        super().__init__(x, y, boats, squadrons, projs, d, speed, turn_rate, team, max_health, aa_power)
        self.fighter_turn_rate = fighter_turn_rate
        self.bomber_turn_rate = bomber_turn_rate
        self.camera = None
        self.sending_bombers = None
        self.fighter_power = fighter_power
        self.fighter_health = fighter_health
        self.bomber_health = bomber_health
        self.bomb_damage = bomb_damage
        self.bombers = m.ceil(bombers)
        self.fighters = m.ceil(fighters)
        self.bombers_per_squadron = m.ceil(bombers_per_squadron)
        self.fighters_per_squadron = m.ceil(fighters_per_squadron)
        self.fighter_fuel = fighter_fuel
        self.fighter_speed = fighter_speed
        self.bomber_fuel = bomber_fuel
        self.bomber_speed = bomber_speed
        self.my_squadrons = []

        # AI modes
        self.mode = "offensive"
        self.plane_cooldown = 0
        if self.team == 1:
            self.plane_cooldown = 0
        # else:
        #     self.plane_cooldown = random.randint(300, 500)
        self.bomber_range = self.bomber_fuel * self.bomber_speed - 50

    def update(self, camera):
        self.camera = camera
        if self.plane_cooldown > 0:
            self.plane_cooldown -= 1 * camera.dt
        self.plane_cooldown = max(0, self.plane_cooldown)  # To keep it above 0
        if self.plane_cooldown == 0 and self.sending_bombers is not None:
            if self.team == 2:
                self.send_bombers(self.sending_bombers, extra_cooldown=random.randint(200, 2000))
            else:
                self.send_bombers(self.sending_bombers)
            self.sending_bombers = None

        self.shoot_at_planes()
        if self.team == 1:
            if len(self.waypoints) > 0:
                self.follow_waypoints()
            else:
                self.d += self.turn_rate * camera.dt
        self.pos_update(camera)

        if self.health <= 0:
            self.active = False

        """
        Removing plane squadrons that are done either because they finished their mission or ran out of fuel
        """
        old_my_squadrons = self.my_squadrons.copy()
        for s in old_my_squadrons:
            if s.mode == "done" and s.active:
                self.global_squadrons.remove(s)
                self.my_squadrons.remove(s)
                if isinstance(s, BomberSquadron):
                    self.bombers += len(s.planes)
                else:
                    self.fighters += len(s.planes)

        """
        AI control for the carriers
        """
        if self.team == 2:  # Enemy carriers are AI controlled... here we go
            # Sending fighters to defend boats being attack by bombers
            self.ai_send_fighters()

            # Sending bombers to attack enemy boats
            self.ai_send_bombers()

            if self.mode == "defensive":
                # Move away from the average position of the enemy destroyers
                ax, ay, count = 0, 0, 0
                for b in self.global_boats:
                    if b.team == 1 and isinstance(b, Destroyer):
                        ax += b.x
                        ay += b.y
                        count += 1
                if count > 0:
                    ax /= count
                    ay /= count

                    d = m.atan2(ay - self.y, ax - self.x) + m.pi  # Opposite direction from average posotion of enemy destoyres
                    distance = m.dist((self.x, self.y), (ax, ay))
                    if distance < 500:
                        if m.cos(d) * m.sin(self.d) > m.sin(d) * m.cos(self.d):  # Deciding which way to turn to face the point
                            self.d -= self.turn_rate * camera.dt
                        else:
                            self.d += self.turn_rate * camera.dt
                    else:
                        self.d += self.turn_rate * camera.dt
            elif self.mode == "offensive":
                # Move towards closest enemy boat
                cec = sorted(self.global_boats, key=lambda b: m.dist((b.x, b.y), (self.x, self.y)) if b.team == 1 else float("inf"))[0]
                d = m.atan2(cec.y - self.y, cec.x - self.x)
                # Move away if too close
                if self.bombers > 0:
                    br = self.bomber_range
                else:
                    br = 0
                if m.dist((cec.x, cec.y), (self.x, self.y)) > br - 50:
                    inverse = 1
                else:
                    inverse = -1
                if m.cos(d) * m.sin(self.d) > m.sin(d) * m.cos(self.d):  # Deciding which way to turn to face the point
                    self.d -= self.turn_rate * inverse * camera.dt
                else:
                    self.d += self.turn_rate * inverse * camera.dt

    def ai_send_fighters(self):
        for s in self.global_squadrons:
            if s.team == 1 and s.target_boat.team == 2:  # They are attacking one of my boats
                should_send_fighters = True
                # Checking if there is already a fighter squad defending that boat
                for st in self.global_squadrons:
                    if st.target_boat == s.target_boat and st.team == 2:
                        should_send_fighters = False
                # Checking if a boat that is closer could send their fighters instead
                my_distance = m.dist((self.x, self.y), (s.target_boat.x, s.target_boat.y))
                for bt in self.global_boats:
                    # Is this boat a carrier and does it have fighters avaliable
                    if bt.team == 2 and isinstance(bt, Carrier) and bt.fighters > 0:
                        their_distance = m.dist((bt.x, bt.y), (s.target_boat.x, s.target_boat.y))
                        if their_distance < my_distance:  # Are they closer to the boat that needs defense
                            should_send_fighters = False

                # We have no fighters already defending that boat and no other boats are closer to help,
                # so we will send in our own squad
                if should_send_fighters:
                    self.send_fighters(s.target_boat)

    def ai_choose_boat_bomb(self):  # Figuring out which boat is most tactical to bomb
        ax, ay, count = 0, 0, 0  # Average x, y, for all enemy boats
        potential_boats = []  # All the enemy boats within bombing range and their score as a tuple
        for b in self.global_boats:
            # Check if the boat is from the other team and is close enough

            if b.team == 1:
                ax += b.x
                ay += b.y
                count += 1
                distance_to_carrier = m.dist((self.x, self.y), (b.x, b.y))
                if distance_to_carrier < self.bomber_range:
                    potential_boats.append((b, distance_to_carrier))

        if count == 0:  # There are no enemy boats in play
            return None
        elif count == 1 and len(potential_boats) == 1:
            return potential_boats[0][0]

        ax /= count
        ay /= count
        # pygame.draw.circle(self.camera.foreground, (255, 255, 0), (ax, ay), 10)

        if len(potential_boats) > 1:  # There is more than one boat to choose from within bombing range
            # Giving each boat a score
            for i in range(len(potential_boats)):
                boat = potential_boats[i][0]
                distance_to_carrier = potential_boats[i][1]
                dist_to_average = m.dist((boat.x, boat.y), (ax, ay))

                potential_boats[i] = (boat, distance_to_carrier, dist_to_average)

            potential_boats.sort(key=lambda x: x[1] - 4 * x[2])  # Sorting by distance to carrier - 2 *distance to average

            best_boat = potential_boats[0]
            # Checking if the boat is sufficently isolated from other boats
            return best_boat[0]
            if best_boat[2] > 100:
                return best_boat[0]
            else:
                return None  # No boat is a good target

        elif len(potential_boats) == 1:  # Only one boat within bombing range
            boat = potential_boats[0][0]
            return boat
            #  pygame.draw.circle(self.camera.foreground, (0, 255, 255), (boat.x, boat.y), 10, 2)
            dist_to_average = m.dist((boat.x, boat.y), (ax, ay))
            if dist_to_average > 100:
                return boat
            else:
                return None

    def ai_send_bombers(self):
        boat = self.ai_choose_boat_bomb()
        if boat is not None:

            # pygame.draw.circle(self.camera.foreground, (0, 200, 255), (boat.x, boat.y), 15, 2)
            self.send_fighters(boat)
            self.sending_bombers = boat

    def middle_click_operation(self, target_boat):
        """
        Sends planes to the target boat,
        Sends fighters if the boat is friendly, for defense,
        Sends bombers if the boat is an enemy to attack
        :param target_boat: The boat that was middle_clicked_on while this boat was selected
        :return: Nothing
        """

        if target_boat.team == 1:
            self.send_fighters(target_boat)
        else:
            if self.bombers > 0:  # To avoid just sending fighters
                self.send_fighters(target_boat)
                self.sending_bombers = target_boat
            # self.send_bombers(target_boat)

    def send_bombers(self, target_boat, extra_cooldown=0):
        if self.plane_cooldown == 0:
            count = min(self.bombers, self.bombers_per_squadron)
            if count > 0:
                new_squadron = BomberSquadron(self, self.bomber_speed, self.team, count, target_boat, self.bomb_damage, self.bomber_fuel, self.bomber_health, self.bomber_turn_rate)
                self.global_squadrons.append(new_squadron)
                self.my_squadrons.append(new_squadron)
                self.bombers -= count
                self.plane_cooldown = 100 + extra_cooldown

    def send_fighters(self, target_boat):
        if self.plane_cooldown == 0:
            count = min(self.fighters, self.fighters_per_squadron)
            if count > 0:
                new_squadron = FighterSquadron(self, self.fighter_speed, self.team, count, target_boat,
                                               self.fighter_power, self.fighter_fuel, self.fighter_health, self.fighter_turn_rate, self.global_squadrons, self.global_projs)
                self.global_squadrons.append(new_squadron)
                self.my_squadrons.append(new_squadron)
                self.fighters -= count
                self.plane_cooldown = 10

    def draw(self, camera):
        surface = camera.background
        x = self.x
        y = self.y
        d = self.d

        a = m.atan(1 / 2)
        points = [(x + m.cos(d - a) * size, y + m.sin(d - a) * size),
                  (x + m.cos(d) * size * 1.7, y + m.sin(d) * size * 1.7),
                  (x + m.cos(d + a - .4) * size, y + m.sin(d + a - .4) * size),
                  (x + m.cos(d + a) * size, y + m.sin(d + a) * size),
                  (x + m.cos(d - a + pi) * size, y + m.sin(d - a + pi) * size),
                  (x + m.cos(d + a + pi) * size, y + m.sin(d + a + pi) * size)]

        pygame.draw.polygon(surface, self.color, points, 1)
        #  pygame.draw.circle(surface, (128, 128, 0), (self.x, self.y), self.bomber_speed * self.bomber_fuel, 1)
        for w in self.waypoints:
            pygame.draw.circle(surface, (128, 128, 0), w, 5, 1)
        if len(self.waypoints) > 0:
            pygame.draw.lines(surface, (128, 128, 0), False, [(self.x, self.y)] + self.waypoints)

        self.draw_health_bar(surface)
        pgt.text(surface, (self.x - 25, self.y - 65), str(self.bombers), (128, 128, 0), 15, "right")
        pgt.text(surface, (self.x + 14, self.y - 65), str(self.fighters), (128, 128, 128), 15, "right")


class Destroyer(Boat):
    def __init__(self, x, y, boats, squadrons, proj, d=0, speed=.8, turn_rate=.02, team=1, max_health=50, aa_power=1, gun_power=1, gun_range=100, gun_rate=.005, shell_speed=1.5):
        super().__init__(x, y, boats, squadrons, proj, d, speed, turn_rate, team, max_health, aa_power)
        self.shell_speed = shell_speed
        self.mode = "fwp"  # Follow way points
        self.escort_boat = None
        self.attack_boat = None
        self.gun_power = gun_power
        self.gun_range = gun_range
        self.gun_rate = gun_rate
        self.gun_tick = 0  # For gun timing

    def update(self, camera):
        self.shoot_at_planes()
        if len(self.waypoints) > 0:
            self.mode = "fwp"
            self.follow_waypoints(camera)
        elif self.mode == "escort":
            if self.escort_boat.active:
                self.follow_boat(self.escort_boat, camera)
            else:
                self.mode = "fwp"
        elif self.mode == "attack":
            if self.attack_boat.active:
                self.follow_boat(self.attack_boat, camera)
            else:
                self.mode = "fwp"
        else:
            self.d += self.turn_rate * camera.dt  # Default idle action is turning in a circle
        self.pos_update(camera)

        if self.gun_tick > 1:
            if self.shoot_at_boats():
                self.gun_tick = 0
        else:
            self.gun_tick += self.gun_rate * camera.dt

        if self.health <= 0:
            self.active = False

        if self.team == 2:  # team 2 is AI controlled
            c_c = None  # Closest friendly carrier
            c_d = float("inf")  # Distance to closest friendly carrier

            c_eb = None  # Closest enemy boat
            c_ed = float("inf")  # Distance to closest enemy boat
            for b in self.global_boats:
                if isinstance(b, Carrier) and b.team == 2:
                    distance = m.dist((self.x, self.y), (b.x, b.y))
                    if distance < c_d:
                        c_d = distance
                        c_c = b

                if b.team == 1:  # Enemy boat
                    distance = m.dist((self.x, self.y), (b.x, b.y))
                    if distance < c_ed:
                        c_ed = distance
                        c_eb = b

            if c_c is not None:  # Is there a friendly carrier?
                # There is a friendly carrier
                self.mode = "escort"
                self.escort_boat = c_c
            elif c_eb is not None:  # Is there an enemy boat to attack instead
                self.mode = "attack"
                self.attack_boat = c_eb

    def shoot_at_boats(self):

        # Finding the closest enemy boat
        ceb = None  # Closest enemy boat
        distance_to_closest_enemy_boat = float("inf")
        for b in self.global_boats:
            if b.team != self.team:
                distance = m.dist((b.x, b.y), (self.x, self.y))
                if distance < distance_to_closest_enemy_boat:
                    ceb = b
                    distance_to_closest_enemy_boat = distance

        if distance_to_closest_enemy_boat < self.gun_range:
            self.global_projs.append(Shell(self.x, self.y, lead_shot(self, ceb, self.shell_speed, distance_to_closest_enemy_boat), ceb,
                                           damage=self.gun_power, speed=self.shell_speed))
            return True
        return False
        # Shoot at this boat

    def follow_boat(self, target_boat, camera):
        """
        The destroyer will follow another boat so that the other boat stays within the destroyer's gun's range.
        The destoryer will try to not to get any closer than it has too, to hopefully outrange an enemy destroyer's
        return fire.

        :param target_boat: The boat that this is meant to follow
        """
        lead_x = target_boat.x + m.cos(target_boat.d) * target_boat.speed * 100
        lead_y = target_boat.y + m.sin(target_boat.d) * target_boat.speed * 100


        if (target_boat.team != self.team):  # Barely keep the target in range if enemy
            follow_distance = self.gun_range
        else:
            follow_distance = 80

        dtw = m.atan2(lead_y - self.y, lead_x - self.x)

        distance = m.dist((self.x, self.y), (target_boat.x, target_boat.y))
        if distance < follow_distance * .8:  # Too close, move away from the boat
            if m.cos(dtw) * m.sin(self.d) > m.sin(dtw) * m.cos(self.d):
                self.d += self.turn_rate * camera.dt
            else:
                self.d -= self.turn_rate * camera.dt
        elif distance < follow_distance:  # Start moving parralel to the target boat, it's at the right distance
            if m.cos(target_boat.d) * m.sin(self.d) > m.sin(target_boat.d) * m.cos(self.d):
                self.d -= self.turn_rate * camera.dt
            else:
                self.d += self.turn_rate * camera.dt
        else:  # Move towards the boat, its outside of the shooting range
            if m.cos(dtw) * m.sin(self.d) > m.sin(dtw) * m.cos(self.d):
                self.d -= self.turn_rate * camera.dt
            else:
                self.d += self.turn_rate * camera.dt

    def middle_click_operation(self, target_boat):
        # Escort friendly boats, attack enemy boats
        if target_boat != self:
            self.waypoints = []
            if target_boat.team == 1:
                self.mode = "escort"
                self.escort_boat = target_boat
            else:
                self.mode = "attack"
                self.attack_boat = target_boat

    def draw(self, camera):
        surface = camera.background
        x = self.x
        y = self.y
        d = self.d
        a = m.atan(1 / 3)
        dsize = size * .7
        points = [(x + m.cos(d - a) * dsize, y + m.sin(d - a) * dsize),  # Top left
                  (x + m.cos(d) * dsize * 1.7, y + m.sin(d) * dsize * 1.7),  # Tip of triangle
                  (x + m.cos(d + a) * dsize, y + m.sin(d + a) * dsize),  # Top right
                  (x + m.cos(d - a + pi) * dsize, y + m.sin(d - a + pi) * dsize),
                  (x + m.cos(d + pi) * dsize * 1.2, y + m.sin(d + pi) * dsize * 1.2),
                  (x + m.cos(d + a + pi) * dsize, y + m.sin(d + a + pi) * dsize)]

        pygame.draw.polygon(surface, self.color, points, 1)

        for w in self.waypoints:
            pygame.draw.circle(surface, (128, 128, 0), w, 5, 1)
        if len(self.waypoints) > 0:
            pygame.draw.lines(surface, (128, 128, 0), False, [(self.x, self.y)] + self.waypoints)
        if self.team == 1:
            if self.mode == "attack":
                pygame.draw.line(surface, (200, 0, 200), (self.x, self.y), (self.attack_boat.x, self.attack_boat.y))
            elif self.mode == "escort":
                pygame.draw.line(surface, (0, 200, 200), (self.x, self.y), (self.escort_boat.x, self.escort_boat.y))

        self.draw_health_bar(surface)
