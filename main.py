import pygame
import math as m
from boat import *
from plane import *
from camera import Camera
from menu import MainMenu
from fleet import Fleet

pygame.init()

black = (0, 0, 0, 0)
white = (255, 255, 255)
blue = (0, 0, 255)
red = (255, 0, 0)
green = (0, 255, 0)

d_width = 1920
d_height = 1080

gameDisplay = pygame.display.set_mode((d_width, d_height))
boat_surface = pygame.surface.Surface((d_width, d_height), pygame.SRCALPHA)
plane_surface = pygame.surface.Surface((d_width, d_height), pygame.SRCALPHA)
ui_surface = pygame.surface.Surface((d_width, d_height), pygame.SRCALPHA)

clock = pygame.time.Clock()

players_fleet = Fleet()

camera = Camera(0, 0, [pygame.mouse.get_pos(), pygame.mouse.get_pressed()[0]], 1920, 1080, clock, gameDisplay, boat_surface, plane_surface, ui_surface)
camera.players_fleet = players_fleet
main_menu = MainMenu(camera, players_fleet)



def select_entity(x, y, fleet_things, current_selection):
    for b in fleet_things:
        if m.sqrt((b.x - x) ** 2 + (b.y - y) ** 2) < 40:
            camera.selected_boat_abstract = b
            return b
    return current_selection


def do_menu():
    global camera

    while True:

        camera.mouse = [pygame.mouse.get_pos(), pygame.mouse.get_pressed()[0]]
        if not main_menu.in_battle:

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.__dict__["button"] == 1:  # left click
                        x, y = event.__dict__["pos"]
                        camera.selected_boat_abstract = select_entity(x, y, players_fleet.entities, camera.selected_boat_abstract)

        camera.ui.fill(black)
        camera.background.fill(black)
        camera.foreground.fill(black)
        gameDisplay.fill(black)

        main_menu.update(camera)

        gameDisplay.blit(camera.background, (0, 0))
        gameDisplay.blit(camera.foreground, (0, 0))
        camera.gameDisplay.blit(camera.ui, (0, 0))

        pygame.draw.rect(camera.gameDisplay, white, [10, 10, camera.width - 20, camera.height - 20], 1)
        pgt.text(camera.gameDisplay, (20, 20), str(int(camera.clock.get_fps())), (100, 100, 100), 15, "right")
        pygame.display.update()
        clock.tick(60)


do_menu()
