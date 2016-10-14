import libtcodpy as libtcod
import globals
import classes
import get_input

# Screen size in tiles.
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 60
LIMIT_FPS = 20

# Size of the map display area (map can scroll).
CAMERA_WIDTH = 65
CAMERA_HEIGHT = 53

BAR_WIDTH = 13

# When importing globals: value (value) to globals.
export = globals.Export()
export.msg_width(SCREEN_WIDTH - 2)
export.msg_height(SCREEN_HEIGHT - CAMERA_HEIGHT - 1)

def init_screen():
  libtcod.console_set_custom_font('generic_rl_fnt.png', libtcod.FONT_TYPE_GRAYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
  libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Crooked Fang', False) 
  libtcod.sys_set_fps(LIMIT_FPS)

def init_ui():
  global con, con_width, con_height, side_panel, msg_panel, cursor
  (con_width, con_height) = (globals.map().width, globals.map().height)
  con = libtcod.console_new(con_width, con_height)
  side_panel = libtcod.console_new(SCREEN_WIDTH - CAMERA_WIDTH, CAMERA_HEIGHT)
  msg_panel = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT - CAMERA_HEIGHT)
  cursor = classes.Object(0, 0, '', 'cursor', libtcod.white)

def all(actor): # Call the functions to draw everything in the screen.
  globals.fov_recompute(actor)
  map()
  for object in globals.objects():
    if object != actor:
      draw(object)
  draw(actor)
  blit_map(actor)
  side_bar(actor)
  msg_bar(actor)

def map():
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

def draw(object):
#  if libtcod.map_is_in_fov(globals.map().fov, object.x, object.y):
    libtcod.console_set_default_foreground(con, object.color)
    libtcod.console_put_char(con, object.x, object.y, object.char, libtcod.BKGND_NONE)

def clear(object):
  libtcod.console_put_char(con, object.x, object.y, ' ', libtcod.BKGND_NONE)

def blit_map(center):
  x = center.x - (CAMERA_WIDTH/2)
  if x <= 0: x = 0
  if x + CAMERA_WIDTH >= globals.map().width: x = globals.map().width - CAMERA_WIDTH
  y = center.y - (CAMERA_HEIGHT/2)
  if y <= 0: y = 0
  if y + CAMERA_HEIGHT >= globals.map().height: y = globals.map().height - CAMERA_HEIGHT 
  libtcod.console_blit(con, x, y, CAMERA_WIDTH, CAMERA_HEIGHT, 0, 0, 0)

def side_bar(actor):
  libtcod.console_set_default_background(side_panel, libtcod.black)
  libtcod.console_clear(side_panel)
  if actor == globals.player(): libtcod.console_print_frame(side_panel,0, 2, 15, 10, clear=True)
  libtcod.console_print_ex(side_panel, 1 , 3, libtcod.BKGND_NONE, libtcod.LEFT, globals.player().name.capitalize() + ' lvl: ' + str(globals.player().fighter.level))
  render_bar(1, 5, BAR_WIDTH, 'HP', globals.player().fighter.hp, globals.player().fighter.max_hp, libtcod.light_red, libtcod.darker_red)
  render_bar(1, 7, BAR_WIDTH, 'XP', globals.player().fighter.xp, globals.player().fighter.lvl_base + globals.player().fighter.level * globals.player().fighter.lvl_factor, libtcod.light_purple, libtcod.darker_purple)
  libtcod.console_print_ex(side_panel, 1 , 9, libtcod.BKGND_NONE, libtcod.LEFT, 'Def: ' + str(globals.player().fighter.defense) )# + ' + ' + str(sum(equip.equipment.defense_bonus for equip in globals.player().fighter.equipment.values() if equip is not None)))
  libtcod.console_print_ex(side_panel, 1 , 10, libtcod.BKGND_NONE, libtcod.LEFT, 'Pow: ' + str(globals.player().fighter.power) )# + ' + ' + str(sum(equip.equipment.power_bonus for equip in globals.player().fighter.equipment.values() if equip is not None)))
#  libtcod.console_print_ex(side_panel, 1, 1, libtcod.BKGND_NONE, libtcod.LEFT, 'D. level ' + str(dungeon_level))
  libtcod.console_blit(side_panel, 0, 0, SCREEN_WIDTH - CAMERA_WIDTH, CAMERA_HEIGHT, 0, CAMERA_WIDTH, 0) 

def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
  bar_width = int(float(value) / maximum * total_width)
  libtcod.console_set_default_background(side_panel, back_color)
  libtcod.console_rect(side_panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)
  libtcod.console_set_default_background(side_panel, back_color)
  if bar_width > 0:
    libtcod.console_rect(side_panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)
  libtcod.console_set_default_foreground(side_panel, libtcod.white)
  libtcod.console_print_ex(side_panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER, name + ': ' + str(value) + '/' + str(maximum))

def msg_bar(actor):
  libtcod.console_set_default_background(msg_panel, libtcod.black)
  libtcod.console_clear(msg_panel)
  y = 1
  for (line, color) in globals.game_msgs():
    libtcod.console_set_default_foreground(msg_panel, color)
    libtcod.console_print_ex(msg_panel, 1, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
    y += 1
  if actor.ai.state == 'playing':
    standing = [obj.name for obj in globals.objects() if obj.x == actor.x and obj.y == actor.y and obj.name != actor.name]
    if not len(standing) == 0:
      standing = ', '.join(standing)
      libtcod.console_set_default_foreground(msg_panel, libtcod.light_gray)
      libtcod.console_print_ex(msg_panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, 'Standing on: ' + standing)
  if actor.ai.state == 'looking':
    libtcod.console_set_default_foreground(msg_panel, libtcod.light_gray)
    libtcod.console_print_ex(msg_panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, 'Looking at: ' + look_names())
#  if actor.ai.state == 'target':
#    libtcod.console_set_default_foreground(msg_panel, libtcod.light_gray)
#    libtcod.console_print_ex(msg_panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, 'Target: ' + look_names())
  libtcod.console_blit(msg_panel, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT - CAMERA_HEIGHT, 0, 0, CAMERA_HEIGHT)

def look_names():
  (x, y) = (cursor.x, cursor.y)
  names = []
  for obj in globals.objects():
    if obj.x == x and obj.y == y and libtcod.map_is_in_fov(globals.map().fov, obj.x, obj.y):
      if obj.fighter:
        names.append(obj.name + '(lv' + str(obj.fighter.level) +')')
      else:
        names.append(obj.name)
  if len(names) != 0:
    names = ', '.join(names)
  else:
    names = 'Nothing'
  return names.capitalize()

def start_cursor(x, y):
  global old_fore, old_back
  (cursor.x, cursor.y) = (x, y)
  old_back = globals.map().topography[cursor.x][cursor.y].back_light
  old_fore = globals.map().topography[cursor.x][cursor.y].fore_light
  globals.map().topography[cursor.x][cursor.y].back_light = libtcod.black
  globals.map().topography[cursor.x][cursor.y].fore_light = libtcod.white

def cursor_move(dx, dy):
  if libtcod.map_is_in_fov(globals.map().fov, cursor.x + dx, cursor.y + dy):
    clear_cursor()
    start_cursor(cursor.x + dx, cursor.y + dy)

def clear_cursor():
  globals.map().topography[cursor.x][cursor.y].back_light = old_back
  globals.map().topography[cursor.x][cursor.y].fore_light = old_fore

def get_cursor():
  tuple = (cursor.x, cursor.y)
  return tuple

def menu(header, options, width):
  if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options')
  header_height = libtcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
  if header == '':
    header_height =0
  height = len(options) + header_height
  window = libtcod.console_new(width, height)
  libtcod.console_set_default_foreground(window, libtcod.white)
  libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)
  y = header_height
  letter_index = ord('a')
  for (option_text, option_color) in options:
    text = '(' + chr(letter_index) + ')' + option_text
    libtcod.console_set_default_foreground(window, option_color)
    libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
    y += 1
    letter_index += 1
  x = SCREEN_WIDTH/2 - width/2
  y = SCREEN_HEIGHT/2 - height/2
  libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)
  libtcod.console_flush()
  while True:
    key = get_input.block_for_key()
    if not (key.vk == libtcod.KEY_ALT or key.vk == libtcod.KEY_CONTROL or key.vk == libtcod.KEY_SHIFT):
      break
  if key.vk == libtcod.KEY_ENTER and key.lalt:
      libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
  index = key.c - ord('a')
  if index >=0 and index < len(options): return index
  return None

def msgbox(text, width=50):
  menu(text,[], width)
  libtcod.console_wait_for_keypress(True)
