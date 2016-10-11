import libtcodpy as libtcod
import globals

# Screen size in tiles.
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 60
LIMIT_FPS = 20

# Size of the map display area (map can scroll).
CAMERA_WIDTH = 65
CAMERA_HEIGHT = 53

def init_screen():
  libtcod.console_set_custom_font('generic_rl_fnt.png', libtcod.FONT_TYPE_GRAYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
  libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Crooked Fang', False) 
  libtcod.sys_set_fps(LIMIT_FPS)

def init_ui():
  global con, con_width, con_height
  (con_width, con_height) = (globals.map().width, globals.map().height)
  con = libtcod.console_new(con_width, con_height)

def all(): # Call the functions to draw everything in the screen.
  globals.fov_recompute(globals.player())
  lvl()
  for object in globals.objects():
    if object != globals.player():
      draw(object)
  draw(globals.player())

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

def blit_map(center):
  x = center.x - (CAMERA_WIDTH/2)
  if x <= 0: x = 0
  if x + CAMERA_WIDTH >= globals.map().width: x = globals.map().width - CAMERA_WIDTH
  y = center.y - (CAMERA_HEIGHT/2)
  if y <= 0: y = 0
  if y + CAMERA_HEIGHT >= globals.map().height: y = globals.map().height - CAMERA_HEIGHT 
  libtcod.console_blit(con, x, y, CAMERA_WIDTH, CAMERA_HEIGHT, 0, 0, 0)
