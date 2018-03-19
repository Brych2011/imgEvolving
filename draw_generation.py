from single_creature import Genome
import argparse
import glob
import os
import json
from pygame import image

parser = argparse.ArgumentParser(description='script for rendering images of a population')

parser.add_argument('-d', '--directory', help='specify path to evolving project')
parser.add_argument('-g', '--generation', help='specify which generation to draw')
parser.add_argument('-s', '--scale', type=int)

args = vars(parser.parse_args())

path = args['directory']
findings = glob.glob(os.path.join(path, '{}*json'.format(args['generation'])))
print(findings)

new_im = image.load(os.path.join(path, 'target.bmp'))
Genome.set_target(new_im)

file = open(findings[0], 'r')
save = json.load(file)
gen = save[0]
population = []
for genome in save[1]:
    population.append(Genome(len(genome), genome))
path2 = os.path.join(path, 'gen {} images'.format(args['generation']))
os.makedirs(path2)
i = 0
for creature in population:
    creature.draw(save=True, scale=args['scale'], path=path2, name=str(i), show=False)
    i += 1
