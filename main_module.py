# This is the main game file and it will be deliberately short.
import libtcodpy as libtcod # "The Doryen Library" v1.5.1 Source: https://bitbucket.org/libtcod/libtcod
import classes #Here are the classes shared between modules (Tile, Object and Rect).
import component #The game components are defined here.
import ai #Artificial Inteligence classes.
import cartographer #This handles the map object (tecniaclly a class but it deserves special treatment).
import demographic #Functions to generate creatures and items and populate areas.
import render #All related to displaying stuff on the screen.
import get_input #Self explainatory.
import globals #Here live some functions useful in many places

LIMIT_FPS = 20

# Screen size in tiles.
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 60

# Default map size. 
MAP_WIDTH = 65
MAP_HEIGHT = 53

# Size of the map display area (map can scroll).
CAMERA_WIDTH = 65
CAMERA_HEIGHT = 53

# Default parameters for dungeon generator (posibly other map generators).
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30

# This is used by demographic to populate rooms.
MAX_ROOM_MONSTERS = 7

# Initialize the game screen.
libtcod.console_set_custom_font('generic_rl_fnt.png', libtcod.FONT_TYPE_GRAYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Crooked Fang', False) 
libtcod.sys_set_fps(LIMIT_FPS)

# Player character initialization.
globals.init_player('new')

# Create level and populate it.
globals.init_map('new')
#globals.init_map('new', width=MAP_WIDTH, height=MAP_HEIGHT, map_function=cartographer.make_dungeon, max_rooms=MAX_ROOMS, min_room_size=ROOM_MIN_SIZE, max_room_size=ROOM_MAX_SIZE)
(globals.player().x, globals.player().y) = globals.map().rooms[0].center()
globals.objects().extend(demographic.populate_level(MAX_ROOM_MONSTERS))

globals.set_game_state('playing')
player_action = None

# Main loop.
while not libtcod.console_is_window_closed():
  render.all()
  render.blit_map(CAMERA_WIDTH, CAMERA_HEIGHT, globals.player())
  libtcod.console_flush()
  globals.player().fighter.check_state()
  player_action = get_input.handle_keys(globals.player())
  for object in globals.objects():
    render.clear(object)
  if player_action == 'exit':
    break
  if globals.get_game_state() == 'playing' and player_action != 'didnt-take-turn':
    for object in globals.objects():
      if object.fighter:
        object.fighter.check_state()
      if object.ai:
        object.ai.take_turn()
