import numpy as np
import pygame
from shapes import SimulationRules, Circle
from PIL import Image
from neat_like_sim import Species


class Genome(object):

    def __init__(self, figures, rules: SimulationRules, determined_genome=None):

        if determined_genome:
            self.gene_list = determined_genome
            self.figure_count = len(self.gene_list)

        else:
            self.figure_count = figures
            self.gene_list = [Circle.random_circle(rules) for i in range(self.figure_count)]

        self.innovation_indices = [g.innovation for g in self.gene_list]
        self.gene_dict = {c.innovation: c for c in self.gene_list}
        self.max_innovation = max(self.innovation_indices)
        self.rules = rules
        self.species = None

        self.__fitness = None
        self.__array = None
        self.fitness_up_to_date = False
        self.array_up_to_date = False

    @property
    def fitness(self):
        assert self.fitness_up_to_date
        return self.__fitness

    @property
    def adjusted_fitness(self):
        return self.fitness / self.species.size

    @property
    def array(self):
        assert self.array_up_to_date
        return self.__array

    def get_surface(self, scale=1):
        im = pygame.Surface((self.rules.target_size[0] * scale, self.rules.target_size[1] * scale), pygame.SRCALPHA)
        for figure in sorted(self.gene_dict.keys(), key=lambda i: i.z):
            im.blit(figure.get_surface(scale), (0, 0))

        return im

    def update_array(self):
        pgim = self.get_surface()

        self.__array = pygame.surfarray.array3d(pgim).astype("int16")
        self.array_up_to_date = True

    def update_fitness(self):
        self.__fitness = np.linalg.norm(self.rules.target_array.flatten() - self.array.flatten()) * -1
        self.fitness_up_to_date = True

    def gentle_mutate(self):
        for figure in self.gene_list:
            figure.gaussian_change()

        self.fitness_up_to_date = False
        self.array_up_to_date = False

    def compatibility_distance(self, other):
        disjoint = 0
        excess = 0
        compatible_gene_difference = 0

        for g in other.gene_dict.keys():
            matching = self.gene_dict.get(g.innovation)
            if matching:
                compatible_gene_difference += g.distance(matching)
            else:
                if g.innovation < self.max_innovation:
                    disjoint += 1
                else:
                    excess += 1

        for g in self.gene_dict.keys():
            matching = other.gene_dict.get(g.innovation)
            if matching:
                pass  # already processed
            else:
                if g.innovation < other.max_innovation:
                    disjoint += 1
                else:
                    excess += 1

        return disjoint * self.rules.distance_weights['disjoint'] +\
               excess * self.rules.distance_weights['excess'] + \
               compatible_gene_difference * self.rules.distance_weights['comp_genes']

    def new_circle(self):
        new = Circle.random_circle(self.rules)
        self.gene_list.append(new)
        self.gene_dict[new.innovation] = new




