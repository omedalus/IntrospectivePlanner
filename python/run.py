
import ipl

print('RUNNING INTROSPECTIVE PLANNER')

game = ipl.games.ElMazeGame(3,3)
organism = ipl.Organism(game)

organism.play()

print('')
print('Terminus reached in {} turns.'.format(game.turn))
print('Organism experience state: ' + str(vars(organism.exst)))

