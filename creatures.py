import numpy as np
import pygame
from shapes import SimulationRules, Circle, debug_random_circle
from PIL import Image
import time
from copy import deepcopy
import os
if __name__ == '__main__':
    from neat_like_sim import Species

DEFAULT = object()


class Genome(object):

    def __init__(self, figures, rules: SimulationRules, determined_genome=None):

        if determined_genome:
            self.gene_list = determined_genome
            self.figure_count = len(self.gene_list)

        else:
            self.figure_count = figures
            self.gene_list = [Circle.random_circle(rules) for i in range(self.figure_count)]

        self.gene_dict = {c.innovation: c for c in self.gene_list}
        self.rules = rules
        self.species = None

        self.__fitness = None
        self.__array = None
        self.fitness_up_to_date = False
        self.array_up_to_date = False

        self.update_array()
        self.update_fitness()

    @property
    def max_innovation(self):
        return max(self.gene_dict.keys()) if self.gene_dict.keys() else 0

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
        for key in sorted(self.gene_dict.keys(), key=lambda i: self.gene_dict[i].z):
            im.blit(self.gene_dict[key].get_surface(scale), (0, 0))

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

        for innovation, g in other.gene_dict.items():
            matching = self.gene_dict.get(innovation)
            if matching:
                compatible_gene_difference += g.distance(matching)
            else:
                if g.innovation < self.max_innovation:
                    disjoint += 1
                else:
                    excess += 1

        for innovation, g in self.gene_dict.items():
            matching = other.gene_dict.get(innovation)
            if matching:
                pass  # already processed
            else:
                if innovation < other.max_innovation:
                    disjoint += 1
                else:
                    excess += 1

        return disjoint * self.rules.distance_weights['disjoint'] +\
               excess * self.rules.distance_weights['excess'] + \
               compatible_gene_difference * self.rules.distance_weights['comp_genes']

    def new_circle(self):
        # new = Circle.random_circle(self.rules)
        new = debug_random_circle(self.rules)
        self.gene_list.append(new)
        self.gene_dict[new.innovation] = new

    def draw(self, scale=1, show=False, save=False, path='./', name = DEFAULT):
        """Method used for rendering genome's image and showing it or saving"""
        pgim = self.get_surface(scale)

        pg_stringim = pygame.image.tostring(pgim, 'RGB')  # transform into PIL.Image for .show() method
        im = Image.frombytes('RGB', (self.rules.target_size[0] * scale, self.rules.target_size[1] * scale), pg_stringim)

        if save:
            if name == DEFAULT:
                name = str(int(time.time())) + ".bmp"
            final_name = os.path.join(path, name)
            im.save(final_name, 'BMP')
        if show:
            im.show()

    def safe_copy(self):
        return Genome(determined_genome=deepcopy(self.gene_list), rules=self.rules, figures="doesnot matter")



