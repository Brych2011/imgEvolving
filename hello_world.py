import random

TARGET = 'Litwo, Ojczyzno moja! Ty jestes jak zdrowie! Ile cie trzeba cenic, ten tylko sie dowie, kto cie stracil. Dzis pieknosc twa w calej ozdobie widze i opisuje, bo testknie po tobie.'
GEN_LEN = len(TARGET)
SINGS = 'qwertyuiopsadfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBN M!,-.;'

def starting_population(n):
    population = []
    for i in range(n):
        genome = ''
        for j in range(len(TARGET)):
            genome += random.choice(SINGS)
        population.append(genome)
    return population


def breed(s1, s2):
    genome1 = s1[:GEN_LEN//2] + s2[GEN_LEN//2:]
    genome2 = s2[:GEN_LEN//2] + s1[GEN_LEN//2:]

    if random.randint(0,10) == 0:
        mod_gen = list(genome1)
        mod_gen[random.randint(0, GEN_LEN-1)] = random.choice(SINGS)
        genome1 = list_to_string(mod_gen)

    if random.randint(0,10) == 0:
        mod_gen = list(genome2)
        mod_gen[random.randint(0, GEN_LEN-1)] = random.choice(SINGS)
        genome2 = list_to_string(mod_gen)

    return genome1, genome2


def check_fitness(genome):
    result = 0
    for i in range(GEN_LEN):
        if genome[i] == TARGET[i]:
            result += 1
    return result


def sort_population(pop):
    temp = [(i, check_fitness(i)) for i in pop]
    return [i[0] for i in sorted(temp, key= lambda temp:temp[1] * -1)]

def next_gen(sorted_pop):
    new_pop = []
    breedable = sorted_pop[:len(sorted_pop)//2]
    new_pop.extend(breedable)
    for i in range(0,len(breedable), 2):
        new_pop.extend(breed(breedable[i], breedable[i+1]))
    if len(new_pop) != len(sorted_pop):
        x = 42/0
    return new_pop

def list_to_string(l):
    result = ''
    for i in l:
        result += i
    return result


pop = starting_population(500)
for i in range(10000):
    sorted_pop = sort_population(pop)
    print(sorted_pop[0])
    if pop[0] == TARGET:
        print(i)
        break
    pop = next_gen(sorted_pop)




