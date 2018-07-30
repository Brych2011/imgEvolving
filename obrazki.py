import pygame
import random
import json
from single_creature import Genome, Circle, Color, Polygon
from copy import deepcopy, copy
import argparse
import os
from PIL import Image
import multiprocessing
import pickle

from math import inf

MUTATION_RATE = 1


class Population(object):

    def __init__(self, mutation_rate=0.3, lenght=inf, multiprocessed=True, **kwargs):
        """file, size,  mutation_rate, circles, length=inf"""
        self.multiprocessed = multiprocessed
        self.pool = multiprocessing.Pool(12, initializer=init_worker, initargs=(kwargs['image'],))
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
            if kwargs.get('target'):
                Genome.set_target(kwargs['target'])
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

        if self.multiprocessed:
            kids = list(self.pool.map(breed, breedable))
        else:
            kids = list(map(breed, breedable))

        for i in kids, breedable:
            for j in i:
                new_pop.extend(j)
        self.creature_list = new_pop
        self.generation += 1

        if self.generation >= self.length:
            self.finished = True

    def legacy_save(self, directory, addition=''):
        name = '{}g {}c {}p {}.json'.format(self.generation, self.creature_list[0].figures, self.size, addition)
        file = open(os.path.join(directory, name), 'w')
        list_population = [i.get_list_representation() for i in self.creature_list]
        json.dump([self.generation, list_population], file)
        file.close()

    def save(self, directory, addition=''):
        name = '{}g {}c {}p {}.pickle'.format(self.generation, self.creature_list[0].figures, self.size, addition)
        if self.multiprocessed:
            no_pool = copy(self)
            del no_pool.pool
            file = open(os.path.join(directory, name), 'wb')
            pickle.dump(no_pool, file)
            file.close()
        else:
            file = open(os.path.join(directory, name), 'wb')
            pickle.dump(self, file)
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

    for i in range(kid1.figures):
        if random.randint(0, 1):
            kid1.genome[i] = deepcopy(creature2.genome[i])
    if random.randint(1, 1000) < 1000 * MUTATION_RATE:
        kid1.mutate()

    kid1.update_array()
    kid1.update_fitness()

    for i in range(kid2.figures):
        if random.randint(0, 1):
            kid2.genome[i] = deepcopy(creature1.genome[i])
    if random.randint(1, 1000) < 1000 * MUTATION_RATE:
        kid2.mutate()

    kid2.update_array()
    kid2.update_fitness()
    return kid1, kid2


def init_worker(img):
    Genome.set_target(img)


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

    args = vars(parser.parse_args())

    path = args['directory']
    if os.path.exists(path):
        new_im = pygame.image.load(os.path.join(path, 'target.bmp'))

        Genome.set_target(new_im)

        file_list = [f for f in os.listdir(path) if f.endswith('.pickle')]
        sorted_file_list = sorted(file_list, key=lambda file_list: int(file_list[:file_list.find('g')]))
        file = open(os.path.join(path, sorted_file_list[-1]), 'rb')
        mPopulation = pickle.load(file)
        mPopulation.pool = multiprocessing.Pool(12, initializer=init_worker, initargs=(new_im,))


    else:
        os.makedirs(path)

        chosen_image = Image.open(args['image'])
        chosen_image.save(os.path.join(path, 'original.' + chosen_image.format.lower()))
        chosen_image.thumbnail((90, 90))

        chosen_image.save(os.path.join(path, 'target.bmp'), 'BMP')

        Genome.set_target(chosen_image)

        mPopulation = Population(size=args['population'], circles=8, image=chosen_image)

    try:
        max_fitness = mPopulation.creature_list[0].fitness
        last_size_fitness = -inf
        while True:
            mPopulation.sort()
            mPopulation.next_gen()

            if mPopulation.get_circle_diversity() < mPopulation.creature_list[0].figures * 1.5:
                pass

            if mPopulation.generation % 50 == 2:
                mPopulation.save(path)
                print('generation: {:<6} best fitness: {:<11} '
                      'diversity of with {} circles'.format(mPopulation.generation,
                                                               mPopulation.creature_list[0].fitness,
                                                               mPopulation.creature_list[0].figures))

            if mPopulation.generation % 500 == 1:

                if mPopulation.best_creature.fitness - last_size_fitness > 0 and\
                        mPopulation.best_creature.fitness / max_fitness - 1 < 0.003 and \
                        mPopulation.best_creature.figures <= args['circles']:

                    last_size_fitness = mPopulation.best_creature.fitness
                    for i in mPopulation.creature_list:
                        new_figure = Circle() if random.randint(0, 1) else Polygon()
                        i.genome.insert(random.randint(0, i.figures), new_figure)
                        i.figures += 1
                        i.update_array()
                        i.update_fitness()
                max_fitness = mPopulation.best_creature.fitness



    except KeyboardInterrupt:
        mPopulation.creature_list[0].draw(scale=7, save=True, path=path, name='ziemniaki.bmp', show=True)
        mPopulation.save(path)

