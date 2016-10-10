import libtcodpy as libtcod
import component
import classes

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

def set_game_state(new_state):
  global game_state
  game_state = new_state

def get_game_state():
  state = game_state
  return state

def is_blocked (map, x, y, object_list):
  if map.topography[x][y].blocked:
    return True
  for object in object_list:
    if object.blocks and object.x == x and object.y == y:
      return True
  return False

def fov_recompute(actor, map):
  libtcod.map_compute_fov(map.fov, actor.x, actor.y, actor.fighter.sight, True, 0)

def inflict_poison(attacker, target):
  if libtcod.random_get_int(0, 1, 100) > target.fighter.poison_resist:
    target.fighter.state = 'poison'
    target.fighter.state_inflictor = attacker
#    if target == player or allies.count(target) > 0: 
    print target.name.capitalize() + ' has been poisoned by ' + attacker.name + '.'#, libtcod.purple)
#    if attacker == player or allies.count(attacker) > 0:
#      message(attacker.name.capitalize() + ' has poisoned ' + target.name + '.', libtcod.fuchsia)