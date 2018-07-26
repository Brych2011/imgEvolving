from random import randrange, randint

import pygame
from PIL import Image
import numpy as np


class SimulationRules(object):
    """data class to pass to everything. Mostly avoids nasty globals"""

    def __init__(self, target_img, target_array, target_size, max_circle_radius, max_margin, propability_scales,
                 distance_weights, distance_threshold, children_per_gen):
        self.target_img = target_img
        self.target_array = target_array
        self.target_size = target_size
        self.max_circle_radius = max_circle_radius
        self.max_margin = max_margin
        self.propability_scales = propability_scales
        self.max_innovation = 0
        self.distance_weights = distance_weights
        self.distance_threshold = distance_threshold
        self.children_per_gen = children_per_gen


class Gene(object):

    def __init__(self, rules: SimulationRules):
        self.innovation = rules.max_innovation
        self.rules = rules
        self.rules.max_innovation += 1


class Circle(Gene):

    def __init__(self, x, y, r, z, color, rules: SimulationRules):
        super().__init__(rules)

        self.__x = None
        self.__y = None
        self.__r = None

        self.x = x
        self.y = y
        self.r = r
        self.z = z
        self.color = color

        self.rules = rules

    def get_surface(self, scale=1):
        im = pygame.Surface((self.rules.target_size[0] * scale, self.rules.target_size[1] * scale), pygame.SRCALPHA)
        pygame.draw.circle(im, self.color, (self.x * scale, self.y * scale), self.r * scale)
        return im

    def gaussian_change(self):
        self.x += np.random.normal(scale=self.rules.propability_scales['x'])
        self.y += np.random.normal(scale=self.rules.propability_scales['y'])
        self.r += np.random.normal(scale=self.rules.propability_scales['r'])
        self.z += np.random.normal(scale=self.rules.propability_scales['z'])
        self.color = self.color + np.random.normal(scale=self.rules.propability_scales['color'])

    def distance(self, other):
        x_dif = (self.x - other.x) * self.rules.distance_weights['x']
        y_dif = (self.y - other.y) * self.rules.distance_weights['y']
        r_dif = (self.r - other.r) * self.rules.distance_weights['r']
        z_dif = (self.z - other.z) * self.rules.distance_weights['z']
        color_dif = np.linalg.norm(self.color - other.color) * self.rules.distance_weights['color']

        return x_dif + y_dif + r_dif + z_dif + color_dif

    @property
    def pygame_color(self):
        return pygame.Color(*list(map(int, self.color + 0.5)))

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @property
    def r(self):
        return self.__r

    @x.setter
    def x(self, value):
        if value < 0 - self.rules.max_margin:
            self.__x = 0 - self.rules.max_margin
        elif value > self.rules.target_size[0] + self.rules.max_margin:
            self.__x = self.rules.target_size[0] + self.rules.max_margin
        else:
            self.__x = value

    @y.setter
    def y(self, value):
        if value < 0 - self.rules.max_margin:
            self.__y = 0 - self.rules.max_margin
        elif value > self.rules.target_size[1] + self.rules.max_margin:
            self.__y = self.rules.target_size[1] + self.rules.max_margin
        else:
            self.__y = value

    @r.setter
    def r(self, value):
        if value < 1:
            self.__r = value
        elif value > self.rules.max_circle_radius:
            self.__r = self.rules.max_circle_radius
        else:
            self.__r = value

    @classmethod
    def random_circle(cls, rules: SimulationRules):
        return cls(x=randrange(0 - rules.max_margin, rules.target_size[0] + rules.max_margin),
                   y=randrange(0 - rules.max_margin, rules.target_size[1] + rules.max_margin),
                   r=randint(1, rules.max_circle_radius),
                   z=np.random.normal(scale=rules.propability_scales['z'] * 10),
                   color=pygame.Color([randrange(256) for i in range(4)]),
                   rules=rules)
