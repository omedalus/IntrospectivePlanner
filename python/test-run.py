import ipl 
import pickle

game = ipl.games.ElMazeGame(3,2)
organism = ipl.Organism()
organism.verbosity = 1

organism.randomtest = False
organism.configure(game.player_config())
#organism.outcome_likelihood_estimator = None

try:
  exprepo = pickle.load(open("organism-exprepo.p", "rb"))
  organism.experience_repo = exprepo
  pass
except FileNotFoundError:
  print('No experience repository file found. Starting from scratch.')


organism.reset_state()
organism.action_outcome_lookahead = 5

while not game.eof():
  game.draw()

  print('\nRUNNER: Turn {}'.format(game.turn))
  organism.handle_sensor_input(game.sensors())

  oa = organism.choose_action()
  if oa.outcomes and len(oa.outcomes):
    print('Expected outcomes:')
    for outcome in oa.outcomes:
      print('\t{}'.format(outcome))
  else:
    print('(Action has no foreseen outcomes)')

  game.act(oa.actuators)


print()
print('RUNNER: Predefined action sequence complete.')
organism.handle_sensor_input(game.sensors())
organism.maintenance()

game.draw()

pickle.dump(organism.experience_repo, open("organism-exprepo.p", "wb"))
