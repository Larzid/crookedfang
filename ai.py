import libtcodpy as libtcod
import globals
import render
import get_input

class BasicMonster:
  def __init__(self):
    self.action = ''
    self.state = 'playing'
  def take_turn(self):
    if self.state == 'playing':
      monster = self.owner
      globals.fov_recompute(monster)
      target = None
      enemies = [creature for creature in globals.objects() if creature.ai and creature.ai.state != 'dead' and creature.fighter and creature.fighter.faction != monster.fighter.faction and libtcod.map_is_in_fov(globals.map().fov, creature.x, creature.y)]
      if len(enemies) > 0:
        closest_dist = monster.fighter.sight + 1
        for object in enemies:
          dist = monster.distance_to(object)
          if dist < closest_dist:
            target = object
            closest_dist = dist
      if target is not None:
        if monster.distance_to(target) >= 2:
          monster.move_astar(target)
        elif target.fighter.hp > 0:
          monster.fighter.attack(target)
      else:
        self.action = 'didnt-take-turn'
        while self.action == 'didnt-take-turn':
          (x, y) = (libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1))
          if not globals.is_blocked(monster.x + x, monster.y + y):
            self.action = 'moved'
            monster.move(x, y)
      self.owner.fighter.check_status = True
  def level_up(self):
    if self.owner.fighter.level % 3 == 0: self.owner.fighter.max_hp += 20
    self.owner.fighter.hp = self.owner.fighter.max_hp
    if self.owner.fighter.level % 2 == 0: self.owner.fighter.power += 1
    if self.owner.fighter.level % 2 == 1: self.owner.fighter.defense += 1

class PlayerControlled:
  def __init__(self):
    self.action = ''
    self.state = 'playing'
  def take_turn(self):
    self.action = 'didnt-take-turn'
    while self.action == 'didnt-take-turn':
      render.all(self.owner)
      libtcod.console_flush()
      self.action = get_input.handle_keys(self.owner)
      for object in globals.objects():
        render.clear(object)
      if self.owner.fighter:
        self.owner.fighter.check_status = True
  def level_up(self):
    if self.owner.fighter.level % 3 == 0: self.owner.fighter.max_hp += 20
    self.owner.fighter.hp = self.owner.fighter.max_hp
    if self.owner.fighter.level % 2 == 0: self.owner.fighter.power += 1
    if self.owner.fighter.level % 2 == 1: self.owner.fighter.defense += 1
#    choice = None
#    while choice == None:
#      choice = menu('Level up! Choose a stat to raise:\n',
#        [('Constitution (+20 HP, from ' + str(who.fighter.max_hp) + ')', libtcod.red),
#        ('Strength (+1 attack, from ' + str(who.fighter.power) + ')', libtcod.green),
#        ('Agility (+1 defense, from ' + str(who.fighter.defense) + ')', libtcod.blue)], 40)
#    if choice == 0:
#      who.fighter.base_max_hp += 20
#      who.fighter.hp += 20
#    elif choice == 1:
#      who.fighter.base_power += 1
#    elif choice == 2:
#      who.fighter.base_defense += 1
