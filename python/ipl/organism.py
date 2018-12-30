
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

      gs = self.game.state()
      if 'VICTORY' in gs or 'DEAD' in gs:
        break

      a = self.__choose_action()
      print(a)

      self.__exst.last_action = a

      # TODO: Test the action's precondition against the game state.

      self.game.action(a)


  def __choose_action(self):
    possible_actions = ['NORTH', 'SOUTH', 'EAST', 'WEST']
    astr = random.choice(possible_actions)
    return Action(astr)
