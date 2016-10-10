import libtcodpy as libtcod
import globals

def all(): # Call the functions to draw everything in the screen.
  globals.fov_recompute(globals.player())
  lvl()
  for object in globals.objects():
    if object != globals.player():
      draw(object)
  draw(globals.player())

def init_map_console():
  global con, con_width, con_height
  (con_width, con_height) = (globals.map().width, globals.map().height)
  con = libtcod.console_new(con_width, con_height)

def draw(object):
#  if libtcod.map_is_in_fov(globals.map().fov, object.x, object.y):
    libtcod.console_set_default_foreground(con, object.color)
    libtcod.console_put_char(con, object.x, object.y, object.char, libtcod.BKGND_NONE)

def clear(object):
  libtcod.console_put_char(con, object.x, object.y, ' ', libtcod.BKGND_NONE)

def lvl():
  for y in range(globals.map().height):
    for x in range(globals.map().width):
      visible = libtcod.map_is_in_fov(globals.map().fov, x, y)
      wall = globals.map().topography[x][y].block_sight
      if not visible:
#        if globals.map().topography[x][y].explored:
        libtcod.console_put_char_ex(con, x, y, globals.map().topography[x][y].tile_face, globals.map().topography[x][y].fore_dark, globals.map().topography[x][y].back_dark)
      else:
        libtcod.console_put_char_ex(con, x, y, globals.map().topography[x][y].tile_face, globals.map().topography[x][y].fore_light, globals.map().topography[x][y].back_light)
        globals.map().topography[x][y].explored = True

def blit_map(width, height, center):
  x = center.x - (width/2)
  if x <= 0: x = 0
  if x + width >= globals.map().width: x = globals.map().width - width
  y = center.y - (height/2)
  if y <= 0: y = 0
  if y + height >= globals.map().height: y = globals.map().height - height 
  libtcod.console_blit(con, x, y, width, height, 0, 0, 0)
