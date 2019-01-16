import ipl 

game = ipl.games.ElMazeGame(3,2)
organism = ipl.Organism()
organism.verbosity = 1

organism.configure(game.player_config())

organism.reset_state()
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
    print('(Action has no outcomes)')

  game.act(oa.actuators)


print()
print('RUNNER: Predefined action sequence complete.')
organism.handle_sensor_input(game.sensors())
organism.maintenance()

game.draw()
