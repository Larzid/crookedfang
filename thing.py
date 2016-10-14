import libtcodpy as libtcod
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
#    if self.owner.equipment:
#      self.owner.equipment.toggle_equip(user)
#      return
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