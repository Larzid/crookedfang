import libtcodpy as libtcod

FOV_ALGO = 0
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10

def init_map_console(width, height):
  global con, con_width, con_height
  (con_width, con_height) = (width, height)
  con = libtcod.console_new(con_width, con_height)

def make_fov_map(map):
  global fov_map
  fov_map = libtcod.map_new(map.width, map.height)
  for y in range(map.height):
    for x in range(map.width):
      libtcod.map_set_properties(fov_map, x, y, not map.topography[x][y].block_sight, not map.topography[x][y].blocked)
  return fov_map

def fov_recompute(actor):
  libtcod.map_compute_fov(fov_map, actor.x, actor.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

def draw(object):
  if libtcod.map_is_in_fov(fov_map, object.x, object.y):
    libtcod.console_set_default_foreground(con, object.color)
    libtcod.console_put_char(con, object.x, object.y, object.char, libtcod.BKGND_NONE)

def clear(object):
  libtcod.console_put_char(con, object.x, object.y, ' ', libtcod.BKGND_NONE)

def map(map):
  for y in range(map.height):
    for x in range(map.width):
      visible = libtcod.map_is_in_fov(fov_map, x, y)
      wall = map.topography[x][y].block_sight
      if not visible:
        if map.topography[x][y].explored:
          libtcod.console_put_char_ex(con, x, y, map.topography[x][y].tile_face, map.topography[x][y].fore_dark, map.topography[x][y].back_dark)
      else:
        libtcod.console_put_char_ex(con, x, y, map.topography[x][y].tile_face, map.topography[x][y].fore_light, map.topography[x][y].back_light)
        map.topography[x][y].explored = True

def blit_map(width, height, center, map_width, map_height):
  x = center.x - (width/2)
  if x <= 0: x = 0
  if x + width >= map_width: x = map_width - width
  y = center.y - (height/2)
  if y <= 0: y = 0
  if y + height >= map_height: y = map_height - height 
  libtcod.console_blit(con, x, y, width, height, 0, 0, 0)
