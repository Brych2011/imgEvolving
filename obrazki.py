import pygame
import random
import json
from single_creature import Genome, Circle, Color
from copy import deepcopy
import argparse
import os
from PIL import Image
import multiprocessing
import time

from math import inf

MUTATION_RATE = 0.3


class Population(object):

    def __init__(self, mutation_rate=0.3, lenght=inf,  **kwargs):
        """file, size,  mutation_rate, circles, length=inf"""
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

        kids = list(map(breed, breedable))

        for i in kids, breedable:
            for j in i:
                new_pop.extend(j)
        self.creature_list = new_pop
        self.generation += 1

        if self.generation >= self.length:
            self.finished = True

    def save(self, directory, addition=''):
        name = '{}g {}c {}p{}.json'.format(self.generation, self.creature_list[0].circles, self.size, addition)
        file = open(os.path.join(directory, name), 'w')
        list_population = [i.get_list_representation() for i in self.creature_list]
        json.dump([self.generation, list_population], file)
        file.close()

    def get_circle_diversity(self, better=False):
        existing_circles = []
        if better:
            thing_to_iterate = self.creature_list[:self.size//2]
        else:
            thing_to_iterate = self.creature_list
        for creature in thing_to_iterate:
            for circle in creature.genome:
                if not circle in existing_circles:
                    existing_circles.append(circle)
        return len(existing_circles)

    def merge(self, second_pop):
        if self.best_creature.fitness <= second_pop.best_creature.fitness:
            second_pop.merge(self)
        else:
            self.creature_list[1:] = second_pop.creature_list[:-1]


def select(population):
    """function for selecting and pairing genomes to breed. Population should be sorted beforehand"""
    sum_fitness = 0
    max_fitness = population[0].fitness
    min_fintess = population[-1].fitness
    temp = []
    result = []
    for creature in population:
        sum_fitness += creature.fitness - min_fintess
        temp.append((creature, creature.fitness - min_fintess))

    for i in range(population.size//4):
        ok = False
        while not ok:
            chosen = random.randrange(0, sum_fitness)
            for entry in temp:
                chosen -= entry[1]
                if chosen <= 0:
                    candidate1 = entry[0]
            chosen = random.randrange(0, sum_fitness)
            for entry in temp:
                chosen -= entry[1]
                if chosen <= 0:
                    candidate2 = entry[0]
            ok = candidate1 is candidate2
        result.append((candidate1, candidate2))
    return result
        

def dumb_select(population):
    result = []
    for i in range(0, population.size//2, 2):
        result.append((population[i], population[i+1]))
    return result


def breed(tuple_creatures):
    creature1, creature2 = tuple_creatures
    kid1, kid2 = deepcopy(creature1), deepcopy(creature2)

    for i in range(kid1.circles):
        if random.randint(0, 1):
            kid1.genome[i] = deepcopy(creature2.genome[i])
    if random.randint(1, 1000) < 1000 * MUTATION_RATE:
        kid1.mutate(0.6)

    kid1.update_array()
    kid1.update_fitness()

    for i in range(kid2.circles):
        if random.randint(0, 1):
            kid2.genome[i] = deepcopy(creature1.genome[i])
    if random.randint(1, 1000) < 1000 * MUTATION_RATE:
        kid2.mutate(0.6)

    kid2.update_array()
    kid2.update_fitness()
    return kid1, kid2


def init_worker(img):
    Genome.change_target(img)


def run_subpopulation(size, circles, pipe_entry, dir, saved=None, population=None):
    if saved:
        pop = Population(file=saved)
    elif population:
        pop = population
    else:
        pop = Population(size=size, circles=circles)
    end = False
    local_path = os.path.join(dir, multiprocessing.current_process().name)
    try:
        while True:
            pop.sort()
            pop.save(dir)
            pop.next_gen()
            if pipe_entry.poll():
                ans = pipe_entry.recv()
                if ans == 3:
                    pipe_entry.send((pop.get_circle_diversity(), pop.get_circle_diversity(better=True)))
                elif ans == 2:
                    pipe_entry.send(pop.best_creature.fitness)
                elif ans == 1:
                    pop.save(dir)
                    print(multiprocessing.current_process().name + 'done')
                elif ans == 0:
                    pipe_entry.send(pop)
                    break

    except KeyboardInterrupt:
        pop.save(dir)
        pop.best_creature.draw(scale=5, show=True, save=True, path=dir)
        print(multiprocessing.current_process().name + 'saved')


def best_pop(populations):
    best = (None, inf * -1)
    for i in enumerate(populations):
        i[1][0].send(2)
        received = i[1][0].recv()
        if received > best[1]:
            best = (i[0], received)
    return best


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Image evolving thing')

    parser.add_argument('-i', '--image', help='specify image file. Omitted if continuing')
    parser.add_argument('-d', '--directory', help='specify directory for saving population', required=True)
    parser.add_argument('-c', '--circles', help='max amount of circles on a picture. Omitted if continuing', type=int)
    parser.add_argument('-p', '--population', help='specify size of the population. Omitted if continuing', type=int)
    parser.add_argument('-r', '--parallel', help='specify amount of parallel populations', type=int)

    args = parser.parse_args()
    dir_args = vars(args)

    path = dir_args['directory']
    if os.path.exists(path):
        new_im = pygame.image.load(os.path.join(path, 'target.bmp'))
        Genome.change_target(new_im)

        settings_file = open(os.path.join(path, 'settings.json'))
        settings = json.load(settings_file)

        pops = []
        for i in settings['populations']['names']:
            pop_path = os.path.join(path, i)
            file_list = [f for f in os.listdir(pop_path) if f.endswith('.json')]
            sorted_file_list = sorted(file_list, key=lambda file_list: int(file_list[:file_list.find('g')]))
            file = open(os.path.join(pop_path, sorted_file_list[-1]), 'r')
            pipe1, pipe2 = multiprocessing.Pipe()
            process = multiprocessing.Process(target=run_subpopulation, name=i,
                                              args=(settings['population_size'], settings['circles'], pipe2, pop_path),
                                              kwargs={'saved': file})
            pops.append((pipe1, process))
            process.start()

    else:
        os.makedirs(path)

        chosen_image = Image.open(dir_args['image'])
        chosen_image.save(os.path.join(path, 'original.' + chosen_image.format.lower()))
        chosen_image.thumbnail((90, 90))
        chosen_image.save(os.path.join(path, 'target.bmp'), 'BMP')
        Genome.change_target(chosen_image)

        settings_file = open(os.path.join(path, 'settings.json'), 'w')
        settings = {'populations':{'amount': args.parallel, 'names': [], 'finished_names': []},
                    'population_size': args.population, 'circles': args.circles, 'const_circles': True}

        pops = []
        for i in range(args.parallel):
            pop_name = 'pop' + str(i)
            settings['populations']['names'].append(pop_name)
            pipe1, pipe2 = multiprocessing.Pipe()
            process = multiprocessing.Process(target=run_subpopulation, name=pop_name,
                                              args=(args.population, args.circles, pipe2, os.path.join(args.directory, pop_name)))
            pops.append([pipe1, process])
            pops[i][1].start()
            os.makedirs(os.path.join(path, pop_name))

        json.dump(settings, settings_file)
        settings_file.close()

    try:
        lead = 0
        print(settings['populations']['names'])
        while True:
            time.sleep(10)
            lead = best_pop(pops)
            pops[lead[0]][0].send(3)  # Query best population for diversity
            diversity = pops[lead[0]][0].recv()
            print(diversity)

            if diversity[1] < settings['circles'] * 1.4:
                pops[lead[0]][0].send(0)
                received_good_pop = pops[lead[0]][0].recv()
                pops[lead[0]][1].join()
                name1 = pops[lead[0]][1].name
                del pops[lead[0]]

                lead = best_pop(pops)

                pops[lead[0]][0].send(0)
                received_bad_pop = pops[lead[0]][0].recv()
                pops[lead[0]][1].join()
                name2 = pops[lead[0]][1].name
                del pops[lead[0]]

                received_good_pop.merge(received_bad_pop)

                pipe1, pipe2 = multiprocessing.Pipe()
                better_process = multiprocessing.Process(target=run_subpopulation, name=name1,
                                                         kwargs={'population': received_good_pop},
                                                         args=(args.population, args.circles, pipe2,
                                                               os.path.join(args.directory, name1)))
                better_process.start()
                pops.append((pipe1, better_process))

                new_name = 'pop{}'.format(str(len(settings['populations']['names']) + len(settings['populations']['finished_names'])))
                pipe1, pipe2 = multiprocessing.Pipe()
                os.makedirs(os.path.join(args.directory, new_name))
                new_process = multiprocessing.Process(target=run_subpopulation, name=new_name,
                                              args=(args.population, args.circles, pipe2, os.path.join(args.directory, new_name)))
                new_process.start()
                pops.append((pipe1, new_process))

                settings['populations']['names'].remove(name2)
                settings['populations']['names'].append(new_name)
                settings['populations']['finished_names'].append(name2)

                print('population {} merged with population {}'.format(name1, name2))


            print(lead[1])
            time.sleep(5)
            """
            for i in pops:
                i[0].send(1)
            """

    except KeyboardInterrupt:
        json.dump(settings, settings_file)
        print('please wait for saving')
        for i in pops:
            i[1].join()

