import libtcodpy as libtcod
import function

class BasicMonster:
  def take_turn(self, level_map, object_list):
    monster = self.owner
    function.fov_recompute(monster, level_map)
    target = None
    enemies = [creature for creature in object_list if creature.fighter and creature.fighter.faction != monster.fighter.faction and libtcod.map_is_in_fov(level_map.fov, creature.x, creature.y)]
    if len(enemies) > 0:
      closest_dist = monster.fighter.sight + 1
      for object in enemies:
        dist = monster.distance_to(object)
        if dist < closest_dist:
          target = object
          closest_dist = dist
    if target is not None:
      if monster.distance_to(target) >= 2:
        monster.move_astar(level_map, target, object_list)
      elif target.fighter.hp > 0:
        print 'The ' + self.owner.name + ' punches you!'
#        monster.fighter.attack(target)
    else:
      movement = False
      while movement is False:
        (x, y) = (libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1))
        if not function.is_blocked(level_map, monster.x + x, monster.y + y, object_list):
          movement = True
          monster.move(level_map, x, y, object_list)
    print 'The ' + self.owner.name + ' growls!'