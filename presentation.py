from single_creature import Genome, Circle, Color
from obrazki import breed

c1 = Genome(4)

c2 = Genome(4)

c1.draw(scale=5, show=True, save=False)
c2.draw(scale=5, show=True, save=False)
input('press enter to show kids')

nc1, nc2 = breed((c1, c2))

nc1.draw(scale=5, show=True, save=False)
nc2.draw(scale=5, show=True, save=False)
