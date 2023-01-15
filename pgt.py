import pygame


class Text:
    def __init__(self, x, y, text, text_color, text_size, align="center"):
        self.font = pygame.font.SysFont(None, text_size)
        self.text = self.font.render(text, True, text_color)
        self.x = x
        self.y = y
        r = self.text.get_rect()
        if align == "center":
            x -= r.width / 2
            y -= r.height / 2

    def draw(self, surface):
        surface.blit(self.text, (self.x, self.y))


def text(surface, coor, text, text_color, text_size, align="center"):
    font = pygame.font.SysFont(None, text_size)
    text = font.render(text, True, text_color)
    x, y = coor[0], coor[1]
    r = text.get_rect()
    if align == "center":
        x -= r.width / 2
        y -= r.height / 2
    surface.blit(text, (x, y))


class Button:
    def __init__(self, surface, rect, text, text_color, text_size, action, color, highlighted_color, arg=None):
        self.surface = surface
        self.action = action
        self.rect = rect
        self.text = text
        self.text_color = text_color
        self.text_size = text_size
        self.action = action
        self.color = color
        self.highlighted_color = highlighted_color
        self.arg = arg

        self.font = pygame.font.SysFont(None, text_size)
        self.text = self.font.render(text, True, text_color)
        self.textrect = self.text.get_rect()

        self.buttoncenter = (rect[0] + rect[2] / 2, rect[1] + rect[3] / 2)

        self.textcenter = (rect[0] + self.textrect[2] / 2, rect[1] + self.textrect[3] / 2)

        self.surface.blit(self.text, (
            rect[0] - (self.textcenter[0] - self.buttoncenter[0]),
            rect[1] - (self.textcenter[1] - self.buttoncenter[1])))

    def update(self, mouse=None, newx=None, newy=None):
        global canclick

        if newx is not None:
            self.rect[0] = newx
        if newy is not None:
            self.rect[1] = newy
        if mouse is not None:
            mouse = [pygame.mouse.get_pos(), pygame.mouse.get_pressed()[0]]
        mousex, mousey, click = mouse[0][0], mouse[0][1], mouse[1]

        if not click:
            canclick = True

        if self.rect[0] < mousex < self.rect[0] + self.rect[2] and mousey > self.rect[1] and mousey < self.rect[1] + \
                self.rect[3]:
            if self.color != "none":
                pygame.draw.rect(self.surface, self.highlighted_color, self.rect)

            if click and canclick:

                if self.arg is None:
                    self.action()

                else:
                    self.action(self.arg)

                canclick = False

        else:
            if self.color != "none":
                pygame.draw.rect(self.surface, self.color, self.rect)

        self.surface.blit(self.text, (self.rect[0] - (self.textcenter[0] - self.buttoncenter[0]),
                                      self.rect[1] - (self.textcenter[1] - self.buttoncenter[1])))
