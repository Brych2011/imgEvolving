import pygame
from obrazki import Population, Genome, Circle, Color
import multiprocessing
import random
from PIL import Image
from io import BytesIO
import requests
from copy import deepcopy

SCREEN_SIZE = (800, 600)


def run_pop(pop_size, circles, target, queue):
    Genome.set_target(target)
    pop = Population(size=pop_size, circles=circles)
    while True:
        pop.sort()
        queue.put((pop.creature_list[0], pop.creature_list[-1], pop.generation))
        pop.next_gen()

url ='https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg/161px-Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg'
response = requests.get(url)
target_img = Image.open(BytesIO(response.content))
target_img.thumbnail((50, 50))
"""
q = multiprocessing.Queue()
evolving_process = multiprocessing.Process(target=run_pop, args=(4, 70, target_img, q))
evolving_process.start()
while q.empty():
    pass
"""
Genome.set_target(target_img)
creature = Genome(8)
gen = 0
improvements = 0
fitness_checkpoint = creature.fitness
threshold = 0.05

# initialize game engine
pygame.init()
pygame.font.init()
# set screen width/height and caption
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption('My Game')
myfont = pygame.font.SysFont('Helvetica', 30)
# initialize clock. used later in the loop.
clock = pygame.time.Clock()

# Loop until the user clicks close button
done = False
while not done:
    # write event handlers here
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # write game logic here
    kid = deepcopy(creature)
    kid.mutate()
    kid.update_array()
    kid.update_fitness()
    if kid.fitness > creature.fitness:
        creature = kid
        improvements += 1

    if gen % 1500 == 0:
        if creature.fitness / fitness_checkpoint - 1 < threshold:
            new_circle = Circle(random.randint(0 - Genome.legal_border, Genome.target_shape[1] + Genome.legal_border),
                                # #x
                                random.randint(0 - Genome.legal_border, Genome.target_shape[0] + Genome.legal_border),
                                # #y
                                random.randint(1, Genome.max_radius), Color())
            creature.genome.insert(random.randint(0, creature.circles), new_circle)
            creature.circles += 1
            threshold *= 0.8
            print('new circle added')
        fitness_checkpoint = creature.fitness

    gen += 1
    gen_text = myfont.render('generacja: ' + str(gen), True, (0, 0, 0))
    improvement_text = myfont.render('poprawy' + str(improvements), True, (0,0,0))
    # clear the screen before drawing
    screen.fill((255, 255, 255))
    screen.blit(creature.get_surface(5), (0, 0))
    screen.blit(gen_text, (300, 300))
    screen.blit(improvement_text, (300, 350))
    screen.blit(kid.get_surface(5), (500, 0))
    pygame.display.update()

pygame.quit()
