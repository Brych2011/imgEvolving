import pygame
import json
import argparse
import os
from PIL import Image
import imageio
import numpy as np

parser = argparse.ArgumentParser(description='Create GIF images based on best creatures')

parser.add_argument('-d', '--directory', help='Save directory path path')
parser.add_argument('-s', '--scale', help='Scale of result GIF', type=int)
parser.add_argument('-f', '--fps', help='Determine FPS. Default 10', type=int)


args = vars(parser.parse_args())
scale = args['scale']

if not args['fps']:
    args['fps'] = 10

path = args['directory']
file_list = [f for f in os.listdir(path) if f.endswith('.json')]
sorted_file_list = sorted(file_list, key=lambda file_list: int(file_list[:file_list.find('g')]))

target_im = Image.open(os.path.join(path, 'target.bmp'))

image_list = []
for i in sorted_file_list:
    file = open(os.path.join(path, i))
    try:
        gen, population = json.load(file)
    except json.JSONDecodeError:
        print('unreadable file:', i)
    creature = population[0]
    file.close()

    pgim = pygame.Surface((target_im.size[0] * scale, target_im.size[1] * scale), pygame.SRCALPHA)

    for circle in creature:
        new_im = pygame.Surface((circle[2] * 2 * scale, circle[2] * 2 * scale),
                                pygame.SRCALPHA)  # create a surface of size of the circle
        pygame.draw.circle(new_im, circle[0],
                           (circle[2] * scale, circle[2] * scale),
                           circle[2] * scale)  # #draw circle in the middle of its Surface
        pgim.blit(new_im, [(circle[1][0] - circle[2]) * scale,
                           (circle[1][1] - circle[2]) * scale])  # #blit onto main surface

    pg_stringim = pygame.image.tostring(pgim, 'RGB')
    im = Image.frombytes('RGB', (target_im.size[0] * scale, target_im.size[1] * scale), pg_stringim)
    image_list.append(np.array(im))

imageio.mimsave(os.path.join(path, 'animation.gif'), image_list, loop=1, fps=args['fps'])
