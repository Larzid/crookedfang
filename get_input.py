import libtcodpy as libtcod
import render
import globals

def block_for_key():
  while True:
    key = libtcod.console_check_for_keypress(True)
    if (key.vk == libtcod.KEY_NONE):
      continue
    if (key.vk == libtcod.KEY_ALT or key.vk == libtcod.KEY_SHIFT or key.vk == libtcod.KEY_CONTROL):
      continue
    break
  return key

def handle_keys(actor):
  key = block_for_key()
  if key.vk == libtcod.KEY_ENTER and key.lalt:
    libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
  elif key.vk == libtcod.KEY_ESCAPE:
    return 'exit'
  if actor.ai.state == 'playing':
    if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
      move_or_attack(actor, 0, -1)
    elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
      move_or_attack(actor, 0, 1)
    elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
      move_or_attack(actor, -1, 0)
    elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
      move_or_attack(actor, 1, 0)
    elif key.vk == libtcod.KEY_HOME or key.vk == libtcod.KEY_KP7:
      move_or_attack(actor, -1, -1)
    elif key.vk == libtcod.KEY_PAGEUP or key.vk == libtcod.KEY_KP9:
      move_or_attack(actor, 1, -1)
    elif key.vk == libtcod.KEY_END or key.vk == libtcod.KEY_KP1:
      move_or_attack(actor, -1, 1)
    elif key.vk == libtcod.KEY_PAGEDOWN or key.vk == libtcod.KEY_KP3:
      move_or_attack(actor, 1, 1)
    elif key.vk == libtcod.KEY_KP5:
      pass
    else:
      key_char = chr(key.c)
      if key_char == 'l':
        action = look(actor)
        return action
      return 'didnt-take-turn'

def look(actor):
  actor.ai.state = 'looking'
  render.start_cursor(actor.x, actor.y)
  render.all(actor)
  libtcod.console_flush()
  while actor.ai.state == 'looking':
    key = block_for_key()
    if key.vk == libtcod.KEY_ENTER and (key.lalt or key.ralt):
      libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    elif key.vk == libtcod.KEY_ESCAPE:
      actor.ai.state == 'playing'
      return 'exit'
    elif key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
      render.cursor_move(0, -1)
    elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
      render.cursor_move(0, 1)
    elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
      render.cursor_move(-1, 0)
    elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
      render.cursor_move(1, 0)
    elif key.vk == libtcod.KEY_HOME or key.vk == libtcod.KEY_KP7:
      render.cursor_move(-1, -1)
    elif key.vk == libtcod.KEY_PAGEUP or key.vk == libtcod.KEY_KP9:
      render.cursor_move(1, -1)
    elif key.vk == libtcod.KEY_END or key.vk == libtcod.KEY_KP1:
      render.cursor_move(-1, 1)
    elif key.vk == libtcod.KEY_PAGEDOWN or key.vk == libtcod.KEY_KP3:
      render.cursor_move(1, 1)
    else:
      key_char = chr(key.c)
      if key_char == 'l':
        render.clear_cursor()
        actor.ai.state = 'playing'
        return 'didnt-take-turn'
    render.all(actor)
    libtcod.console_flush()

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
