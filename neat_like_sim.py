import pickle
from copy import deepcopy, copy
from operator import attrgetter
from random import choice, randint, randrange

import pygame
import numpy as np
from PIL import Image
from creatures import Genome
from shapes import SimulationRules
from sklearn.preprocessing import normalize
import multiprocessing
import os


class Species(object):

    def __init__(self, founder, rules):
        self.genomes = [founder]
        self.rules = rules

        self.current_alpha = founder

    def next_generation(self):
        self.current_alpha = choice(self.genomes)
        self.genomes = [self.current_alpha]

    def species_fitness(self):
        # equivalent of summing adjusted fitness values
        return sum([g.fitness for g in self.genomes]) / len(self.genomes)

    @property
    def size(self):
        return len(self.genomes)


class Population(object):

    def __init__(self, size, rules: SimulationRules):

        self.creature_list = [Genome(0, rules) for i in range(size)]
        self.rules = rules
        self.species_list = []
        self.generation = 0
        self.pool = multiprocessing.Pool(12)
        self.best_creature = None

    def divide_to_species(self):
        for creature in self.creature_list:

            for s in self.species_list:
                if creature.compatibility_distance(s.current_alpha) < self.rules.distance_threshold:
                    creature.species = s
                    s.genomes.append(creature)
                    break
            else:
                new_species = Species(creature, self.rules)
                creature.species = new_species
                self.species_list.append(new_species)

    def assign_breed_opportunities(self):
        total_fitness = sum((c.adjusted_fitness for c in self.creature_list))
        breeding_tickets = {s: self.rules.children_per_gen * s.species_fitness() / total_fitness for s in self.species_list}
        return breeding_tickets

    def next_gen(self):

        self.divide_to_species()

        breeding_tickets = self.assign_breed_opportunities()
        parent_pairs = []
        for s in self.species_list:
            parent_pairs.extend(choose_breeding(s, breeding_tickets[s]))

        kids = list(self.pool.map(breed, parent_pairs))
        self.creature_list.sort(key=lambda c: c.adjusted_fitness * -1)
        self.best_creature = self.creature_list[0]
        to_retire = self.creature_list[-len(kids):]

        for c in to_retire:
            c.species.genomes.remove(c)
            if c.species.size < 1:
                self.species_list.remove(c.species)

        self.creature_list[-len(kids):] = kids

        for s in self.species_list:
            s.next_generation()
        self.generation += 1

    def save(self, directory):
        no_pool = copy(self)
        del no_pool.pool
        name = os.path.join(directory, "{}g {}p.pickle")
        file = open(name, 'wb')
        pickle.dump(no_pool, file)
        file.close()


def breed(parents):
    if len(parents) == 1:
        kid = parents[0].safe_copy()
        kid.gentle_mutate()
        if randrange(10000) < parents[0].rules.serious_mutation_rate * 10000:
            kid.new_circle()
        kid.update_array()
        kid.update_fitness()

        return kid

    else:

        new_genome = []

        more_fit = parents[0] if parents[0].fitness > parents[1].fitness else parents[1]
        less_fit = parents[1] if parents[0].fitness > parents[1].fitness else parents[0]

        for i in more_fit.gene_dict.keys():
            matching = less_fit.gene_dict.get(i)
            if matching:
                new_genome.append(deepcopy(matching) if randint(0, 1) else deepcopy(more_fit.gene_dict[i]))
            else:
                new_genome.append(deepcopy(more_fit.gene_dict[i]))

        kid = Genome(0, more_fit.rules, determined_genome=new_genome)
        kid.gentle_mutate()

        if randrange(10000) < more_fit.rules.serious_mutation_rate * 10000:
            kid.new_circle()

        kid.update_array()
        kid.update_fitness()

        return kid


def choose_breeding(species: Species, n):
    if len(species.genomes) == 1:
        return [(species.genomes[0],) for i in range(int(n + 0.5))]

    else:
        fit_array = np.array([g.fitness for g in species.genomes]).reshape(1, -1)
        probability_dist = normalize(fit_array, norm='l1').reshape(species.size) * -1  # change sign because fitness is negative and we need positive here

        return [np.random.choice(species.genomes, 2, p=probability_dist) for i in range(int(n + 0.5))]


def test_map(parents):
    print('witam', len(parents))


if __name__ == '__main__':
    im_path = 'mona_lisa.jpg'
    pil_obj = Image.open(im_path)
    pil_obj.thumbnail((70, 70))
    data = pil_obj.tobytes()
    pygame_img = pygame.image.fromstring(data, pil_obj.size, pil_obj.mode)
    rules = SimulationRules(target_img=pygame_img,
                            target_array=pygame.surfarray.array3d(pygame_img),
                            target_size=pygame_img.get_size(),
                            max_circle_radius=70,
                            max_margin=20,
                            propability_scales={'x': 8, 'y': 8, 'z': 8, 'r': 8, 'color': 20},
                            distance_weights={'x':1, 'y': 1, 'z': 0.5, 'r': 3, 'color': 0.1,
                                              'disjoint': 1, 'excess': 1, 'comp_genes': 0.1},
                            distance_threshold=5,
                            children_per_gen=400,
                            serious_mutation_rate=0.1)

    mPopulation = Population(1000, rules)
    try:
        while True:
            mPopulation.next_gen()
            if mPopulation.generation % 10 == 0:
                print("Generation {}. Max fitness: {:.2f} Number of species: {}".format(mPopulation.generation, mPopulation.best_creature.fitness, len(mPopulation.species_list)))
            if mPopulation.generation % 100 == 0:
                mPopulation.save("firstTest")
    except KeyboardInterrupt:
        mPopulation.save("firstTest")
        mPopulation.best_creature.draw(show=True, save=True, scale=10)
        mPopulation.pool.close()
