import ipl 

game = ipl.games.ElMazeGame(3,2)
organism = ipl.Organism()
organism.verbosity = 1

organism.init_game(game)

action_program = [
    [1, 0, 0, 0],
    [1, 0, 0, 0],
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [1, 0, 0, 0],
    [1, 0, 0, 0]
]

for iturn, pa in enumerate(action_program):
  print('\nRUNNER: Turn {}'.format(iturn + 1))
  organism.handle_sensor_input(game.sensors())

  oa = organism.choose_action(pa)
  if oa.consequences and len(oa.consequences):
    print('Expected consequences:')
    for consequence in oa.consequences:
      print('\t{}'.format(consequence))
  else:
    print('(Action has no consequences)')

  game.act(oa.actuators)
  

print()
print('RUNNER: Predefined action sequence complete.')
organism.handle_sensor_input(game.sensors())
