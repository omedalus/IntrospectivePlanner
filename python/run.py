
import ipl

print('RUNNING INTROSPECTIVE PLANNER')

game = ipl.games.ElMazeGame(3,3)
organism = ipl.Organism(game)

organism.play()