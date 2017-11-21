from single_creature import Genome
from multiprocessing import Pool
import time


def call_mutate(creature):
    creature.mutate()
    creature.update_array()
    creature.update_fitness()
    return creature


if __name__ == '__main__':
    genome_list = [Genome(100) for i in range(5000)]
    p = Pool(5)
    t1 = time.time()
    genome_list = list(p.map(call_mutate, genome_list))
    time_multi = time.time() - t1
    t2 = time.time()
    for creature in genome_list:
        creature.mutate()
        creature.update_array()
        creature.update_fitness()
    time_single = time.time() - t2
    t3 = time.time()
    genome_list = list(p.imap(call_mutate, genome_list, chunksize=1000))
    time_imap = time.time() - t3

    print(time_multi, time_single, time_imap)




