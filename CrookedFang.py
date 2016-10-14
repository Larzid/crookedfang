# V-0.0.1

# Custom side panel for stats & message panel at the bottom
# Added sight element to fighter class for FOV calculations in all fighter objects
# Improved AI clasess
# Stacking items
# Keyboard look comand
# Inventory implemented as component of fighter class (monster inventory)
# Colored menus
# Keyboard target area function
# Keyboard target monster function
# Persistent dungeon levels with Monster and Item respawning when reentering if needed
# Fighter class is aware of who is attacking to propperly assign EXP
# Equipment menu
# Equipment implemented in Fighter Class (Monsters can use equipment)
# Dual weilding (Even combinations of Ranged and Melee weapons) (Ranged weapons will only fire if weilded in the 'good hand')
# Town map generator with BSP houses (Town level is empty right now)
# Ranged weapons (1) and some (1) throwable items
# Projectile path (will not fire ranged weapon or throw item if the path is obstucted)
# handle_keys() function can take control any NPC trough the Possessed_Monster AI class
# Heal over time (everybody)
# fighter.state implemented to deal with status ailments
# turn counter
# Melee attacks can inflict aditional effects
# Creatures may inflict secondary effect when attacking un-armed with creature.fighter.nat_atk_effect
# Melee weapons may grant secondary effect with weapon.equipment.bonus_effect
# Wielding a weapon disables nat_atk_effect wether or not the weapon grants bonus_effect

# KNOWN BUGS
# (FIXED) fireball damage re applies when result in monster death

import libtcodpy as libtcod
import math
import textwrap
import shelve
import glob
import os
import random
import time

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 60
LIMIT_FPS = 15
MAP_WIDTH = 65
MAP_HEIGHT = 53
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
FOV_ALGO = 0
FOV_LIGHT_WALLS = True
BAR_WIDTH = 13
MSG_WIDTH = SCREEN_WIDTH - 2
MSG_HEIGHT = SCREEN_HEIGHT - MAP_HEIGHT - 1
INVENTORY_WIDTH = 50
LEVEL_UP_BASE = 200
LEVEL_UP_FACTOR = 150

MAX_ALLIES = 4

DEPTH = 3
MIN_SIZE = 3
FULL_ROOMS = True

########
#CLASES#
########

class Tile:
  def __init__(self, blocked, block_sight=None, tile_face=None, back_light=None, back_dark=None, fore_light=None, fore_dark=None):
    self.explored = False
    self.blocked = blocked
    if block_sight is None: block_sight = blocked
    self.block_sight = block_sight
    self.tile_face = tile_face
    self.back_light = back_light
    self.back_dark = back_dark
    self.fore_light = fore_light
    self.fore_dark = fore_dark

class Object:
  def __init__(self, x, y, char, name, color, blocks=False, always_visible=False, fighter=None, ai=None, sight=None, item=None, spell=None, equipment=None, gen=None):
    self.x = x
    self.y = y
    self.char = char
    self.name = name
    self.color = color
    self.blocks = blocks
    self.always_visible = always_visible
    self.fighter = fighter
    if self.fighter:
      self.fighter.owner = self
    self.ai = ai
    if self.ai:
      self.ai.owner = self
    self.sight = sight
    if self.sight:
      self.sight.owner = self
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
    self.gen = gen
  def move(self, dx, dy):
    if self.x + dx >= 0 and self.x + dx <= MAP_WIDTH - 1 and self.y + dy >= 0 and self.y + dy <= MAP_HEIGHT - 1 and not is_blocked(self.x + dx, self.y + dy):
      self.x += dx
      self.y += dy
  def draw(self):
    libtcod.map_compute_fov(fov_map, player.x, player.y, player.fighter.sight, FOV_LIGHT_WALLS, FOV_ALGO)
    if libtcod.map_is_in_fov(fov_map, self.x, self.y) or (self.always_visible and map[self.x][self.y].explored):
      if libtcod.map_is_in_fov(fov_map, self.x, self.y):
        libtcod.console_set_default_foreground(con, self.color)
      else:
        libtcod.console_set_default_foreground(con, libtcod.dark_sepia)
      libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)
    for pov in allies:
      libtcod.map_compute_fov(fov_map, pov.x, pov.y, pov.fighter.sight, FOV_LIGHT_WALLS, FOV_ALGO)
      if libtcod.map_is_in_fov(fov_map, self.x, self.y) or (self.always_visible and map[self.x][self.y].explored):
        if libtcod.map_is_in_fov(fov_map, self.x, self.y):
          libtcod.console_set_default_foreground(con, self.color)
        else:
          libtcod.console_set_default_foreground(con, libtcod.darkest_sepia)
        libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)
  def clear(self):
    if libtcod.map_is_in_fov(fov_map, self.x, self.y):
      libtcod.console_set_default_foreground(con, libtcod.black)
    else:
      libtcod.console_set_default_foreground(con, libtcod.darkest_sepia)
    if map[self.x][self.y].explored:
      libtcod.console_put_char(con, self.x, self.y, chr(172), libtcod.BKGND_NONE)
    else:
      libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)
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
    fov = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
    for y1 in range(MAP_HEIGHT):
      for x1 in range(MAP_WIDTH):
        libtcod.map_set_properties(fov, x1, y1, not map[x1][y1].block_sight, not map[x1][y1].blocked)
    for obj in objects:
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
    global objects
    objects.remove(self)
    objects.insert(0, self)
  def distance(self, x, y):
    return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

class Rect:
  def __init__(self, x, y, w, h):
    self.x1 = x
    self.y1 = y
    self.x2 = x + w
    self.y2 = y + h
  def center(self):
    center_x = (self.x1 + self.x2)/2
    center_y = (self.y1 + self.y2)/2
    return (center_x, center_y)
  def intersect(self, other):
    return (self.x1 <= other.x2 and self.x2 >= other.x1 and
            self.y1 <= other.y2 and self.y2 >= other.y1)
  def intersect_loose(self, other):
    return (self.x1 <= other.x2+1 and self.x2 >= other.x1-1 and
            self.y1 <= other.y2+1 and self.y2 >= other.y1-1)

###################
#COMPONENT CLASSES#
###################

class Fighter:
  def __init__(self, hp, defense, power, sight, poison_resist, state=None, state_inflictor=None, xp_bonus=0, xp=0, level=1, inv_max=None, death_function=None, last_hurt=None, nat_atk_effect=None): # Any component expected to change over gameplay should be added to player_status in next_level() and previous_level()
    self.base_max_hp = hp
    self.hp = hp
    self.base_defense = defense
    self.base_power = power
    self.base_sight = sight
    self.poison_resist = poison_resist
    self.state = state
    self.state_inflictor = state_inflictor
    self.xp_bonus = xp_bonus
    self.xp = xp
    self.level = level
    if inv_max != None
      self.inventory = []
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
      self.last_hurt = turn
      if self.hp <= 0:
        function = self.death_function
        if function is not None:
          function(self.owner, attacker)
        if attacker is not None: attacker.fighter.xp += self.xp_bonus
  def attack(self, target):
    damage = self.power - target.fighter.defense
    if damage > 0:
      if target == player or allies.count(target) > 0:
        message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.', libtcod.sepia)
      else:
        message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.', libtcod.green)
      target.fighter.take_damage(self.owner, damage)
      if target.fighter is not None:
        effect_list = self.secondary_effect
        if len(effect_list)>0:
          for effect in effect_list:
            if effect is not None:
              effect(self.owner, target)
    else:
      message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no efect!', libtcod.red)
  def heal(self, amount):
    self.hp += amount
    if self.hp > self.max_hp:
      self.hp = self.max_hp
  def check_state(self):
    if self.state is None and self.last_hurt is not None and turn - self.last_hurt != 0 and (turn - self.last_hurt) % 10 == 0:
      self.heal(1)
    if self.state == 'poison':
      self.take_damage(self.state_inflictor, max(int(self.max_hp / 100), 1))
      if self.owner == player or allies.count(self.owner) > 0: message(self.owner.name.capitalize() + ' looses ' + str(max(int(self.max_hp / 100), 1)) + ' hit points due to poison.', libtcod.red)
      if self.state_inflictor == player or allies.count(self.state_inflictor) > 0: message(self.owner.name.capitalize() + ' looses ' + str(max(int(self.max_hp / 100), 1)) + ' hit points due to poison.', libtcod.green)
      if libtcod.random_get_int(0, 1, 100) <= self.poison_resist:
        if self.state_inflictor == player or allies.count(self.state_inflictor) > 0: message(self.owner.name.capitalize() + ' is no longer poisoned.', libtcod.orange)
        self.state = 'normal'
        self.state_inflictor = None
        if self.owner == player or allies.count(self.owner) > 0: message(self.owner.name.capitalize() + ' is no longer poisoned.', libtcod.green)

class Item:
  def __init__(self, qty, ammo=None, projectile_bonus=None, stackable=True , use_function=None):
    self.qty = qty
    self.ammo = ammo
    self.projectile_bonus = projectile_bonus
    self.stackable = stackable
    self.use_function = use_function
  def pick_up(self, owner):
    if len(owner.fighter.inventory) >= owner.fighter.inv_max:
      if owner == player or allies.count(owner) > 0: msgbox('Your inventory is full, cannot pick up ' + self.owner.name + '.')
    else:
      if self.stackable:
        has_item = False
        for package in owner.fighter.inventory:
          if package.name == self.owner.name:
            has_item = True
            package.item.qty = package.item.qty + self.qty
            objects.remove(self.owner)
            if owner == player or allies.count(owner) > 0: message('You picked up ' + str(self.qty) + ' ' + self.owner.name + ' and now have ' + str(package.item.qty) + '!', libtcod.green)
            break
        if not has_item:
          owner.fighter.inventory.append(self.owner)
          objects.remove(self.owner)
          if owner == player or allies.count(owner) > 0: message('You picked up ' + str(self.qty) + ' ' + self.owner.name + '!', libtcod.green)
      else:
        owner.fighter.inventory.append(self.owner)
        objects.remove(self.owner)
        if owner == player or allies.count(owner) > 0: message('You picked up ' + str(self.qty) + ' ' + self.owner.name + '!', libtcod.green)
  def use(self, user):
    if self.owner.equipment:
      self.owner.equipment.toggle_equip(user)
      return
    if self.use_function is None:
      if user == player or allies.count(user) > 0: msgbox('The ' + self.owner.name + ' cannot be used.')
    else:
      if self.use_function(self.owner, user) != 'cancelled':
        if self.qty > 1:
          self.qty =self.qty - 1
        else:
          user.fighter.inventory.remove(self.owner)
  def drop(self, owner):
    objects.append(self.owner)
    owner.fighter.inventory.remove(self.owner)
    (self.owner.x, self.owner.y) = (owner.x, owner.y)
    if owner == player or allies.count(owner) > 0: message('You dropped ' + str(self.qty) + ' ' + self.owner.name + '.', libtcod.yellow)

class Spell:
  def __init__(self, power=None, spell_range=None, effect=None):
    self.power = power
    self.spell_range = spell_range
    self.effect = effect

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
      if user.fighter.equipment['good hand'] is None:
        self.is_equipped = True
        user.fighter.equipment['good hand'] = self.owner
        user.fighter.inventory.remove(self.owner)
        if user == player or allies.count(user) > 0: message('Equipped ' + self.owner.name + ' on ' + 'good hand' + '.', libtcod.light_green)
      elif user.fighter.equipment['off hand'] is None:
        self.is_equipped = True
        user.fighter.equipment['off hand'] = self.owner
        user.fighter.inventory.remove(self.owner)
        if user == player or allies.count(user) > 0: message('Equipped ' + self.owner.name + ' on ' + 'off hand' + '.', libtcod.light_green)
      else:
        hand = menu('Equip to which hand?',[('good hand', libtcod.white), ('off hand', libtcod.white)], 22)
        if hand == 0:
          user.fighter.equipment['good hand'].equipment.is_equipped = False
          user.fighter.inventory.append(user.fighter.equipment['good hand'])
          if user == player or allies.count(user) > 0: message('Dequipped ' + user.fighter.equipment['good hand'].name + ' from ' + 'good hand' + '.', libtcod.light_yellow)
          self.is_equipped = True
          user.fighter.equipment['good hand'] = self.owner
          user.fighter.inventory.remove(self.owner)
          if user == player or allies.count(user) > 0: message('Equipped ' + self.owner.name + ' on ' + 'good hand' + '.', libtcod.light_green)
        elif hand == 1:
          user.fighter.equipment['off hand'].equipment.is_equipped = False
          user.fighter.inventory.append(user.fighter.equipment['off hand'])
          if user == player or allies.count(user) > 0: message('Dequipped ' + user.fighter.equipment['off hand'].name + ' from ' + 'off hand' + '.', libtcod.light_yellow)
          self.is_equipped = True
          user.fighter.equipment['off hand'] = self.owner
          user.fighter.inventory.remove(self.owner)
          if user == player or allies.count(user) > 0: message('Equipped ' + self.owner.name + ' on ' + 'off hand' + '.', libtcod.light_green)
    else:
      if user.fighter.equipment[self.slot] is not None: user.fighter.equipment[self.slot].equipment.dequip(user)
      self.is_equipped = True
      user.fighter.equipment[self.slot] = self.owner
      user.fighter.inventory.remove(self.owner)
      if user == player or allies.count(user) > 0: message('Equipped ' + self.owner.name + ' on ' + self.slot + '.', libtcod.light_green)
  def dequip(self, user):
    if not self.is_equipped: return
    if self.owner == user.fighter.equipment['good hand']: user.fighter.equipment['good hand'] = None
    elif self.owner == user.fighter.equipment['off hand']: user.fighter.equipment['off hand'] = None
    else: user.fighter.equipment[self.slot] = None
    user.fighter.inventory.append(self.owner)
    self.is_equipped = False
    if user == player or allies.count(user) > 0: message('Dequipped ' + self.owner.name + ' from ' + self.slot + '.', libtcod.light_yellow)

##############
#A.I. CLASSES#
##############

class BasicMonster:
  def take_turn(self):
    monster = self.owner
    fov_recompute = True
    libtcod.map_compute_fov(fov_map, monster.x, monster.y, monster.fighter.sight, FOV_LIGHT_WALLS, FOV_ALGO)
    if libtcod.map_is_in_fov(fov_map, player.x, player.y):
      if monster.distance_to(player) >= 2:
        monster.move_astar(player)
      elif player.fighter.hp > 0:
        monster.fighter.attack(player)
    else:
      movement = False
      for ally in allies:
        if libtcod.map_is_in_fov(fov_map, ally.x, ally.y):
          if monster.distance_to(ally) >= 2:
            monster.move_astar(ally)
            movement = True
          elif ally.fighter.hp > 0:
            monster.fighter.attack(ally)
            movement = True
      while movement is False:
        (x, y) = (libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1))
        if not is_blocked(monster.x + x, monster.y + y):
          movement = True
          monster.move(x, y)

class BitingMonster:
  def take_turn(self):
    monster = self.owner
    fov_recompute = True
    libtcod.map_compute_fov(fov_map, monster.x, monster.y, monster.fighter.sight, FOV_LIGHT_WALLS, FOV_ALGO)
    if libtcod.map_is_in_fov(fov_map, player.x, player.y):
      if monster.distance_to(player) >= 2:
        monster.move_astar(player)
      elif player.fighter.hp > 0:
        monster.fighter.attack(player, secondary_effect=inflict_poison)
    else:
      movement = False
      for ally in allies:
        if libtcod.map_is_in_fov(fov_map, ally.x, ally.y):
          if monster.distance_to(ally) >= 2:
            monster.move_astar(ally)
            movement = True
          elif ally.fighter.hp > 0:
            monster.fighter.attack(ally)
            movement = True
      while movement is False:
        (x, y) = (libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1))
        if not is_blocked(monster.x + x, monster.y + y):
          movement = True
          monster.move(x, y)

class EquippingMonster:
  def take_turn(self):
    monster = self.owner
    fov_recompute = True
    libtcod.map_compute_fov(fov_map, monster.x, monster.y, monster.fighter.sight, FOV_LIGHT_WALLS, FOV_ALGO)
    if libtcod.map_is_in_fov(fov_map, player.x, player.y):
      if monster.fighter.equipment['good hand'] is not None and monster.fighter.equipment['good hand'].equipment.ammo:
        projectile = [proj for proj in monster.fighter.inventory if monster.fighter.equipment['good hand'].equipment.ammo == proj.item.ammo]
      if monster.fighter.equipment['good hand'] is not None and monster.fighter.equipment['good hand'].equipment.ammo and len(projectile) > 0:
        if not projectile_attack(monster, projectile[0], player) == 'cancelled':
          if projectile[0].item.qty > 1:
            projectile[0].item.qty -= 1
          else:
            actor.fighter.inventory.remove(projectile[0])
      elif monster.distance_to(player) >= 2:
        monster.move_astar(player)
      elif player.fighter.hp > 0:
        monster.fighter.attack(player)
    else:
      movement = False
      for ally in allies:
        if libtcod.map_is_in_fov(fov_map, ally.x, ally.y):
          if monster.fighter.equipment['good hand'] is not None and monster.fighter.equipment['good hand'].equipment.ammo:
            projectile = [proj for proj in monster.fighter.inventory if monster.fighter.equipment['good hand'].equipment.ammo == proj.item.ammo]
          if monster.fighter.equipment['good hand'] is not None and monster.fighter.equipment['good hand'].equipment.ammo and len(projectile) > 0:
            if not projectile_attack(monster, projectile[0], ally) == 'cancelled':
              if projectile[0].item.qty > 1:
                projectile[0].item.qty -= 1
              else:
                actor.fighter.inventory.remove(projectile[0])
              movement = True
          elif monster.distance_to(ally) >= 2:
            monster.move_astar(ally)
            movement = True
          elif ally.fighter.hp > 0:
            monster.fighter.attack(ally)
            movement = True
      if movement == False:
        items = [item for item in objects if item.equipment and libtcod.map_is_in_fov(fov_map, item.x, item.y)]
        for obj in items:
          if obj.equipment.slot == 'hand':
            if monster.fighter.equipment['good hand'] is None:
              obj.item.pick_up(monster)
              obj.item.use(monster)
              if obj.equipment.ammo and obj.equipment.ammo == 'arrow':
                item_component = Item(15, ammo='arrow', projectile_bonus = 1)
                item = Object(0, 0, chr(147), 'arrow', libtcod.dark_gray, item=item_component)
                monster.fighter.inventory.append(item)
          elif monster.fighter.equipment[obj.equipment.slot] is None:
            obj.item.pick_up(monster)
            obj.item.use(monster)
          elif monster.fighter.equipment['good hand'] is not None and monster.fighter.equipment['good hand'].equipment.ammo and monster.fighter.equipment['good hand'].equipment4.ammo == obj.item.ammo:
            obj.item.pick_up(monster)
        while movement is False:
          (x, y) = (libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1))
          if not is_blocked(monster.x + x, monster.y + y):
            movement = True
            monster.move(x, y)

class ConfusedMonster:
  def __init__(self, old_ai, num_turns):
    self.old_ai = old_ai
    self.num_turns = num_turns
  def take_turn(self):
    if self.num_turns > 0:
      self.owner.move(libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1))
      self.num_turns -= 1
    else:
      self.owner.ai = self.old_ai
      message('The ' + self.owner.name + ' is no longer confused!', libtcod.red)

class PossessedMonster:
  def __init__(self, old_ai, old_color, old_char, old_death, num_turns):
    self.old_ai = old_ai
    self.num_turns = num_turns
    self.old_color = old_color
    self.old_char = old_char
    self.old_death = old_death
    self.check_state = True
  def take_turn(self):
    if self.num_turns > 0:
      action = 'didnt-take-turn'
      while action == 'didnt-take-turn':
        fov_recompute = True
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)
        libtcod.console_flush()
        check_level_up(self.owner)
        if self.check_state == True:
          self.owner.fighter.check_state()
          self.check_state = False
        for object in objects:
          object.clear()
        render_all(self.owner)
        libtcod.map_compute_fov(fov_map, self.owner.x, self.owner.y, self.owner.fighter.sight, FOV_LIGHT_WALLS, FOV_ALGO)
        action = handle_keys(self.owner)
      self.check_state = True
#      self.num_turns -= 1
#    else:
#      self.owner.ai = self.old_ai
#      message('The ' + self.owner.name + ' is no longer possessed!', libtcod.red)


#################################
#DUNGEON GENERATION & POPULATION#
#################################

def make_map():
  global map, objects, stairs_down, stairs_up, rooms
  objects = [player]
  map = [[ Tile(blocked=True, tile_face=chr(173), back_light=libtcod.black, back_dark=libtcod.black, fore_light=libtcod.white, fore_dark=libtcod.dark_gray) for y in range(MAP_HEIGHT) ] for x in range(MAP_WIDTH) ]
  rooms = []
  num_rooms = 0
  for r in range(MAX_ROOMS):
    w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
    h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
    x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
    y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)
    new_room = Rect(x, y, w, h)
    failed = False
    for other_room in rooms:
      if new_room.intersect(other_room):
        failed = True
        break
    if not failed:
      create_room(new_room)
      (new_x, new_y) = new_room.center()
      if num_rooms == 0:
        player.x = new_x
        player.y = new_y
        stairs_up = Object(new_x, new_y, chr(175), 'some stairs going up', libtcod.sepia, always_visible=True)
        if len(allies) > 0: (allies[0].x, allies[0].y) = (new_x -1, new_y -1)
        if len(allies) > 1: (allies[1].x, allies[1].y) = (new_x +1, new_y -1)
        if len(allies) > 2: (allies[2].x, allies[2].y) = (new_x +1, new_y +1)
        if len(allies) > 3: (allies[3].x, allies[3].y) = (new_x -1, new_y +1)
      else:
        (prev_x, prev_y) = rooms[num_rooms-1].center()
        if libtcod.random_get_int(0, 0, 1) == 1:
          create_h_tunnel(prev_x, new_x, prev_y)
          create_v_tunnel(prev_y, new_y, new_x)
        else:
          create_v_tunnel(prev_y, new_y, prev_x)
          create_h_tunnel(prev_x, new_x, new_y)
      place_objects(new_room)
      rooms.append(new_room)
      num_rooms += 1
  stairs_down = Object(new_x, new_y, chr(174), 'some stairs going down', libtcod.sepia, always_visible=True)
  objects.append(stairs_down)
  stairs_down.send_to_back()
  objects.append(stairs_up)
  stairs_up.send_to_back()

def create_room(room):
  global map
  for x in range(room.x1 + 1, room.x2):
    for y in range(room.y1 + 1, room.y2):
      map[x][y].blocked = False
      map[x][y].block_sight = False
      map[x][y].tile_face = chr(172)
      map[x][y].back_light=libtcod.darker_sepia
      map[x][y].back_dark=libtcod.darkest_sepia
      map[x][y].fore_light=libtcod.black
      map[x][y].fore_dark=libtcod.darkest_sepia

def create_h_tunnel(x1, x2, y):
  global map
  for x in range(min(x1, x2), max(x1, x2) +1):
    map[x][y].blocked = False
    map[x][y].block_sight = False
    map[x][y].tile_face = chr(172)
    map[x][y].back_light=libtcod.darker_sepia
    map[x][y].back_dark=libtcod.darkest_sepia
    map[x][y].fore_light=libtcod.black
    map[x][y].fore_dark=libtcod.darkest_sepia

def create_v_tunnel(y1, y2, x):
  global map
  for y in range(min(y1, y2), max(y1, y2) +1):
    map[x][y].blocked = False
    map[x][y].block_sight = False
    map[x][y].tile_face = chr(172)
    map[x][y].back_light=libtcod.darker_sepia
    map[x][y].back_dark=libtcod.darkest_sepia
    map[x][y].fore_light=libtcod.black
    map[x][y].fore_dark=libtcod.darkest_sepia

def make_world():
  global map, objects, rooms, num_rooms
  objects = [player]
  (player.x, player.y) = (1, 1)
  map = [[ Tile(blocked=False, block_sight=False, tile_face=chr(250), back_light=libtcod.darker_green, back_dark=libtcod.darkest_green, fore_light=libtcod.dark_green, fore_dark=libtcod.darkest_green) for y in range(MAP_HEIGHT) ] for x in range(MAP_WIDTH) ]
  rooms = []
  for r in range(20):
    new_town = Object(libtcod.random_get_int(0, 2, MAP_WIDTH - 2), libtcod.random_get_int(0, 2, MAP_HEIGHT - 2), '0', 'town # ' + str(r), libtcod.sepia, always_visible=True)
    failed = False
    for other_town in rooms:
      if new_town.distance_to(other_town) < 5:
        failed = True
        break
    if not failed:
      rooms.append(new_town)
  objects = objects + rooms

def pick_char():
  pick = libtcod.random_get_int(0, 1, 100)
  if pick <= 16: return '`'
  elif pick <= 32: return "'"
  elif pick <= 48: return ','
  elif pick <= 64: return ';'
  elif pick <= 80: return ':'
  else: return '.'

def make_town():
  global map, objects, stairs_down, rooms, num_rooms
  objects = [player]
  (player.x, player.y) = (1, 1)
  map = [[ Tile(blocked=False, block_sight=False, tile_face=chr(250), back_light=libtcod.darker_green, back_dark=libtcod.darkest_green, fore_light=libtcod.dark_green, fore_dark=libtcod.darkest_green) for y in range(MAP_HEIGHT) ] for x in range(MAP_WIDTH) ]
  rooms = []
  num_rooms = 0
  for r in range(15):
    w = libtcod.random_get_int(0, 8, 12)
    h = libtcod.random_get_int(0, 8, 12)
    x = libtcod.random_get_int(0, 2, MAP_WIDTH - w - 2)
    y = libtcod.random_get_int(0, 2, MAP_HEIGHT - h - 2)
    new_room = Rect(x, y, w, h)
    failed = False
    for other_room in rooms:
      if new_room.intersect_loose(other_room):
        failed = True
        break
    if not failed:
      make_bsp(new_room, 3)
      (new_x, new_y) = new_room.center()
      door = False
      while door == False:
        if libtcod.random_get_int(0, 0, 1)==0:
          door_pos = libtcod.random_get_int(0, new_room.x1 + 1, new_room.x2 - 1)
          if libtcod.random_get_int(0, 0, 1)==0:
            if not is_blocked(door_pos, new_room.y2 - 1):
              map[door_pos][new_room.y2] = Tile(blocked=False, block_sight=False, tile_face=chr(172), back_light=libtcod.darker_sepia, back_dark=libtcod.darkest_sepia, fore_light=libtcod.black, fore_dark=libtcod.darkest_sepia)
              door = True
          else:
            if not is_blocked(door_pos, new_room.y1 + 1):
              map[door_pos][new_room.y1] = Tile(blocked=False, block_sight=False, tile_face=chr(172), back_light=libtcod.darker_sepia, back_dark=libtcod.darkest_sepia, fore_light=libtcod.black, fore_dark=libtcod.darkest_sepia)
              door = True
        else:
          door_pos = libtcod.random_get_int(0, new_room.y1 + 1, new_room.y2 - 1)
          if libtcod.random_get_int(0, 0, 1)==0:
            if not is_blocked(new_room.x2 - 1, door_pos):
              map[new_room.x2][door_pos] = Tile(blocked=False, block_sight=False, tile_face=chr(172), back_light=libtcod.darker_sepia, back_dark=libtcod.darkest_sepia, fore_light=libtcod.black, fore_dark=libtcod.darkest_sepia)
              door = True
          else:
            if not is_blocked(new_room.x1 + 1, door_pos):
              map[new_room.x1][door_pos] = Tile(blocked=False, block_sight=False, tile_face=chr(172), back_light=libtcod.darker_sepia, back_dark=libtcod.darkest_sepia, fore_light=libtcod.black, fore_dark=libtcod.darkest_sepia)
              door = True
      rooms.append(new_room)
      num_rooms += 1

def make_bsp(room, depth):
  global map, objects, stairs_down, bsp_rooms
  objects = [player]
  for y in range(room.y1, room.y2 + 1):
    for x in range(room.x1, room.x2 + 1):
      map[x][y] = Tile(blocked=True, block_sight=True, tile_face=chr(173), back_light=libtcod.white, back_dark=libtcod.gray, fore_light=libtcod.dark_red, fore_dark=libtcod.darker_red)
  bsp_rooms = []
  bsp = libtcod.bsp_new_with_size(room.x1, room.y1, room.x2 - room.x1, room.y2 - room.y1)
  libtcod.bsp_split_recursive(bsp, 0, depth, MIN_SIZE + 1, MIN_SIZE + 1, 1.5, 1.5)
  libtcod.bsp_traverse_inverted_level_order(bsp, traverse_node)
#  if num_rooms == 0:
  stairs_down_location = random.choice(bsp_rooms)
  bsp_rooms.remove(stairs_down_location)
  stairs_down = Object(stairs_down_location[0], stairs_down_location[1], chr(174), 'some stairs going down', libtcod.sepia, always_visible=True)
  objects.append(stairs_down)
  stairs_down.send_to_back()
  for room in bsp_rooms:
    new_room = Rect(room[0], room[1], 2, 2)

def traverse_node(node, dat):
  global map, bsp_rooms
  if libtcod.bsp_is_leaf(node):
    minx = node.x + 1
    maxx = node.x + node.w - 1
    miny = node.y + 1
    maxy = node.y + node.h - 1
    if maxx == MAP_WIDTH - 1: maxx -= 1
    if maxy == MAP_HEIGHT - 1: maxy -= 1
    if FULL_ROOMS == False:
      minx = libtcod.random_get_int(None, minx, maxx - MIN_SIZE + 1)
      miny = libtcod.random_get_int(None, miny, maxy - MIN_SIZE + 1)
      maxx = libtcod.random_get_int(None, minx + MIN_SIZE - 2, maxx)
      maxy = libtcod.random_get_int(None, miny + MIN_SIZE - 2, maxy)
    node.x = minx
    node.y = miny
    node.w = maxx-minx + 1
    node.h = maxy-miny + 1
    for x in range(minx, maxx +1):
      for y in range(miny, maxy + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False
        map[x][y].tile_face = chr(172)
        map[x][y].back_light=libtcod.darker_sepia
        map[x][y].back_dark=libtcod.darkest_sepia
        map[x][y].fore_light=libtcod.black
        map[x][y].fore_dark=libtcod.darkest_sepia

    bsp_rooms.append(((minx + maxx) / 2, (miny + maxy) / 2))
  else:
    left = libtcod.bsp_left(node)
    right = libtcod.bsp_right(node)
    node.x = min(left.x, right.x)
    node.y = min(left.y, right.y)
    node.w = max(left.x + left.w, right.x + right.w) - node.x
    node.h = max(left.y + left.h, right.y + right.h) - node.y
    if node.horizontal:
      if left.x + left.w - 1 < right.x or right.x + right.w - 1 < left.x:
        x1 = libtcod.random_get_int(None, left.x, left.x + left.w - 1)
        x2 = libtcod.random_get_int(None, right.x, right.x + right.w - 1)
        y = libtcod.random_get_int(None, left.y + left.h, right.y)
        vline_up(map, x1, y - 1)
        hline(map, x1, y, x2)
        vline_down(map, x2, y + 1)
      else:
        minx = max(left.x, right.x)
        maxx = min(left.x + left.w - 1, right.x + right.w - 1)
        x = libtcod.random_get_int(None, minx, maxx)
        vline_down(map, x, right.y)
        vline_up(map, x, right.y - 1)
    else:
      if left.y + left.h - 1 < right.y or right.y + right.h - 1 < left.y:
        y1 = libtcod.random_get_int(None, left.y, left.y + left.h - 1)
        y2 = libtcod.random_get_int(None, right.y, right.y + right.h - 1)
        x = libtcod.random_get_int(None, left.x + left.w, right.x)
        hline_left(map, x - 1, y1)
        vline(map, x, y1, y2)
        hline_right(map, x + 1, y2)
      else:
        miny = max(left.y, right.y)
        maxy = min(left.y + left.h - 1, right.y + right.h - 1)
        y = libtcod.random_get_int(None, miny, maxy)
        hline_left(map, right.x - 1, y)
        hline_right(map, right.x, y)

def vline(map, x, y1, y2):
  if y1 > y2:
    y1,y2 = y2,y1
  for y in range(y1,y2+1):
    map[x][y].blocked = False
    map[x][y].block_sight = False
    map[x][y].tile_face = chr(172)
    map[x][y].back_light=libtcod.darker_sepia
    map[x][y].back_dark=libtcod.darkest_sepia
    map[x][y].fore_light=libtcod.black
    map[x][y].fore_dark=libtcod.darkest_sepia
 
def vline_up(map, x, y):
  while y >= 0 and map[x][y].blocked == True:
    map[x][y].blocked = False
    map[x][y].block_sight = False
    map[x][y].tile_face = chr(172)
    map[x][y].back_light=libtcod.darker_sepia
    map[x][y].back_dark=libtcod.darkest_sepia
    map[x][y].fore_light=libtcod.black
    map[x][y].fore_dark=libtcod.darkest_sepia
    y -= 1
 
def vline_down(map, x, y):
  while y < MAP_HEIGHT and map[x][y].blocked == True:
    map[x][y].blocked = False
    map[x][y].block_sight = False
    map[x][y].tile_face = chr(172)
    map[x][y].back_light=libtcod.darker_sepia
    map[x][y].back_dark=libtcod.darkest_sepia
    map[x][y].fore_light=libtcod.black
    map[x][y].fore_dark=libtcod.darkest_sepia
    y += 1
 
def hline(map, x1, y, x2):
  if x1 > x2:
    x1,x2 = x2,x1
  for x in range(x1,x2+1):
    map[x][y].blocked = False
    map[x][y].block_sight = False
    map[x][y].tile_face = chr(172)
    map[x][y].back_light=libtcod.darker_sepia
    map[x][y].back_dark=libtcod.darkest_sepia
    map[x][y].fore_light=libtcod.black
    map[x][y].fore_dark=libtcod.darkest_sepia
 
def hline_left(map, x, y):
  while x >= 0 and map[x][y].blocked == True:
    map[x][y].blocked = False
    map[x][y].block_sight = False
    map[x][y].tile_face = chr(172)
    map[x][y].back_light=libtcod.darker_sepia
    map[x][y].back_dark=libtcod.darkest_sepia
    map[x][y].fore_light=libtcod.black
    map[x][y].fore_dark=libtcod.darkest_sepia
    x -= 1
 
def hline_right(map, x, y):
  while x < MAP_WIDTH and map[x][y].blocked == True:
    map[x][y].blocked = False
    map[x][y].block_sight = False
    map[x][y].tile_face = chr(172)
    map[x][y].back_light=libtcod.darker_sepia
    map[x][y].back_dark=libtcod.darkest_sepia
    map[x][y].fore_light=libtcod.black
    map[x][y].fore_dark=libtcod.darkest_sepia
    x += 1

def is_blocked(x ,y):
  if map[x][y].blocked:
    return True
  for object in objects:
    if object.blocks and object.x == x and object.y == y:
      return True
  for object in allies:
    if object.blocks and object.x == x and object.y == y:
      return True
  return False

def place_objects(room):
  spawn_monsters(room)
  spawn_items(room)

def spawn_monsters(room):
  max_monsters = from_dungeon_level([[2, 1], [3, 4], [5, 6]])
  monster_chances = {}
  monster_chances['snake'] = 40
  monster_chances['orc'] = 40
  monster_chances['troll'] = from_dungeon_level([[15, 3], [30, 5], [60, 7]])
  num_monsters = libtcod.random_get_int(0, 0, max_monsters)
  for i in range(num_monsters):
    x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
    y = libtcod.random_get_int(0, room.y1+1, room.y2-1)
    if not is_blocked(x, y):
      choice = random_choice(monster_chances)
      if choice == 'orc':
        fighter_component = Fighter(hp=20, defense=0, power=4, sight=10, poison_resist=20, xp_bonus=35, inv_max=5, death_function=monster_death)
        ai_component = EquippingMonster()
        monster = Object(x, y, 'o', 'orc', libtcod.desaturated_green, blocks=True, fighter=fighter_component, ai=ai_component, gen=turn)
      elif choice == 'snake':
        fighter_component = Fighter(hp=10, defense=0, power=3, sight=15, poison_resist=80, xp_bonus=20, inv_max=1, death_function=monster_death, nat_atk_effect=inflict_poison)
        ai_component = BasicMonster()
        monster = Object(x, y, 's', 'snake', libtcod.darker_green, blocks=True, fighter=fighter_component, ai=ai_component, gen=turn)
      elif choice == 'troll':
        fighter_component = Fighter(hp=30, defense=2, power=8, sight=5, poison_resist=30, xp_bonus=100, inv_max=1, death_function=monster_death)
        ai_component = BasicMonster()
        monster = Object(x, y, 'T', 'troll', libtcod.darker_green, blocks=True, fighter=fighter_component, ai=ai_component, gen=turn)
        item_component = Item(5)
        gold = Object(0, 0, chr(166), 'gold', libtcod.gold, item=item_component)
        monster.fighter.inventory.append(gold)
      objects.append(monster)

def spawn_items(room):
  max_items = from_dungeon_level([[1, 1], [2, 4]])
  item_chances = {}
  item_chances['possess'] = 5
  item_chances['bow'] = 5
  item_chances['arrow'] = 10
  item_chances['throwing knife'] = from_dungeon_level([[10, 2]])
  item_chances['dagger'] = 10
  item_chances['machete'] = from_dungeon_level([[10, 2]])
  item_chances['sword'] = from_dungeon_level([[10, 3]])
  item_chances['heal'] = 35
  item_chances['lightning'] = from_dungeon_level([[25, 4]])
  item_chances['fireball'] =  from_dungeon_level([[25, 6]])
  item_chances['confuse'] =   from_dungeon_level([[10, 2]])
  num_items = libtcod.random_get_int(0, 0, max_items)
  for i in range(num_items):
    x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
    y = libtcod.random_get_int(0, room.y1+1, room.y2-1)
    if not is_blocked(x, y):
      choice = random_choice(item_chances)
      if choice == 'heal':
        item_component = Item(1, use_function=spell)
        spell_component = Spell(power=40, effect=cast_heal)
        item = Object(x, y, chr(144), 'healing potion', libtcod.violet, item=item_component, spell=spell_component)
      elif choice == 'lightning':
        item_component = Item(1, use_function=spell)
        spell_component = Spell(power=40, spell_range =5 , effect=cast_lightning)
        item = Object(x, y, chr(151), 'scroll of lightning bolt', libtcod.light_yellow, item=item_component, spell=spell_component)
      elif choice == 'fireball':
        item_component = Item(1, use_function=spell)
        spell_component = Spell(power=25, spell_range =3 , effect=cast_fireball)
        item = Object(x, y, chr(151), 'scroll of fireball', libtcod.red, item=item_component, spell=spell_component)
      elif choice == 'confuse':
        item_component = Item(1, use_function=spell)
        spell_component = Spell(power=10, spell_range =5 , effect=cast_confuse)
        item = Object(x, y, chr(151), 'scroll of confusion', libtcod.purple, item=item_component, spell=spell_component)
      elif choice == 'possess':
        item_component = Item(1, use_function=spell)
        spell_component = Spell(power=10, spell_range =5 , effect=cast_possess)
        item = Object(0, 0, chr(151), 'scroll of possession', libtcod.green, item=item_component, spell=spell_component)
      elif choice == 'sword':
        equipment_component = Equipment(slot='hand', power_bonus = 3)
        item = Object(x, y, chr(148), 'sword', libtcod.sky, equipment=equipment_component)
      elif choice == 'machete':
        equipment_component = Equipment(slot='hand', power_bonus = 2)
        item = Object(x, y, chr(148), 'machete', libtcod.gray, equipment=equipment_component)
      elif choice == 'dagger':
        equipment_component = Equipment(slot='hand', power_bonus = 1)
        item = Object(x, y, chr(150), 'dagger', libtcod.silver, equipment=equipment_component)
      elif choice == 'throwing knife':
        item_component = Item(1, projectile_bonus = 2, use_function=projectile)
        item = Object(x, y, chr(150), 'throwing knife', libtcod.light_blue, item=item_component)
      elif choice == 'bow':
        equipment_component = Equipment(slot='hand', ammo='arrow', power_bonus = 1)
        item = Object(x, y, chr(146), 'bow', libtcod.dark_gray, equipment=equipment_component)
      elif choice == 'arrow':
        item_component = Item(5, ammo='arrow', projectile_bonus = 1)
        item = Object(x, y, chr(147), 'arrow', libtcod.dark_gray, item=item_component)
      if item.equipment and item.equipment.slot == 'hand' and item.equipment.ammo == None and libtcod.random_get_int(0, 1, 100) <= 50:
        item.name = 'poisoned ' + item.name
        item.equipment.bonus_effect = inflict_poison
      objects.append(item)
      item.send_to_back()

def random_choice_index(chances):
  dice = libtcod.random_get_int(0, 1, sum(chances))
  running_sum = 0
  choice = 0
  for w in chances:
    running_sum += w
    if dice <= running_sum:
      return choice
    choice += 1

def random_choice(chances_dict):
  chances = chances_dict.values()
  strings = chances_dict.keys()
  return strings[random_choice_index(chances)]

def from_dungeon_level(table):
  for (value, level) in reversed(table):
    if dungeon_level >= level:
      return value
  return 0

#################
#EVENT FUNCTIONS#
#################

def move_or_attack(actor, dx, dy):
  global fov_recompute
  x = actor.x + dx
  y = actor.y + dy
  target = None
  for object in objects:
    if object.fighter and object.x == x and object.y == y:
      target = object
      break
  for object in allies:
    if object.fighter and object.x == x and object.y == y:
      target = object
      break
  if target is not None:  
    actor.fighter.attack(target)
    fov_recompute = True
  else:
    actor.move(dx, dy)
    fov_recompute = True

def player_death(player, attacker):
  global game_state
  if attacker is not None: message('You were killed by ' + attacker.name.capitalize() + '!', libtcod.red)
  else: message('You died of severe battle wounds.', libtcod.red)
  game_state = 'dead'
  player.char = '%'
  player.color = libtcod.dark_red
  for f in glob.glob('lvl*'):
    os.remove(f)

def monster_death(monster, attacker):
  eq = [piece for piece in monster.fighter.equipment.values() if piece is not None]
  for obj in eq:
    obj.equipment.dequip(monster)
  for obj in monster.fighter.inventory:
    obj.item.drop(monster)
  if attacker is not None: message(monster.name.capitalize() + ' was killed by ' + attacker.name.capitalize() + '!', libtcod.orange)
  else: message(monster.name.capitalize() + ' died of severe battle wounds.', libtcod.orange)
  monster.char = '%'
  monster.color = libtcod.dark_red
  monster.blocks = False
  monster.fighter = None
  monster.ai = None
  monster.name = 'remains of ' + monster.name
  monster.send_to_back()

def ally_death(monster, attacker):
  allies.remove(monster)
  objects.append(monster)
  monster.ai.old_death(monster, attacker)

def check_level_up(who):
  level_up_xp = LEVEL_UP_BASE + who.fighter.level * LEVEL_UP_FACTOR
  if who.fighter.xp >= level_up_xp:
    who.fighter.level += 1
    who.fighter.xp -= level_up_xp
    message('Your battle skills grow stronger! You reached level ' + str(who.fighter.level) + '!', libtcod.yellow)
    if who == player or allies.count(who)>0:
      choice = None
      while choice == None:
        choice = menu('Level up! Choose a stat to raise:\n',
          [('Constitution (+20 HP, from ' + str(player.fighter.max_hp) + ')', libtcod.red),
          ('Strength (+1 attack, from ' + str(player.fighter.power) + ')', libtcod.green),
          ('Agility (+1 defense, from ' + str(player.fighter.defense) + ')', libtcod.blue)], 40)
      if choice == 0:
        who.fighter.base_max_hp += 20
        who.fighter.hp += 20
      elif choice == 1:
        who.fighter.base_power += 1
      elif choice == 2:
        who.fighter.base_defense += 1
    
################
#U.I. FUNCTIONS#
################

def render_map():
  for y in range(MAP_HEIGHT):
    for x in range(MAP_WIDTH):
      visible = libtcod.map_is_in_fov(fov_map, x, y)
      wall = map[x][y].block_sight
      if not visible:
        if map[x][y].explored:
          libtcod.console_put_char_ex(con, x, y, map[x][y].tile_face, map[x][y].fore_dark, map[x][y].back_dark)
      else:
        libtcod.console_put_char_ex(con, x, y, map[x][y].tile_face, map[x][y].fore_light, map[x][y].back_light)
        map[x][y].explored = True
        
def render_all(actor):
  global fov_map
  global fov_recompute
# Render Map
  if fov_recompute:
    fov_recompute = False
    for pov in allies: 
      if pov != actor:
        libtcod.map_compute_fov(fov_map, pov.x, pov.y, pov.fighter.sight, FOV_LIGHT_WALLS, FOV_ALGO)
        render_map()
    if actor != player:
      libtcod.map_compute_fov(fov_map, player.x, player.y, player.fighter.sight, FOV_LIGHT_WALLS, FOV_ALGO)
      render_map()
    libtcod.map_compute_fov(fov_map, actor.x, actor.y, actor.fighter.sight, FOV_LIGHT_WALLS, FOV_ALGO)
    render_map()
  for object in objects:
    if object != actor:
      object.draw()
  for object in allies:
    if object != actor:
      object.draw()
  actor.draw()
  libtcod.console_blit(con, 0, 0, MAP_WIDTH, MAP_HEIGHT, 0, 0, 0)
# Render Side Bar  
  libtcod.console_set_default_background(side_panel, libtcod.black)
  libtcod.console_clear(side_panel)
  if actor == player: libtcod.console_print_frame(side_panel,0, 2, 15, 10, clear=True)
  libtcod.console_print_ex(side_panel, 1 , 3, libtcod.BKGND_NONE, libtcod.LEFT, player.name.capitalize() + ' lvl: ' + str(player.fighter.level))
  render_bar(1, 5, BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp, libtcod.light_red, libtcod.darker_red)
  render_bar(1, 7, BAR_WIDTH, 'XP', player.fighter.xp, LEVEL_UP_BASE + player.fighter.level * LEVEL_UP_FACTOR, libtcod.light_purple, libtcod.darker_purple)
  libtcod.console_print_ex(side_panel, 1 , 9, libtcod.BKGND_NONE, libtcod.LEFT, 'Def: ' + str(player.fighter.base_defense) + ' + ' + str(sum(equip.equipment.defense_bonus for equip in player.fighter.equipment.values() if equip is not None)))
  libtcod.console_print_ex(side_panel, 1 , 10, libtcod.BKGND_NONE, libtcod.LEFT, 'Pow: ' + str(player.fighter.base_power) + ' + ' + str(sum(equip.equipment.power_bonus for equip in player.fighter.equipment.values() if equip is not None)))
  libtcod.console_print_ex(side_panel, 1, 1, libtcod.BKGND_NONE, libtcod.LEFT, 'D. level ' + str(dungeon_level))
  if len(allies) > 0:
    if actor == allies[0]: libtcod.console_print_frame(side_panel,0, 11, 15, 10, clear=True)
    libtcod.console_print_ex(side_panel, 1 , 12, libtcod.BKGND_NONE, libtcod.LEFT, allies[0].name.capitalize() + ' lvl: ' + str(allies[0].fighter.level))
    render_bar(1, 14, BAR_WIDTH, 'HP', allies[0].fighter.hp, allies[0].fighter.max_hp, libtcod.light_red, libtcod.darker_red)
    render_bar(1, 16, BAR_WIDTH, 'XP', allies[0].fighter.xp, LEVEL_UP_BASE + allies[0].fighter.level * LEVEL_UP_FACTOR, libtcod.light_purple, libtcod.darker_purple)
    libtcod.console_print_ex(side_panel, 1 , 18, libtcod.BKGND_NONE, libtcod.LEFT, 'Def: ' + str(allies[0].fighter.base_defense) + ' + ' + str(sum(equip.equipment.defense_bonus for equip in allies[0].fighter.equipment.values() if equip is not None)))
    libtcod.console_print_ex(side_panel, 1 , 19, libtcod.BKGND_NONE, libtcod.LEFT, 'Pow: ' + str(allies[0].fighter.base_power) + ' + ' + str(sum(equip.equipment.power_bonus for equip in allies[0].fighter.equipment.values() if equip is not None)))
  if len(allies) > 1:
    if actor == allies[1]: libtcod.console_print_frame(side_panel,0, 20, 15, 10, clear=True)
    libtcod.console_print_ex(side_panel, 1 , 21, libtcod.BKGND_NONE, libtcod.LEFT, allies[1].name.capitalize() + ' lvl: ' + str(allies[1].fighter.level))
    render_bar(1, 23, BAR_WIDTH, 'HP', allies[1].fighter.hp, allies[1].fighter.max_hp, libtcod.light_red, libtcod.darker_red)
    render_bar(1, 25, BAR_WIDTH, 'XP', allies[1].fighter.xp, LEVEL_UP_BASE + allies[1].fighter.level * LEVEL_UP_FACTOR, libtcod.light_purple, libtcod.darker_purple)
    libtcod.console_print_ex(side_panel, 1 , 27, libtcod.BKGND_NONE, libtcod.LEFT, 'Def: ' + str(allies[1].fighter.base_defense) + ' + ' + str(sum(equip.equipment.defense_bonus for equip in allies[1].fighter.equipment.values() if equip is not None)))
    libtcod.console_print_ex(side_panel, 1 , 28, libtcod.BKGND_NONE, libtcod.LEFT, 'Pow: ' + str(allies[1].fighter.base_power) + ' + ' + str(sum(equip.equipment.power_bonus for equip in allies[1].fighter.equipment.values() if equip is not None)))
  if len(allies) > 2:
    if actor == allies[2]: libtcod.console_print_frame(side_panel,0, 29, 15, 10, clear=True)
    libtcod.console_print_ex(side_panel, 1 , 30, libtcod.BKGND_NONE, libtcod.LEFT, allies[2].name.capitalize() + ' lvl: ' + str(allies[2].fighter.level))
    render_bar(1, 32, BAR_WIDTH, 'HP', allies[2].fighter.hp, allies[2].fighter.max_hp, libtcod.light_red, libtcod.darker_red)
    render_bar(1, 34, BAR_WIDTH, 'XP', allies[2].fighter.xp, LEVEL_UP_BASE + allies[2].fighter.level * LEVEL_UP_FACTOR, libtcod.light_purple, libtcod.darker_purple)
    libtcod.console_print_ex(side_panel, 1 , 36, libtcod.BKGND_NONE, libtcod.LEFT, 'Def: ' + str(allies[2].fighter.base_defense) + ' + ' + str(sum(equip.equipment.defense_bonus for equip in allies[2].fighter.equipment.values() if equip is not None)))
    libtcod.console_print_ex(side_panel, 1 , 37, libtcod.BKGND_NONE, libtcod.LEFT, 'Pow: ' + str(allies[2].fighter.base_power) + ' + ' + str(sum(equip.equipment.power_bonus for equip in allies[2].fighter.equipment.values() if equip is not None)))
  if len(allies) > 3:
    if actor == allies[3]: libtcod.console_print_frame(side_panel,0, 38, 15, 10, clear=True)
    libtcod.console_print_ex(side_panel, 1 , 39, libtcod.BKGND_NONE, libtcod.LEFT, allies[3].name.capitalize() + ' lvl: ' + str(allies[3].fighter.level))
    render_bar(1, 41, BAR_WIDTH, 'HP', allies[3].fighter.hp, allies[3].fighter.max_hp, libtcod.light_red, libtcod.darker_red)
    render_bar(1, 43, BAR_WIDTH, 'XP', allies[3].fighter.xp, LEVEL_UP_BASE + allies[3].fighter.level * LEVEL_UP_FACTOR, libtcod.light_purple, libtcod.darker_purple)
    libtcod.console_print_ex(side_panel, 1 , 45, libtcod.BKGND_NONE, libtcod.LEFT, 'Def: ' + str(allies[3].fighter.base_defense) + ' + ' + str(sum(equip.equipment.defense_bonus for equip in allies[3].fighter.equipment.values() if equip is not None)))
    libtcod.console_print_ex(side_panel, 1 , 46, libtcod.BKGND_NONE, libtcod.LEFT, 'Pow: ' + str(allies[3].fighter.base_power) + ' + ' + str(sum(equip.equipment.power_bonus for equip in allies[3].fighter.equipment.values() if equip is not None)))
  libtcod.console_blit(side_panel, 0, 0, SCREEN_WIDTH - MAP_WIDTH, MAP_HEIGHT, 0, MAP_WIDTH, 0) 
# Render Message Bar
  libtcod.console_set_default_background(msg_panel, libtcod.black)
  libtcod.console_clear(msg_panel)
  y = 1
  for (line, color) in game_msgs:
    libtcod.console_set_default_foreground(msg_panel, color)
    libtcod.console_print_ex(msg_panel, 1, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
    y += 1
  if game_state == 'playing':
    standing = [obj.name for obj in objects if obj.x == player.x and obj.y == player.y and obj.name != 'Player']
    if not len(standing) == 0:
      standing = ', '.join(standing)
      libtcod.console_set_default_foreground(msg_panel, libtcod.light_gray)
      libtcod.console_print_ex(msg_panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, 'Standing on: ' + standing)
  if game_state == 'looking':
    libtcod.console_set_default_foreground(msg_panel, libtcod.light_gray)
    libtcod.console_print_ex(msg_panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, 'Looking at: ' + look_names())
  if game_state == 'target':
    libtcod.console_set_default_foreground(msg_panel, libtcod.light_gray)
    libtcod.console_print_ex(msg_panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, 'Target: ' + look_names())
  libtcod.console_blit(msg_panel, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT - MAP_HEIGHT, 0, 0, MAP_HEIGHT)

def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
  bar_width = int(float(value) / maximum * total_width)
  libtcod.console_set_default_background(side_panel, back_color)
  libtcod.console_rect(side_panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)
  libtcod.console_set_default_background(side_panel, back_color)
  if bar_width > 0:
    libtcod.console_rect(side_panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)
  libtcod.console_set_default_foreground(side_panel, libtcod.white)
  libtcod.console_print_ex(side_panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,
    name + ': ' + str(value) + '/' + str(maximum))

def message(new_msg, color = libtcod.white):
  new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)
  for line in new_msg_lines:
    if len(game_msgs) == MSG_HEIGHT:
      del game_msgs[0]
    game_msgs.append( (line, color) )

def menu(header, options, width):
  if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options')
  header_height = libtcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
  if header == '':
    header_height =0
  height = len(options) + header_height
  window = libtcod.console_new(width, height)
  libtcod.console_set_default_foreground(window, libtcod.white)
  libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)
  y = header_height
  letter_index = ord('a')
  for (option_text, option_color) in options:
    text = '(' + chr(letter_index) + ')' + option_text
    libtcod.console_set_default_foreground(window, option_color)
    libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
    y += 1
    letter_index += 1
  x = SCREEN_WIDTH/2 - width/2
  y = SCREEN_HEIGHT/2 - height/2
  libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)
  libtcod.console_flush()
#  key = libtcod.console_wait_for_keypress(True)
  while True:
    key = block_for_key()
    if not (key.vk == libtcod.KEY_ALT or key.vk == libtcod.KEY_CONTROL or key.vk == libtcod.KEY_SHIFT):
      break
  if key.vk == libtcod.KEY_ENTER and key.lalt:
      libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
  index = key.c - ord('a')
  if index >=0 and index < len(options): return index
  return None

def block_for_key():
  key = libtcod.Key()
  mouse = libtcod.Mouse()
  while True:
    libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)
    if (key.vk == libtcod.KEY_NONE):
      continue
    if (key.vk == libtcod.KEY_ALT or key.vk == libtcod.KEY_SHIFT or key.vk == libtcod.KEY_CONTROL):
      continue
    break
  return key

def inventory_menu(actor, header):
  if len(actor.fighter.inventory) == 0:
    options = [('Inventory is empty.', libtcod.white)]
  else:
    options = [(' ' + str(item.item.qty) + ' ' + item.char + ' ' + item.name, item.color) for item in actor.fighter.inventory]
  index = menu(header, options, INVENTORY_WIDTH)
  if index is None or len(actor.fighter.inventory) == 0: return None
  return actor.fighter.inventory[index].item

def equipment_menu(actor):
  options = actor.fighter.equipment.keys()
  text = []
  for option in options:
    if actor.fighter.equipment[option] == None:
      text.append((' ' + option.capitalize() + ' - ' + 'empty', libtcod.darker_red))
    else :
      text.append((' ' + option.capitalize() + ' - ' + actor.fighter.equipment[option].name, actor.fighter.equipment[option].color))
  index = menu('Equipment', text, 25)
  if index is None: return None
  if actor.fighter.equipment[options[index]] is None: return options[index]
  return actor.fighter.equipment[options[index]]

def equipable_items(actor, slot):
  items = [(' ' + obj.char + ' ' + obj.name, obj.color) for obj in actor.fighter.inventory if obj.equipment and obj.equipment.slot == slot]
  text = [(' ' + obj.char + ' ' + obj.name, obj.color) for obj in actor.fighter.inventory if obj.equipment and obj.equipment.slot == chosen_equipment]
  if len(items) == 0: 
    msgbox('No equipable items')
    return None
  else:
    item = menu('Select item to equip', text, 25)
    if item is None: return None
    return items[item]

def msgbox(text, width=50):
  menu(text,[], width)
  libtcod.console_wait_for_keypress(True)

def help():
  msgbox('     Movement/Melee Attack    \
                                 \
  Up:      Arrow up,    Numpad 8\
  Down:    Arrow down,  Numpad 2\
  Left:    Arrow left,  Numpad 4\
  Right:   Arrow right, Numpad 6\
  Up+Lft:  Home,        Numpad 7\
  Up+Rgt:  Page Up,     Numpad 9\
  Dn+Lft:  End,         Numpad 1\
  Dn+Rgt:  Page Down,   Numpad 3\
                                   \
        Character Actions       \
                                 \
  Pick up Item:         g       \
  Drop Item:            d       \
  Inventory/Use Item:   i       \
  Equipment Menu:       e       \
  Shoot ranged weapon:  f       \
  Look (start/stop):    l       \
  Climb Stairs Up:      <       \
  Decend Stairs Down:   >       \
                                   \
       Looking & Targetting     \
                                 \
  Cursor movement:  See Above   \
  Confirm Target:  Enter/Return \
  Cancell Target:   Back Space  \
  Stop Looking:         l       \
                                 \
  View this screen:     ?', 32)

##################
#KEYBOARD & INPUT#
##################

def handle_keys(actor):
  global fov_recompute
  global game_state
  global key
  if key.vk == libtcod.KEY_ENTER and key.lalt:
    libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
  elif key.vk == libtcod.KEY_ESCAPE:
    return 'exit'
  if game_state == 'playing':
    if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
      move_or_attack(actor, 0, -1)
    elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
      move_or_attack(actor, 0, 1)
    elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
      move_or_attack(actor, -1, 0)
    elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
      move_or_attack(actor, 1, 0)
    elif key.vk == libtcod.KEY_HOME or key.vk == libtcod.KEY_KP7:
      move_or_attack(actor, -1, -1)
    elif key.vk == libtcod.KEY_PAGEUP or key.vk == libtcod.KEY_KP9:
      move_or_attack(actor, 1, -1)
    elif key.vk == libtcod.KEY_END or key.vk == libtcod.KEY_KP1:
      move_or_attack(actor, -1, 1)
    elif key.vk == libtcod.KEY_PAGEDOWN or key.vk == libtcod.KEY_KP3:
      move_or_attack(actor, 1, 1)
    elif key.vk == libtcod.KEY_KP5:
      pass
    else:
      fov_recompute = True
      key_char = chr(key.c)
      if key_char == '?':
        help()
      elif key_char == 'l':
        start_cursor(actor.x, actor.y)
        fov_recompute = True
        libtcod.console_flush()
        render_all(actor)
        game_state = 'looking'
        return 'didnt-take-turn'
      elif key_char == 'g':
        for object in objects:
          if object.x == actor.x and object.y == actor.y and object.item:
            object.item.pick_up(actor)
            break
        return 'didnt-take-turn'
      elif key_char == 'i':
        chosen_item = inventory_menu(actor, 'Press the key next to an item to use it, or any other to cancel.\n')
        if chosen_item is not None:
          chosen_item.use(actor)
        else: return 'didnt-take-turn'
      elif key_char == 'd':
        chosen_item = inventory_menu(actor, 'Press the key next to an item to drop it, or any other to cancel.\n')
        if chosen_item is not None:
          chosen_item.drop(actor)
        else: return 'didnt-take-turn'
      elif key_char == 'e':
        chosen_equipment = equipment_menu(actor)
        if chosen_equipment is not None and type(chosen_equipment) is not str:
          chosen_equipment.equipment.toggle_equip(actor)
        elif type(chosen_equipment) is str:
          if chosen_equipment == 'good hand' or chosen_equipment == 'off hand': chosen_equipment = 'hand'
          items = [obj for obj in actor.fighter.inventory if obj.equipment and obj.equipment.slot == chosen_equipment]
          text = [(' ' + obj.char + ' ' + obj.name, obj.color) for obj in actor.fighter.inventory if obj.equipment and obj.equipment.slot == chosen_equipment]
          if len(items) == 0: 
            msgbox('No equipable items', 20)
            return 'didnt-take-turn'
          else:  
            item = menu('Select item to equip', text, 25)
            if item is not None:
              items[item].equipment.toggle_equip(actor)
            else: return 'didnt-take-turn'
      elif key_char == 'f':
        if actor.fighter.equipment['good hand'] is not None and actor.fighter.equipment['good hand'].equipment.ammo:
          action = shoot_weapon(actor, 'good hand')
          if action == 'cancelled': return 'didnt-take-turn'
        elif actor.fighter.equipment['off hand'] is not None and actor.fighter.equipment['off hand'].equipment.ammo:
          msgbox("Can't shoot with off hand", 26)
          return 'didnt-take-turn'
        else: return 'didnt-take-turn'
      elif key_char == '>':
        if stairs_down.x == player.x and stairs_down.y == player.y:
          next_level()
        else: return 'didnt-take-turn'
      elif key_char == '<' and dungeon_level >= 1:
        if stairs_up.x == player.x and stairs_up.y == player.y:
          previous_level()
        else: return 'didnt-take-turn'
      else:
        return 'didnt-take-turn'
  if game_state == 'looking':
    if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
      cursor_move(0, -1)
    elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
      cursor_move(0, 1)
    elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
      cursor_move(-1, 0)
    elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
      cursor_move(1, 0)
    elif key.vk == libtcod.KEY_HOME or key.vk == libtcod.KEY_KP7:
      cursor_move(-1, -1)
    elif key.vk == libtcod.KEY_PAGEUP or key.vk == libtcod.KEY_KP9:
      cursor_move(1, -1)
    elif key.vk == libtcod.KEY_END or key.vk == libtcod.KEY_KP1:
      cursor_move(-1, 1)
    elif key.vk == libtcod.KEY_PAGEDOWN or key.vk == libtcod.KEY_KP3:
      cursor_move(1, 1)
    else:
      key_char = chr(key.c)
      if key_char == 'l':
        game_state = 'playing'
    return 'didnt-take-turn'

def look_names():
  global cursor
  (x, y) = (cursor.x, cursor.y)
  names = []
  for obj in objects:
    if obj.x == x and obj.y == y and libtcod.map_is_in_fov(fov_map, obj.x, obj.y):
      names.append(obj.name)
  if len(names) != 0:
    names = ', '.join(names)
  else:
    names = 'Nothing'
  return names.capitalize()

def target_area(actor):
  global key, cursor, game_state
  game_state = 'target'
  start_cursor(actor.x, actor.y)
  while game_state == 'target':
    libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)
    render_all(actor)
    libtcod.console_flush()
    if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
      cursor_move(0, -1)
    elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
      cursor_move(0, 1)
    elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
      cursor_move(-1, 0)
    elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
      cursor_move(1, 0)
    elif key.vk == libtcod.KEY_HOME or key.vk == libtcod.KEY_KP7:
      cursor_move(-1, -1)
    elif key.vk == libtcod.KEY_PAGEUP or key.vk == libtcod.KEY_KP9:
      cursor_move(1, -1)
    elif key.vk == libtcod.KEY_END or key.vk == libtcod.KEY_KP1:
      cursor_move(-1, 1)
    elif key.vk == libtcod.KEY_PAGEDOWN or key.vk == libtcod.KEY_KP3:
      cursor_move(1, 1)
    elif key.vk == libtcod.KEY_ENTER or key.vk == libtcod.KEY_KPENTER:
      clear_cursor()
      game_state = 'playing'
      return (cursor.x, cursor.y)
    elif key.vk == libtcod.KEY_BACKSPACE:
      clear_cursor()
      game_state = 'playing'
      return (None, None)

def target_monster(actor):
  global key, cursor, game_state
  monsters = [obj for obj in objects if obj.fighter and obj != actor and libtcod.map_is_in_fov(fov_map, obj.x, obj.y)]
  if len(monsters) == 0: 
    message('No enemies in range', libtcod.red)
    return None
  index = 0
  start_cursor(monsters[index].x, monsters[index].y)
  game_state = 'target'
  while game_state == 'target':
    libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)
    render_all(actor)
    libtcod.console_flush()
    if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8 or key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
      clear_cursor()
      index += 1
      if index > len(monsters)-1: index = 0
      start_cursor(monsters[index].x, monsters[index].y)
    if key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2 or key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
      clear_cursor()
      index -= 1
      if index < 0: index = len(monsters)-1
      start_cursor(monsters[index].x, monsters[index].y)
    if key.vk == libtcod.KEY_BACKSPACE:
      clear_cursor()
      game_state = 'playing'
      return None
    if key.vk == libtcod.KEY_ENTER or key.vk == libtcod.KEY_KPENTER:
      clear_cursor()
      game_state = 'playing'
      return monsters[index]

def closest_monster(actor, max_range):
  closest_enemy = None
  closest_dist = max_range + 1
  for object in objects:
    if object.fighter and not object == actor and libtcod.map_is_in_fov(fov_map, object.x, object.y):
      dist = actor.distance_to(object)
      if dist < closest_dist:
        closest_enemy = object
        closest_dist = dist
  return closest_enemy

def start_cursor(x, y):
  (cursor.x, cursor.y) = (x, y)
  libtcod.console_set_char_background(con, cursor.x, cursor.y, libtcod.black)
  libtcod.console_set_char_foreground(con, cursor.x, cursor.y, libtcod.white)

def cursor_move(dx, dy):
  if libtcod.map_is_in_fov(fov_map, cursor.x + dx, cursor.y + dy):
    clear_cursor()
    start_cursor(cursor.x + dx, cursor.y + dy)

def clear_cursor():
  libtcod.console_set_char_background(con, cursor.x, cursor.y, map[cursor.x][cursor.y].back_light)
  libtcod.console_set_char_foreground(con, cursor.x, cursor.y, map[cursor.x][cursor.y].fore_light)

##################
#STATUS FUNCTIONS#
##################

def inflict_poison(attacker, target):
  if libtcod.random_get_int(0, 1, 100) > target.fighter.poison_resist:
    target.fighter.state = 'poison'
    target.fighter.state_inflictor = attacker
    if target == player or allies.count(target) > 0: message(target.name.capitalize() + ' has been poisoned by ' + attacker.name + '.', libtcod.purple)
    if attacker == player or allies.count(attacker) > 0: message(attacker.name.capitalize() + ' has poisoned ' + target.name + '.', libtcod.fuchsia)
  
############
#PROJECTILE#
############

def projectile(proj, attacker):
  target = target_monster(attacker)
  if target is None: return 'cancelled'
  if projectile_attack(attacker, proj, target) == 'cancelled': return 'cancelled'

def projectile_attack(attacker, projectile, target):
  libtcod.line_init(attacker.x, attacker.y, target.x, target.y)
  hit = True
  (x, y) = libtcod.line_step()
  while (not x is None):
    for obj in objects:
      if obj.blocks and x == obj.x and y == obj.y and obj != attacker and obj != target:
        hit = False
        break
    (x, y) = libtcod.line_step()
  if hit == True:
    if projectile.item.projectile_bonus is not None:
      if attacker.fighter.equipment['good hand'] is not None and attacker.fighter.equipment['good hand'].equipment.ammo and projectile.item.ammo and attacker.fighter.equipment['good hand'].equipment.ammo == projectile.item.ammo:
        damage = attacker.fighter.power + projectile.item.projectile_bonus
      else: damage = attacker.fighter.base_power + projectile.item.projectile_bonus
    else: damage = attacker.fighter.base_power
    message(attacker.name.capitalize() + ' shoot ' + target.name + ' with ' + projectile.name + ' for ' + str(damage) + 'hit points.', libtcod.silver)
    target.fighter.take_damage(attacker, damage)
  else:
    message('No clear shot for ' + target.name, libtcod.red)
    return 'cancelled'

def shoot_weapon(actor, hand):
  items = [obj for obj in actor.fighter.inventory if obj.item.ammo and obj.item.ammo == actor.fighter.equipment[hand].equipment.ammo]
  text = [(' ' + obj.char + ' ' + obj.name, obj.color) for obj in actor.fighter.inventory if obj.item.ammo and obj.item.ammo == actor.fighter.equipment['good hand'].equipment.ammo]
  if len(items) == 0: 
    msgbox("You don't have any " + actor.fighter.equipment[hand].equipment.ammo, 20)
    return 'cancelled'
  else:  
    item = menu('Select projectile', text, 25)
    if item is not None:
      if not projectile(items[item], actor) == 'cancelled':
        if items[item].item.qty > 1:
          items[item].item.qty -= 1
        else:
          actor.fighter.inventory.remove(items[item])
      else: return 'cancelled'

#################
#SPELL FUNCTIONS#
#################

def spell(owner, caster):
  if owner.spell.effect(owner, caster) == 'cancelled': return 'cancelled'
  
def cast_heal(owner, caster):
  if caster.fighter.hp == caster.fighter.max_hp:
    message('You are already at full health.', libtcod.red)
    return 'cancelled'
  message('Your wounds start to feel better!', libtcod.light_violet)
  caster.fighter.heal(owner.spell.power)

def cast_lightning(owner, caster):
  monster = closest_monster(caster ,owner.spell.spell_range)
  if monster is None:
    message('No enemy is close enough to strike.', libtcod.red)
    return 'cancelled'
  message('A lighting bolt strikes the ' + monster.name + ' with a loud thunder! The damage is '
    + str(owner.spell.power) + ' hit points.', libtcod.light_blue)
  monster.fighter.take_damage(caster, owner.spell.power)

def cast_confuse(owner, caster):
  monster = target_monster(caster)
  if monster is None: return 'cancelled'
  old_ai = monster.ai
  monster.ai = ConfusedMonster(old_ai, owner.spell.power)
  monster.ai.owner = monster
  message('The eyes of the ' + monster.name + ' look vacant, as he starts to stumble around!', libtcod.light_green)

def cast_possess(owner, caster):
  if len(allies) < MAX_ALLIES:
    monster = target_monster(caster)
    if monster is None: return 'cancelled'
    objects.remove(monster)
    allies.append(monster)
    old_ai = monster.ai
    old_color = monster.color
    old_char = monster.char
    old_death = monster.fighter.death_function
    monster.char = '@'
    monster.fighter.death_function = ally_death
    monster.ai = PossessedMonster(old_ai, old_color, old_char, old_death, owner.spell.power)
    monster.ai.owner = monster
    monster.always_visible = True
    message('The eyes of the ' + monster.name + ' look straight ahead, it is ready to obey!', libtcod.light_green)

def cast_fireball(owner, caster):
  message('Select target tile with movement keys, [ENTER] to confirm and [BACKSPACE] to cancel')
  (x, y) = target_area(caster)
  if x is None: return 'cancelled'
  message('The fireball explodes, burning everything within ' + str(owner.spell.spell_range) + ' tiles!', libtcod.orange)
  victims = [victim for victim in objects if victim.distance(x, y) <= owner.spell.spell_range and victim.fighter]
  for victim in victims:
    message('The ' + victim.name + ' gets burned for ' + str(owner.spell.power) + ' hit points.', libtcod.orange)
    victim.fighter.take_damage(caster, owner.spell.power)

################
#MAIN FUNCTIONS#
################

def main_menu():
  img = libtcod.image_load('menu_background.png')
  while not libtcod.console_is_window_closed():
    libtcod.image_blit_2x(img, 0, 0, 0)
    libtcod.console_set_default_foreground(0, libtcod.light_yellow)
    libtcod.console_print_ex(0, SCREEN_WIDTH/2, SCREEN_HEIGHT/2-4, libtcod.BKGND_NONE, libtcod.CENTER, 'CROOKED FANG')
    libtcod.console_print_ex(0, SCREEN_WIDTH/2, SCREEN_HEIGHT-2, libtcod.BKGND_NONE, libtcod.CENTER, 'By Larzid')
    options =[('New Game', libtcod.green), ('Continue Game', libtcod.white), ('Controls', libtcod.sky), ('Quit', libtcod.red)]
    choice = menu('', options, 18)
    if choice == 0:
      new_game()
      play_game()
    if choice == 1:
      try:
        load_game()
      except:
        msgbox('\n No saved game to load.\n', 24)
        continue
      play_game()
    if choice == 2:
      help()
      continue
    elif choice == 3:
      break

def new_game():
  global player, allies, game_state, game_msgs, dungeon_level, max_d_level, turn
  turn = 1
  fighter_component = Fighter(hp=100, defense=1, power=4, sight=7, poison_resist=30, inv_max=25, death_function=player_death)
  player = Object(0, 0, '@', 'Player', libtcod.white, blocks=True, fighter=fighter_component, gen=turn)
  allies = []
# Starting Items
  item_component = Item(1, use_function=spell)
  spell_component = Spell(power=40, effect=cast_heal)
  item = Object(0, 0, chr(144), 'healing potion', libtcod.violet, item=item_component, spell=spell_component)
  player.fighter.inventory.append(item)
  item_component = Item(5, projectile_bonus = 2, use_function=projectile)
  item = Object(0, 0, chr(150), 'throwing knife', libtcod.light_blue, item=item_component)
  player.fighter.inventory.append(item)
  item_component = Item(5, use_function=spell)
  spell_component = Spell(power=10, spell_range =5 , effect=cast_possess)
  item = Object(0, 0, chr(151), 'scroll of possession', libtcod.green, item=item_component, spell=spell_component)
  player.fighter.inventory.append(item)
  dungeon_level = 0
  max_d_level = 1
  for f in glob.glob('lvl*'):
    os.remove(f)
  make_town()
  initialize_fov()
  game_state = 'playing'
  game_msgs = []
  message('You were bored, you craved adventure and due to your total lack of common sense and reckless impulsive behavior you came here, to some strange ruins half a world away from what you call civilization!', libtcod.light_cyan)
  message('Did you at least told somebody what you where up to?', libtcod.crimson)
  message('Well, its kinda late for that.', libtcod.light_purple)

def initialize_fov():
  global fov_recompute, fov_map, cursor
  libtcod.console_clear(con)
  fov_recompute = True
  fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
  cursor = Object(0, 0, '', 'cursor', libtcod.white)
  for y in range(MAP_HEIGHT):
    for x in range(MAP_WIDTH):
      libtcod.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)

def play_game():
  global key, mouse, turn
  player_action = None
  key = libtcod.Key()
  mouse = libtcod.Mouse()
  player_check_state = True
  while not libtcod.console_is_window_closed():
    fov_recompute = True
    libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)
    libtcod.console_flush()
    check_level_up(player)
    if player_check_state == True:
      player.fighter.check_state()
      player_check_state = False
    render_all(player)
    libtcod.map_compute_fov(fov_map, player.x, player.y, player.fighter.sight, FOV_LIGHT_WALLS, FOV_ALGO)
    player_action = handle_keys(player)
    for object in objects:
      object.clear()
    if player_action == 'exit':
      save_game()
      break
    if game_state == 'playing' and player_action != 'didnt-take-turn':
      
      for object in allies:
        if object.ai:
          object.ai.take_turn()
      for object in objects:
        if object.ai:
          object.fighter.check_state()
          object.ai.take_turn()
      player_check_state = True
      turn += 1

def save_game():
  file = shelve.open('savegame', 'n')
  file['map'] = map
  file['rooms'] = rooms
  file['objects'] = objects
  file['player_index'] = objects.index(player)
  file['game_msgs'] = game_msgs
  file['game_state'] = game_state
  file['stairs_down_index'] = objects.index(stairs_down)
  if dungeon_level >= 1:
    file['stairs_up_index'] = objects.index(stairs_up)
  file['dungeon_level'] = dungeon_level
  file['max_d_level'] = max_d_level
  file['turn'] = turn
  file['allies'] = allies
  file.close()

def load_game():
  global map, rooms, objects, player, allies, game_msgs, game_state, stairs_down, stairs_up, dungeon_level, max_d_level, turn
  file = shelve.open('savegame', 'r')
  map = file['map']
  rooms = file['rooms']
  objects = file['objects']
  player = objects[file['player_index']]
  allies = file['allies']
  game_msgs = file['game_msgs']
  game_state = file['game_state']
  stairs_down = objects[file['stairs_down_index']]
  dungeon_level = file['dungeon_level']
  max_d_level = file['max_d_level']
  turn = file['turn']
  if dungeon_level >= 1:
    stairs_up = objects[file['stairs_up_index']]
  file.close()
  initialize_fov()

#########################
#DUNGEON LEVEL FUNCTIONS#
#########################

def next_level():
  global dungeon_level, max_d_level
  if dungeon_level + 1 > max_d_level:
    message('You take a moment to rest, and recover your strength.', libtcod.light_violet)
    player.fighter.heal(player.fighter.max_hp / 2)
    message('After a rare moment of peace, you descend deeper into the heart of the dungeon...', libtcod.red)
    max_d_level += 1
  else:
    message('You descend deeper into the heart of the dungeon...', libtcod.red)
  player_status = [player.fighter.hp, player.fighter.base_max_hp, player.fighter.base_defense, player.fighter.base_power, player.fighter.base_sight, player.fighter.inventory, player.fighter.xp, player.fighter.level, player.fighter.equipment] #Anything added here shoule be also added in previous_level()
  save_level('lvl'+str(dungeon_level))
  dungeon_level += 1
  try:
    load_level('lvl'+str(dungeon_level))
  except:
    make_map()
    initialize_fov()
  init_level(player_status)
  (player.x, player.y) = (stairs_up.x, stairs_up.y)
  if len(allies) > 0: (allies[0].x, allies[0].y) = (player.x -1, player.y -1)
  if len(allies) > 1: (allies[1].x, allies[1].y) = (player.x +1, player.y -1)
  if len(allies) > 2: (allies[2].x, allies[2].y) = (player.x +1, player.y +1)
  if len(allies) > 3: (allies[3].x, allies[3].y) = (player.x -1, player.y +1)
  initialize_fov()
  
def previous_level():
  global dungeon_level
  message('You ascend into a higher level of the dungeon...', libtcod.red)
  player_status = [player.fighter.hp, player.fighter.base_max_hp, player.fighter.base_defense, player.fighter.base_power, player.fighter.base_sight, player.fighter.inventory, player.fighter.xp, player.fighter.level, player.fighter.equipment] #Anything added here shoule be also added in next_level()
  save_level('lvl'+str(dungeon_level))
  dungeon_level -= 1
  try:
    load_level('lvl'+str(dungeon_level))
  except:
    if dungeon_level >= 1:
      make_map()
      initialize_fov()
    else:
      make_town()
      initialize_fov()
  init_level(player_status)
  (player.x, player.y) = (stairs_down.x, stairs_down.y)
  if len(allies) > 0: (allies[0].x, allies[0].y) = (player.x -1, player.y -1)
  if len(allies) > 1: (allies[1].x, allies[1].y) = (player.x +1, player.y -1)
  if len(allies) > 2: (allies[2].x, allies[2].y) = (player.x +1, player.y +1)
  if len(allies) > 3: (allies[3].x, allies[3].y) = (player.x -1, player.y +1)
  initialize_fov()
  
def init_level(player_status):
  [player.fighter.hp, player.fighter.base_max_hp, player.fighter.base_defense, player.fighter.base_power, player.fighter.base_sight, player.fighter.inventory, player.fighter.xp, player.fighter.level, player.fighter.equipment] = player_status #Also load additions to Figter class here
  if dungeon_level >= 1:
    items = [obj for obj in objects if obj.item]
    if len(items) == 0:
      for room in rooms:
        spawn_items(room)
    monsters = [obj for obj in objects if obj.fighter and obj != player]
    if len(monsters) == 0:
      for room in rooms:
        spawn_monsters(room)

def save_level(filename):
  file = shelve.open(filename, 'n')
  file['lvl'] = map
  file['rooms_lvl'] = rooms
  file['objects_lvl'] = objects
  file['player_lvl'] = objects.index(player)
  file['stairs_down_lvl'] = objects.index(stairs_down)
  if dungeon_level >= 1:
    file['stairs_up_lvl'] = objects.index(stairs_up)
  file.close()

def load_level(filename):
  global dungeon_level, map, rooms, player, objects, stairs_down, stairs_up, max_d_level
  file = shelve.open(filename, 'r')
  map = file['lvl']
  rooms = file['rooms_lvl']
  objects = file['objects_lvl']
  player = objects[file['player_lvl']]
  stairs_down = objects[file['stairs_down_lvl']]
  if dungeon_level >= 1:
    stairs_up = objects[file['stairs_up_lvl']]
  file.close()

######
#INIT#
######

libtcod.console_set_custom_font('generic_rl_fnt.png', libtcod.FONT_TYPE_GRAYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Crooked Fang', False)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
libtcod.sys_set_fps(LIMIT_FPS)
side_panel = libtcod.console_new(SCREEN_WIDTH-MAP_WIDTH, MAP_HEIGHT)
msg_panel = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT - MAP_HEIGHT)
main_menu()