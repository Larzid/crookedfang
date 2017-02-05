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
      target = globals.closest_enemy(monster, monster.creature.sight)
      if target is not None:
        if monster.distance_to(target) >= 2:
          monster.move_astar(target)
        elif target.creature.hp > 0:
          monster.creature.attack(target)
      else:
        self.action = 'didnt-take-turn'
        while self.action == 'didnt-take-turn':
          (x, y) = (libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1))
          if not globals.is_blocked(monster.x + x, monster.y + y):
            self.action = 'moved'
            monster.move(x, y)
      self.owner.creature.check_status = True
  def level_up(self):
    if self.owner.creature.level % 3 == 0: self.owner.creature.max_hp += 20
    self.owner.creature.hp = self.owner.creature.max_hp
    if self.owner.creature.level % 2 == 0: self.owner.creature.power += 1
    if self.owner.creature.level % 2 == 1: self.owner.creature.defense += 1

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
      if self.owner.creature:
        self.owner.creature.check_status = True
  def level_up(self):
    choice = None
    while choice == None:
      choice = render.menu('Level up! Choose a stat to raise:\n',
        [('Constitution (+20 HP, from ' + str(self.owner.creature.max_hp) + ')', libtcod.red),
        ('Strength (+1 attack, from ' + str(self.owner.creature.power) + ')', libtcod.green),
        ('Agility (+1 defense, from ' + str(self.owner.creature.defense) + ')', libtcod.blue)], 40)
    if choice == 0:
      self.owner.creature.base_max_hp += 20
      self.owner.creature.hp += 20
    elif choice == 1:
      self.owner.creature.base_power += 1
    elif choice == 2:
      self.owner.creature.base_defense += 1

class ConfusedMonster:
  def __init__(self, old_ai, num_turns):
    self.action = ''
    self.state = 'playing'
    self.old_ai = old_ai
    self.num_turns = num_turns
  def take_turn(self):
    if self.num_turns > 0:
      self.owner.move(libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1))
      self.num_turns -= 1
    else:
      self.owner.ai = self.old_ai
      render.message('The ' + self.owner.name + ' is no longer confused!', libtcod.red)
