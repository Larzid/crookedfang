import libtcodpy as libtcod
import component
import classes
import cartographer

def init_player(action):
  global player_object, objects_list
  if action == 'new':
    fighter_component = component.Fighter(faction='player', hp=100, defense=1, power=4, sight=7, poison_resist=30, death_function=component.player_death)
    player_object = classes.Object(0, 0, '@', 'player', libtcod.white, blocks=True, fighter=fighter_component)
    objects_list = [player_object]

def player():
  obj = player_object
  return obj

def objects():
  list = objects_list
  return list

def init_map(action, width=None, height=None, map_function=None, max_rooms=None, min_room_size=None, max_room_size=None):
  global level_map
  if action == 'new':
    if map_function is None:
      level_map = cartographer.Map(width, height)
    elif max_rooms == None:
      level_map = cartographer.Map(width, height, map_function)
    else:
      level_map = cartographer.Map(width, height, map_function, max_rooms, min_room_size, max_room_size)

def map():
  level = level_map
  return level

def set_game_state(new_state):
  global game_state
  game_state = new_state

def get_game_state():
  state = game_state
  return state

def is_blocked (x, y):
  if level_map.topography[x][y].blocked:
    return True
  for object in objects_list:
    if object.blocks and object.x == x and object.y == y:
      return True
  return False

def fov_recompute(actor):
  libtcod.map_compute_fov(level_map.fov, actor.x, actor.y, actor.fighter.sight, True, 0)

def inflict_poison(attacker, target):
  if libtcod.random_get_int(0, 1, 100) > target.fighter.poison_resist:
    target.fighter.state = 'poison'
    target.fighter.state_inflictor = attacker
#    if target == player_object: 
    print target.name.capitalize() + ' has been poisoned by ' + attacker.name + '.'#, libtcod.purple)
#    if attacker == player_object:
#      message(attacker.name.capitalize() + ' has poisoned ' + target.name + '.', libtcod.fuchsia)