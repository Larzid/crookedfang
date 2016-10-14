import libtcodpy as libtcod
import render
import globals

INVENTORY_WIDTH = 50

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
      elif key_char == 'g':
        for object in globals.objects():
          if object.x == actor.x and object.y == actor.y and object.item:
            object.item.pick_up(actor)
            break
        return 'didnt-take-turn'
      elif key_char == 'i':
        chosen_item = inventory_menu(actor, 'Press the key next to an item to use it, or any other to cancel.\n')
        if chosen_item is not None:
          chosen_item.use(actor)
        else: return 'didnt-take-turn'
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

def target_enemy(actor):
  creatures = [obj for obj in globals.objects() if obj.fighter and obj != actor and libtcod.map_is_in_fov(globals.map().fov, obj.x, obj.y)]
  if len(creatures) == 0: 
    globals.message('No enemies in range', libtcod.red)
    return None
  index = 0
  render.start_cursor(creatures[index].x, creatures[index].y)
  actor.ai.state = 'target'
  render.all(actor)
  libtcod.console_flush()
  while actor.ai.state == 'target':
    key = block_for_key()
    if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8 or key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
      render.clear_cursor()
      index += 1
      if index > len(creatures)-1: index = 0
      render.start_cursor(creatures[index].x, creatures[index].y)
    if key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2 or key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
      render.clear_cursor()
      index -= 1
      if index < 0: index = len(creatures)-1
      render.start_cursor(creatures[index].x, creatures[index].y)
    if key.vk == libtcod.KEY_BACKSPACE:
      render.clear_cursor()
      actor.ai.state = 'playing'
      return None
    if key.vk == libtcod.KEY_ENTER or key.vk == libtcod.KEY_KPENTER:
      render.clear_cursor()
      actor.ai.state = 'playing'
      return creatures[index]
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

def inventory_menu(actor, header):
  if len(actor.fighter.inventory) == 0:
    options = [('Inventory is empty.', libtcod.white)]
  else:
    options = [(' ' + str(item.item.qty) + ' ' + item.char + ' ' + item.name, item.color) for item in actor.fighter.inventory]
  index = render.menu(header, options, INVENTORY_WIDTH)
  if index is None or len(actor.fighter.inventory) == 0: return None
  return actor.fighter.inventory[index].item
