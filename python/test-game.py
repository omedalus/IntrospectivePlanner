import ipl 

game = ipl.games.ElMazeGame(3,2)
organism = ipl.Organism()
organism.verbosity = 1

organism.configure(game.player_config())

action_program = [
    [1, 0, 0, 0],
    [1, 0, 0, 0],
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [1, 0, 0, 0],
    [1, 0, 0, 0]
]

organism.reset_state()
for iturn, pa in enumerate(action_program):
  print('\nRUNNER: Turn {}'.format(iturn + 1))
  organism.handle_sensor_input(game.sensors())

  oa = organism.choose_action(pa)
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
