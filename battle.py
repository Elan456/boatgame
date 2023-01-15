import pygame
import math as m
from projectile import *
from boat import *
from plane import *
from fleet import *
from effects import *

white = (255, 255, 255)
black = (0, 0, 0)


# noinspection PyTypeChecker
class Battle:
    def __init__(self, camera):

        self.squadrons = []
        self.projs = []
        self.boats = []
        self.effects = []
        self.done = False
        self.boats_sunk = 0

        # Populating the boats with the player's boats

        fleet = camera.players_fleet

        for ab in fleet.boats:

            if isinstance(ab, AbstractCarrier):
                self.spawn_abstract_carrier(ab, fleet, camera.width / 2 + random.randint(-30, 30),
                                            camera.height / 2 + random.randint(-30, 30), 1)
            elif isinstance(ab, AbstractDestroyer):
                self.spawn_abstract_destroyer(ab, camera.width / 2 + random.randint(-30, 30),
                                              camera.height / 2 + random.randint(-30, 30), 1)

        camera.selected_boat = self.boats[0]

    def spawn_abstract_carrier(self, ab, fleet, x, y, team):
        self.boats.append(
            Carrier(x, y, self.boats, self.squadrons, self.projs, team=team,
                    speed=ab.speed, turn_rate=ab.turn_rate, max_health=ab.health, aa_power=ab.aa_power,
                    bomber_speed=fleet.bombers.speed, bombers_per_squadron=ab.bomber_squad_size,
                    bomb_damage=fleet.bombers.damage, bomber_fuel=fleet.bombers.fuel,
                    bomber_health=fleet.bombers.health, bomber_turn_rate=fleet.bombers.turn_rate,
                    fighter_speed=fleet.fighters.speed,
                    fighters_per_squadron=ab.fighter_squad_size, fighter_power=fleet.fighters.damage,
                    fighter_fuel=fleet.fighters.fuel, fighter_health=fleet.fighters.health,
                    fighter_turn_rate=fleet.fighters.turn_rate,
                    fighters=ab.fighter_count, bombers=ab.bomber_count)
        )

    def spawn_abstract_destroyer(self, ab, x, y, team):
        self.boats.append(
            Destroyer(x, y, self.boats, self.squadrons, self.projs, team=team,
                      speed=ab.speed, turn_rate=ab.turn_rate, max_health=ab.health, aa_power=ab.aa_power,
                      gun_power=ab.gun_damage, gun_range=ab.gun_range, gun_rate=ab.gun_fire_rate,
                      shell_speed=ab.shell_speed)
        )


class Infinite(Battle):
    def __init__(self, camera):
        super().__init__(camera)

    def update(self, camera):

        camera.mouse = [pygame.mouse.get_pos(), pygame.mouse.get_pressed()[0]]

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.done = True
            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.__dict__["button"] == 1:  # left click
                    x, y = event.__dict__["pos"]
                    for b in self.boats:
                        if m.sqrt((b.x - x) ** 2 + (b.y - y) ** 2) < 40:
                            camera.selected_boat = b
                            break
                elif event.__dict__["button"] == 3:  # right click

                    x, y = event.__dict__["pos"]
                    if len(camera.selected_boat.waypoints) > 0 and m.sqrt(
                            (camera.selected_boat.waypoints[-1][0] - x) ** 2 + (
                                    camera.selected_boat.waypoints[-1][1] - y) ** 2) < 50:
                        camera.selected_boat.waypoints = []
                    else:
                        camera.selected_boat.waypoints.append(event.__dict__["pos"])
                elif event.__dict__["button"] == 2:  # middle click
                    if camera.selected_boat.team == 1:
                        x, y = event.__dict__["pos"]
                        for b in self.boats:
                            """
                            Later we could check for the closest boat under 40 instead of the first boat less than 40
                            away. This is will aid when there are multiple boats clustered together
                            """
                            if m.sqrt((b.x - x) ** 2 + (b.y - y) ** 2) < 40:
                                camera.selected_boat.middle_click_operation(b)
                                break  # So multiple boats are not selected

        camera.foreground.fill((0, 0, 0, 0))
        camera.background.fill((0, 0, 0, 0))

        old_projs = self.projs.copy()
        old_boats = self.boats.copy()
        old_squadrons = self.squadrons.copy()
        enemy_boat_count = 0
        friendly_boat_count = 0
        for entity in old_boats + old_squadrons + old_projs:
            entity.update(camera)
            entity.draw(camera)
            if isinstance(entity, Boat):
                if entity.team == 2:
                    enemy_boat_count += 1
                else:
                    friendly_boat_count += 1
            if not entity.active:
                if isinstance(entity, Shell):
                    self.projs.remove(entity)
                    if entity.hit_target:
                        self.effects.append(Explosion(entity.x, entity.y))
                    else:
                        self.effects.append(Splash(entity.x, entity.y))
                elif isinstance(entity, Bullet):
                    self.projs.remove(entity)
                elif isinstance(entity, Boat):
                    self.boats.remove(entity)
                    if entity.team == 2:
                        camera.players_fleet.money += 5 * 1.05 ** self.boats_sunk
                        self.boats_sunk += 1

                elif isinstance(entity, Squadron):
                    self.squadrons.remove(entity)

        old_effects = self.effects.copy()
        for e in old_effects:
            e.update(camera)
            if not e.active:  # Remove the effects that are done
                self.effects.remove(e)

        if enemy_boat_count == 0:
            enemy_fleet = Fleet()
            # Upgrading the bombers and fighters
            for _ in range(self.boats_sunk // 2 + 1):
                enemy_fleet.bombers.random_upgrade()
                enemy_fleet.fighters.random_upgrade()

            c = random.randint(1, max(1, self.boats_sunk))

            for _ in range(c):
                # 2 Destroyers for every carrier on average

                if random.choice([0, 0, 1]) == 0:
                    new_boat = AbstractDestroyer()
                else:
                    new_boat = AbstractCarrier()

                """
                Each enemy boat is given a number of random upgrades equal to how many boats you have sunk
                """
                for _ in range(self.boats_sunk // 2 + 1):
                    new_boat.random_upgrade()
                    # Some upgrades will have no effect

                if isinstance(new_boat, AbstractCarrier):
                    self.spawn_abstract_carrier(new_boat, enemy_fleet, random.choice([-10, camera.width + 10]),
                                                camera.height / 2, 2)
                else:
                    self.spawn_abstract_destroyer(new_boat, random.choice([-10, camera.width + 10]),
                                                  random.choice([-10, camera.height + 10]), 2)

        if friendly_boat_count == 0:
            self.done = True

        pygame.draw.circle(camera.ui, (0, 255, 0), (camera.selected_boat.x + m.cos(camera.selected_boat.d) * 20 / 2,
                                                    camera.selected_boat.y + m.sin(camera.selected_boat.d) * 20 / 2),
                           20 * 2.5, 1)
        if isinstance(camera.selected_boat, Destroyer):
            if camera.selected_boat.gun_tick <= 1:
                pygame.draw.circle(camera.gameDisplay, (0, 0, 255), (camera.selected_boat.x, camera.selected_boat.y),
                                   camera.selected_boat.gun_range, 1)
            else:
                pygame.draw.circle(camera.gameDisplay, (0, 255, 255), (camera.selected_boat.x, camera.selected_boat.y),
                                   camera.selected_boat.gun_range, 1)
        pgt.text(camera.ui, (camera.width - 200, 30), "Money: $" + str(round(camera.players_fleet.money, 2)), (128, 128, 0), 30,
                 "left")
        pgt.text(camera.ui, (camera.width - 200, 60), "Sunk: " + str(self.boats_sunk), (0, 200, 0), 30, "left")
        pgt.text(camera.ui, (camera.width - 200, 90), "Next Boat: +$" + str(round(5 * 1.05 ** self.boats_sunk, 2)), (0, 200, 0), 30,
                 "left")


class Level(Battle):
    pass
