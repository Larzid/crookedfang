# This is the main game file and it will be deliberately short.
import libtcodpy as libtcod # "The Doryen Library" v1.5.1 Source: https://bitbucket.org/libtcod/libtcod
import classes #Here are the classes shared between modules (Tile, Object and Rect).
import component #The game components are defined here.
import ai #Artificial Inteligence classes.
import cartographer #This handles the map object (tecniaclly a class but it deserves special treatment).
import demographic #Functions to generate creatures and items and populate areas.
import render #All related to displaying stuff on the screen.
import get_input #Self explainatory.
import function #Here live some functions useful in many places

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
MAX_ROOM_MONSTERS = 3

def render_all(): # Call the functions to draw everything in the screen.
  function.fov_recompute(player, level_map)
  render.map(level_map)
  for object in objects:
    render.draw(object, level_map)

# Initialize the game screen.
libtcod.console_set_custom_font('generic_rl_fnt.png', libtcod.FONT_TYPE_GRAYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Crooked Fang', False) 
render.init_map_console(MAP_WIDTH, MAP_HEIGHT) # Create an off-screen console for the map.
libtcod.sys_set_fps(LIMIT_FPS)

# Player character initialization.
fighter_component = component.Fighter(faction='player', hp=100, defense=1, power=4, sight=7, poison_resist=30)
player = classes.Object(0, 0, '@', 'player', libtcod.white, blocks=True, fighter=fighter_component)
objects = [player]

# Create level and populate it.
level_map = cartographer.Map(width=MAP_WIDTH, height=MAP_HEIGHT)
#level_map =cartographer.Map(width=MAP_WIDTH, height=MAP_HEIGHT, map_function=cartographer.make_dungeon, max_rooms=MAX_ROOMS, min_room_size=ROOM_MIN_SIZE, max_room_size=ROOM_MAX_SIZE)
(player.x, player.y) = level_map.rooms[0].center()
objects.extend(demographic.populate_level(level_map.rooms, MAX_ROOM_MONSTERS))

game_state = 'playing'
player_action = None

# Main loop.
while not libtcod.console_is_window_closed():
  render_all()
  render.blit_map(CAMERA_WIDTH, CAMERA_HEIGHT, player, level_map.width, level_map.height)
  libtcod.console_flush()
  player.fighter.check_state()
  player_action = get_input.handle_keys(game_state, player, level_map, objects)
  for object in objects:
    render.clear(object)
  if player_action == 'exit':
    break
  if game_state == 'playing' and player_action != 'didnt-take-turn':
    for object in objects:
      if object.ai:
        object.fighter.check_state()
        object.ai.take_turn(level_map, objects)
