from random import choice, randint, randrange

import pygame
import numpy as np
from PIL import Image
from creatures import Genome
from shapes import SimulationRules


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


def breed(parents):
    new_genome = []

    more_fit = parents[0] if parents[0].fitness > parents[1].fitness else parents[1]
    less_fit = parents[1] if parents[0].fitness > parents[1].fitness else parents[0]

    for i in more_fit.gene_dict.keys():
        matching = less_fit.gene_dict.get(i)
        if matching:
            new_genome.append(matching if randint(0, 1) else more_fit.gene_dict[i])
        else:
            new_genome.append(more_fit.gene_dict[i])

    kid = Genome(0, more_fit.rules, determined_genome=new_genome)
    kid.gentle_mutate()

    if randrange(10000) < more_fit.rules.serious_mutation_rate * 10000:
        kid.new_circle()

    kid.update_array()
    kid.update_fitness()

    return kid
