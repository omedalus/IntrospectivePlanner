
import ipl

print('RUNNING INTROSPECTIVE PLANNER')

organism = ipl.Organism()

for i in range(0, 100):
  print('')

  print('RUN #{}'.format(i + 1))
  game = ipl.games.ElMazeGame(3, 3)
  organism.game = game
  organism.play()

  print('Terminus reached in {} turns.'.format(game.turn))
  if len(organism.exst.synaptomes) > 2:
    print('Organism experience state: ' + str(organism.exst))

  if 'VICTORY' in game.state():
    #print('Applying reinforcement.')
    organism.apply_reinforcement(100)
