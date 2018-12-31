
from ..action import Action

import random

CARDINALS = ['NORTH', 'EAST', 'SOUTH', 'WEST']
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

    self.__is_alive = True 
    self.__position = 0
    self.__orientation = 'NORTH' # random.choice(CARDINALS)
    self.__victory_position = num_steps_before_bend + num_steps_after_bend
    self.__bend_position = num_steps_before_bend


  def __str__(self):
    gs = self.state()
    retval = '#{} {} @{}:'.format(self.turn, self.__orientation, self.__position)
    retval += str(gs)
    return retval


  def command_vocabulary(self):
    # Lists all possible actions that are available in this game.
    return set(['GO', 'CHECK CAN_GO', 'TURN LEFT', 'TURN RIGHT'])



  def get_attemptable_actions(self):
    retval = set()
    retval.add(Action('GO'))
    retval.add(Action('CHECK CAN_GO'))
    retval.add(Action('TURN LEFT'))
    retval.add(Action('TURN RIGHT'))



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



  # Performs command cmd, which is given as a string.
  # Every command induces some kind of change of state.
  # This can mean either a change in the game state,
  # or a change in the experience state.
  def command(self, cmd, experience_state=None):
    self.turn += 1

    gs = self.state()
    if 'DEAD' in gs or 'VICTORY' in gs:
      return False

    if cmd.startswith('CHECK'):
      cmdparts = cmd.split()
      cmdkey = cmdparts[1]
      experience_state.checked[cmdkey] = 'FORWARD' in gs
      return True

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

