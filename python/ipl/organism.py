
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

    synaptomes = set()
    synaptomes.add(Synaptome('CAN_GO', Synapton('GAME', 'FORWARD'), 'GO'))
    synaptomes.add(Synaptome('SHOULD_TURN_LEFT', Synapton('CHECKED', 'CAN_GO', False), 'TURN LEFT'))
    self.seed_synaptomes(synaptomes, 100)


  def seed_synaptomes(self, synaptomes, entrenchment):
    for s in synaptomes:
      s.entrenchment = entrenchment
      self.exst.synaptomes[s.name] = s


  def play(self):
    if not self.game:
      raise ValueError("Can't play if no game is defined. Set game property.")


    print('Playing game: ' + self.game.title)
    while True:
      gs = self.game.state()
      if 'VICTORY' in gs or 'DEAD' in gs:
        break

      Organism.__check_synaptomes(2, 4, self.exst, gs)

      attemptable_actions = Organism.__generate_action_candidates(self.exst)

      cmd = Organism.__choose_action(attemptable_actions, self.exst)
      if not cmd:
        cmd = self.game.generate_random_command()

      self.game.command(cmd, self.exst)
      self.exst.last_command = cmd

      Organism.__generate_random_emergent_synaptomes(.2, 0.5, 0.5, self.exst, gs)
      print('Num synaptomes: {}'.format(len(self.exst.synaptomes)))

      Organism.__cull_random_synaptomes(0.5, self.exst, gs)
      


  def apply_reinforcement(self, magnitude):
    # All synaptomes receive the reinforcement!
    # Divide equally among all synaptomes, so that
    # synaptomes that are members of less populous
    # and more parsimonious regimes get rewarded more.
    all_synaptomes = list(self.exst.synaptomes.values())
    if not len(all_synaptomes):
      return
    mag_per_syn = int(magnitude / len(all_synaptomes))
    for s in all_synaptomes:
      s.entrenchment += mag_per_syn


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

      
  @staticmethod
  def __generate_random_emergent_synaptomes(num_to_generate, prob_add_synapton, prob_add_action, exst, gs):
    checked_synaptomes = list(exst.checked.keys())
    active_gamestate_atoms = list(gs)
    while num_to_generate > 0:
      num_to_generate -= 1
      if num_to_generate < 0:
        if random.random() > num_to_generate + 1:
          break

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

      cmd = None
      if random.random() <= prob_add_action:
        cmd = exst.last_command

      synaptome = Synaptome(randname, synaptons, cmd)
      exst.synaptomes[synaptome.name] = synaptome



  @staticmethod
  def __check_synaptomes(num_check_per_round, num_rounds, experience_state, game_state):
    # NOTE: For now, checks all synaptomes. In the future,
    # will run a GA that checks them competitively, because
    # the collection of all synaptomes will be computationally
    # infeasible to check directly.
    # Also, synaptome dependencies can be recursive, so checking them 
    # exhaustively would result in an infinite loop anyway.    
    # For now, we will at least shuffle the synaptomes just as a precursor
    # for making them driven by a GA.
    for i in range(0, num_rounds):
      is_dirty = False
      synaptomes = list(experience_state.synaptomes.values())
      random.shuffle(synaptomes)
      synaptomes = synaptomes[:num_check_per_round]

      for s in synaptomes:
        is_fulfilled = s.is_fulfilled(experience_state, game_state)
        if experience_state.checked.get(s.name) != is_fulfilled:
          is_dirty = True

        experience_state.checked[s.name] = is_fulfilled
        # If a synaptome has actually been fulfilled, give it a little
        # bit of reinforcement. This will eventually be equivalent to
        # a Q-learning factor, and may be a completely separate metric
        # called "recent_usage" or something. Either way, synaptomes
        # that have been recently used should be immune from culling.
        #if is_fulfilled:
        #  s.entrenchment += 10

      if not is_dirty:
        break


  @staticmethod
  def __generate_action_candidates(exst):
    retval = set()
    for skey,sval in exst.checked.items():
      if not sval:
        continue
      sm = exst.synaptomes.get(skey)
      if not sm:
        continue
      if not sm.command:
        continue
      retval.add(sm.command)
    return retval


  @staticmethod
  def __choose_action(attemptable_actions, exst):
    if not attemptable_actions or not len(attemptable_actions):
      return None
    a = random.choice(list(attemptable_actions))
    return a
