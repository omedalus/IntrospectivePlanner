

class TeeMazeGame:
  """
  Another stupid-simple game. This one is designed to make the organism
  learn to turn left when it comes to the end of a hallway of 
  pre-defined length.
  """
  def __init__(self, num_steps_before_turn, num_steps_after_turn):
    self.__is_alive = True 
    self.__position = 0
    self.__victory_position = num_steps_before_turn + num_steps_after_turn
    self.__num_steps_before_turn = num_steps_before_turn
    self.__num_steps_after_turn = num_steps_after_turn


  def __game_state(self):
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

  # Performs action a, which must be an Action object.
  # If a has a precondition, the game first tries to match
  # the precondition of a, and then performs the action 
  # iff the precondition was satisfied.
  def action(self, a):
    s = self.__game_state()
    if 'VICTORY' in s or 'DEAD' in s:
      return

    if ('NORTH' in s and a == 'NORTH') or ('WEST' in s and a == 'WEST'):
      self.__position += 1

