import libtcodpy as libtcod
import globals
import render
import get_input

class BasicMonster:
  def __init__(self, action=None):
    self.action = action
  def take_turn(self):
    monster = self.owner
    globals.fov_recompute(monster)
    target = None
    enemies = [creature for creature in globals.objects() if creature.fighter and creature.fighter.faction != monster.fighter.faction and libtcod.map_is_in_fov(globals.map().fov, creature.x, creature.y)]
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
      movement = False
      while movement is False:
        (x, y) = (libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1))
        if not globals.is_blocked(monster.x + x, monster.y + y):
          movement = True
          monster.move(x, y)

class PlayerControlled:
  def __init__(self, action=None):
    self.action = action
  def take_turn(self):
    self.action = 'didnt-take-turn'
    render.all(self.owner)
    libtcod.console_flush()
    while self.action == 'didnt-take-turn':
      self.action = get_input.handle_keys(self.owner)
    for object in globals.objects():
      render.clear(object)
    if self.owner.fighter:
      self.owner.fighter.check_status = True
