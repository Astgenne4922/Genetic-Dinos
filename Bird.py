import pygame as pg

from consts import Game, Physics


class Bird(pg.sprite.Sprite):
    def __init__(self, bird_sprites, height):
        super(Bird, self).__init__()

        self.sprites = bird_sprites
        self.image = bird_sprites[0]
        self.type = height
        self.rect = self.image.get_rect()
        self.rect.move_ip(Game.SIZE[0], Game.SIZE[
            1] - Physics.GROUND_HEIGHT - (50 if height == 0 else 110 if height == 1 else 185 if height == 2 else 0))

        self.anim_frame_count = 0

    def update(self, speed):
        self.rect.move_ip(-speed, 0)

        self.image = self.sprites[0 if self.anim_frame_count > 15 else 1]

        self.anim_frame_count += 1
        self.anim_frame_count %= 30

        if self.rect.right < 0:
            self.kill()
