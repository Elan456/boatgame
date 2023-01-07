import pygame
import math as m
from projectile import *
from boat import *
from plane import *
from fleet import *

white = (255, 255, 255)
black = (0, 0, 0)


class Battle:
    def __init__(self, camera):
        print("camera:", camera)
        self.squadrons = []
        self.projs = []
        self.boats = []
        self.done = False
        self.boats_sunk = 0

        # Populating the boats with the player's boats

        fleet = camera.players_fleet
        print("fleet:", fleet)
        for ab in fleet.boats:
            print(ab.speed)
            if isinstance(ab, AbstractCarrier):
                self.boats.append(
                    Carrier(camera.width / 2, camera.height / 2, self.boats, self.squadrons, self.projs,
                            speed=ab.speed, turn_rate=ab.turn_rate, max_health=ab.health, aa_power=ab.aa_power,
                            bomber_speed=fleet.bombers.speed, bombers_per_squadron=ab.bomber_squad_size,
                            bomb_damage=fleet.bombers.damage, bomber_fuel=fleet.bombers.fuel,
                            bomber_health=fleet.bombers.health, fighter_speed=fleet.fighters.speed,
                            fighters_per_squadron=ab.fighter_squad_size, fighter_power=fleet.fighters.damage,
                            fighter_fuel=fleet.fighters.fuel, fighter_health=fleet.fighters.health,
                            fighters=ab.fighter_count, bombers=ab.bomber_count)
                )
            elif isinstance(ab, AbstractDestroyer):
                self.boats.append(
                    Destroyer(camera.width / 2, camera.height / 2, self.boats, self.squadrons, self.projs,
                              speed=ab.speed, turn_rate=ab.turn_rate, max_health=ab.health, aa_power=ab.aa_power,
                              gun_power=ab.gun_damage, gun_range=ab.gun_range, gun_rate=ab.gun_fire_rate)
                )

        camera.selected_boat = self.boats[0]


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
                    if len(camera.selected_boat.waypoints) > 0 and m.sqrt((camera.selected_boat.waypoints[-1][0] - x) ** 2 + (camera.selected_boat.waypoints[-1][1] - y) ** 2) < 10:
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
                elif isinstance(entity, Bullet):
                    self.projs.remove(entity)
                elif isinstance(entity, Boat):
                    self.boats.remove(entity)
                    if entity.team == 2:
                        camera.players_fleet.money += 5 * 1.2 ** self.boats_sunk
                        self.boats_sunk += 1

                elif isinstance(entity, Squadron):
                    self.squadrons.remove(entity)

        if enemy_boat_count == 0:
            c = random.randint(1, max(1, self.boats_sunk))
            bs = self.boats_sunk
            for _ in range(c):
                # 2 Destroyers for every carrier on average

                if random.choice([0, 0, 1]) == 0:
                    self.boats.append(Destroyer(random.choice([-100, 2000]), random.choice([-100, 2000]), self.boats,
                                                self.squadrons, self.projs, team=2, max_health=3 * 1.1 ** self.boats_sunk,
                                                aa_power=1 * 1.1 ** self.boats_sunk, gun_power=.5 * 1.3 ** self.boats_sunk,
                                                gun_range=50 * 1.1 ** self.boats_sunk, gun_rate=.001 * 1.1 ** self.boats_sunk))
                else:
                    self.boats.append(Carrier(random.choice([-100, 2000]), camera.height / 2, self.boats,
                                              self.squadrons, self.projs, team=2,
                                              max_health=8 * 1.1 ** bs, speed=.2 * 1.01 ** bs, turn_rate=.005 * 1.1 ** bs,
                                              aa_power=.5 * 1.1 ** bs, bombers=3 * 1.1 ** bs, bombers_per_squadron=1 * 1.1 ** bs,
                                              fighters=2 * 1.1 ** bs, fighters_per_squadron=1 * 1.1 ** bs, bomber_health=20 * 1.1 ** bs,
                                              bomber_fuel=200 * 1.1 ** bs, bomb_damage=1 * 1.1 ** bs
                                              ))

        if friendly_boat_count == 0:
            self.done = True

        pygame.draw.circle(camera.ui, (0, 255, 0), (camera.selected_boat.x + m.cos(camera.selected_boat.d) * 20 / 2, camera.selected_boat.y + m.sin(camera.selected_boat.d) * 20 / 2), 20 * 2.5, 1)
        if isinstance(camera.selected_boat, Destroyer):
            if camera.selected_boat.gun_tick <= 1:
                pygame.draw.circle(camera.gameDisplay, (0, 0, 255), (camera.selected_boat.x, camera.selected_boat.y), camera.selected_boat.gun_range, 1)
            else:
                pygame.draw.circle(camera.gameDisplay, (0, 255, 255), (camera.selected_boat.x, camera.selected_boat.y), camera.selected_boat.gun_range, 1)
        pgt.text(camera.ui, (1700, 30), "Money: $" + str(round(camera.players_fleet.money, 2)), (128, 128, 0), 30, "left")
        pgt.text(camera.ui, (1700, 60), "Sunk: " + str(self.boats_sunk), (0, 200, 0), 30, "left")
        pgt.text(camera.ui, (1700, 90), "Next Boat: +$" + str(round(5 * 1.2 ** self.boats_sunk, 2)), (0, 200, 0), 30, "left")



class Level(Battle):
    pass
