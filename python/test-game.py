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
  print('\nRUNNER: Turn {}'.format(iturn))
  oa = organism.handle_sensor_input(game.sensors(), pa)
  game.act(oa)

print('\n')
print('RUNNER: Predefined action sequence complete.')
oa = organism.handle_sensor_input(game.sensors(), pa)
