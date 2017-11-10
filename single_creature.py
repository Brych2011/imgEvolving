import pygame
from PIL import Image
import random
import json
from copy import deepcopy
import time

"""
IMAGE = Image.open('mona_lisa_small.jpg')
IMAGE.thumbnail((90,60))
IMAGE.save('mona_lisa_even_smaller.jpg', 'JPEG')
TARGET = np.array(IMAGE)
"""
pg_im = pygame.image.load('mona_lisa_even_smaller.jpg')   # #load target image
TARGET = pygame.surfarray.array3d(pg_im).astype('int16')  # #convert to int16 array
SIZE = pg_im.get_size()
SHAPE = TARGET.shape
print(SIZE)
print(TARGET.shape)
CIRCLES = 45
DEFAULT = object()

LEGAL_BORDER = 30  # #how far out of image can circle's middle be


class Color(list):
    """used for representation of color"""

    def __init__(self, *args):
        if len(args) == 4:
            for i in args:
                if i < 0:
                    i = 0
                elif i > 255:
                    i = 255
            list.__init__(self, args)

        else:
            list.__init__(self, [random.randint(0, 255) for i in range(4)])

    def __setitem__(self, key, value):
        if value > 255:
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
        self.color = Color(color)

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, value):
        if value < 0 - LEGAL_BORDER:
            self.__x = 0 - LEGAL_BORDER
        elif value > Genome.target_shape[1] + LEGAL_BORDER:
            self.__x = Genome.target_shape[1] + LEGAL_BORDER
        else:
            self.__x = value

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, value):
        if value < 0 - LEGAL_BORDER:
            self.__y = 0 - LEGAL_BORDER
        elif value > Genome.target_shape[0] + LEGAL_BORDER:
            self.__y = Genome.target_shape[0] + LEGAL_BORDER
        else:
            self.__y = value

    @property
    def radius(self):
        return self.__radius

    @radius.setter
    def radius(self, value):
        if value < 1:
            self.__radius = 1
        else:
            self.__radius = value
        

class Genome(object):
    """genome with properties of given amount of circles"""

    pg_im = pygame.image.load('mona_lisa_even_smaller.jpg')  # #load target image
    target = pygame.surfarray.array3d(pg_im).astype('int16')  # #convert to int16 array
    target_shape = target.shape
    max_radius = 50

    def __init__(self, circles, genome_list=DEFAULT):
        self.genome = []
        self.circles = circles
        self.__array = []
        self.__fitness = 0
        self.update_array()

        self.size = Genome.target.shape
        if genome_list == DEFAULT:
            for i in range(circles):
                new_circle = Circle(random.randint(0 - LEGAL_BORDER, Genome.target_shape[1] + LEGAL_BORDER),  # #x
                                    random.randint(0 - LEGAL_BORDER, Genome.target_shape[0] + LEGAL_BORDER),  # #y
                                    Color(), random.randint(1, Genome.max_radius))
                self.genome.append(new_circle)
        else:
            for circle in genome_list:
                circle[0] = Color(circle[0])
            self.genome = genome_list

        self.update_fitness()
        self.update_array()

    @property
    def array(self):
        return self.__array
    
    @property
    def fitness(self):
        return self.__fitness

    def update_array(self):
        pgim = pygame.Surface(SIZE, pygame.SRCALPHA)
        for circle in self.genome:
            new_im = pygame.Surface((circle.radius * 2, circle.radius * 2),
                                    pygame.SRCALPHA)  # create a surface of size of the circle
            pygame.draw.circle(new_im, circle.color,
                               (circle.radius, circle.radius),
                               circle.radius)  # #draw circle in the middle of its Surface
            pgim.blit(new_im, [circle.x - circle.radius, circle.y - circle.radius)  # #blit onto main surface
        self.__array = pygame.surfarray.array3d(pgim).astype('int16')
        
    def update_fitness(self):
        self.__fitness = (sum(abs(TARGET - self.array).flat) ** 2) * -1

    def mutate(self):
        repeat = True
        while repeat:
            choice = random.randint(1, 5)  # #choose a random mutation
            if choice == 1:  # #redefine color
                chosen = random.randrange(0, self.circles)
                for i in range(3):
                    self.genome[chosen].color[i] = random.randint(0, 255)
            elif choice == 2:  # #redefine position
                self.genome[random.randrange(0, self.circles)][1] = [random.randint(0, SIZE[0] - 1),
                                                                     random.randint(0, SIZE[1] - 1)]
            elif choice == 3:  # #redefine radius
                self.genome[random.randrange(0, self.circles)][2] = random.randint(1, 30)
            elif choice == 4:  # #swap two circles on z axis
                index1 = random.randrange(0, self.circles)
                index2 = random.randrange(0, self.circles)
                while index1 == index2:
                    index2 = random.randrange(0, self.circles)  # #generate two random indices
                temp = self.genome[index1]
                self.genome[index1] = self.genome[index2]  # #swap them
                self.genome[index2] = temp
            elif choice == 5:  # #redefine opacity
                self.genome[random.randrange(0, self.circles)][0][3] = random.randint(0, 255)
            repeat = not random.randint(0, 9)  # #have 10% chance for another mutation
        self.update_array()
        self.update_fitness()

    def draw(self, scale=1, save=False):
        pgim = pygame.Surface((SIZE[0] * scale, SIZE[1] * scale), pygame.SRCALPHA)

        for circle in self.genome:  # #same as in genome_to_array
            new_im = pygame.Surface((circle[2] * 2 * scale, circle[2] * 2 * scale), pygame.SRCALPHA)

            pygame.draw.circle(new_im, circle[0].color_list, (circle[2] * scale, circle[2] * scale),
                               circle[2] * scale)  # #draw circle in the middle of its Surface
            pgim.blit(new_im, [(circle[1][i] - circle[2]) * scale for i in range(2)])

        pg_stringim = pygame.image.tostring(pgim, 'RGBA')
        im = Image.frombytes('RGBA', (SIZE[0] * scale, SIZE[1] * scale), pg_stringim)

        if save:

            im.save(str(int(time.time()))+".bmp", 'BMP')
        im.show()

    def get_list_representation(self):
        result = self.genome.copy()
        for i in range(self.circles):
            result[i][0] = result[i][0].color_list
        return result

    @staticmethod
    def change_target(image_object):
        """change the target of all creatures. Requires pygame surface as an argument"""
        Genome.target = pygame.surfarray.array3d(image_object).astype('int16')  # #convert to int16 array
        Genome.target_shape = Genome.target.shape
"""
def genome_to_array(genome):
    pgim = pygame.Surface(SIZE, pygame.SRCALPHA)
    for circle in genome:
        new_im = pygame.Surface((circle[2] * 2, circle[2] * 2), pygame.SRCALPHA)  #create a surface of size of the circle
        color = circle[0].copy()
        color.append(circle[3])  # #add opacity to the color argument
        pygame.draw.circle(new_im, color, (circle[2], circle[2]), circle[2])  # #draw circle in the middle
        pgim.blit(new_im, [circle[1][i] - circle[2] for i in range(2)])  # #blit onto main surface
    return pygame.surfarray.array3d(pgim).astype('int16')  # #return as int16 array


def random_genome():
    creates a random genome
    result = []
    for i in range(CIRCLES):
        pos = [random.randint(0, SIZE[0]-1), random.randint(0, SIZE[1]-1)]
        color = [random.randint(0, 255) for i in range(3)]
        radius = random.randint(1, 30)
        opacity = random.randint(0,255)
        result.append([color, pos, radius, opacity])
    return result

random_genome()
def check_fitness(genome):
    returns genome's fitness counted by difference in rgb values
    genome_array = genome_to_array(genome)
    fitness = (sum(abs(TARGET - genome_array).flat) ** 2) * -1
    # #squared for rewarding better creatures, difference is a negative trait, hence * -1
    return fitness


def draw_creature(genome, scale=1, save=False):
    pgim = pygame.Surface((SIZE[0] * scale, SIZE[1] * scale), pygame.SRCALPHA)
    for circle in genome:  # #same as in genome_to_array
        new_im = pygame.Surface((circle[2] * 2 * scale, circle[2] * 2 * scale), pygame.SRCALPHA)
        color = circle[0].copy()
        color.append(circle[3])
        pygame.draw.circle(new_im, color, (circle[2] * scale, circle[2] * scale), circle[2] * scale)
        pgim.blit(new_im, [(circle[1][i] - circle[2]) * scale for i in range(2)])
    pg_stringim = pygame.image.tostring(pgim, 'RGBA')
    im = Image.frombytes('RGBA', (SIZE[0] * scale, SIZE[1] * scale), pg_stringim)

    if save:

        im.save(str(int(time.time()))+".bmp", 'BMP')
    im.show()


def mutate(start_genome):
    genome = deepcopy(start_genome)  # #deepcopy is necessary (apparently)
    repeat = True
    while repeat:
        choice = random.randint(1, 5)  # #choose a random mutation
        if choice == 1:  # #redefine color
            genome[random.randint(0, CIRCLES - 1)][0] = [random.randint(0, 255) for i in range(3)]
        elif choice == 2:  # #redefine position
            genome[random.randint(0, CIRCLES - 1)][1] = [random.randint(0, SIZE[0] - 1),
                                                         random.randint(0, SIZE[1] - 1)]
        elif choice == 3:  # #redefine radius
            genome[random.randint(0, CIRCLES - 1)][2] = random.randint(1,30)
        elif choice == 4:  # #swap two circles on z axis
            index1 = random.randint(0, CIRCLES-1)
            index2 = random.randint(0, CIRCLES-1)
            while index1 == index2:
                index2 = random.randint(0, CIRCLES - 1)  # #generate two random indices
            temp = genome[index1]
            genome[index1] = genome[index2]  # #swap them
            genome[index2] = temp
        elif choice == 5:  # #redefine opacity
            genome[random.randint(0, CIRCLES - 1)][3] = random.randint(0,255)
        repeat = not random.randint(0, 9)  # #have 10% chance for another mutation
    return genome
"""

if __name__ == '__main__':
    try:
        improvements = 0
        while True:
            ans = input('n - new file \nc - continue latest creature\n')
            if ans.lower() == 'n':
                creature = Genome(50)
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
            if creature.fitness < kid.fitness:  # #replace genome if mutation if beneficial
                creature = kid
                improvements += 1
            gen += 1
    except KeyboardInterrupt:
        creature.draw(scale=7, save=True)

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
    """
    show_fitness_errors(creature)
    w,h,d = TARGET.shape
    print(tuple(np.average(TARGET.reshape(w*h, d), axis=0)))
    test = [[[85,72,53], [30, 20], 200, 255]]
    test2 = [[[255,255,255], [45,30], 90, 255]]
    print('creature: {}'.format(check_fitness(creature)))
    print('average:  {}'.format(check_fitness(test)))
    print('aberage2: {}'.format(check_fitness3(test)))
    print('white:    {}'.format(check_fitness(test2)))
    draw_creature(test)
    draw_creature(creature)
    """



