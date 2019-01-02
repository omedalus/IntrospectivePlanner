
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

    print('Seeding actions')
    self.game.seed_actions(self.__exst)


    print('Playing game: ' + self.game.title)
    while True:
      print('')
      print('Game: ' + str(self.game))

      gs = self.game.state()
      if 'VICTORY' in gs or 'DEAD' in gs:
        break

      Organism.__check_synaptomes(self.__exst, gs)

      print('Experience: ' + str(vars(self.__exst)))

      attemptable_actions = Organism.__generate_action_candidates(self.__exst)

      a = Organism.__choose_action(attemptable_actions, self.__exst)
      if not a:
        a = Action(self.game.generate_random_command())
      print('Chosen Action: ' + str(a))

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
    for i in range(0, 10):
      is_dirty = False
      synaptomes = list(experience_state.synaptomes.values())
      random.shuffle(synaptomes)

      for s in synaptomes:
        is_fulfilled = s.is_fulfilled(experience_state, game_state)
        if experience_state.checked.get(s.name) != is_fulfilled:
          is_dirty = True
        experience_state.checked[s.name] = is_fulfilled

      if not is_dirty:
        break


  @staticmethod
  def __generate_action_candidates(exst):
    retval = set()
    for a in exst.actions:
      precondition_met = True
      if a.precondition:
        precondition_met = exst.checked.get(a.precondition)
      if precondition_met:
        retval.add(a)
    return retval


  @staticmethod
  def __choose_action(attemptable_actions, exst):
    print('Attemptible actions: ' + str(attemptable_actions))
    if not attemptable_actions or not len(attemptable_actions):
      return None
    a = random.choice(list(attemptable_actions))
    return a
