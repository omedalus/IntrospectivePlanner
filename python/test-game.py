import ipl 

game = ipl.games.ElMazeGame(3,2)
organism = ipl.Organism()

organism.init_game(game)
organism.action_generator.generate()
print(organism.action_generator.population)

action_program = [
    [1, 0, 0, 0],
    [1, 0, 0, 0],
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [1, 0, 0, 0],
    [1, 0, 0, 0]
]

print(game.io_vector_labels())

for pa in action_program:
  print(game.sensors())

  oa = organism.handle_sensor_input(game.sensors(), pa)
  game.act(oa)

print(game.sensors())

