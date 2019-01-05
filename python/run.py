
import ipl
import sys

organism = ipl.Organism()

turn_total = 0

interval = 100

for i in range(0, 10000):
  game = ipl.games.ElMazeGame(10, 10)
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
