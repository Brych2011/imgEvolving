import pygame
from PIL import Image
import numpy as np
import random
import json
from single_creature import Genome
from copy import deepcopy

POPULATION = 16
MUTATION_RATE = 0.1


def sort_population(pop):
    temp = [(i, i.fitness) for i in pop]
    return [i[0] for i in sorted(temp, key=lambda temp: temp[1] * -1)]


def next_gen(sorted_pop):
    new_pop = []
    breedable = sorted_pop[:len(sorted_pop)//2]
    new_pop.extend(breedable)
    for i in range(0, len(breedable)):
        kid = deepcopy(breedable[i])
        kid.mutate()
        new_pop.append(kid)
    return new_pop


def breed(creature1, creature2):
    kid1, kid2 = deepcopy(creature1), deepcopy(creature2)
    for i in range(kid1.circles):
        if random.randint(0, 1):
            kid1.genome[i] = creature2.genome[1]
    if random.randint(1,1000) < 1000 * MUTATION_RATE:
        kid1.mutate()

    for i in range(kid2.circles):
        if random.randint(0, 1):
            kid2.genome[i] = creature1.genome[1]
    if random.randint(1, 1000) < 1000 * MUTATION_RATE:
        kid2.mutate()

    return kid1, kid2


def save_population(pop):
    file = open('saved_instance.json', 'w')
    list_population = [i.get_list_representation() for i in pop]
    json.dump([gen, list_population], file)
    file.close()


if __name__ == '__main__':
    try:
        file = open('saved_instance.json', 'r')
        save = json.load(file)
        gen = save[0]
        population = []
        for genome in save[1]:
            population.append(Genome(len(genome), genome))

    except FileNotFoundError:
        gen = 0
        population = []
        for i in range(POPULATION):
            population.append(Genome(25))

    try:
        while True:
            sorted_pop = sort_population(population)
            population = next_gen(sorted_pop)
            gen += 1
            if gen % 200 == 0:
                print(gen, population[0].fitness)
                if gen % 1000 == 0:
                    save_population(population)

    except KeyboardInterrupt:
        population[0].draw(scale=7, save=True)
        save_population(population)

