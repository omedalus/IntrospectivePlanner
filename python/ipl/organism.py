
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
    #self.seed_synaptomes(synaptomes, 10)
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

    stress = 0.01
    while True:
      stress += 0.01 * (.1 - stress)
      self.exst.decay(stress, 0)

      gs = self.game.state()
      if 'VICTORY' in gs or 'DEAD' in gs:
        break

      self.exst.check_synaptomes(gs, 10, 10)

      cmd = self.exst.choose_command(stress)
      if not cmd:
        cmd = self.game.generate_random_command()

      self.game.command(cmd, self.exst)
      self.exst.last_command = cmd

      Organism.__generate_random_emergent_synaptomes(stress, 0.5, 0.5, self.exst, gs)
      # print('Num synaptomes: {}'.format(len(self.exst.synaptomes)))

      Organism.__cull_random_synaptomes(stress * 10, self.exst)
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

      sm.decay(entrenchment_decay_prob=cull_prob)
      if sm.entrenchment > 0:
        continue

      del exst.synaptomes[skey]

      
  @staticmethod
  def __generate_random_emergent_synaptomes(num_to_generate, prob_add_synapton, prob_add_action, exst, gs):
    checked_synaptomes = exst.get_checked_synaptomes()
    active_gamestate_atoms = list(gs)
    while num_to_generate > 0:
      num_to_generate -= 1
      if num_to_generate < 0:
        if random.random() > num_to_generate + 1:
          break

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
          if not len(checked_synaptomes):
            continue
          sm = random.choice(checked_synaptomes)
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

      synaptome = Synaptome(randname, synaptons, cmd)
      exst.synaptomes[synaptome.name] = synaptome


