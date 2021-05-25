import pygame as pg

from Cactus import Cactus
from consts import Game, Physics


class Dino(pg.sprite.Sprite):
    def __init__(self, jump_sprite, duck_sprites, run_sprites):
        super(Dino, self).__init__()

        self.jump_sprite = jump_sprite
        self.duck_sprites = duck_sprites
        self.run_sprites = run_sprites

        self.anim_frame_count = 0

        self.posY = 0
        self.velY = 0
        self.gravity = 1.2

        self.image = self.run_sprites[0]
        self.rect = self.image.get_rect()
        self.rect.move_ip(
            (Physics.PLAYER_X_POS, Game.SIZE[1] - Physics.GROUND_HEIGHT - self.image.get_height() + 40))

        self.is_duck = False

    def move(self):
        self.posY += self.velY

        if self.posY > 0:
            self.velY -= self.gravity
        else:
            self.posY = 0
            self.velY = 0

        self.animate()

    def jump(self, is_big):
        if self.posY == 0:
            if is_big:
                self.gravity = 1
                self.velY = 20
            else:
                self.gravity = 1.2
                self.velY = 16

    def duck(self, is_duck):
        if self.posY != 0 and is_duck:
            self.gravity = 3

        self.is_duck = is_duck

    def animate(self):
        frame = 0 if self.anim_frame_count > 5 else 1

        if self.is_duck and self.posY == 0:
            self.image = self.duck_sprites[frame]
        elif self.posY == 0:
            self.image = self.run_sprites[frame]
        else:
            self.image = self.jump_sprite

        self.rect = self.image.get_rect()
        self.rect.move_ip(
            (Physics.PLAYER_X_POS, Game.SIZE[1] - Physics.GROUND_HEIGHT - self.posY - self.image.get_height() + 40))

        self.anim_frame_count += 1
        self.anim_frame_count %= 10

    def check_collision(self, obstacles):
        for o in obstacles:
            if pg.sprite.collide_rect(self, o):
                return True
        return False

    def look(self, obstacles, obstacle_speed):
        closest = None
        closest_idx = -1

        o = obstacles.sprites()

        for i in range(len(o)):
            if closest is not None and self.rect.right < o[i].rect.left < (closest.rect.left - self.rect.right):
                closest = o[i]
                closest_idx = i

        vision = [0 for _ in range(7)]

        if closest:
            # distance to obstacle
            vision[0] = 10. / (closest.rect.left - self.rect.right)
            # obstacle height
            vision[1] = closest.rect.height
            # obstacle width
            vision[2] = closest.rect.width
            # is bird
            vision[3] = 0 if isinstance(closest, Cactus) else 1
            # obstacle speed
            vision[4] = obstacle_speed
            # dino y position
            vision[5] = self.posY
            # gap between obstacles
            second_closest = None
            for (i, o) in range(len(o)):
                if closest is not None and i != closest_idx and 0 < (o[i].rect.left - self.rect.right) < (
                        second_closest.rect.left - self.rect.right):
                    second_closest = o[i]
            vision[6] = 0 if not second_closest else 1. / (
                    (closest.rect.left - self.rect.right) - second_closest.rect.left - self.rect.right)
        else:
            vision = [0, 0, 0, 0, obstacle_speed, self.posY, 0]

        return vision

    def think(self, decision):
        decision_max = max(decision)
        decision_max_idx = decision.index(decision_max)

        if decision_max < 0.7:
            self.duck(False)
            return

        if decision_max_idx == 0:
            self.jump(False)
        elif decision_max_idx == 1:
            self.jump(True)
        elif decision_max_idx == 2:
            self.duck(True)
