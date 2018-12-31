
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

    print('Seeding synaptome')
    self.game.seed_synaptomes(self.__exst)

    print('Playing game: ' + self.game.title)
    while True:
      print('')
      print(self.game)
      print(vars(self.__exst))

      gs = self.game.state()
      if 'VICTORY' in gs or 'DEAD' in gs:
        break

      Organism.__check_synaptomes(self.__exst, gs)

      attemptable_actions = self.__generate_action_candidates()

      a = Organism.__choose_action(attemptable_actions, self.__exst)
      print(a)

      self.game.command(a.command, self.__exst)
      self.__exst.last_command = a.command


  @staticmethod
  def __check_synaptomes(experience_state, game_state):
    # NOTE: For now, checks all synaptomes. In the future,
    # will run a GA that checks them competitively, because
    # the collection of all synaptomes will be computationally
    # infeasible to check directly.
    # Also, synaptome dependencies can be recursive, so checking them 
    # exhaustively would result in an infinite loop anyway.    
    # For now, we will at least shuffle the synaptomes just as a precursor
    # for making them driven by a GA.
    synaptomes = list(experience_state.synaptomes.values())
    random.shuffle(synaptomes)

    for s in synaptomes:
      is_fulfilled = s.is_fulfilled(experience_state, game_state)
      experience_state.checked[s.name] = is_fulfilled


  def __generate_action_candidates(self):
    return self.game.get_attemptable_actions()


  @staticmethod
  def __choose_action(attemptable_actions, exst):
    viable_choices = set()
    if exst.checked.get('CAN_GO'):
      viable_choices.add('GO')
    else:
      viable_choices.add('TURN LEFT')

    astr = random.choice(list(viable_choices))
    return Action(astr)
