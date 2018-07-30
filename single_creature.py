import pygame
from PIL import Image
import numpy as np
import random
import json
from copy import deepcopy
import time
import os


DEFAULT = object()


class Shape(object):
    """Empty object for defining genome sub-shapes"""

    maxInnovation = 0

    def __init__(self, sort_of_center):
        self.margin = 15
        self.innovation = Shape.maxInnovation
        Shape.maxInnovation += 1
        pass

    def random_change(self):
        pass

    def get_surface(self, scale=1):
        pass

    def get_center(self):
        pass


class Polygon(Shape):
    max_sides = 5
    min_sides = 3

    def __init__(self, center=None, coords=None, color=None):
        super().__init__(center)

        if coords is not None and \
                center is None and \
                Polygon.min_sides <= len(coords) <= Polygon.max_sides:
            self.coords = coords
        elif center:
            self.coords = [(random.randint(center[0] - self.margin, center[0] + self.margin),
                            random.randint(center[1] - self.margin, center[1] + self.margin))
                           for i in range(random.randint(Polygon.min_sides, Polygon.max_sides))]
        else:
            self.coords = [(random.randint(-Genome.legal_border, Genome.target_shape[0] + Genome.legal_border),
                            random.randint(-Genome.legal_border, Genome.target_shape[1] + Genome.legal_border))
                           for i in range(random.randint(Polygon.min_sides, Polygon.max_sides))]

        if color is not None:
            self.color = color
        else:
            self.color = Color()

    def random_change(self):
        if len(self.coords) == Polygon.min_sides:
            choice = random.randint(0,1) * 2  # only 0 and 2 are viable options
        elif len(self.coords) == Polygon.max_sides:
            choice = random.randint(0,1)
        else:
            choice = random.randint(0,2)

        if choice == 0:  # shift one points coordinates
            changing = random.randrange(0, len(self.coords))
            self.coords[changing] = (random.randint(-Genome.legal_border, Genome.target_shape[0] + Genome.legal_border),
                                     random.randint(-Genome.legal_border, Genome.target_shape[1] + Genome.legal_border))

        if choice == 1:  # remove a point
            del self.coords[random.randrange(0, len(self.coords))]

        if choice == 2:
            self.coords.insert(random.randint(0, len(self.coords)),
                               (random.randint(-Genome.legal_border, Genome.target_shape[0] + Genome.legal_border),
                                random.randint(-Genome.legal_border, Genome.target_shape[1] + Genome.legal_border)))

    def get_surface(self, scale=1):
        im = pygame.Surface((Genome.im_size[0] * scale, Genome.im_size[1] * scale), pygame.SRCALPHA)
        pygame.draw.polygon(im, self.color, [(x * scale, y * scale) for x, y in self.coords])
        return im

    def get_center(self):
        return sum([i[0] for i in self.coords]) // len(self.coords), sum([i[1] for i in self.coords]) // len(self.coords)


class Color(list):
    """used for representation of color"""

    def __init__(self, *args):
        if len(args) == 4:  # #round all illegal arguments
            args = list(args)
            for i in range(4):
                if args[i] < 0:
                    args[i] = 0
                elif args[i] > 255:
                    args[i] = 255
            list.__init__(self, args)

        else:  # #init with random values if not specified
            list.__init__(self, [random.randint(0, 255) for i in range(4)])

    def __setitem__(self, key, value):
        if value > 255:  # #round illegal values
            list.__setitem__(self, key, 255)
        elif value < 0:
            list.__setitem__(self, key, 0)
        else:
            list.__setitem__(self, key, value)


class Circle(Shape):
    """representation of one circle in genome. Takes care of legality of dimensions"""

    def __init__(self, center=None, coords=None, radius=None, color=None):
        super().__init__(center)

        if coords is not None and center is None:
            self.x, self.y = coords
        elif center:
            self.x, self.y = (random.randint(center[0] - self.margin, center[0] + self.margin),
                              random.randint(center[1] - self.margin, center[1] + self.margin))
        else:
            self.x = random.randrange(0 - Genome.legal_border, Genome.target_shape[1] + Genome.legal_border)

            self.y = random.randrange(0 - Genome.legal_border, Genome.target_shape[0] + Genome.legal_border)
        self.__radius = radius if radius else random.randint(1, Genome.max_radius)
        self.color = Color(*color) if color else Color()  # #init Color object

    def random_change(self):
        choice = random.randint(1, 4)  # #choose a random mutation
        if choice == 1:  # #redefine color
            for i in range(3):
                self.color[i] = random.randint(0, 255)
        elif choice == 2:  # #redefine position
            self.x = random.randrange(0 - Genome.legal_border, Genome.target_shape[1] + Genome.legal_border)

            self.y = random.randrange(0 - Genome.legal_border, Genome.target_shape[0] + Genome.legal_border)
        elif choice == 3:  # #redefine radius
            self.radius = random.randint(1, Genome.max_radius)

        elif choice == 4:  # #redefine opacity
            self.color[3] = random.randint(0, 255)

    def get_surface(self, scale=1):
        im = pygame.Surface((Genome.im_size[0] * scale, Genome.im_size[1] * scale), pygame.SRCALPHA)
        pygame.draw.circle(im, self.color, (self.x * scale, self.y * scale), self.radius * scale)
        return im

    def get_center(self):
        return self.x, self.y

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, value):  # #force x to be within certain range
        if value < 0 - Genome.legal_border:
            self.__x = 0 - Genome.legal_border
        elif value > Genome.target_shape[1] + Genome.legal_border:
            self.__x = Genome.target_shape[1] + Genome.legal_border
        else:
            self.__x = value

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, value):  # #force y to be within certain range
        if value < 0 - Genome.legal_border:
            self.__y = 0 - Genome.legal_border
        elif value > Genome.target_shape[0] + Genome.legal_border:
            self.__y = Genome.target_shape[0] + Genome.legal_border
        else:
            self.__y = value

    @property
    def radius(self):
        return self.__radius

    @radius.setter
    def radius(self, value):  # #round illegal values
        if value < 1:
            self.__radius = 1
        elif value > Genome.max_radius:
            self.__radius = Genome.max_radius
        else:
            self.__radius = value

    def __eq__(self, other):
        return isinstance(other, Circle) and \
               self.x == other.x and \
               self.y == other.y and \
               self.radius == other.radius and \
               self.color == other.color
        

class Genome(object):
    """genome with properties of given amount of circles"""

    # init default settings, can be changed via change_target() method
    pg_im = pygame.image.load('mona_lisa_even_smaller.jpg')  # #load target image
    im_size = pg_im.get_size()
    target = pygame.surfarray.array3d(pg_im).astype('int16')  # #convert to int16 array
    target_shape = target.shape
    max_radius = 50

    legal_border = 30  # #how far out of image can circle's middle be

    def __init__(self, figure_count, genome_list=DEFAULT):
        self.genome = []
        self.figures = figure_count
        self.__array = []
        self.__fitness = 0
        self.update_array()

        self.size = Genome.target.shape
        if genome_list == DEFAULT:  # if source list of a genome was not specified
            self.genome = [Circle() if random.randint(0, 1) else Polygon() for i in range(figure_count)]
        else:
            for i in genome_list:  # #genome list has syntax: [[[r,g,b,a],[x,y],radius], ....]
                self.genome.append(Circle(i[1][0],  # #read x
                                          i[1][1],  # #read y
                                          i[2],  # #read radius
                                          Color(*i[0])))  # # read color

        self.update_fitness()
        self.update_array()

    @property
    def array(self):
        return self.__array
    
    @property
    def fitness(self):
        return self.__fitness

    def update_array(self):
        """Method updating the array representation of an image. Should be called after every change,
        along with update_fitness() method"""
        pgim = self.get_surface(1)
        self.__array = pygame.surfarray.array3d(pgim).astype('int16')

    def update_fitness(self):
        """Method calculating genome's fitness. Should be called after every change, after update_array()"""

        self.__fitness = np.linalg.norm(Genome.target.flatten() - self.array.flatten()) * -1
        """Difference is calculated as array of absolute values of results of subtracktions. It is then flatted and
           summed. Result is squared for faster evolution and multiplied by -1, as difference from target is a
           negative trait"""

    def mutate(self):
        repeat = True
        while repeat:
            chosen_figure = random.randrange(0, self.figures)
            choice = random.randint(0, 3)
            if choice == 0:  # swap two figures
                index1 = random.randrange(0, self.figures)
                index2 = random.randrange(0, self.figures)
                temp = self.genome[index1]
                self.genome[index1] = self.genome[index2]
                self.genome[index2] = temp

            elif choice == 1:  # change figure
                center = self.genome[chosen_figure].get_center()
                self.genome[chosen_figure] = Circle(center=center) if isinstance(self.genome[chosen_figure], Polygon) else Polygon(center=center)

            else:
                self.genome[chosen_figure].random_change()
            repeat = not random.randint(0, 3)  # #have 25% chance for another mutation

    def draw(self, scale=1, show=False, save=False, path='./', name = DEFAULT):
        """Method used for rendering genome's image and showing it or saving"""
        pgim = self.get_surface(scale)

        pg_stringim = pygame.image.tostring(pgim, 'RGB')  # transform into PIL.Image for .show() method
        im = Image.frombytes('RGB', (Genome.im_size[0] * scale, Genome.im_size[1] * scale), pg_stringim)

        if save:
            if name == DEFAULT:
                name = str(int(time.time())) + ".bmp"
            final_name = os.path.join(path, name)
            im.save(final_name, 'BMP')
        if show:
            im.show()

    def get_surface(self, scale=1):
        pgim = pygame.Surface((Genome.im_size[0] * scale, Genome.im_size[1] * scale), pygame.SRCALPHA)

        for figure in self.genome:
            pgim.blit(figure.get_surface(scale), (0, 0))

        return pgim

    def get_list_representation(self):
        """Used to generate list representation ready to save with json"""
        result = []
        for i in range(self.figures):
            new_circle = []
            new_circle.append(self.genome[i].color)
            new_circle.append([self.genome[i].x, self.genome[i].y])
            new_circle.append(self.genome[i].radius)  # Same list syntax as in __init__()
            result.append(new_circle)
        return result

    @staticmethod
    def set_target(image_object):
        """change the target of all creatures. Requires pygame surface as an argument"""
        if isinstance(image_object, pygame.Surface):
            Genome.im_size = image_object.get_size()
            Genome.target = pygame.surfarray.array3d(image_object).astype('int16')  # #convert to int16 array
            Genome.target_shape = Genome.target.shape
            Genome.target_image = image_object
        elif isinstance(image_object, Image.Image):
            mode = image_object.mode
            size = image_object.size
            data = image_object.tobytes()
            image_object = pygame.image.fromstring(data, size, mode)
            Genome.target_image = image_object
            Genome.im_size = image_object.get_size()
            Genome.target = pygame.surfarray.array3d(image_object).astype('int16')  # #convert to int16 array
            Genome.target_shape = Genome.target.shape
        else:
            raise IOError('Image type can only be pygame.Surface of Image.Image')


if __name__ == '__main__':
    try:
        improvements = 0
        new_im = pygame.image.load('small_version.jpg')
        Genome.set_target(new_im)
        while True:
            ans = input('n - new file \nc - continue latest creature\n')
            if ans.lower() == 'n':
                creature = Genome(70)
                starting_fitness = creature.fitness
                gen = 0
                break
            if ans.lower() == 'c':
                latest_txt = open('latest.txt', 'r')
                name = latest_txt.readline()
                saved = open(name, 'r')
                gen, genome = json.load(saved)
                creature = Genome(len(genome), genome)
                starting_fitness = creature.fitness
                latest_txt.close()
                saved.close()
                break

        while True:
            if gen % 500 == 0:
                print(gen, creature.fitness)  # #check progress every 500 gens
            kid = deepcopy(creature)  # #create a mutated kid
            kid.mutate()
            kid.update_array()
            kid.update_fitness()
            if creature.fitness < kid.fitness:  # #replace genome if mutation if beneficial
                creature = kid
                improvements += 1
            gen += 1

    except KeyboardInterrupt:
        creature.draw(scale=15, save=True)

        name = str('saved_instance' + str(int(time.time())))
        print(name)
        latest_file = open('latest.txt', 'w')
        latest_file.write(name)
        latest_file.close()
        file = open('saved_instance' + str(int(time.time())), 'w')
        json.dump([gen, creature.get_list_representation()], file)
        file.close()

        print('improved {} times'.format(improvements))
        print('starting {}'.format(starting_fitness))
        print('end      {}'.format(creature.fitness))

