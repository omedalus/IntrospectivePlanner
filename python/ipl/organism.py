
from .experience_state import ExperienceState
from .reflex_action_statement import ReflexActionStatement

from .synapticle import Synapticle
from .synapton import Synapton

from .action import Action

import random
import statistics


class Organism:
  """
  Give it a Game, and watch it play!
  """

  def __init__(self, game=None):
    self.game = game
    self.exst = ExperienceState()

    synaptons = set()
    synaptons.add(Synapton('CAN_GO', Synapticle('INPUT', 'FORWARD')))
    synaptons.add(Synapton('GO_GO', Synapticle('CHECKED', 'CAN_GO', True), 'GO'))
    synaptons.add(Synapton('SHOULD_TURN_LEFT', Synapticle('CHECKED', 'CAN_GO', False), 'TURN LEFT'))
    synaptons.add(Synapton('DUMMY', [
      Synapticle('CHECKED', 'CAN_GO', False),
      Synapticle('CHECKED', 'CAN_GO', True)
    ], 'TURN BACK'))
    self.seed_synaptons(synaptons)
    self.fell_off_garden_path = set()


  def check_garden_path(self):
    for gp in ['CAN_GO', 'GO_GO', 'SHOULD_TURN_LEFT']:
      if gp not in self.exst.synaptons and gp not in self.fell_off_garden_path:
        print('{} got deleted!'.format(gp))
        self.fell_off_garden_path.add(gp)


  def seed_synaptons(self, synaptons):
    for s in synaptons:
      s.expectation.n = 1000000
      self.exst.synaptons[s.name] = s


  def play(self, verbosity=0):
    if not self.game:
      raise ValueError("Can't play if no game is defined. Set game property.")

    if verbosity >= 1:
      print('Playing {}'.format(self.game.title))

    # Sleep-cycle maintenance phase?
    self.exst.clear()
    self.exst.delete_sophistries()


    desperation = 0
    while True:
      self.exst.start_turn()

      # Desperation slowly climbs the longer the game goes on.
      #desperation += 0.01 * (.1 - desperation)

      gs = self.game.state()
      if 'VICTORY' in gs or 'DEAD' in gs:
        if verbosity >= 1:
          print('Game state (turn {}): {}'.format(self.game.turn, gs))
        break

      self.game.set_experience(self.exst)
      self.exst.check_synaptons(100)

      # The odds of just performing a Hail Mary are proportional
      # to the amount of desperation being experienced by the organism.
      cmd = self.exst.choose_command(desperation, self.game.generate_random_command)
      if verbosity >= 1:
        print('{}: => Command: {}'.format(self.game, cmd))
      self.game.command(cmd)

      # The odds of generating new synaptons rise as desperation rises.
      # Organism.__generate_random_emergent_synaptomes(desperation, 0.5, self.exst, gs)

      self.exst.delete_orphaned_dependencies()
      self.check_garden_path()

      
      

  def receive_reinforcement(self, magnitude):
    self.exst.receive_reinforcement(magnitude)


      
  @staticmethod
  def __generate_random_emergent_synaptomes(num_to_generate, prob_add_synapton, exst, gs):
    generated_sms = set()

    # Synaptomes are eligible for being selected as a dependency if they
    # don't have a corresponding command.
    eligible_synaptomes = list(exst.synaptons.values())
    eligible_synaptomes = [sn for sn in eligible_synaptomes if not sn.command]

    # Gamestate atoms are eligible if they are currently active.
    eligible_gamestate_atoms = list(gs)

    if not len(eligible_synaptomes) and not len(eligible_gamestate_atoms):
      # Cannot generate a synapton with no eligible sources!
      return

    while num_to_generate > 0:
      num_to_generate -= 1
      if num_to_generate < 0:
        if random.random() >= num_to_generate + 1:
          break

      synapticles = set()
      randname = 'SYNAPTOME_' + str(int(random.random() * 1000000000))

      while True: 
        # Make a new synapton, possibly with multiple synapticles, per the 
        # synapticle addition decay rate.
        basis = random.choice(list(Synapticle.BASES))
        if basis == 'GAME':
          if not len(eligible_gamestate_atoms):
            continue
          keyname = random.choice(eligible_gamestate_atoms)
          synapticle = Synapticle(basis, keyname)
          synapticles.add(synapticle)
        elif basis == 'CHECKED':
          if not len(eligible_synaptomes):
            continue
          sn = random.choice(eligible_synaptomes)
          synapticle = Synapticle(basis, sn.name, sn.checkstate)
          synapticles.add(synapticle)
        elif basis == 'LAST_ACTION':
          # The logic for this is kinda wonky. Save it for later.
          continue
          if not exst.last_command:
            continue
          synapticle = Synapticle(basis, exst.last_command)
          synapticles.add(synapticle)          
        else:
          # Not supported yet, roll again.
          continue
      
        droll = random.random()
        if droll > prob_add_synapton:
          break

      # If the synapton only has one synapticle, then it's eligible for bearing an action.
      # The probability for bearing an action is the same as that of having another synapticle.
      cmd = None
      if len(synapticles) == 1 and random.random() <= prob_add_synapton:
        cmd = exst.last_command

      sn = Synapton(randname, synapticles, cmd)
      exst.synaptons[sn.name] = sn
      generated_sms.add(sn)
      
    for sn in generated_sms:
      # Freshly generated (or reactivated) synaptons get to start with 
      # the lowest viable level of entrenchment. Better not squander it.
      entch_sms = exst.get_entrenched_synaptomes()
      if not len(entch_sms):
        sn.entrenchment = 1
      else:
        sn.entrenchment = min([sn.entrenchment for sn in entch_sms]) + 1

    return generated_sms
      


