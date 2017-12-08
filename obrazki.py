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
        file = kwargs.get('file')
        self.mutation_rate = mutation_rate
        self.length = lenght
        if file:
            self.generation, population_list = json.load(file)
            self.creature_list = []
            for genome in population_list:
                self.creature_list.append(Genome(len(genome), genome))

            self.size = len(self.creature_list)
        else:
            self.size = kwargs['size']
            self.creature_list = [Genome(kwargs['circles']) for i in range(self.size)]
            self.generation = 0

    def sort(self):
        temp = [(i, i.fitness) for i in self.creature_list]
        self.creature_list = [i[0] for i in sorted(temp, key=lambda item: item[1] * -1)]

    def next_gen(self):
        self.sort()

        new_pop = []
        breedable = [(self.creature_list[i], self.creature_list[i+1]) for i in range(0, self.size//2, 2)]

        kids = list(map(breed, breedable))

        for i in kids, breedable:
            for j in i:
                new_pop.extend(j)
        self.creature_list = new_pop

    def save(self, directory):
        name = '{}g {}c {}p.json'.format(self.generation, self.creature_list[0].circles, self.size)
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


def sort_population(pop):
    temp = [(i, i.fitness) for i in pop]
    sorted_temp = [i[0] for i in sorted(temp, key=lambda temp: temp[1] * -1)]
    return sorted_temp


def next_gen(sorted_pop):
    new_pop = []
    breedable = [(sorted_pop[i], sorted_pop[i+1], T) for i in range(0, len(sorted_pop)//2, 2)]

    kids = list(pool.map(breed, breedable))

    for i in kids:
        new_pop.extend(i)
    for i in breedable:
        new_pop.extend(i[:2])
    return new_pop


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


def count_difference(pop):
    max_difference = len(pop[0].array.flat) * 255
    differences = []
    for i in range(1, len(pop)):
        dif = sum(abs(pop[0].array - pop[i].array).flat)
        differences.append(dif)
    return (sum(differences)/len(differences))/max_difference


def check_circle_diversity(pop):
    existing_circles = []
    for creature in pop:
        for circle in creature.genome:
            if not circle in existing_circles:
                existing_circles.append(circle)
    return len(existing_circles)


def init_worker(img):
    Genome.change_target(img)


def save_population(pop):
    name = '{}g {}c {}p.json'.format(gen, pop[0].circles, len(pop))
    file = open(os.path.join(path, name), 'w')
    list_population = [i.get_list_representation() for i in pop]
    json.dump([gen, T, list_population], file)
    file.close()


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

        Genome.change_target(new_im)

        file_list = [f for f in os.listdir(path) if f.endswith('.json')]
        sorted_file_list = sorted(file_list, key=lambda file_list: int(file_list[:file_list.find('g')]))
        file = open(os.path.join(path, sorted_file_list[-1]), 'r')
        mPopulation = Population(file=file)

    else:
        os.makedirs(path)

        chosen_image = Image.open(args['image'])
        chosen_image.save(os.path.join(path, 'original.' + chosen_image.format.lower()))
        chosen_image.thumbnail((90, 90))

        chosen_image.save(os.path.join(path, 'target.bmp'), 'BMP')

        Genome.change_target(chosen_image)

        mPopulation = Population(size=args['population'], circles=100)

    try:
        max_fitness = mPopulation.creature_list[0].fitness
        while True:
            mPopulation.sort()
            mPopulation.next_gen()
            mPopulation.generation += 1

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

