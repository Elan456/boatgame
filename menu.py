import pygame
import pgt
from fleet import *
import battle
import math as m

white = (255, 255, 255)
black = (0, 0, 0)

red = (255, 0, 0)
dark_red = (150, 0, 0)

green = (0, 255, 0)
dark_green = (0, 150, 0)

blue = (0, 50, 255)
dark_blue = (0, 50, 150)

b_width = 250
b_height = 80

yspac = 115  # Spacing in the y direction
text_size = 25


def nata():
    print("hello")


def button_quit():
    pygame.quit()
    quit()


class MainMenu:
    def __init__(self, camera, players_fleet):
        self.players_fleet = players_fleet
        self.buttons = [pgt.Button(camera.ui, [100, 100, 500, 250], "Levels", black, 60, nata, dark_green, green),
                        pgt.Button(camera.ui, [100, 400, 500, 250], "Infinite", black, 60, self.activate_infinite_mode,
                                   dark_green, green),
                        pgt.Button(camera.ui, [650, 400, 500, 250], "Upgrades", black, 60, self.open_upgrade_menu,
                                   dark_green, green),
                        pgt.Button(camera.ui, [650, 100, 500, 250], "Help", black, 60, self.show_help, dark_green,
                                   green)]
        self.quit_button = pgt.Button(camera.ui, [camera.width - 550, camera.height - 300, 500, 250], "Quit", black, 60,
                                   self.try_quit, dark_red, red)
        self.confirm_quit_button = pgt.Button(camera.ui, [camera.width - 550, camera.height - 800, 100, 100], "Quit!",
                                              black, 30,
                                              button_quit, dark_red, red)
        self.help = False
        self.in_upgrade_menu = False
        self.in_battle = False
        self.upgrade_menu = UpgradeMenu(self, camera, players_fleet)
        self.help_menu = Help(self, camera)
        self.infinite_battle = battle.Infinite(camera)
        self.camera = camera
        self.trying_to_quit = 0

    def try_quit(self):
        self.trying_to_quit = 100

    def show_help(self):
        if self.help:
            self.help = False
        else:
            self.help = True

    def activate_infinite_mode(self):
        self.infinite_battle = battle.Infinite(self.camera)
        self.in_battle = True

    def open_upgrade_menu(self):
        self.in_upgrade_menu = True

    def update(self, camera):
        if self.trying_to_quit > 0:
            self.trying_to_quit -= 1
        if self.in_battle:
            self.infinite_battle.update(camera)
            if self.infinite_battle.done:
                self.in_battle = False

        elif self.in_upgrade_menu:
            self.upgrade_menu.update(camera)
        elif self.help:
            self.help_menu.update(camera)
        else:
            for b in self.buttons:
                b.update(camera.mouse)
            if self.trying_to_quit > 0:
                self.confirm_quit_button.update(camera.mouse)
            else:
                self.quit_button.update(camera.mouse)


class UpgradeMenu:
    def __init__(self, main_menu, camera, players_fleet):
        start_y = 30
        start_x = camera.width - 320

        self.players_fleet = players_fleet
        players_fleet.fx, players_fleet.fy = 50, 900
        players_fleet.bx, players_fleet.by = 100, 900
        self.carrier_cost = 0
        self.destroyer_cost = 0

        self.main_menu = main_menu

        self.exit_button = pgt.Button(camera.ui, [start_x, start_y + yspac * 8, b_width, b_height], "Exit", black,
                                      text_size, self.button_exit, dark_red, red)

        self.buy_boat = [
            BuyButton(camera.ui, [50, 700, b_width, b_height], "New Carrier", "carrier"),
            BuyButton(camera.ui, [350, 700, b_width, b_height], "New Destroyer", "destroyer")
        ]

        self.buttons_entity = [
            UpgradeButton(camera.ui, [start_x, start_y + yspac * 0, b_width, b_height], "Health", "health"),
            UpgradeButton(camera.ui, [start_x, start_y + yspac * 1, b_width, b_height], "Speed", "speed"),
            UpgradeButton(camera.ui, [start_x, start_y + yspac * 2, b_width, b_height], "Turn Rate", "turn_rate")
        ]

        self.buttons_boat = self.buttons_entity + [
            UpgradeButton(camera.ui, [start_x, start_y + yspac * 3, b_width, b_height], "Anti Air", "aa_power")
        ]

        self.buttons_carrier = self.buttons_entity + self.buttons_boat + [
            UpgradeButton(camera.ui, [start_x, start_y + yspac * 4, b_width, b_height], "Bomber Count", "bomber_count"),
            UpgradeButton(camera.ui, [start_x, start_y + yspac * 5, b_width, b_height], "Bomber Squad Size",
                          "bomber_squad_size"),
            UpgradeButton(camera.ui, [start_x, start_y + yspac * 6, b_width, b_height], "Fighter Count",
                          "fighter_count"),
            UpgradeButton(camera.ui, [start_x, start_y + yspac * 7, b_width, b_height], "Fighter Squad Size",
                          "fighter_squad_size")
        ]

        self.buttons_destroyer = self.buttons_entity + self.buttons_boat + [
            UpgradeButton(camera.ui, [start_x, start_y + yspac * 4, b_width, b_height], "Gun Damage", "gun_damage"),
            UpgradeButton(camera.ui, [start_x, start_y + yspac * 5, b_width, b_height], "Gun Range", "gun_range"),
            UpgradeButton(camera.ui, [start_x, start_y + yspac * 6, b_width, b_height], "Gun Fire Rate",
                          "gun_fire_rate"),
            UpgradeButton(camera.ui, [start_x, start_y + yspac * 7, b_width, b_height], "Shell Speed",
                          "shell_speed")
        ]

        self.buttons_plane = self.buttons_entity + [
            UpgradeButton(camera.ui, [start_x, start_y + yspac * 3, b_width, b_height], "Fuel", "fuel"),
            UpgradeButton(camera.ui, [start_x, start_y + yspac * 4, b_width, b_height], "Damage", "damage")
        ]

    def button_exit(self):
        self.main_menu.in_upgrade_menu = False

    def update(self, camera):

        selected = camera.selected_boat_abstract
        self.show_fleet(camera)
        self.exit_button.update(camera.mouse)
        valid_upgrades = []
        if selected is not None:
            valid_upgrades += self.buttons_entity

            if isinstance(selected, AbstractBoat):
                valid_upgrades += self.buttons_boat

                if isinstance(selected, AbstractCarrier):
                    valid_upgrades += self.buttons_carrier

                if isinstance(selected, AbstractDestroyer):
                    valid_upgrades += self.buttons_destroyer
            if isinstance(selected, AbstractPlane):
                valid_upgrades += self.buttons_plane

        for u in valid_upgrades:
            u.update(camera)

        for u in self.buy_boat:
            u.update(camera)

        pgt.text(camera.ui, (100, 900), "Money: $" + str(round(self.players_fleet.money, 2)), (128, 128, 0), 40, "left")

    def show_fleet(self, camera):
        x = 50
        y = 50
        c = 0
        for b in self.players_fleet.entities:
            b.x = x
            b.y = y
            c += 1
            if c == 2:
                y += 90
                x = 0
            b.draw(camera)
            x += 50

        if camera.selected_boat_abstract is not None:
            x, y = camera.selected_boat_abstract.x, camera.selected_boat_abstract.y
            pygame.draw.circle(camera.ui, (0, 255, 0), (x, y), 10, 1)


class BuyButton:
    def __init__(self, surface, rect, name, boat_type):
        self.boat_type = boat_type
        self.name = name
        self.rect = rect
        self.surface = surface
        self.players_fleet = None
        self.cost = 0
        self.x, self.y, self.w, self.h = rect

        self.button = pgt.Button(surface, rect, "", (0, 0, 0), 1, self.buy_boat, (128, 128, 0), (150, 150, 50))

    def buy_boat(self):
        if self.players_fleet.money >= self.cost:
            self.players_fleet.money -= self.cost
            if self.boat_type == "carrier":
                self.players_fleet.add_new_carrier()
            else:
                self.players_fleet.add_new_destroyer()

    def update(self, camera):
        self.players_fleet = camera.players_fleet
        if self.boat_type == "carrier":
            self.cost = 10 * 1.5 ** self.players_fleet.carrier_count
        elif self.boat_type == "destroyer":
            self.cost = 5 * 1.3 ** self.players_fleet.destroyer_count

        self.button.update(camera.mouse)
        pgt.text(camera.ui, (self.x + self.w / 2, self.y + 20), "New " + self.boat_type, black, 30)
        pgt.text(camera.ui, (self.x + self.w / 2, self.y + 50), "$" + str(round(self.cost, 2)), black, 30)


def draw_star(surface, x, y, size, thickness):
    points = [(x, y)]
    angle = m.pi / 2 - m.radians(18)
    for n in range(5):
        n_x, n_y = points[-1]
        points.append((n_x + m.cos(angle) * size, n_y + m.sin(angle) * size))
        angle += m.radians(144)

    pygame.draw.lines(surface, (255, 255, 0), False, points, thickness)


class UpgradeButton:
    xspac = 30
    yspac = 30

    def __init__(self, surface, rect, name, upgrade_name):
        self.players_fleet = None
        self.upgrade_name = upgrade_name
        self.name = name
        self.surface = surface
        self.rect = rect
        self.x, self.y, self.w, self.h = rect

        self.action = self.do_upgrade
        self.color = dark_blue
        self.highlighted_color = blue

        self.button = pgt.Button(surface, rect, "", (0, 0, 0), 1, self.action, self.color, self.highlighted_color)

    def get_cost(self):
        self.selected = self.camera.selected_boat_abstract
        return 1 * (5 ** (self.selected.upgrade_stage[self.upgrade_name] - 1))

    def do_upgrade(self):

        if self.players_fleet.money >= self.cost and self.selected.upgrade_stage[self.upgrade_name] < 6:

            self.players_fleet.money -= self.cost
            self.selected.upgrade(self.upgrade_name)

    def update(self, camera):
        self.camera = camera
        self.players_fleet = camera.players_fleet
        self.selected = camera.selected_boat_abstract
        # The selected will always be relevant to this upgrade because that is the only time this upgrade will be
        # updated
        self.cost = self.get_cost()
        show_cost = round(self.cost, 1)
        current_value = round(getattr(self.selected, self.upgrade_name), 3)

        self.button.update(camera.mouse)
        pgt.text(camera.ui, (self.x + 5, self.y + self.h - 25), self.name, black, 30, "right")

        if self.selected.upgrade_stage[self.upgrade_name] < 6:  # Can they still buy upgrades
            pgt.text(camera.ui, (self.x + 5, self.y + 30), "$ " + str(show_cost), black, 40, "right")

        pgt.text(camera.ui, (self.x + 50 + UpgradeButton.xspac, self.y + 5), "Current: " + str(current_value), black,
                 35, "right")
        star_x = self.x + 90
        star_y = self.y + 10

        for n in range(self.selected.upgrade_stage[self.upgrade_name] - 1):
            draw_star(camera.ui, star_x, star_y, 30, 2)
            star_x += 35


class LevelSelect:
    pass


class HelpText(pgt.Text):
    def __init__(self, x, y, text):
        super().__init__(x, y, text, black, 35, "left")


class Help:
    def __init__(self, main_menu, camera):
        self.camera = camera
        self.main_menu = main_menu

        self.exit_button = pgt.Button(camera.ui, [camera.width - 200, camera.height - 150, 150, 100], "Exit", black,
                                      text_size, self.button_exit, dark_red, red)

        startx = 100
        starty = 100
        spacy = 35

        self.texts = [
            HelpText(startx, starty, "How to play:"),
            HelpText(startx, starty + spacy * 1, "    Left click to select boats"),
            HelpText(startx, starty + spacy * 3, "    Right click to set waypoints for the selected boat"),
            HelpText(startx, starty + spacy * 4,
                     "    Right click twice in the same spot to clear waypoints for the selected boat"),
            HelpText(startx, starty + spacy * 6, "    Middle click on another boat to do the selected boat's special"),
            HelpText(startx, starty + spacy * 7, "    Middle clicking on a friendly boat does something different"),
            HelpText(startx, starty + spacy * 8, "    than middle clicking on an enemy boat for the selected boat"),
            HelpText(startx, starty + spacy * 9, "        Destroyer - Escort/Engage"),
            HelpText(startx, starty + spacy * 10, "        Carrier- Send protective fighters/bombing attack"),
            HelpText(startx, starty + spacy * 12, "    Each boat you sink will give more money than the last"),
            HelpText(startx, starty + spacy * 13, "    Enemy boats also become more powerful as more are sunk"),
            HelpText(startx, starty + spacy * 15, "How to upgrade:"),
            HelpText(startx, starty + spacy * 16, "    Click on the Upgrades button in the main menu"),
            HelpText(startx, starty + spacy * 17, "    Select a boat from the left side"),
            HelpText(startx, starty + spacy * 18, "    Purchase relevant upgrades on the right side"),
            HelpText(startx, starty + spacy * 19,
                     "    In the top left corner, you can select your bombers or fighters to upgrade them"),
            HelpText(startx, starty + spacy * 20, "    Upgrading the planes will make them better for all carriers"),
            HelpText(startx, starty + spacy * 21,
                     "    The two buttons on the bottom of the left side allow you to purchase more boats"),
        ]

    def button_exit(self):
        self.main_menu.help = False

    def update(self, camera):
        pygame.draw.rect(camera.ui, (139, 69, 19), [50, 50, camera.width - 100, camera.height - 100])
        self.exit_button.update(camera.mouse)
        for t in self.texts:
            t.draw(camera.ui)
