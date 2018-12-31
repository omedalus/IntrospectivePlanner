
from .experience_state import ExperienceState
from .reflex_action_statement import ReflexActionStatement

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

    print('Playing game: ' + self.game.title)
    while True:
      print('')
      print(self.game)
      print(vars(self.__exst))

      gs = self.game.state()
      if 'VICTORY' in gs or 'DEAD' in gs:
        break

      possible_actions = self.__generate_possible_actions()

      a = Organism.__choose_action(possible_actions, self.__exst)
      print(a)

      self.game.command(a.command, self.__exst)
      self.__exst.last_command = a.command

  def __generate_possible_actions(self):
    return self.game.action_vocabulary()


  @staticmethod
  def __choose_action(possible_actions, exst):
    viable_choices = set()
    if exst.last_command != 'CAN_GO':
      viable_choices.add('CAN_GO')
    elif exst.checked.get('CAN_GO'):
      viable_choices.add('GO')
    else:
      viable_choices.add('TURN LEFT')

    astr = random.choice(list(viable_choices))
    return Action(astr)
