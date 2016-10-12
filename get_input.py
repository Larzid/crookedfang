import libtcodpy as libtcod
import render
import globals

def handle_keys(actor):
  key = libtcod.console_wait_for_keypress(True)
  if key.vk == libtcod.KEY_ENTER and key.lalt:
    libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
  elif key.vk == libtcod.KEY_ESCAPE:
    return 'exit'
  if actor.ai.state == 'playing':
    if libtcod.console_is_key_pressed(libtcod.KEY_UP):
      move_or_attack(actor, 0, -1)
    elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
      move_or_attack(actor, 0, 1)
    elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
      move_or_attack(actor, -1, 0)
    elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
      move_or_attack(actor, 1, 0)
    else: return 'didnt-take-turn'

def move_or_attack(actor, dx, dy):
  x = actor.x + dx
  y = actor.y + dy
  target = None
  for object in globals.objects():
    if object.x == x and object.y == y and object.fighter:
      target = object
      break
  if target is not None:
    actor.fighter.attack(target)
  else:
    actor.move(dx, dy)
    globals.fov_recompute(actor)
