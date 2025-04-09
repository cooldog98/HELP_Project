from object import Object
import pygame
from os.path import isfile, join


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = self.get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

    def get_block(self, size):
        path = join('graphic', 'walland green.jpg')
        image = pygame.image.load(path).convert_alpha()
        surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
        rect = pygame.Rect(0, 0, size, size)
        surface.blit(image, (0, 0), rect)
        return pygame.transform.scale(surface, (size, size))
