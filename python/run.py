
import ipl
import sys
import random

import argparse
parser = argparse.ArgumentParser(description='Run an AI through a game over and over again until it figures out how to win consistently.')
parser.add_argument('ngames', help='How many times to run the game.', type=int)
parser.add_argument(
    '-r', '--report', 
    help='Reporting interval. How many game runs occur between each line of reporting output.', 
    type=int)
args = parser.parse_args()

organism = ipl.Organism()

turn_total = 0

rint = args.report or args.ngames

for i in range(0, args.ngames):
  game = ipl.games.ElMazeGame(int(10*random.random()) + 2, int(10*random.random()) + 2)
  organism.game = game
  organism.play()

  if 'VICTORY' in game.state():
    organism.receive_reinforcement(1000 * game.par / game.turn)

  imod = (i+1) % rint
  turn_total += (game.turn / game.par)


  if imod == 0:
    turn_avg = turn_total / rint
    turn_total = 0

    print('{}\t{}\t{}\t{:.2f}'.format(
      i+1,
      turn_avg,
      len(organism.exst.synaptons),
      organism.exst.angst()
    ))



print('Organism experience state: \n' + str(organism.exst))

# Add one last demonstration run, with step-by-step annotation,
# to see wtf the organism is doing.
print('\n\nFINAL SAMPLE RUN')
game = ipl.games.ElMazeGame(int(10*random.random()) + 2, int(10*random.random()) + 2)
organism.game = game
organism.play(1)
