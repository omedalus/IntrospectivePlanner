

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


  def state(self):
    retval = set()
    if self.__position == self.__victory_position:
      retval.add('Victory')

    if self.__position < self.__num_steps_before_turn:
      retval.add('North')
    elif self.__position < self.__victory_position:
      retval.add('West')

    if self.__position > 0:
      if self.__position <= self.__num_steps_before_turn:
        retval.add('South')
      else:
        retval.add('East')
      
    if not self.__is_alive:
      retval.add('Dead')
    
    return retval

  def action(self, a):
    s = self.state()
    if 'Victory' in s or 'Dead' in s:
      return

    if ('North' in s and a == 'North') or ('West' in s and a == 'West'):
      self.__position += 1

      