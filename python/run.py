
import ipl
import sys

organism = ipl.Organism()

for i in range(0, 1000):
  game = ipl.games.ElMazeGame(3, 3)
  organism.game = game
  organism.play()

  print('{}\t{}\t{}'.format(
    i,
    game.turn,
    len(organism.exst.synaptomes)
  ))

  if 'VICTORY' in game.state():
    organism.apply_reinforcement(10)


print('Organism experience state: \n' + str(organism.exst))
