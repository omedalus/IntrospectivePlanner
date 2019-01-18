import ipl 
import pickle
import numpy # pylint: disable=E0401

organism = ipl.Organism()
organism.randomtest = True

game = ipl.games.ElMazeGame(3, 2)
organism.configure(game.player_config())

if not organism.randomtest:
  try:
    exprepo = pickle.load(open("organism-exprepo.p", "rb"))
    organism.experience_repo = exprepo
  except FileNotFoundError:
    print('No experience repository file found. Starting from scratch.')


aturns = []

for irun in range(1000):
  organism.reset_state()

  game = ipl.games.ElMazeGame(3, 2)
  while not game.eof():
    organism.handle_sensor_input(game.sensors())

    oa = organism.choose_action()
    game.act(oa.actuators)

  organism.handle_sensor_input(game.sensors())
  organism.maintenance()

  numturns = game.turn
  print('Run {} completed in {} turns.'.format(irun+1, numturns))

  aturns.append(numturns)

print()
print('RESULTS')
print('# turns completion: {:.2f} +- {:.2f}'.format(numpy.mean(aturns), numpy.std(aturns)))
