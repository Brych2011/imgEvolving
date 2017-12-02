import pygame
from PIL import Image
import random
import json
from copy import deepcopy
import time
import os


DEFAULT = object()


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


class Circle(object):
    """representation of one circle in genome. Takes care of legality of dimensions"""

    def __init__(self, x, y, radius, color):
        self.__x = x
        self.__y = y
        self.__radius = radius
        self.color = Color(*color)  # #init Color object

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
        return self.x == other.x and \
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

    def __init__(self, circles, genome_list=DEFAULT):
        self.genome = []
        self.circles = circles
        self.__array = []
        self.__fitness = 0
        self.update_array()

        self.size = Genome.target.shape
        if genome_list == DEFAULT:  # if source list of a genome was not specified
            for i in range(circles):  # Generate new one with random circles
                new_circle = Circle(random.randint(0 - Genome.legal_border, Genome.target_shape[1] + Genome.legal_border),  # #x
                                    random.randint(0 - Genome.legal_border, Genome.target_shape[0] + Genome.legal_border),  # #y
                                    random.randint(1, Genome.max_radius), Color())
                self.genome.append(new_circle)
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
        pgim = pygame.Surface(Genome.im_size, pygame.SRCALPHA)
        for circle in self.genome:
            new_im = pygame.Surface((circle.radius * 2, circle.radius * 2),
                                    pygame.SRCALPHA)  # create a surface of size of the circle
            pygame.draw.circle(new_im, circle.color,
                               (circle.radius, circle.radius),
                               circle.radius)  # #draw circle in the middle of its Surface
            pgim.blit(new_im, [circle.x - circle.radius, circle.y - circle.radius])  # #blit onto main surface
        self.__array = pygame.surfarray.array3d(pgim).astype('int16')

    def update_fitness(self):
        """Method calculating genome's fitness. Should be called after every change, after update_array()"""

        self.__fitness = (sum(abs(Genome.target - self.array).flat) ** 2) * -1
        """Difference is calculated as array of absolute values of results of subtracktions. It is then flatted and
           summed. Result is squared for faster evolution and multiplied by -1, as difference from target is a
           negative trait"""

    def mutate(self):
        repeat = True
        while repeat:
            choice = random.randint(1, 5)  # #choose a random mutation
            if choice == 1:  # #redefine color
                chosen = random.randrange(0, self.circles)
                for i in range(3):
                    self.genome[chosen].color[i] = random.randint(0, 255)
            elif choice == 2:  # #redefine position
                self.genome[random.randrange(0, self.circles)].x = random.randrange(0 - Genome.legal_border,
                                                                                    Genome.target_shape[1] + Genome.legal_border)

                self.genome[random.randrange(0, self.circles)].y = random.randrange(0 - Genome.legal_border,
                                                                                    Genome.target_shape[0] + Genome.legal_border)
            elif choice == 3:  # #redefine radius
                self.genome[random.randrange(0, self.circles)].radius = random.randint(1, Genome.max_radius)

            elif choice == 4:  # #swap two circles on z axis
                index1 = random.randrange(0, self.circles)
                index2 = random.randrange(0, self.circles)
                while index1 == index2:
                    index2 = random.randrange(0, self.circles)  # #generate two random indices
                temp = self.genome[index1]
                self.genome[index1] = self.genome[index2]  # #swap them
                self.genome[index2] = temp

            elif choice == 5:  # #redefine opacity
                self.genome[random.randrange(0, self.circles)].color[3] = random.randint(0, 255)
            repeat = not random.randint(0, 3)  # #have 25% chance for another mutation

    def draw(self, scale=1, show=False, save=False, path='./', name = DEFAULT):
        """Method used for rendering genome's image and showing it or saving"""
        pgim = pygame.Surface((Genome.im_size[0] * scale, Genome.im_size[1] * scale), pygame.SRCALPHA)

        for circle in self.genome:
            new_im = pygame.Surface((circle.radius * 2 * scale, circle.radius * 2 * scale),
                                    pygame.SRCALPHA)  # create a surface of size of the circle
            pygame.draw.circle(new_im, circle.color,
                               (circle.radius * scale, circle.radius * scale),
                               circle.radius * scale)  # #draw circle in the middle of its Surface
            pgim.blit(new_im, [(circle.x - circle.radius) * scale,
                               (circle.y - circle.radius) * scale])  # #blit onto main surface

        pg_stringim = pygame.image.tostring(pgim, 'RGB')  # transform into PIL.Image for .show() method
        im = Image.frombytes('RGB', (Genome.im_size[0] * scale, Genome.im_size[1] * scale), pg_stringim)

        if save:
            if name == DEFAULT:
                name = str(int(time.time())) + ".bmp"
            final_name = os.path.join(path, name)
            im.save(final_name, 'BMP')
        if show:
            im.show()

    def get_list_representation(self):
        """Used to generate list representation ready to save with json"""
        result = []
        for i in range(self.circles):
            new_circle = []
            new_circle.append(self.genome[i].color)
            new_circle.append([self.genome[i].x, self.genome[i].y])
            new_circle.append(self.genome[i].radius)  # Same list syntax as in __init__()
            result.append(new_circle)
        return result

    @staticmethod
    def change_target(image_object):
        """change the target of all creatures. Requires pygame surface as an argument"""
        if isinstance(image_object, pygame.Surface):
            Genome.im_size = image_object.get_size()
            Genome.target = pygame.surfarray.array3d(image_object).astype('int16')  # #convert to int16 array
            Genome.target_shape = Genome.target.shape
        elif isinstance(image_object, Image.Image):
            mode = image_object.mode
            size = image_object.size
            data = image_object.tobytes()
            image_object = pygame.image.fromstring(data, size, mode)
            Genome.im_size = image_object.get_size()
            Genome.target = pygame.surfarray.array3d(image_object).astype('int16')  # #convert to int16 array
            Genome.target_shape = Genome.target.shape
        else:
            raise IOError('Image type can only be pygame.Surface of Image.Image')


if __name__ == '__main__':
    try:
        improvements = 0
        new_im = pygame.image.load('small_version.jpg')
        Genome.change_target(new_im)
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

