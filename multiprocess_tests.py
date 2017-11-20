from single_creature import Genome
from multiprocessing import Pool
import time


def call_mutate(creature):
    creature.mutate()
    creature.update_array()
    creature.update_fitness()

if __name__ == '__main__':
    genome_list = [Genome(5) for i in range(20000)]
    t1 = time.time()
    p = Pool(70)
    p.map(call_mutate, genome_list)
    time_multi = time.time() - t1
    t2 = time.time()
    for creature in genome_list:
        creature.mutate()
        creature.update_array()
        creature.update_fitness()
    time_single = time.time() - t2

    print(time_multi, time_single)




