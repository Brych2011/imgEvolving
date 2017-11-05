import pygame
from PIL import Image
import numpy as np
import random
import json

IMAGE = Image.open('mona_lisa.jpg')
TARGET = np.array(IMAGE)
SIZE = IMAGE.size
SHAPE = TARGET.shape
ACCURACY = 5
CIRCLES = 50
MUTATION_RATE = 0.1
POPULATION = 52
print(SIZE)


def random_genome():
    result = []
    for i in range(CIRCLES):
        pos = [random.randint(0, SIZE[0]-1), random.randint(0, SIZE[1]-1)]
        color = [random.randint(0, 255) for i in range(3)]
        radius = random.randint(1, 75)
        result.append([color, pos, radius])
    return result


def genome_to_array(genome):
    pgim = pygame.Surface((SIZE[1], SIZE[0]))
    for circle in genome:
        pygame.draw.circle(pgim, circle[0], circle[1], circle[2])
    return pygame.surfarray.array3d(pgim)


def check_fintness(genome):
    genome_array = genome_to_array(genome)
    fitness = 0
    for i in range(0, SHAPE[1], ACCURACY):
        for j in range(0, SHAPE[0], ACCURACY):
            fitness += sum(abs(TARGET[j][i] - genome_array[j][i]))
    return fitness


def permutate_colors(previous, rate):
    permutation = [random.randint(rate * -1, rate) for i in range(3)]
    result = [previous[i] + permutation[i] for i in range(3)]
    for i in range(3):
        if result[i] > 255:
            result[i] = 255
        elif result[i] < 0:
            result[i] = 0
    return result


def breed(genome1, genome2):
    new_genome1 = genome1[:CIRCLES//2] + genome2[CIRCLES//2:]
    new_genome2 = genome2[:CIRCLES//2] + genome1[CIRCLES//2:]

    if random.randint(1,40) == 1:
        new_genome1[random.randint(0,CIRCLES-1)][0] = [random.randint(0, 255) for i in range(3)]

    if random.randint(1,60)==1:
        new_genome1[random.randint(0,CIRCLES - 1)][1] = [random.randint(0, SIZE[0]-1), random.randint(0, SIZE[1]-1)]

    if random.randint(1, 60) == 1:
        new_genome1[random.randint(0, CIRCLES - 1)][2] = random.randint(1,75)

    if random.randint(1, 40) == 1:
        new_genome2[random.randint(0,CIRCLES-1)][0] = [random.randint(0, 255) for i in range(3)]

    if random.randint(1, 60) == 1:
        new_genome2[random.randint(0, CIRCLES - 1)][1] = [random.randint(0, SIZE[0] - 1),
                                                          random.randint(0, SIZE[1] - 1)]

    if random.randint(1, 60) == 1:
        new_genome2[random.randint(0, CIRCLES - 1)][2] = random.randint(1, 75)

    return new_genome1, new_genome2


def sort_population(pop):
    temp = [(i, check_fintness(i)) for i in pop]
    return [i[0] for i in sorted(temp, key=lambda temp: temp[1])]


def next_gen(sorted_pop):
    new_pop = []
    breedable = sorted_pop[:len(sorted_pop)//2]
    new_pop.extend(breedable)
    for i in range(0, len(breedable), 2):
        new_pop.extend(breed(breedable[i], breedable[i+1]))
    return new_pop


def draw_creature(genome):
    pgim = pygame.Surface((SIZE[0], SIZE[1]))
    for circle in genome:
        pygame.draw.circle(pgim, circle[0], circle[1], circle[2])
    pg_stringim = pygame.image.tostring(pgim, 'RGBA')
    im = Image.frombytes('RGBA', (SIZE[0], SIZE[1]), pg_stringim)
    im.show()


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


    draw_creature(sorted_pop[0])
    IMAGE.show()
