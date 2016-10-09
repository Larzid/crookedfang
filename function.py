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
