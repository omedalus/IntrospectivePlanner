
import ipl
import sys

print('RUNNING INTROSPECTIVE PLANNER')
print('Run#\t#Turns\tSynLen', file=sys.stderr)

organism = ipl.Organism()

for i in range(0, 100):
  print('')

  print('RUN #{}'.format(i + 1))
  game = ipl.games.ElMazeGame(3, 3)
  organism.game = game
  organism.play()

  print('Terminus reached in {} turns.'.format(game.turn))
  print('Organism experience state: \n' + str(organism.exst))

  print('{}\t{}\t{}'.format(
    i,
    game.turn,
    len(organism.exst.synaptomes)
  ), file=sys.stderr)

  if 'VICTORY' in game.state():
    #print('Applying reinforcement.')
    organism.apply_reinforcement(100)
