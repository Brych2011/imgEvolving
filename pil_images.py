from PIL import Image, ImageDraw
import pygame
import random
# # hey there
SIZE = 500,500
CIRCLES = 50


def draw_creature(genome):
    pgim = pygame.Surface((SIZE[0], SIZE[1]), pygame.SRCALPHA)
    for circle in genome:
        new_im = pygame.Surface((circle[2] * 2, circle[2] * 2), pygame.SRCALPHA)
        color = circle[0].copy()
        color.append(circle[3])
        pygame.draw.circle(new_im, color, (circle[2], circle[2]), circle[2])
        pgim.blit(new_im, [circle[1][i] - circle[2] for i in range(2)])
    pg_stringim = pygame.image.tostring(pgim, 'RGBA')
    im = Image.frombytes('RGBA', (SIZE[0], SIZE[1]), pg_stringim)
    im.show()


def random_genome():
    result = []
    for i in range(CIRCLES):
        pos = [random.randint(0, SIZE[0]-1), random.randint(0, SIZE[1]-1)]
        color = [random.randint(0, 255) for i in range(3)]
        radius = random.randint(1, 100)
        opacity = random.randint(0, 255)
        result.append([color, pos, radius, opacity])
    return result


creature = [[[200,100,100], [0,0], 50, 255]]
draw_creature(creature)
draw_creature(random_genome())
