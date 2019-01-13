import ipl 

game = ipl.games.ElMazeGame(3,2)

print(game.io_vector_labels())


print(game.sensors())
game.act([1, 0, 0, 0])

print(game.sensors())
game.act([1, 0, 0, 0])

print(game.sensors())
game.act([1, 0, 0, 0])

print(game.sensors())
game.act([0, 1, 0, 0])

print(game.sensors())
game.act([1, 0, 0, 0])

print(game.sensors())
game.act([1, 0, 0, 0])

print(game.sensors())

