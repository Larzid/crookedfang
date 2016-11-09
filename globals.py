import libtcodpy as libtcod
import combat
import classes
import cartographer
import generator
import textwrap
import ai
import shelve

# The Export class receives values from modules that import it and sets them as module-wise globals.
# Basically allows to get data from a module without havin to import it.
class Export:
  def msg_width(self, width):
    global MSG_WIDTH
    MSG_WIDTH = width

  def msg_height(self, height):
    global MSG_HEIGHT
    MSG_HEIGHT = height

# Global player reference.
def player():
  obj = player_object
  return obj

# Global map reference
def map():
  level = level_map
  return level

# Global object list reference
def objects():
  list = level_map.objects
  return list

def game_msgs():
  msgs = message_list
  return msgs

def init_game_msgs():
  global message_list
  message_list = []

def init_turn_counter():
  global turn_counter
  turn_counter = 0

def turn():
  global turn_counter
  counter = turn_counter
  return counter

def next_turn():
  global turn_counter
  turn_counter += 1

def init_level_counter():
  global level_counter, max_dungeon_level
  level_counter = 1
  max_dungeon_level = 1

def d_level():
  global level_counter
  counter = level_counter
  return counter

def max_d_level():
  global max_dungeon_level
  max_lvl = max_dungeon_level
  return max_lvl

# Player character initialization.
def init_player():
  global player_object
  fighter_component = combat.Fighter(faction='player', hp=100, defense=1, power=4, sight=7, poison_resist=30, xp_bonus=350, lvl_base=200, lvl_factor=150, inv_max=26, death_function=combat.player_death)
  ai_component = ai.PlayerControlled()
  player_object = classes.Object(0, 0, '@', 'player', libtcod.white, blocks=True, fighter=fighter_component, ai=ai_component)

# Map object initialization
def init_map(width=None, height=None, map_function=None, max_rooms=None, min_room_size=None, max_room_size=None):
  global level_map
  if width is None and height is None:
    if map_function is None:
      level_map = cartographer.Map()
    elif max_rooms == None:
      level_map = cartographer.Map(map_function=map_function)
    else:
      level_map = cartographer.Map(max_rooms, min_room_size, max_room_size)
  elif height is None:
    if map_function is None:
      level_map = cartographer.Map(width, width)
    elif max_rooms == None:
      level_map = cartographer.Map(width, width, map_function)
    else:
      level_map = cartographer.Map(width, width, map_function, max_rooms, min_room_size, max_room_size)
  else:
    if map_function is None:
      level_map = cartographer.Map(width, height)
    elif max_rooms == None:
      level_map = cartographer.Map(width, height, map_function)
    else:
      level_map = cartographer.Map(width, height, map_function, max_rooms, min_room_size, max_room_size)
  (player_object.x, player_object.y) = level_map.rooms[0].center()
  level_map.objects.append(player_object)
  level_map.objects.extend(generator.populate_level())
  level_map.objects.extend(generator.level_items())
  for object in level_map.objects:
    if object.item:
      object.send_to_back() 

# Start new game.
def new_game():
  init_player()
#  globals.init_map()
  init_map(map_function=cartographer.make_dungeon)
  init_game_msgs()
  init_turn_counter()
  init_level_counter()
  message('You were bored, you craved adventure and due to your total lack of common sense and reckless impulsive behavior you came here, to some strange ruins half a world away from what you call civilization!', libtcod.light_cyan)
  message('Did you at least told somebody what you where up to?', libtcod.crimson)
  message('Well, its kinda late for that.', libtcod.light_purple)

# Main loop.
def play_game():
  while not libtcod.console_is_window_closed():
    next_turn()
    for object in level_map.objects:
      if object.fighter and object.fighter.check_status:
        object.fighter.status_check()
      if object.fighter and object.ai:
        object.ai.take_turn()
    if player_object.ai.action == 'exit':
      break

def save_game():
  player_index = level_map.objects.index(player_object)
  level_map.objects.pop(player_index)
  file = shelve.open('savegame', 'n')
  file['map'] = level_map
  file['player'] = player_object
  file['messages'] = message_list
  file['turn'] = turn_counter
  file['d_level'] = level_counter
  file['max_d_lvl'] = max_dungeon_level
  file.close()

def load_game():
  global level_map, player_object, message_list, turn_counter, level_counter, max_dungeon_level
  file = shelve.open('savegame', 'r')
  level_map = file['map']
  level_map.fov = level_map.make_fov_map()
  player_object = file['player']
  level_map.objects.insert(0, player_object)
  message_list = file['messages']
  turn_counter = file['turn']
  level_counter = file['d_level']
  max_dungeon_level = file['max_d_lvl']
  file.close()

def is_blocked (x, y):
  if level_map.topography[x][y].blocked:
    return True
  for object in level_map.objects:
    if object.blocks and object.x == x and object.y == y:
      return True
  return False

def fov_recompute(actor):
  libtcod.map_compute_fov(level_map.fov, actor.x, actor.y, actor.fighter.sight, True, 0)

def message(new_msg, color = libtcod.white):
  new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)
  for line in new_msg_lines:
    if len(message_list) == MSG_HEIGHT:
      del message_list[0]
    message_list.append( (line, color) )

def closest_enemy(actor, max_range):
  closest_creature = None
  closest_dist = max_range + 1
  for object in level_map.objects:
    if object.fighter and not object == actor and object.ai and object.ai.state != 'dead' and object.fighter and object.fighter.faction != actor.fighter.faction and libtcod.map_is_in_fov(level_map.fov, object.x, object.y):
      dist = actor.distance_to(object)
      if dist < closest_dist:
        closest_creature = object
        closest_dist = dist
  return closest_creature

def inflict_poison(attacker, target):
  if libtcod.random_get_int(0, 1, 100) > target.fighter.poison_resist:
    target.fighter.status = 'poison'
    target.fighter.status_inflictor = attacker
    if target == player_object: 
      message(target.name.capitalize() + ' has been poisoned by ' + attacker.name + '.', libtcod.purple)
    if attacker == player_object:
      message(attacker.name.capitalize() + ' has poisoned ' + target.name + '.', libtcod.fuchsia)
