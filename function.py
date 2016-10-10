import libtcodpy as libtcod

def is_blocked (map, x, y, object_list):
  if map.topography[x][y].blocked:
    return True
  for object in object_list:
    if object.blocks and object.x == x and object.y == y:
      return True
  return False

def fov_recompute(actor, map):
  libtcod.map_compute_fov(map.fov, actor.x, actor.y, actor.fighter.sight, True, 0)

def inflict_poison(attacker, target):
  if libtcod.random_get_int(0, 1, 100) > target.fighter.poison_resist:
    target.fighter.state = 'poison'
    target.fighter.state_inflictor = attacker
#    if target == player or allies.count(target) > 0: 
    print target.name.capitalize() + ' has been poisoned by ' + attacker.name + '.'#, libtcod.purple)
#    if attacker == player or allies.count(attacker) > 0:
#      message(attacker.name.capitalize() + ' has poisoned ' + target.name + '.', libtcod.fuchsia)