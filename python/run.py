
import ipl
import sys

organism = ipl.Organism()

turn_total = 0

for i in range(0, 1000):
  game = ipl.games.ElMazeGame(3, 3)
  organism.game = game
  organism.play()

  turn_total += game.turn
  turn_avg = turn_total / (i + 1)

  if i % 100 == 0:
    print('{}\t{}\t{}\t{}\t{}'.format(
      i,
      game.turn,
      turn_avg,
      len(organism.exst.synaptomes),
      len([sm for sm in organism.exst.synaptomes.values() if sm.entrenchment > 0])
    ))

  if 'VICTORY' in game.state():
    organism.apply_reinforcement(100 / game.turn)


print('Organism experience state: \n' + str(organism.exst))
