import pygame
import json
import argparse
import os
from PIL import Image
import imageio
import numpy as np
import pickle
from obrazki import Population

parser = argparse.ArgumentParser(description='Create GIF images based on best creatures')

parser.add_argument('-d', '--directory', help='Save directory path path')
parser.add_argument('-s', '--scale', help='Scale of result GIF', type=int)
parser.add_argument('-f', '--fps', help='Determine FPS. Default 10', type=int)


args = vars(parser.parse_args())
scale = args['scale']

if not args['fps']:
    args['fps'] = 10

path = args['directory']
file_list = [f for f in os.listdir(path) if f.endswith('.pickle')]
sorted_file_list = sorted(file_list, key=lambda file_list: int(file_list[:file_list.find('g')]))

target_im = Image.open(os.path.join(path, 'target.bmp'))

image_list = []
for i in sorted_file_list:
    file = open(os.path.join(path, i), 'rb')
    pop = pickle.load(file)
    file.close()

    pgim = pop.best_creature.get_surface(scale=scale)

    image_list.append(pygame.surfarray.array3d(pgim).transpose((1, 0, 2)))

imageio.mimsave(os.path.join(path, 'animation.gif'), image_list, loop=1, fps=args['fps'])
