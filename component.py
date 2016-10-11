import libtcodpy as libtcod
import globals

class Fighter:
  def __init__(self, faction, hp, defense, power, sight, poison_resist, state=None, state_inflictor=None, xp_bonus=None, xp=None, level=None, inv_max=None, death_function=None, last_hurt=None, nat_atk_effect=None): # Any component expected to change over gameplay should be added to player_status in next_level() and previous_level()
    self.faction = faction
    self.max_hp = hp
    self.hp = hp
    self.defense = defense
    self.power = power
    self.sight = sight
    self.poison_resist = poison_resist
    if state == None: state = 'normal'
    self.state = state
    self.state_inflictor = state_inflictor
    if xp_bonus == None: xp_bonus = 0
    self.xp_bonus = xp_bonus
    if xp == None: xp = 0
    self.xp = xp
    if level == None: level = 1
    self.level = level
    self.inventory = []
    if inv_max == None: inv_max = 1
    self.inv_max = inv_max
    self.equipment = {'good hand':None, 'off hand':None, 'head':None, 'torso':None, 'feet':None}
    self.death_globals = death_function
    self.last_hurt = last_hurt
    self.nat_atk_effect = nat_atk_effect
  @property
  def secondary_effect(self):
#    if self.equipment is None or (self.equipment['good hand'] is None and self.equipment['off hand'] is None):
    return [self.nat_atk_effect]
#    else:
#      sec_effect = []
#      if self.equipment['good hand'] is not None:
#        sec_effect.append(self.equipment['good hand'].equipment.bonus_effect)
#      if self.equipment['off hand'] is not None:
#        sec_effect.append(self.equipment['off hand'].equipment.bonus_effect)
#      return sec_effect
  def take_damage(self, attacker, damage):
    if damage > 0:
      self.hp -= damage
#      self.last_hurt = turn
      if self.hp <= 0:
        globals = self.death_globals
        if globals is not None:
          globals(self.owner, attacker)
#        if attacker is not None: attacker.fighter.xp += self.xp_bonus
  def attack(self, target):
    damage = self.power - target.fighter.defense
    if damage > 0:
      if target == globals.player():
        globals.message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.', libtcod.sepia)
      elif self.owner == globals.player():
        globals.message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.', libtcod.green)
      target.fighter.take_damage(self.owner, damage)
      if target.fighter is not None:
        effect_list = self.secondary_effect
        if len(effect_list)>0:
          for effect in effect_list:
            if effect is not None:
              effect(self.owner, target)
    else:
      globals.message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no efect!', libtcod.red)
  def heal(self, amount):
    self.hp += amount
    if self.hp > self.max_hp:
      self.hp = self.max_hp
  def check_state(self):
#    if self.state == 'normal' and self.last_hurt is not None and turn - self.last_hurt != 0 and (turn - self.last_hurt) % 10 == 0:
#      self.heal(1)
    if self.state == 'poison':
      if self.owner == globals.player():
        globals.message(self.owner.name.capitalize() + ' looses ' + str(max(int(self.max_hp / 100), 1)) + ' hit points due to poison.', libtcod.red)
      if self.state_inflictor == globals.player():
        globals.message(self.owner.name.capitalize() + ' looses ' + str(max(int(self.max_hp / 100), 1)) + ' hit points due to poison.', libtcod.green)
      self.take_damage(self.state_inflictor, max(int(self.max_hp / 100), 1))
      if libtcod.random_get_int(0, 1, 100) <= self.poison_resist:
        if self.state_inflictor == globals.player():
          globals.message(self.owner.name.capitalize() + ' is no longer poisoned.', libtcod.orange)
        self.state = 'normal'
        self.state_inflictor = None
        if self.owner == globals.player(): 
          globals.message(self.owner.name.capitalize() + ' is no longer poisoned.', libtcod.green)

def player_death(player, attacker):
  if attacker is not None: globals.message('You were killed by ' + attacker.name.capitalize() + '!', libtcod.red)
  else: globals.message('You died of severe battle wounds.', libtcod.red)
  globals.set_game_state('dead')
  globals.player().char = '%'
  globals.player().color = libtcod.dark_red
#  for f in glob.glob('lvl*'):
#    os.remove(f)

def monster_death(monster, attacker):
#  eq = [piece for piece in monster.fighter.equipment.values() if piece is not None]
#  for obj in eq:
#    obj.equipment.dequip(monster)
#  for obj in monster.fighter.inventory:
#    obj.item.drop(monster)
  if attacker is not None: globals.message(monster.name.capitalize() + ' was killed by ' + attacker.name.capitalize() + '!', libtcod.orange)
  else: globals.message(monster.name.capitalize() + ' died of severe battle wounds.', libtcod.orange)
  monster.char = '%'
  monster.color = libtcod.dark_red
  monster.blocks = False
  monster.fighter = None
  monster.ai = None
  monster.name = 'remains of ' + monster.name
  monster.send_to_back()
