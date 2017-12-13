import pygame
import random
import json
from single_creature import Genome, Circle, Color
from copy import deepcopy
import argparse
import os
from PIL import Image
import multiprocessing

from math import inf

MUTATION_RATE = 0.3


class Population(object):

    def __init__(self, mutation_rate=0.3, lenght=inf,  **kwargs):
        """file, size,  mutation_rate, circles, length=inf"""
        self.pool = multiprocessing.Pool(4, init_worker(Genome.target_image))
        self.mutation_rate = mutation_rate
        self.length = lenght
        self.finished = False
        file = kwargs.get('file')
        if file:
            self.generation, population_list = json.load(file)
            self.creature_list = []
            for genome in population_list:
                self.creature_list.append(Genome(len(genome), genome))

            self.size = len(self.creature_list)
            self.best_creature = self.creature_list[0]
        else:
            self.size = kwargs['size']
            self.creature_list = [Genome(kwargs['circles']) for i in range(self.size)]
            self.generation = 0
            self.best_creature = self.creature_list[0]

    def sort(self):
        temp = [(i, i.fitness) for i in self.creature_list]
        self.creature_list = [i[0] for i in sorted(temp, key=lambda item: item[1] * -1)]
        self.best_creature = self.creature_list[0]

    def next_gen(self):
        self.sort()

        new_pop = []
        breedable = [(self.creature_list[i], self.creature_list[i+1]) for i in range(0, self.size//2, 2)]

        kids = list(self.pool.map(breed, breedable))

        for i in kids, breedable:
            for j in i:
                new_pop.extend(j)
        self.creature_list = new_pop
        self.generation += 1

        if self.generation >= self.length:
            self.finished = True

    def save(self, directory, addition=''):
        name = '{}g {}c {}p {}.json'.format(self.generation, self.creature_list[0].circles, self.size, addition)
        file = open(os.path.join(directory, name), 'w')
        list_population = [i.get_list_representation() for i in self.creature_list]
        json.dump([self.generation, list_population], file)
        file.close()

    def get_circle_diversity(self):
        existing_circles = []
        for creatue in self.creature_list:
            for circle in creatue.genome:
                if not circle in existing_circles:
                    existing_circles.append(circle)
        return len(existing_circles)

    def merge(self, second_pop):
        if self.best_creature.fitness <= second_pop.best_creature.fitness:
            second_pop.merge(self)
        else:
            self.creature_list[self.size//4:] = second_pop.creature_list[:-1 * self.size//4]


def breed(tuple_creatures):
    creature1, creature2 = tuple_creatures
    kid1, kid2 = deepcopy(creature1), deepcopy(creature2)

    for i in range(kid1.circles):
        if random.randint(0, 1):
            kid1.genome[i] = deepcopy(creature2.genome[i])
    if random.randint(1, 1000) < 1000 * MUTATION_RATE:
        kid1.mutate()

    kid1.update_array()
    kid1.update_fitness()

    for i in range(kid2.circles):
        if random.randint(0, 1):
            kid2.genome[i] = deepcopy(creature1.genome[i])
    if random.randint(1, 1000) < 1000 * MUTATION_RATE:
        kid2.mutate()

    kid2.update_array()
    kid2.update_fitness()
    return kid1, kid2


def init_worker(img):
    Genome.change_target(img)


def run_subpopulation(size, circles, pipe_entry, dir):
    pop = Population(size=size, circles=circles)
    end = False
    while not end:
        pop.sort()
        pop.next_gen()
        if pipe_entry.poll():
            ans = pipe_entry.recv()
            if ans == 2:
                pipe_entry.send(pop.generation)
            elif ans == 1:
                pop.save(dir, multiprocessing.current_process().name)
            else:
                end = True
    pipe_entry.send(pop)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Image evolving thing')

    parser.add_argument('-i', '--image', help='specify image file. Omitted if continuing')
    parser.add_argument('-d', '--directory', help='specify directory for saving population', required=True)
    parser.add_argument('-c', '--circles', help='max amount of circles on a picture. Omitted if continuing', type=int)
    parser.add_argument('-p', '--population', help='specify size of the population. Omitted if continuing', type=int)
    parser.add_argument('-r', '--paralell', help='specify amount of parallel populations', type=int)

    args = parser.parse_args()
    dir_args = vars(args)

    path = dir_args['directory']
    if os.path.exists(path):
        new_im = pygame.image.load(os.path.join(path, 'target.bmp'))

        Genome.change_target(new_im)

        file_list = [f for f in os.listdir(path) if f.endswith('.json')]
        sorted_file_list = sorted(file_list, key=lambda file_list: int(file_list[:file_list.find('g')]))
        file = open(os.path.join(path, sorted_file_list[-1]), 'r')
        mPopulation = Population(file=file)

    else:
        os.makedirs(path)

        chosen_image = Image.open(dir_args['image'])
        chosen_image.save(os.path.join(path, 'original.' + chosen_image.format.lower()))
        chosen_image.thumbnail((90, 90))

        chosen_image.save(os.path.join(path, 'target.bmp'), 'BMP')

        Genome.change_target(chosen_image)

        mPopulation = Population(size=dir_args['population'], circles=dir_args['circles'])

    try:
        max_fitness = mPopulation.creature_list[0].fitness
        while True:
            mPopulation.sort()
            mPopulation.next_gen()

            if mPopulation.get_circle_diversity() < mPopulation.creature_list[0].circles * 1.5:
                pass

            if mPopulation.generation % 50 == 2:
                mPopulation.save(path)
                print('generation: {:<6} best fitness: {:<11} '
                      'diversity of {} with {} circles'.format(mPopulation.generation,
                                                               mPopulation.creature_list[0].fitness,
                                                               mPopulation.get_circle_diversity(),
                                                               mPopulation.creature_list[0].circles))

            """
            if gen % 30 == 1:
                if (population[0].fitness - max_fitness) / abs(max_fitness) < 0.01 and population[0].circles <= args['circles']:
                    for i in population:
                        new_circle = Circle(random.randint(0 - Genome.legal_border, Genome.target_shape[1] + Genome.legal_border),  # #x
                                            random.randint(0 - Genome.legal_border, Genome.target_shape[0] + Genome.legal_border),  # #y
                                            random.randint(1, Genome.max_radius), Color())
                        i.genome.insert(random.randint(0, i.circles), new_circle)
                        i.circles += 1
                        i.update_array()
                        i.update_fitness()
                save_population(population)
                max_fitness = population[0].fitness
            """

    except KeyboardInterrupt:
        mPopulation.creature_list[0].draw(scale=7, save=True, path=path, name='ziemniaki.bmp', show=True)
        mPopulation.save(path)

