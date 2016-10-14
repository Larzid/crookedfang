import libtcodpy as libtcod
import globals

class Fighter:
  def __init__(self, faction, hp, defense, power, sight, poison_resist, status=None, status_inflictor=None, check_status=True, xp_bonus=None, lvl_base=None, lvl_factor=None, level=None, inv_max=None, death_function=None, last_hurt=None, nat_atk_effect=None): # Any component expected to change over gameplay should be added to player_status in next_level() and previous_level()
    self.faction = faction
    self.max_hp = hp
    self.hp = hp
    self.defense = defense
    self.power = power
    self.sight = sight
    self.poison_resist = poison_resist
    if status == None: status = 'normal'
    self.status = status
    self.status_inflictor = status_inflictor
    self.check_status = check_status
    if xp_bonus == None: xp_bonus = 0
    self.xp_bonus = xp_bonus
    self.xp = 0
    if lvl_base == None: lvl_base = 0
    self.lvl_base = lvl_base
    if lvl_factor == None: lvl_factor = 0
    self.lvl_factor = lvl_factor
    if level == None: level = 1
    self.level = level
    self.inventory = []
    if inv_max == None: inv_max = 1
    self.inv_max = inv_max
    self.equipment = {'good hand':None, 'off hand':None, 'head':None, 'torso':None, 'feet':None}
    self.death_function = death_function
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
      self.last_hurt = globals.turn()
      if self.hp <= 0:
        function = self.death_function
        if function is not None:
          function(self.owner, attacker)
        if attacker.fighter: attacker.fighter.xp += self.xp_bonus
  def attack(self, target):
    damage = self.power - target.fighter.defense
    if damage > 0:
      if target == globals.player():
        globals.message(self.owner.name.capitalize() + '(lv' + str(self.level) + ')' + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.', libtcod.sepia)
      elif self.owner == globals.player():
        globals.message(self.owner.name.capitalize() + ' attacks ' + target.name + '(lv' + str(target.fighter.level) + ')' + ' for ' + str(damage) + ' hit points.', libtcod.green)
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
  def status_check(self):
    check_level_up(self)
    if self.status == 'normal' and self.last_hurt is not None and globals.turn() - self.last_hurt != 0 and (globals.turn() - self.last_hurt) % 10 == 0:
      self.heal(1)
    if self.status == 'poison':
      if self.owner == globals.player():
        globals.message(self.owner.name.capitalize() + ' looses ' + str(max(int(self.max_hp / 100), 1)) + ' hit points due to poison.', libtcod.red)
      if self.status_inflictor == globals.player():
        globals.message(self.owner.name.capitalize() + ' looses ' + str(max(int(self.max_hp / 100), 1)) + ' hit points due to poison.', libtcod.green)
      self.take_damage(self.status_inflictor, max(int(self.max_hp / 100), 1))
      if libtcod.random_get_int(0, 1, 100) <= self.poison_resist:
        if self.status_inflictor == globals.player():
          globals.message(self.owner.name.capitalize() + ' is no longer poisoned.', libtcod.orange)
        self.status = 'normal'
        self.status_inflictor = None
        if self.owner == globals.player(): 
          globals.message(self.owner.name.capitalize() + ' is no longer poisoned.', libtcod.green)
    self.check_status = False

def check_level_up(who):
  level_up_xp = who.lvl_base + who.level * who.lvl_factor
  if who.xp >= level_up_xp and level_up_xp != 0:
    who.level += 1
    who.xp -= level_up_xp
    if who.owner == globals.player():
      globals.message('Your battle skills grow stronger! You reached level ' + str(who.level) + '!', libtcod.yellow)
    who.owner.ai.level_up()

def player_death(player, attacker):
  if attacker is not None: globals.message('You were killed by ' + attacker.name.capitalize() + '!', libtcod.red)
  else: globals.message('You died of severe battle wounds.', libtcod.red)
  player.ai.state = 'dead'
  player.char = '%'
  player.color = libtcod.dark_red
  player.blocks = False
  player.name = 'remains of ' + player.name
  player.send_to_back()
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
