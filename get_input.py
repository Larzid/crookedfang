import libtcodpy as libtcod
import render

def handle_keys(game_state, actor, map, object_list):
  key = libtcod.console_wait_for_keypress(True)
  if key.vk == libtcod.KEY_ENTER and key.lalt:
    libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
  elif key.vk == libtcod.KEY_ESCAPE:
    return 'exit'
  if game_state == 'playing':
    if libtcod.console_is_key_pressed(libtcod.KEY_UP):
      move_or_attack(actor, map, 0, -1, object_list)
    elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
      move_or_attack(actor, map, 0, 1, object_list)
    elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
      move_or_attack(actor, map, -1, 0, object_list)
    elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
      move_or_attack(actor, map, 1, 0, object_list)
    else: return 'didn-take-turn'

def move_or_attack(actor, map, dx, dy, object_list):
  x = actor.x + dx
  y = actor.y + dy
  target = None
  for object in object_list:
    if object.x == x and object.y == y:
      target = object
      break
  if target is not None:
    print 'The ' + target.name + ' laughs at your attacks!'
  else:
    actor.move(map, dx, dy, object_list)
    render.fov_recompute(actor)