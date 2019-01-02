
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
    self.exst = ExperienceState()

  def play(self):
    if not self.game:
      raise ValueError("Can't play if no game is defined. Set game property.")


    print('Playing game: ' + self.game.title)
    while True:
      gs = self.game.state()
      if 'VICTORY' in gs or 'DEAD' in gs:
        break

      Organism.__check_synaptomes(self.exst, gs)

      Organism.__cull_random_synaptomes(0.5, self.exst, gs)
      Organism.__generate_random_emergent_synaptomes(1, 0.5, self.exst, gs)
      Organism.__generate_random_conditioned_actions(1, self.exst, gs)

      attemptable_actions = Organism.__generate_action_candidates(self.exst)

      a = Organism.__choose_action(attemptable_actions, self.exst)
      if not a:
        a = Action(self.game.generate_random_command())

      self.game.command(a.command, self.exst)
      self.exst.last_command = a.command


  def apply_reinforcement(self, magnitude):
    # All synaptomes receive the reinforcement!
    for s in self.exst.synaptomes.values():
      s.entrenchment += magnitude


  @staticmethod
  def __cull_random_synaptomes(survival_prob, exst, gs):
    items = list(exst.synaptomes.items())
    for skey, s in items:
      droll = random.random()
      if droll <= survival_prob:
        continue

      s.entrenchment -= 1
      if s.entrenchment > 0:
        continue

      del exst.synaptomes[skey]
      if skey in exst.checked:
        del exst.checked[skey]
      exst.actions = set([a for a in exst.actions if a.precondition != skey])

      
  @staticmethod
  def __generate_random_emergent_synaptomes(num_to_generate, prob_add_synapton, exst, gs):
    checked_synaptomes = list(exst.checked.keys())
    active_gamestate_atoms = list(gs)
    for i in range(0, num_to_generate):
      synaptons = set()
      randname = 'SYNAPTOME_' + str(int(random.random() * 1000000000))

      while True: 
        # Make a new synaptome out of between 1 to 4 synaptons.
        basis = random.choice(list(Synapton.BASES))
        if basis == 'GAME':
          if not len(active_gamestate_atoms):
            continue
          keyname = random.choice(active_gamestate_atoms)
          synapton = Synapton(basis, keyname)
          synaptons.add(synapton)
        elif basis == 'CHECKED':
          if not len(checked_synaptomes):
            continue
          keyname = random.choice(checked_synaptomes)
          value = exst.checked[keyname]
          synapton = Synapton(basis, keyname, value)
          synaptons.add(synapton)
        elif basis == 'LAST_ACTION':
          if not exst.last_command:
            continue
          synapton = Synapton(basis, exst.last_command)
          synaptons.add(synapton)          
        else:
          # Not supported yet, roll again.
          continue
      
        droll = random.random()
        if droll > prob_add_synapton:
          break

      synaptome = Synaptome(randname, synaptons)
      exst.synaptomes[synaptome.name] = synaptome


  @staticmethod
  def __generate_random_conditioned_actions(num_to_generate, exst, gs):
    if not exst.last_command:
      return
    active_checked_synaptomes = [skey for skey,sval in exst.checked.items() if sval]
    if not len(active_checked_synaptomes):
      return
    for i in range(0, num_to_generate):
      skey = random.choice(active_checked_synaptomes)
      a = Action(exst.last_command, skey)
      exst.actions.add(a)





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
    if not attemptable_actions or not len(attemptable_actions):
      return None
    a = random.choice(list(attemptable_actions))
    return a
