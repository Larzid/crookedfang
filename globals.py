import libtcodpy as libtcod
import combat
import classes
import cartographer
import demographic
import textwrap
import ai

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

def set_game_state(new_state):
  global game_state
  game_state = new_state

def get_game_state():
  state = game_state
  return state

def game_msgs():
  msgs = mesage_list
  return msgs

def init_game_msgs(action):
  global mesage_list
  if action == 'new':
    mesage_list = []

def init_turn_counter(action):
  global turn_counter
  if action == 'new':
    turn_counter = 0

def turn():
  global turn_counter
  counter = turn_counter
  return counter

def next_turn():
  global turn_counter
  turn_counter += 1

# Player character initialization.
def init_player(action):
  global player_object
  if action == 'new':
    fighter_component = combat.Fighter(faction='player', hp=100, defense=1, power=4, sight=7, poison_resist=30, death_function=combat.player_death)
    ai_component = ai.PlayerControlled()
    player_object = classes.Object(0, 0, '@', 'player', libtcod.white, blocks=True, fighter=fighter_component, ai=ai_component)

# Map object initialization
def init_map(action, width=None, height=None, map_function=None, max_rooms=None, min_room_size=None, max_room_size=None):
  global level_map
  if action == 'new':
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
  level_map.objects.extend(demographic.populate_level())

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
    if len(mesage_list) == MSG_HEIGHT:
      del mesage_list[0]
    mesage_list.append( (line, color) )

def inflict_poison(attacker, target):
  if libtcod.random_get_int(0, 1, 100) > target.fighter.poison_resist:
    target.fighter.status = 'poison'
    target.fighter.status_inflictor = attacker
    if target == player_object: 
      message(target.name.capitalize() + ' has been poisoned by ' + attacker.name + '.', libtcod.purple)
    if attacker == player_object:
      message(attacker.name.capitalize() + ' has poisoned ' + target.name + '.', libtcod.fuchsia)
