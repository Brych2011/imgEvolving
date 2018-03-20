import pygame
from obrazki import Population, Genome, Circle, Color
import multiprocessing
import random
from PIL import Image
from io import BytesIO
import requests
from copy import deepcopy

SCREEN_SIZE = (800, 600)


def run_pop(pop_size, circles, target, queue, checkpoint=750, threshold=0.035, decrease=0.95):
    Genome.set_target(target)
    pop = Population(size=pop_size, circles=circles)
    prev_max = pop.best_creature.fitness
    while True:
        pop.sort()
        queue.put((pop.creature_list[0], pop.creature_list[-1], pop.generation))

        if pop.generation % checkpoint == 0:
            if prev_max / pop.best_creature.fitness - 1 < threshold:
                for i in pop.creature_list:
                    new_circle = Circle(
                        random.randint(0 - Genome.legal_border, Genome.target_shape[1] + Genome.legal_border),  # #x
                        random.randint(0 - Genome.legal_border, Genome.target_shape[0] + Genome.legal_border),  # #y
                        random.randint(1, Genome.max_radius), Color())
                    i.genome.insert(random.randint(0, i.circles), new_circle)
                    i.circles += 1
                    i.update_array()
                    i.update_fitness()
                threshold *= decrease
            prev_max = pop.best_creature.fitness

        pop.next_gen()

url ='https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg/161px-Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg'
response = requests.get(url)
target_img = Image.open(BytesIO(response.content))
target_img.thumbnail((50, 50))

q = multiprocessing.Queue()
evolving_process = multiprocessing.Process(target=run_pop, args=(4, 10, target_img, q))
evolving_process.start()
while q.empty():
    pass

enhance = False


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
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                enhance = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                enhance = False

    # write game logic here
    good_creature, bad_creature, gen = q.get()
    gen_text = myfont.render('generacja: ' + str(gen), True, (0, 0, 0))
    circle_text = myfont.render(str(good_creature.circles), True, (0, 0, 0))
    # clear the screen before drawing
    # print(q.qsize())
    screen.fill((255, 255, 255))
    screen.blit(good_creature.get_surface(1 + 4 * enhance), (0, 0))
    screen.blit(gen_text, (300, 300))
    screen.blit(circle_text, (300, 350))
    screen.blit(bad_creature.get_surface(1 + 4 * enhance), (500, 0))
    pygame.display.update()

pygame.quit()
