import pygame

bar_width = 50
bar_height = 2


def draw_bar(surface, x, y, v, max_v, color):
    pygame.draw.rect(surface, (255, 255, 255), [x - bar_width / 2, y - bar_height / 2, bar_width, bar_height])
    pygame.draw.rect(surface, color, [x - bar_width / 2, y - bar_height / 2, bar_width * (v / max_v), bar_height])
