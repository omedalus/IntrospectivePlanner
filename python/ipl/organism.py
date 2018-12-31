
from .experience_state import ExperienceState
from .reflex_action_statement import ReflexActionStatement

from .synapton import Synapton
from .synaptome import Synaptome

from .action import Action

import random


class Organism:
  """
  Give it a Game, and watch it play!
  """


  def __init__(self, game=None):
    self.game = game
    self.__exst = ExperienceState()


  def play(self):
    if not self.game:
      raise ValueError("Can't play if no game is defined. Set game property.")

    foo = Synaptome(Synapton('CHECKED', 'CAN_GO'))

    print('Playing game: ' + self.game.title)
    while True:
      print('')
      print(self.game)
      print(vars(self.__exst))

      print(foo)
      print(foo.is_fulfilled(self.__exst))

      gs = self.game.state()
      if 'VICTORY' in gs or 'DEAD' in gs:
        break

      attemptable_actions = self.__generate_action_candidates()

      a = Organism.__choose_action(attemptable_actions, self.__exst)
      print(a)

      self.game.command(a.command, self.__exst)
      self.__exst.last_command = a.command

  def __generate_action_candidates(self):
    return self.game.get_attemptable_actions()


  @staticmethod
  def __choose_action(attemptable_actions, exst):
    viable_choices = set()
    if exst.last_command != 'CHECK FORWARD':
      viable_choices.add('CHECK FORWARD')
    elif exst.checked.get('FORWARD'):
      viable_choices.add('GO')
    else:
      viable_choices.add('TURN LEFT')

    astr = random.choice(list(viable_choices))
    return Action(astr)
