
import ipl
import sys
import random

organism = ipl.Organism()

turn_total = 0

interval = 100

for i in range(0, 5000):
  game = ipl.games.ElMazeGame(int(10*random.random()) + 2, int(10*random.random()) + 2)
  organism.game = game
  organism.play()

  imod = i % interval
  turn_total += game.turn

  if imod == 0:
    turn_avg = turn_total / interval
    turn_total = 0

    print('{}\t{}\t{}\t{}\t{}'.format(
      i,
      game.turn,
      turn_avg,
      len(organism.exst.synaptomes),
      len(organism.exst.get_entrenched_synaptomes())
    ))


  if 'VICTORY' in game.state():
    organism.apply_reinforcement(1000 / game.turn)


print('Organism experience state: \n' + str(organism.exst))

# Add one last demonstration run, with step-by-step annotation,
# to see wtf the organism is doing.
print('\n\nFINAL SAMPLE RUN')
game = ipl.games.ElMazeGame(int(10*random.random()) + 2, int(10*random.random()) + 2)
organism.game = game
organism.play(1)