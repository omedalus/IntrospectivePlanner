
import ipl

print('RUNNING INTROSPECTIVE PLANNER')

game = ipl.games.TeeMazeGame(3,3)
organism = ipl.Organism(game)

organism.play()