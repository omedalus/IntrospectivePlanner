
from .experience_state import ExperienceState
from .reflex_action_statement import ReflexActionStatement


class Organism:
  """
  Give it a Game, and watch it play!
  """


  def __init__(self):
    self.game = None
    self.__exst = ExperienceState()


  def play(self):
    if not self.game:
      raise ValueError("Can't play if no game is defined. Set game property.")

    while True:
      gs = self.game.state()
      print(gs)
      if 'Victory' in gs or 'Dead' in gs:
        break

      self.__exst.external_inputs = gs
      a = self.__choose_action()
      print(a)
      print('')

      self.game.action(a)


  def __choose_action(self):
    if 'North' in self.__exst.external_inputs:
      return 'North'
    else:
      return 'West'