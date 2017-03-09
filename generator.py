import libtcodpy as libtcod
import engine
import descriptor

def random_choice_index(chances):
  dice = libtcod.random_get_int(0, 1, sum(chances))
  running_sum = 0
  choice = 0
  for w in chances:
    running_sum += w
    if dice <= running_sum:
      return choice
    choice += 1

def random_choice(chances_dict):
  chances = chances_dict.values()
  strings = chances_dict.keys()
  return strings[random_choice_index(chances)]

def gen_creature(room=None, x=None, y=None):
  if room is not None and x is None:
    x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
    y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)
  if not engine.state().level_map.is_blocked(x, y):
    choice = random_choice(descriptor.creature_chances())
    creature = descriptor.creatures(choice, x, y)
    return creature

def gen_item(room=None, x=None, y=None):
  if room is not None and x is None:
    x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
    y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)
  if not engine.state().level_map.is_blocked(x, y):
    choice = random_choice(descriptor.item_chances())
    item = descriptor.items(choice, x, y)
    if item.equipment and item.equipment.slot == 'hand' and item.equipment.ammo == None and libtcod.random_get_int(0, 1, 100) <= 50:
      item.name = 'poisoned ' + item.name
      item.equipment.bonus_effect = descriptor.inflict_poison
    return item

def fill_level(max_room_monsters=None, max_room_items=None):
  if max_room_monsters is None:
    populate_level()
  else:
    populate_level(max_room_monsters)
  if max_room_items is None:
    level_items()
  else:
    level_items(max_room_items)

def populate_room(room, num_monsters):
  creature_list = []
  for i in range(num_monsters):
    creature = gen_creature(room)
    if creature is not None:
      creature_list.append(creature)
  return creature_list

def populate_level(max_room_monsters=descriptor.from_dungeon_level([[2, 1], [3, 4], [5, 6]])):
  final_list = []
  for room in engine.state().level_map.rooms:
    num_monsters = libtcod.random_get_int(0, 0, max_room_monsters)
    final_list.extend(populate_room(room, num_monsters))
  return final_list

def room_items(room, num_items):
  items_list = []
  for i in range(num_items):
    item = gen_item(room)
    if item is not None:
      items_list.append(item)
  return items_list

def level_items(max_room_items=descriptor.from_dungeon_level([[2, 1], [3, 4], [5, 6]])):
  final_list = []
  for room in engine.state().level_map.rooms:
    num_items = libtcod.random_get_int(0, 0, max_room_items)
    final_list.extend(room_items(room, num_items))
  return final_list

