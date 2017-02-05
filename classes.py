import libtcodpy as libtcod
import globals
import render
import combat
import math
import combat

class Object: # Player, NPCs, Items... almost anything on the map is an object.
  def __init__(self, x, y, char, name, color, blocks=False, creature=None, ai=None, item=None, spell=None, equipment=None):
    self.x = x
    self.y = y
    self.char = char
    self.name = name
    self.color = color
    self.blocks = blocks
    self.creature = creature
    if self.creature:
      self.creature.owner = self
    self.ai = ai
    if self.ai:
      self.ai.owner = self
    self.item = item
    if self.item:
      self.item.owner = self
    self.spell = spell
    if self.spell:
      self.spell.owner = self
    self.equipment = equipment
    if self.equipment:
      self.equipment.owner = self
      self.item = Item(1, stackable=False)
      self.item.owner = self
  def move(self, dx, dy):
    if not globals.is_blocked(self.x + dx, self.y + dy):
      self.x += dx
      self.y += dy
  def move_towards(self, target_x, target_y):
    dx = target_x - self.x
    dy = target_y - self.y
    distance = math.sqrt(dx ** 2 + dy ** 2)
    dx = int(round(dx / distance))
    dy = int(round(dx / distance))
    self.move(dx, dy)
  def distance_to(self, other):
    dx = other.x - self.x
    dy = other.y - self.y
    return math.sqrt(dx ** 2 + dy ** 2)
  def move_astar(self, target):
    fov = globals.map().make_fov_map()
    for obj in globals.objects():
      if obj.blocks and obj != self and obj != target:
        libtcod.map_set_properties(fov, obj.x, obj.y, True, False)
    my_path = libtcod.path_new_using_map(fov, 1.41)
    libtcod.path_compute(my_path, self.x, self.y, target.x, target.y)
    if not libtcod.path_is_empty(my_path) and libtcod.path_size(my_path) < 25:
      x, y = libtcod.path_walk(my_path, True)
      if x or y:
        self.x = x
        self.y = y
    else:
      self.move_towards(target.x, target.y)
    libtcod.path_delete(my_path)
  def send_to_back(self):
    globals.objects().remove(self)
    globals.objects().insert(0, self)
  def distance(self, x, y):
    return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

class Creature:
  def __init__(self, faction, hp, defense, power, sight, poison_resist, status=None, status_inflictor=None, check_status=True, xp_bonus=None, lvl_base=None, lvl_factor=None, level=None, inv_max=None, death_function=None, last_hurt=None, nat_atk_effect=None): # Any component expected to change over gameplay should be added to player_status in next_level() and previous_level()
    self.faction = faction
    self.base_max_hp = hp
    self.hp = hp
    self.base_defense = defense
    self.base_power = power
    self.base_sight = sight
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
  def max_hp(self):
    bonus = sum(equip.equipment.max_hp_bonus for equip in self.equipment.values() if equip is not None)
    return self.base_max_hp + bonus
  @property
  def defense(self):
    bonus = sum(equip.equipment.defense_bonus for equip in self.equipment.values() if equip is not None)
    return self.base_defense + bonus
  @property
  def power(self):
    bonus = sum(equip.equipment.power_bonus for equip in self.equipment.values() if equip is not None)
    return self.base_power + bonus
  @property
  def sight(self):
    bonus = sum(equip.equipment.sight_bonus for equip in self.equipment.values() if equip is not None)
    return self.base_sight + bonus
  @property
  def secondary_effect(self):
    if self.equipment is None or (self.equipment['good hand'] is None and self.equipment['off hand'] is None):
      return [self.nat_atk_effect]
    else:
      sec_effect = []
      if self.equipment['good hand'] is not None:
        sec_effect.append(self.equipment['good hand'].equipment.bonus_effect)
      if self.equipment['off hand'] is not None:
        sec_effect.append(self.equipment['off hand'].equipment.bonus_effect)
      return sec_effect
  def take_damage(self, attacker, damage):
    if damage > 0:
      self.hp -= damage
      self.last_hurt = globals.turn()
      if self.hp <= 0:
        function = self.death_function
        if function is not None:
          function(self.owner, attacker)
        if attacker.creature: attacker.creature.xp += self.xp_bonus
  def attack(self, target):
    damage = self.power - target.creature.defense
    if damage > 0:
      if target == globals.player():
        render.message(self.owner.name.capitalize() + '(lv' + str(self.level) + ')' + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.', libtcod.sepia)
      elif self.owner == globals.player():
        render.message(self.owner.name.capitalize() + ' attacks ' + target.name + '(lv' + str(target.creature.level) + ')' + ' for ' + str(damage) + ' hit points.', libtcod.green)
      target.creature.take_damage(self.owner, damage)
      if target.creature is not None:
        effect_list = self.secondary_effect
        if len(effect_list)>0:
          for effect in effect_list:
            if effect is not None:
              effect(self.owner, target)
    else:
      render.message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no efect!', libtcod.red)
  def heal(self, amount):
    self.hp += amount
    if self.hp > self.max_hp:
      self.hp = self.max_hp
  def status_check(self):
    combat.check_level_up(self)
    if self.status == 'normal' and self.last_hurt is not None and globals.turn() - self.last_hurt != 0 and (globals.turn() - self.last_hurt) % 10 == 0:
      self.heal(1)
    if self.status == 'poison':
      if self.owner == globals.player():
        render.message(self.owner.name.capitalize() + ' looses ' + str(max(int(self.max_hp / 100), 1)) + ' hit points due to poison.', libtcod.red)
      if self.status_inflictor == globals.player():
        render.message(self.owner.name.capitalize() + ' looses ' + str(max(int(self.max_hp / 100), 1)) + ' hit points due to poison.', libtcod.green)
      self.take_damage(self.status_inflictor, max(int(self.max_hp / 100), 1))
      if libtcod.random_get_int(0, 1, 100) <= self.poison_resist:
        if self.status_inflictor == globals.player():
          render.message(self.owner.name.capitalize() + ' is no longer poisoned.', libtcod.orange)
        self.status = 'normal'
        self.status_inflictor = None
        if self.owner == globals.player(): 
          render.message(self.owner.name.capitalize() + ' is no longer poisoned.', libtcod.green)
    self.check_status = False

class Item:
  def __init__(self, qty, ammo=None, projectile_bonus=None, stackable=True , use_function=None):
    self.qty = qty
    self.ammo = ammo
    self.projectile_bonus = projectile_bonus
    self.stackable = stackable
    self.use_function = use_function
  def pick_up(self, owner):
    if len(owner.creature.inventory) >= owner.creature.inv_max:
      if owner == globals.player(): render.msgbox('Your inventory is full, cannot pick up ' + self.owner.name + '.')
    else:
      if self.stackable:
        has_item = False
        for package in owner.creature.inventory:
          if package.name == self.owner.name:
            has_item = True
            package.item.qty = package.item.qty + self.qty
            globals.objects().remove(self.owner)
            if owner == globals.player(): render.message('You picked up ' + str(self.qty) + ' ' + self.owner.name + ' and now have ' + str(package.item.qty) + '!', libtcod.green)
            break
        if not has_item:
          owner.creature.inventory.append(self.owner)
          globals.objects().remove(self.owner)
          if owner == globals.player(): render.message('You picked up ' + str(self.qty) + ' ' + self.owner.name + '!', libtcod.green)
      else:
        owner.creature.inventory.append(self.owner)
        globals.objects().remove(self.owner)
        if owner == globals.player(): render.message('You picked up ' + str(self.qty) + ' ' + self.owner.name + '!', libtcod.green)
  def use(self, user):
    if self.owner.equipment:
      self.owner.equipment.toggle_equip(user)
      return
    if self.use_function is None:
      if user == globals.player(): render.msgbox('The ' + self.owner.name + ' cannot be used.')
    else:
      if self.use_function(self.owner, user) != 'cancelled':
        if self.qty > 1:
          self.qty =self.qty - 1
        else:
          user.creature.inventory.remove(self.owner)
  def drop(self, owner):
    globals.objects().append(self.owner)
    owner.creature.inventory.remove(self.owner)
    (self.owner.x, self.owner.y) = (owner.x, owner.y)
    if owner == globals.player(): render.message('You dropped ' + str(self.qty) + ' ' + self.owner.name + '.', libtcod.yellow)

class Equipment:
  def __init__(self, slot, ammo=None, power_bonus=0, defense_bonus=0, max_hp_bonus=0, sight_bonus=0, bonus_effect=None):
    self.slot = slot
    self.ammo = ammo
    self.power_bonus = power_bonus
    self.defense_bonus = defense_bonus
    self.max_hp_bonus= max_hp_bonus
    self.sight_bonus = sight_bonus
    self.bonus_effect = bonus_effect
    self.is_equipped = False
  def toggle_equip(self, user):
    if self.is_equipped:
      self.dequip(user)
    else:
      self.equip(user)
  def equip(self, user):
    if self.slot == 'hand':
      if user.creature.equipment['good hand'] is None:
        self.is_equipped = True
        user.creature.equipment['good hand'] = self.owner
        user.creature.inventory.remove(self.owner)
        if user == globals.player(): render.message('Equipped ' + self.owner.name + ' on ' + 'good hand' + '.', libtcod.light_green)
      elif user.creature.equipment['off hand'] is None:
        self.is_equipped = True
        user.creature.equipment['off hand'] = self.owner
        user.creature.inventory.remove(self.owner)
        if user == globals.player(): render.message('Equipped ' + self.owner.name + ' on ' + 'off hand' + '.', libtcod.light_green)
      else:
        hand = render.menu('Equip to which hand?',[('good hand', libtcod.white), ('off hand', libtcod.white)], 22)
        if hand == 0:
          user.creature.equipment['good hand'].equipment.is_equipped = False
          user.creature.inventory.append(user.creature.equipment['good hand'])
          if user == globals.player(): render.message('Dequipped ' + user.creature.equipment['good hand'].name + ' from ' + 'good hand' + '.', libtcod.light_yellow)
          self.is_equipped = True
          user.creature.equipment['good hand'] = self.owner
          user.creature.inventory.remove(self.owner)
          if user == globals.player(): render.message('Equipped ' + self.owner.name + ' on ' + 'good hand' + '.', libtcod.light_green)
        elif hand == 1:
          user.creature.equipment['off hand'].equipment.is_equipped = False
          user.creature.inventory.append(user.creature.equipment['off hand'])
          if user == globals.player(): render.message('Dequipped ' + user.creature.equipment['off hand'].name + ' from ' + 'off hand' + '.', libtcod.light_yellow)
          self.is_equipped = True
          user.creature.equipment['off hand'] = self.owner
          user.creature.inventory.remove(self.owner)
          if user == globals.player(): render.message('Equipped ' + self.owner.name + ' on ' + 'off hand' + '.', libtcod.light_green)
    else:
      if user.creature.equipment[self.slot] is not None: user.creature.equipment[self.slot].equipment.dequip(user)
      self.is_equipped = True
      user.creature.equipment[self.slot] = self.owner
      user.creature.inventory.remove(self.owner)
      if user == globals.player(): render.message('Equipped ' + self.owner.name + ' on ' + self.slot + '.', libtcod.light_green)
  def dequip(self, user):
    if not self.is_equipped: return
    if self.owner == user.creature.equipment['good hand']: user.creature.equipment['good hand'] = None
    elif self.owner == user.creature.equipment['off hand']: user.creature.equipment['off hand'] = None
    else: user.creature.equipment[self.slot] = None
    user.creature.inventory.append(self.owner)
    self.is_equipped = False
    if user == globals.player(): render.message('Dequipped ' + self.owner.name + ' from ' + self.slot + '.', libtcod.light_yellow)