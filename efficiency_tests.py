import pygame
from PIL import Image, ImageDraw
import numpy as np
import random
import time

IMAGE = Image.open('mona_lisa_small.jpg')
TARGET = np.array(IMAGE)
SIZE = IMAGE.size
IMAGE.show()
IMAGE.thumbnail((90,60))
IMAGE.show()
SHAPE = TARGET.shape
CIRCLES = 50
ACCURACY = 8


def genome_to_array(genome):
    pgim = pygame.Surface((SIZE[0], SIZE[1]), pygame.SRCALPHA)
    for circle in genome:
        new_im = pygame.Surface((circle[2] * 2, circle[2] * 2), pygame.SRCALPHA)
        new_im.fill(circle[0])
        pgim.blit(new_im, circle[1])
    return pygame.surfarray.array3d(pgim)


def pil_genome_to_array(genome):
    result = Image.new('RGBA', SIZE)
    for circle in genome:
        new_circle = Image.new('RGBA', SIZE)
        draw = ImageDraw.Draw(new_circle)
        coordinates = circle[1]
        radius = circle[2]
        draw.ellipse((coordinates[0] - radius, coordinates[1] - radius,
                      coordinates[0] + radius, coordinates[1] + radius), tuple(circle[0]))
        result = Image.alpha_composite(result, new_circle)
        del new_circle
        del draw
    return np.array(result)


def random_genome():
    result = []
    for i in range(CIRCLES):
        pos = [random.randint(0, SIZE[0]-1), random.randint(0, SIZE[1]-1)]
        color = [random.randint(0, 255) for i in range(4)]
        radius = random.randint(1, 75)
        result.append([color, pos, radius])
    return result


creature = random_genome()
t1 = time.time()
for i in range(5000):
    arr_genome = genome_to_array(creature)
t_pygame = time.time() - t1

t1 = time.time()
for i in range(10):
    arr_genome = pil_genome_to_array(creature)
t_pil = time.time() - t1

print(t_pil, t_pygame)
