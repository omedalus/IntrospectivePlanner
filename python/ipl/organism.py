
from .experience_state import ExperienceState
from .reflex_action_statement import ReflexActionStatement

from .synapticle import Synapticle
from .synaptome import Synaptome

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

    synaptomes = set()
    synaptomes.add(Synaptome('CAN_GO', Synapticle('INPUT', 'FORWARD')))
    synaptomes.add(Synaptome('GO_GO', Synapticle('CHECKED', 'CAN_GO', True), 'GO'))
    synaptomes.add(Synaptome('SHOULD_TURN_LEFT', Synapticle('CHECKED', 'CAN_GO', False), 'TURN LEFT'))
    synaptomes.add(Synaptome('DUMMY', [
      Synapticle('CHECKED', 'CAN_GO', False),
      Synapticle('CHECKED', 'CAN_GO', True)
    ], 'TURN LEFT'))
    self.seed_synaptomes(synaptomes, 10)
    self.fell_off_garden_path = set()


  def check_garden_path(self):
    for gp in ['CAN_GO', 'GO_GO', 'SHOULD_TURN_LEFT']:
      if gp not in self.exst.synaptomes and gp not in self.fell_off_garden_path:
        print('{} got deleted!'.format(gp))
        self.fell_off_garden_path.add(gp)


  def seed_synaptomes(self, synaptomes, entrenchment):
    for s in synaptomes:
      s.entrenchment = entrenchment
      self.exst.synaptomes[s.name] = s


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
      # Desperation slowly climbs the longer the game goes on.
      #desperation += 0.01 * (.1 - desperation)

      gs = self.game.state()
      if 'VICTORY' in gs or 'DEAD' in gs:
        if verbosity >= 1:
          print('Game state (turn {}): {}'.format(self.game.turn, gs))
        break

      self.game.set_experience(self.exst)
      self.exst.check_synaptomes(100)

      # The odds of just performing a Hail Mary are proportional
      # to the amount of desperation being experienced by the organism.
      cmd = self.exst.choose_command(desperation, self.game.generate_random_command)
      if verbosity >= 1:
        print('{}: => Command: {}'.format(self.game, cmd))
      self.game.command(cmd)

      # The odds of generating new synaptomes rise as desperation rises.
      Organism.__generate_random_emergent_synaptomes(desperation, 0.5, self.exst, gs)


      # Let checkedstates, entrenchments, etc., all decay a bit, as time is passing.
      self.exst.decay(desperation, desperation)
      self.exst.delete_orphaned_dependencies()

      self.check_garden_path()
      
      

  def receive_reinforcement(self, magnitude):
    self.exst.receive_reinforcement(magnitude)


      
  @staticmethod
  def __generate_random_emergent_synaptomes(num_to_generate, prob_add_synapton, exst, gs):
    generated_sms = set()

    # Synaptomes are eligible for being selected as a dependency if they
    # don't have a corresponding command.
    eligible_synaptomes = list(exst.synaptomes.values())
    eligible_synaptomes = [sm for sm in eligible_synaptomes if not sm.command]

    # Gamestate atoms are eligible if they are currently active.
    eligible_gamestate_atoms = list(gs)

    if not len(eligible_synaptomes) and not len(eligible_gamestate_atoms):
      # Cannot generate a synaptome with no eligible sources!
      return

    while num_to_generate > 0:
      num_to_generate -= 1
      if num_to_generate < 0:
        if random.random() >= num_to_generate + 1:
          break

      synaptons = set()
      randname = 'SYNAPTOME_' + str(int(random.random() * 1000000000))

      while True: 
        # Make a new synaptome, possibly with multiple synaptons, per the 
        # synapticle addition decay rate.
        basis = random.choice(list(Synapticle.BASES))
        if basis == 'GAME':
          if not len(eligible_gamestate_atoms):
            continue
          keyname = random.choice(eligible_gamestate_atoms)
          synapticle = Synapticle(basis, keyname)
          synaptons.add(synapticle)
        elif basis == 'CHECKED':
          if not len(eligible_synaptomes):
            continue
          sm = random.choice(eligible_synaptomes)
          synapticle = Synapticle(basis, sm.name, sm.checkstate)
          synaptons.add(synapticle)
        elif basis == 'LAST_ACTION':
          # The logic for this is kinda wonky. Save it for later.
          continue
          if not exst.last_command:
            continue
          synapticle = Synapticle(basis, exst.last_command)
          synaptons.add(synapticle)          
        else:
          # Not supported yet, roll again.
          continue
      
        droll = random.random()
        if droll > prob_add_synapton:
          break

      # If the synaptome only has one synapticle, then it's eligible for bearing an action.
      # The probability for bearing an action is the same as that of having another synapticle.
      cmd = None
      if len(synaptons) == 1 and random.random() <= prob_add_synapton:
        cmd = exst.last_command

      sm = Synaptome(randname, synaptons, cmd)
      exst.synaptomes[sm.name] = sm
      generated_sms.add(sm)
      
    for sm in generated_sms:
      # Freshly generated (or reactivated) synaptomes get to start with 
      # the lowest viable level of entrenchment. Better not squander it.
      entch_sms = exst.get_entrenched_synaptomes()
      if not len(entch_sms):
        sm.entrenchment = 1
      else:
        sm.entrenchment = min([sm.entrenchment for sm in entch_sms]) + 1

    return generated_sms
      


