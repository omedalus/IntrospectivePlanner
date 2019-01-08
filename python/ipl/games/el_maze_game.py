
from ..action import Action

from ..synapticle import Synapticle
from ..synaptome import Synaptome

import random

CARDINALS = ['NORTH', 'EAST', 'SOUTH', 'WEST']
CARDINALS_ASCII = {
  'NORTH': '^',
  'EAST': '>',
  'SOUTH': 'v',
  'WEST': '<'
}
DIRECTION_TURN_MAGNITUDE = {
  'RIGHT': 1,
  'LEFT': -1,
  'BACK': 2,
  'FORWARD': 0
}
DIRECTIONS = list(DIRECTION_TURN_MAGNITUDE.keys())

def turn(dirstr, startorient):
  if dirstr not in DIRECTIONS:
    raise ValueError('dirstr', 'Must be a direction.')
  if startorient not in CARDINALS:
    raise ValueError('startorient', 'Must be a cardinal direction.')

  i = CARDINALS.index(startorient)
  i += DIRECTION_TURN_MAGNITUDE[dirstr]
  i += len(CARDINALS)
  i %= len(CARDINALS)
  return CARDINALS[i]

def find_turn(startorient, endorient):
  if startorient not in CARDINALS:
    raise ValueError('startorient', 'Must be a cardinal direction.')
  if endorient not in CARDINALS:
    raise ValueError('endorient', 'Must be a cardinal direction.')

  for dir in DIRECTIONS:
    if turn(dir, startorient) == endorient:
      return dir

  return None



class ElMazeGame:
  """
  Stupid-simple game. The organism must turn left when it comes to 
  a bend in a hallway.
  """
  def __init__(self, num_steps_before_bend, num_steps_after_bend):
    self.title = 'El Maze Game {}x{}'.format(num_steps_before_bend, num_steps_after_bend)
    self.turn = 0
    self.par = 3 + num_steps_before_bend + 1 + num_steps_after_bend 

    self.__is_alive = True 
    self.__position = 0
    self.__orientation = random.choice(CARDINALS)
    self.__victory_position = num_steps_before_bend + num_steps_after_bend
    self.__bend_position = num_steps_before_bend



  def generate_random_command(self):
    commands = ['GO', 'TURN LEFT', 'TURN RIGHT', 'TURN BACK']
    return random.choice(commands)


  def state(self):
    if self.__position >= self.__victory_position:
      return set(['VICTORY'])

    cardinal_exits = set()
    if self.__position >= 0 and self.__position < self.__bend_position:
      cardinal_exits.add('NORTH')

    if self.__position > 0 and self.__position <= self.__bend_position:
      cardinal_exits.add('SOUTH')

    if self.__position > self.__bend_position:
      cardinal_exits.add('EAST')

    if self.__position >= self.__bend_position and self.__position < self.__victory_position:
      cardinal_exits.add('WEST')

    relative_exits = set([find_turn(self.__orientation, cardexit) for cardexit in cardinal_exits])    
    return relative_exits


  def set_experience(self, experience_state):
    gs = self.state()
    experience_state.inputs = set(gs)



  # Performs command cmd, which is given as a string.
  def command(self, cmd):
    self.turn += 1

    gs = self.state()
    if 'DEAD' in gs or 'VICTORY' in gs:
      return False

    if cmd.startswith('TURN'):
      cmdparts = cmd.split()
      cmddir = cmdparts[1]
      self.__orientation = turn(cmddir, self.__orientation)
      return True

    if cmd.startswith('GO'):
      if 'FORWARD' in gs:
        if self.__orientation in ['NORTH', 'WEST']:
          self.__position += 1
        else:
          self.__position -= 1
        return True
      return False

    return False


  def __repr__(self):
    retval = '{} turn {}/{}: {} {}'.format(
      self.title,
      self.turn,
      self.par,
      self.__position,
      CARDINALS_ASCII[self.__orientation]
    )
    return retval

