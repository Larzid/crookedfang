import libtcodpy as libtcod
import classes
import component
import ai
import globals

def gen_creature(room=None, x=None, y=None):
  if room is not None and x is None:
    x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
    y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)
  choice = libtcod.random_get_int(0, 0, 100)
  if choice <= 50:
    fighter_component = component.Fighter(faction='wild', hp=10, defense=0, power=3, sight=15, poison_resist=80, death_function=component.monster_death, nat_atk_effect=globals.inflict_poison)
    ai_component = ai.BasicMonster()
    creature = classes.Object(x, y, 's', 'snake', libtcod.darker_red, blocks=True, fighter=fighter_component, ai=ai_component)
  elif choice <= 80:
    fighter_component = component.Fighter(faction='dungeon', hp=20, defense=0, power=4, sight=10, poison_resist=20, death_function=component.monster_death)
    ai_component = ai.BasicMonster()
    creature = classes.Object(x, y, 'o', 'orc', libtcod.desaturated_green, blocks=True, fighter=fighter_component, ai=ai_component)
  else:
    fighter_component = component.Fighter(faction='dungeon', hp=30, defense=2, power=8, sight=5, poison_resist=30, death_function=component.monster_death)
    ai_component = ai.BasicMonster()
    creature = classes.Object(x, y, 'T', 'troll', libtcod.darker_green, blocks=True, fighter=fighter_component, ai=ai_component)
  return creature

def populate_room(room, num_monsters):
  creature_list = []
  for i in range(num_monsters):
    creature = gen_creature(room)
    creature_list.append(creature)
  return creature_list

def populate_level(max_room_monsters):
  final_list = []
  for room in globals.map().rooms:
    num_monsters = libtcod.random_get_int(0, 0, max_room_monsters)
    final_list.extend(populate_room(room, num_monsters))
  return final_list
