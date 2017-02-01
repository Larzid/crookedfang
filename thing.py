import libtcodpy as libtcod
import render
import globals

class Item:
  def __init__(self, qty, ammo=None, projectile_bonus=None, stackable=True , use_function=None):
    self.qty = qty
    self.ammo = ammo
    self.projectile_bonus = projectile_bonus
    self.stackable = stackable
    self.use_function = use_function
  def pick_up(self, owner):
    if len(owner.fighter.inventory) >= owner.fighter.inv_max:
      if owner == globals.player(): render.msgbox('Your inventory is full, cannot pick up ' + self.owner.name + '.')
    else:
      if self.stackable:
        has_item = False
        for package in owner.fighter.inventory:
          if package.name == self.owner.name:
            has_item = True
            package.item.qty = package.item.qty + self.qty
            globals.objects().remove(self.owner)
            if owner == globals.player(): globals.message('You picked up ' + str(self.qty) + ' ' + self.owner.name + ' and now have ' + str(package.item.qty) + '!', libtcod.green)
            break
        if not has_item:
          owner.fighter.inventory.append(self.owner)
          globals.objects().remove(self.owner)
          if owner == globals.player(): globals.message('You picked up ' + str(self.qty) + ' ' + self.owner.name + '!', libtcod.green)
      else:
        owner.fighter.inventory.append(self.owner)
        globals.objects().remove(self.owner)
        if owner == globals.player(): globals.message('You picked up ' + str(self.qty) + ' ' + self.owner.name + '!', libtcod.green)
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
          user.fighter.inventory.remove(self.owner)
  def drop(self, owner):
    globals.objects().append(self.owner)
    owner.fighter.inventory.remove(self.owner)
    (self.owner.x, self.owner.y) = (owner.x, owner.y)
    if owner == globals.player(): globals.message('You dropped ' + str(self.qty) + ' ' + self.owner.name + '.', libtcod.yellow)

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
        if user == globals.player(): globals.message('Equipped ' + self.owner.name + ' on ' + 'good hand' + '.', libtcod.light_green)
      elif user.fighter.equipment['off hand'] is None:
        self.is_equipped = True
        user.fighter.equipment['off hand'] = self.owner
        user.fighter.inventory.remove(self.owner)
        if user == globals.player(): globals.message('Equipped ' + self.owner.name + ' on ' + 'off hand' + '.', libtcod.light_green)
      else:
        hand = menu('Equip to which hand?',[('good hand', libtcod.white), ('off hand', libtcod.white)], 22)
        if hand == 0:
          user.fighter.equipment['good hand'].equipment.is_equipped = False
          user.fighter.inventory.append(user.fighter.equipment['good hand'])
          if user == globals.player(): globals.message('Dequipped ' + user.fighter.equipment['good hand'].name + ' from ' + 'good hand' + '.', libtcod.light_yellow)
          self.is_equipped = True
          user.fighter.equipment['good hand'] = self.owner
          user.fighter.inventory.remove(self.owner)
          if user == globals.player(): globals.message('Equipped ' + self.owner.name + ' on ' + 'good hand' + '.', libtcod.light_green)
        elif hand == 1:
          user.fighter.equipment['off hand'].equipment.is_equipped = False
          user.fighter.inventory.append(user.fighter.equipment['off hand'])
          if user == globals.player(): globals.message('Dequipped ' + user.fighter.equipment['off hand'].name + ' from ' + 'off hand' + '.', libtcod.light_yellow)
          self.is_equipped = True
          user.fighter.equipment['off hand'] = self.owner
          user.fighter.inventory.remove(self.owner)
          if user == globals.player(): globals.message('Equipped ' + self.owner.name + ' on ' + 'off hand' + '.', libtcod.light_green)
    else:
      if user.fighter.equipment[self.slot] is not None: user.fighter.equipment[self.slot].equipment.dequip(user)
      self.is_equipped = True
      user.fighter.equipment[self.slot] = self.owner
      user.fighter.inventory.remove(self.owner)
      if user == globals.player(): globals.message('Equipped ' + self.owner.name + ' on ' + self.slot + '.', libtcod.light_green)
  def dequip(self, user):
    if not self.is_equipped: return
    if self.owner == user.fighter.equipment['good hand']: user.fighter.equipment['good hand'] = None
    elif self.owner == user.fighter.equipment['off hand']: user.fighter.equipment['off hand'] = None
    else: user.fighter.equipment[self.slot] = None
    user.fighter.inventory.append(self.owner)
    self.is_equipped = False
    if user == globals.player(): globals.message('Dequipped ' + self.owner.name + ' from ' + self.slot + '.', libtcod.light_yellow)