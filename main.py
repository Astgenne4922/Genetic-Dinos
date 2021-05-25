import os.path
import random

try:
    import neat
except ImportError:
    import os

    os.system("python -m pip install neat-python")
    import neat

try:
    import pygame as pg
except ImportError:
    import os

    os.system("python -m pip install pygame")
    import pygame as pg

from Bird import Bird
from Cactus import Cactus
from Dino import Dino
from consts import Game, Physics

pg.init()

screen = pg.display.set_mode(Game.SIZE)
pg.display.set_caption(Game.TITLE)

font = pg.font.SysFont("Helvetica", 30)

bird_sprites = [pg.image.load(f"{Game.BIRD_PATH}/{i}.png").convert_alpha() for i in range(2)]
cacti_sprites = [pg.image.load(f"{Game.CACTI_PATH}/{i}.png").convert_alpha() for i in range(3)]
dino_sprites_duck = [pg.image.load(f"{Game.DINO_DUCK_PATH}/{i}.png").convert_alpha() for i in range(2)]
dino_sprites_run = [pg.image.load(f"{Game.DINO_RUN_PATH}/{i}.png").convert_alpha() for i in range(2)]
dino_sprite_jump = pg.image.load(Game.DINO_JUMP_PATH).convert_alpha()

gen = 0


def add_obstacle():
    if random.random() < 0.15:
        return Bird(bird_sprites, random.randint(0, 2))
    else:
        return Cactus(cacti_sprites[random.randint(0, 2)])


def train(genomes, config):
    global gen

    clock = pg.time.Clock()
    SCORE_UPDATE = pg.USEREVENT + 1
    pg.time.set_timer(SCORE_UPDATE, 100)
    game_speed = 0

    min_time_to_obstacle = 60
    to_next_obstacle = 0
    obstacle_speed = 10
    obstacles = pg.sprite.Group()

    neural_nets = []
    dino_genomes = []
    dinos = []

    score = 0

    for _, g in genomes:
        neural_nets.append(neat.nn.FeedForwardNetwork.create(g, config))
        g.fitness = 0
        dino_genomes.append(g)
        dinos.append(Dino(dino_sprite_jump, dino_sprites_duck, dino_sprites_run))

    running = True
    while running:
        clock.tick(Game.FPS + game_speed)

        pressed_keys = pg.key.get_pressed()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                pg.quit()
                quit()
            if event.type == SCORE_UPDATE:
                score += 1
                for idx in range(len(dino_genomes)):
                    dino_genomes[idx].fitness += 1

        if pressed_keys[pg.K_PLUS] or pressed_keys[pg.K_KP_PLUS]:
            game_speed += 10
        elif pressed_keys[pg.K_MINUS] or pressed_keys[pg.K_KP_MINUS]:
            if game_speed > 0:
                game_speed -= 10

        if len(dinos) == 0:
            running = False
            continue

        screen.fill((255, 255, 255))

        score_text = font.render(f"Score: {score}", True, (0, 0, 0))
        screen.blit(score_text, score_text.get_rect().move((10, 10)))

        gen_text = font.render(f"Gen: {gen}", True, (0, 0, 0))
        screen.blit(gen_text, gen_text.get_rect().move((10, 40)))

        pg.draw.line(screen, (0, 0, 0), (0, Game.SIZE[1] - Physics.GROUND_HEIGHT),
                     (Game.SIZE[0], Game.SIZE[1] - Physics.GROUND_HEIGHT))

        to_next_obstacle += 1
        obstacle_speed += 0.002
        if to_next_obstacle > min_time_to_obstacle + random.randint(0, 49):
            obstacles.add(add_obstacle())
            to_next_obstacle = 0
        obstacles.update(obstacle_speed)

        for dino in dinos:
            idx = dinos.index(dino)
            dino.move()
            dino.think(neural_nets[idx].activate(dino.look(obstacles, obstacle_speed)))

            if dino.check_collision(obstacles):
                neural_nets.pop(idx)
                dino_genomes[idx].fitness -= 5
                dino_genomes.pop(idx)
                dinos.pop(idx)

        obstacles.draw(screen)
        screen.blits(((dino.image, dino.rect) for dino in dinos))

        pg.display.flip()

    gen += 1


def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_file)
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(neat.StatisticsReporter())
    winner = p.run(train, 50)

    print(f"\nBest genome:\n{winner}")


if __name__ == "__main__":
    local = os.path.dirname(__file__)
    config_path = os.path.join(local, "config-feedforward.txt")
    run(config_path)
