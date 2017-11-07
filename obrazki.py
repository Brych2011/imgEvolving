import pygame
from PIL import Image
import numpy as np
import random
import json
from single_creature import random_genome, genome_to_array, check_fitness, mutate, draw_creature

IMAGE = Image.open('mona_lisa_even_smaller.jpg')
TARGET = np.array(IMAGE)
SIZE = IMAGE.size
SHAPE = TARGET.shape
CIRCLES = 60
MUTATION_RATE = 0.1
POPULATION = 32
print(SIZE)


def breed(genome1, genome2):
    new_genome1 = []
    new_genome2 = []
    for kid in new_genome1, new_genome2:
        for i in range(CIRCLES):
            if random.randint(0,1) == 0:
                kid.append(genome1[i])
            else:
                kid.append(genome2[i])

    if random.randint(0,1000) < 1000 * MUTATION_RATE:
        new_genome2 = mutate(new_genome2)
    if random.randint(0,1000) < 1000 * MUTATION_RATE:
        new_genome1 = mutate(new_genome1)

    return new_genome1, new_genome2


def sort_population(pop):
    temp = [(i, check_fitness(i)) for i in pop]
    return [i[0] for i in sorted(temp, key=lambda temp: temp[1])]


def next_gen(sorted_pop):
    new_pop = []
    breedable = sorted_pop[:len(sorted_pop)//2]
    new_pop.extend(breedable)
    for i in range(0, len(breedable), 2):
        new_pop.extend(breed(breedable[i], breedable[i+1]))
    return new_pop


if __name__ == '__main__':
    try:
        file = open('saved_instance.json', 'r')
        save = json.load(file)
        population = save[1]
        gen = save[0]

    except FileNotFoundError:
        gen = 0
        population = []
        for i in range(POPULATION):
            population.append(random_genome())


    try:
        while True:
            print(gen)
            sorted_pop = sort_population(population)
            population = next_gen(sorted_pop)
            gen += 1
            if gen % 100 == 0:
                file = open('saved_instance.json', 'w')
                json.dump([gen, population], file)
                file.close()

    except KeyboardInterrupt:
        file = open('saved_instance.json', 'w')
        json.dump([gen, population], file)
        file.close()

    draw_creature(sorted_pop[0], scale=9)
    IMAGE.show()
