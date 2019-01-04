
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
    self.seed_synaptomes(synaptomes, 10)
    self.fell_off_garden_path = set()


  def check_garden_path(self):
    for gp in ['CAN_GO', 'SHOULD_TURN_LEFT']:
      if gp not in self.exst.synaptomes and gp not in self.fell_off_garden_path:
        print('{} got deleted!'.format(gp))
        self.fell_off_garden_path.add(gp)


  def seed_synaptomes(self, synaptomes, entrenchment):
    for s in synaptomes:
      s.entrenchment = entrenchment
      self.exst.synaptomes[s.name] = s


  def play(self):
    if not self.game:
      raise ValueError("Can't play if no game is defined. Set game property.")

    self.exst.decay(1, 0)

    desperation = 0
    while True:
      # Desperation slowly climbs the longer the game goes on.
      #stress += 0.01 * (.1 - stress)

      gs = self.game.state()
      if 'VICTORY' in gs or 'DEAD' in gs:
        break

      self.exst.check_synaptomes(gs, 2, 3)

      # The odds of just performing a Hail Mary are proportional
      # to the amount of desperation being experienced by the organism.
      cmd = self.exst.choose_command(desperation, self.game.generate_random_command)
      self.game.command(cmd, self.exst)

      # The odds of generating new synaptomes rise as desperation rises.
      Organism.__generate_random_emergent_synaptomes(1, 0.5, 0.5, self.exst, gs)


      # Let checkedstates, entrenchments, etc., all decay a bit, as time is passing.
      self.exst.decay(desperation, desperation)


      #Organism.__cull_random_synaptomes((1 - stress)*.1, self.exst)
      self.check_garden_path()
      


  def apply_reinforcement(self, magnitude):
    checked_synaptomes = self.exst.get_checked_synaptomes()
    if not len(checked_synaptomes):
      return
    mag_dist = magnitude / len(checked_synaptomes)
    for sm in checked_synaptomes:
      sm.entrenchment += mag_dist


  @staticmethod
  def __cull_random_synaptomes(cull_prob, exst):
    items = list(exst.synaptomes.items())
    for skey, sm in items:
      prob_die = cull_prob

      droll = random.random()
      if droll > prob_die:
        continue

      if sm.entrenchment <= 0:
        del exst.synaptomes[skey]
        continue

      sm.decay(entrenchment_decay_prob=cull_prob)

      
  @staticmethod
  def __generate_random_emergent_synaptomes(num_to_generate, prob_add_synapton, prob_add_action, exst, gs):
    generated_sms = set()

    all_synaptomes = list(exst.synaptomes.values())
    active_gamestate_atoms = list(gs)
    while num_to_generate > 0:
      num_to_generate -= 1
      if num_to_generate < 0:
        if random.random() >= num_to_generate + 1:
          break

      deentrenched_sms = [sm for sm in exst.synaptomes.values() if sm.entrenchment <= 0]
      if len(deentrenched_sms):
        sm = random.choice(deentrenched_sms)
        # We'll increment your entrenchment at the end of this function.
        # Y'all have ONE more chance to prove yourselves useful.
        generated_sms.add(sm)
        continue

      synaptons = set()
      randname = 'SYNAPTOME_' + str(int(random.random() * 1000000000))

      while True: 
        # Make a new synaptome, possibly with multiple synaptons, per the 
        # synapton addition decay rate.
        basis = random.choice(list(Synapton.BASES))
        if basis == 'GAME':
          if not len(active_gamestate_atoms):
            continue
          keyname = random.choice(active_gamestate_atoms)
          synapton = Synapton(basis, keyname)
          synaptons.add(synapton)
        elif basis == 'CHECKED':
          if not len(all_synaptomes):
            continue
          sm = random.choice(all_synaptomes)
          synapton = Synapton(basis, sm.name, sm.checkstate)
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

      sm = Synaptome(randname, synaptons, cmd)
      exst.synaptomes[sm.name] = sm
      generated_sms.add(sm)
      
    for sm in generated_sms:
      # Freshly generated (or reactivated) synaptomes get to start with the bare
      # minimum level of entrenchment. Better not squander it.
      sm.entrenchment = 1

    return generated_sms
      


