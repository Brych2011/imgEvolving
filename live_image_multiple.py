import pygame
from obrazki import Population, Genome, Circle, Color
import multiprocessing
import random
from PIL import Image
from io import BytesIO
import requests
import numpy as np
import clipboard

# Drogi czytelniku na tyle sprytny i ciekawy, by otworzyć kod, proszę przestań, póki jeszcze jest czas!
# Program poniżej jest napisany wręcz okropnie. Jest niezoptymalizowany i sklecony na szybko na te dni otwarte.
# Nie uświadczysz tu prawie żadnych komentarzy, prawie żadnych stringów dokumentacyjnych (te, które są, są wynikiem kopiowania starszego kodu)
# Mam jednak nadzieję, że jego jakość nie odwiedzie Cię od naszej szkoły. Ona jest naprawdę OK
# Pozdrawiam serdecznie,
# wolący zachować anonimowość autor


SCREEN_SIZE = (800, 600)


def pretty_coordinates(size_tuple, screen_size, scale):
    """Na tę funkcję proszę nie patrzeć. Pisałem ją w gorączce. Serio. Jest okropna"""
    margin = 50
    x_section = screen_size[0] // 4
    # Here be dragons
    return (((x_section - (size_tuple[0] // 2), size_tuple[1] * scale // 2 + margin - size_tuple[1] // 2),
             ((x_section * 3) - (size_tuple[0] // 2), size_tuple[1] * scale // 2 + margin - size_tuple[1] //2)),
            ((x_section - size_tuple[0] * scale // 2, margin), (x_section * 3 - size_tuple[0] * scale // 2, margin)))


def run_pop(pop_size, circles, target, queue, checkpoint=750, threshold=0.035, decrease=0.95):
    Genome.set_target(target)
    print(Genome.target_shape)
    pop = Population(size=pop_size, circles=circles, target=target)
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
                    i.genome.insert(random.randint(0, i.circles-1), new_circle)
                    i.circles += 1
                    i.update_array()
                    i.update_fitness()
                threshold *= decrease
            prev_max = pop.best_creature.fitness

        pop.next_gen()


url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/1280px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg'
response = requests.get(url)
target_img = Image.open(BytesIO(response.content))
target_img.thumbnail((50, 50))
Genome.set_target(target_img)
print(target_img.size)
print(800//4)

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
pygame.display.set_caption('Ewolucja obrazów')
myfont = pygame.font.SysFont('Helvetica', 30)
# initialize clock. used later in the loop.
clock = pygame.time.Clock()

# Loop until the user clicks close button
print(pretty_coordinates(target_img.size, SCREEN_SIZE, 5)[0][0])

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
    gen_text = myfont.render('Pokolenie: ' + str(gen), True, (0, 0, 0))
    circle_text = myfont.render('Liczba kół: ' + str(good_creature.circles), True, (0, 0, 0))
    space_instruction = myfont.render('Przytrzymaj spację, aby powiększyć', True, (0, 0, 0))
    # clear the screen before drawing
    # print(q.qsize())
    coordinates = pretty_coordinates(target_img.size, SCREEN_SIZE, 5)
    screen.fill((255, 255, 255))

    screen.blit(good_creature.get_surface(5 if enhance else 1), coordinates[enhance][0])
    screen.blit(gen_text, (300, 300))
    screen.blit(circle_text, (300, 350))
    screen.blit(space_instruction, (50, 450))
    screen.blit(bad_creature.get_surface(5 if enhance else 1), coordinates[enhance][1])
    pygame.display.update()

pygame.quit()
evolving_process.terminate()