import pygame as pg

from consts import Game, Physics


class Cactus(pg.sprite.Sprite):
    def __init__(self, cacti_type):
        super(Cactus, self).__init__()

        self.image = cacti_type
        self.rect = self.image.get_rect()
        self.rect.move_ip(Game.SIZE[0], Game.SIZE[1] - Physics.GROUND_HEIGHT - self.image.get_height() + 40)

    def update(self, speed):
        self.rect.move_ip(-speed, 0)

        if self.rect.right < 0:
            self.kill()
