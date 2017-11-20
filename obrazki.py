import pygame
import random
import json
from single_creature import Genome, Circle, Color
from copy import deepcopy
import argparse
import os
from PIL import Image
import multiprocessing

MUTATION_RATE = 0.3


def sort_population(pop):
    temp = [(i, i.fitness) for i in pop]
    return [i[0] for i in sorted(temp, key=lambda temp: temp[1] * -1)]


def next_gen(sorted_pop):
    new_pop = []
    breedable = sorted_pop[:len(sorted_pop)//2]
    new_pop.extend(breedable)
    for i in range(0, len(breedable), 2):
        kid1, kid2 = breed(breedable[i], breedable[i+1])
        new_pop.extend((kid1, kid2))
    return new_pop


def breed(creature1, creature2):
    kid1, kid2 = deepcopy(creature1), deepcopy(creature2)

    for i in range(kid1.circles):
        if random.randint(0, 1):
            kid1.genome[i] = deepcopy(creature2.genome[i])
    if random.randint(1, 1000) < 1000 * MUTATION_RATE:
        kid1.mutate()
    else:
        kid1.update_array()
        kid1.update_fitness()

    for i in range(kid2.circles):
        if random.randint(0, 1):
            kid2.genome[i] = deepcopy(creature1.genome[i])
    if random.randint(1, 1000) < 1000 * MUTATION_RATE:
        kid2.mutate()
    else:
        kid2.update_array()
        kid2.update_fitness()
    return kid1, kid2


def save_population(pop):
    name = '{}g {}c {}p.json'.format(gen, pop[0].circles, len(pop))
    file = open(os.path.join(path, name), 'w')
    list_population = [i.get_list_representation() for i in pop]
    json.dump([gen, list_population], file)
    file.close()


if __name__ == '__main__':
    pool = multiprocessing.Pool(4)

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
        save = json.load(file)
        gen = save[0]
        population = []
        for genome in save[1]:
            population.append(Genome(len(genome), genome))

    else:
        os.makedirs(path)

        chosen_image = Image.open(args['image'])
        chosen_image.save(os.path.join(path, 'original.' + chosen_image.format.lower()))
        chosen_image.thumbnail((90, 90))

        chosen_image.save(os.path.join(path, 'target.bmp'), 'BMP')

        Genome.change_target(chosen_image)

        gen = 0
        population = []
        for i in range(args['population']):
            population.append(Genome(3))

    try:
        max_fitness = population[0].fitness
        while True:
            sorted_pop = sort_population(population)
            population = next_gen(sorted_pop)
            gen += 1
            if gen % 50 == 0:
                print(gen, population[0].fitness, population[0].circles)
                if gen % 200 == 0:
                    if (population[0].fitness - max_fitness) / abs(max_fitness) < 0.05 and population[0].circles <= args['circles']:
                        for i in population:
                            i.genome.append(Circle(random.randint(0 - Genome.legal_border, Genome.target_shape[1] + Genome.legal_border),  # #x
                                            random.randint(0 - Genome.legal_border, Genome.target_shape[0] + Genome.legal_border),  # #y
                                            random.randint(1, Genome.max_radius), Color()))
                            i.circles += 1
                            i.update_array()
                            i.update_fitness()
                    save_population(population)
                    max_fitness = population[0].fitness

    except KeyboardInterrupt:
        population[0].draw(scale=7, save=True, path=path, name='ziemniaki.bmp')
        save_population(population)

