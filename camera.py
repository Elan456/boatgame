import pygame


class Camera:
    def __init__(self, x, y, mouse, width, height, clock, gameDisplay, background, foreground, ui):
        self.clock = clock
        self.mouse = mouse
        self.ui = ui
        self.foreground = foreground
        self.background = background
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.selected_boat = None
        self.selected_boat_abstract = None
        self.players_fleet = None
        self.gameDisplay = gameDisplay

