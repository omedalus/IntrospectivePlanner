
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
    self.__orientation = 'NORTH' # random.choice(CARDINALS)
    self.__last_cmd = None

    self.__victory_position = num_steps_before_bend + num_steps_after_bend
    self.__bend_position = num_steps_before_bend



  def eof(self):
    """
    True when the game is over.
    """
    return 'VICTORY' in self.state()


  def player_config(self):
    """Gets a dictionary of configuration arguments that give a player AI information
    about how to initialize.
    Returns:
      {dict} -- Dictionary of configuration arguments.
    """
    vlabels = self.io_vector_labels()
    return {
      'n_sensors': len(vlabels['sensors']),
      'n_actuators': len(vlabels['actuators']),
      'victory_field_idx': vlabels['sensors'].index('VICTORY')
    }


  def io_vector_labels(self):
    """
    Gets the human-readable names of each field in the input and output vectors.
    Useful for keeping track of how the input and output vectors are supposed
    to map to the behaviors of the organism and its actions in the world.
    """
    return {
      'sensors': ['FORWARD', 'LEFT', 'RIGHT', 'BACK', 'VICTORY'],
      'actuators': ['GO', 'TURN LEFT', 'TURN RIGHT', 'TURN BACK']
    }


  def sensors(self):
    """
    Gets the vector of current sensor readings.
    """
    retval = [1 if symbol in self.state() else 0 for symbol in self.io_vector_labels()['sensors']]
    return retval




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



  # Submits the actuator vector for evaluation.
  def act(self, actuators):
    self.turn += 1

    cmds = [label for idx,label in enumerate(self.io_vector_labels()['actuators']) if actuators[idx]>0]

    # To make the problem space a little more tractable and less linearly inseparable,
    # I'll say that 'GO' overrides other commands.
    if 'GO' in cmds:
      cmds = ['GO']

    if len(cmds) != 1:
      return

    cmd = cmds[0]
    self.__last_cmd = cmd

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
    retval = '{} turn {}/{} ({}): @{}{}'.format(
      self.title,
      self.turn,
      self.par,
      self.__last_cmd or '',
      self.__position,
      CARDINALS_ASCII[self.__orientation]
    )
    return retval

  def draw(self):
    print()
    print(self)

    hlen = 1 + self.__victory_position - self.__bend_position
    ss = []
    ss.append('  ' + '-'*(hlen-1) + '+')
    for _ in range(self.__bend_position):
      ss.append(' ' + ' '*hlen + '|')

    agent_line = max(0, self.__bend_position - self.__position)
    agent_x = len(ss[agent_line]) - 1
    if self.__position > self.__bend_position:
      agent_x -= self.__position - self.__bend_position
    sl = list(ss[agent_line])
    sl[agent_x] = CARDINALS_ASCII[self.__orientation]
    ss[agent_line] = ''.join(sl)


    sout = '\n'.join(ss)
    print(sout)

