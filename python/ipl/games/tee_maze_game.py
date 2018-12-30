
from ..action import Action

class TeeMazeGame:
  """
  Another stupid-simple game. This one is designed to make the organism
  learn to turn left when it comes to the end of a hallway of 
  pre-defined length.
  """
  def __init__(self, num_steps_before_turn, num_steps_after_turn):
    self.title = 'Tee Maze Game {}x{}'.format(num_steps_before_turn, num_steps_after_turn)
    self.turn = 0

    self.__is_alive = True 
    self.__position = 0
    self.__victory_position = num_steps_before_turn + num_steps_after_turn
    self.__num_steps_before_turn = num_steps_before_turn
    self.__num_steps_after_turn = num_steps_after_turn

  def __str__(self):
    gs = self.state()
    retval = '#{} @{}:'.format(self.turn, self.__position)
    retval += str(gs)
    return retval

  def state(self):
    retval = set()
    if self.__position == self.__victory_position:
      retval.add('VICTORY')

    if self.__position < self.__num_steps_before_turn:
      retval.add('NORTH')
    elif self.__position < self.__victory_position:
      retval.add('WEST')

    if self.__position > 0:
      if self.__position <= self.__num_steps_before_turn:
        retval.add('SOUTH')
      else:
        retval.add('EAST')
      
    if not self.__is_alive:
      retval.add('DEAD')
    
    return retval

  # Performs action a, which is given as a string.
  # Can be given as an Action object, in which case
  # it takes the "action" member of the Action object.
  def action(self, a):
    if isinstance(a, Action):
      a = a.action

    self.turn += 1

    gs = self.state()
    if 'VICTORY' in gs or 'DEAD' in gs:
      return

    if ('NORTH' in gs and a == 'NORTH') or ('WEST' in gs and a == 'WEST'):
      self.__position += 1

    if ('SOUTH' in gs and a == 'SOUTH') or ('EAST' in gs and a == 'EAST'):
      self.__position -= 1


