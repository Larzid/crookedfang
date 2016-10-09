import libtcodpy as libtcod
import classes
import function

def gen_creature(room=None, x=None, y=None):
  if room is not None and x is None:
    x = libtcod.random_get_int(0, room.x1, room.x2)
    y = libtcod.random_get_int(0, room.y1, room.y2)
  if libtcod.random_get_int(0, 0, 100) < 80:
    creature = classes.Object(x, y, 'o', 'orc', libtcod.desaturated_green, blocks=True)
  else:
    creature = classes.Object(x, y, 'T', 'troll', libtcod.darker_green, blocks=True)
  return creature

def populate_room(room, num_monsters):
  creature_list = []
  for i in range(num_monsters):
    creature_list.append(gen_creature(room))
  return creature_list

def populate_level(room_list, max_room_monsters):
  creature_list = []
  num_monsters = libtcod.random_get_int(0, 0, max_room_monsters)
  for room in room_list:
    creature_list.extend(populate_room(room, num_monsters))
  return creature_list
