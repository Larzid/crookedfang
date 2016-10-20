import libtcodpy as libtcod
import classes
import combat
import ai
import thing
import magic
import globals

# This is used by demographic to populate rooms.
MAX_ROOM_MONSTERS = 3
MAX_ROOM_ITEMS = 2

def gen_creature(room=None, x=None, y=None):
  if room is not None and x is None:
    x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
    y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)
  if not globals.is_blocked(x, y):
    choice = libtcod.random_get_int(0, 0, 100)
    if choice < 50:
      fighter_component = combat.Fighter(faction='wild', hp=10, defense=0, power=3, sight=15, poison_resist=80, xp_bonus=20, lvl_base=20, lvl_factor=15, death_function=combat.monster_death, nat_atk_effect=globals.inflict_poison)
      ai_component = ai.BasicMonster()
      creature = classes.Object(x, y, 's', 'snake', libtcod.darker_red, blocks=True, fighter=fighter_component, ai=ai_component)
    elif choice < 50 + 30:
      fighter_component = combat.Fighter(faction='dungeon', hp=20, defense=0, power=4, sight=10, poison_resist=20, xp_bonus=35, lvl_base=40, lvl_factor=20, death_function=combat.monster_death)
      ai_component = ai.BasicMonster()
      creature = classes.Object(x, y, 'o', 'orc', libtcod.desaturated_green, blocks=True, fighter=fighter_component, ai=ai_component)
    else:
      fighter_component = combat.Fighter(faction='dungeon', hp=30, defense=2, power=8, sight=5, poison_resist=30, xp_bonus=100, lvl_base=200, lvl_factor=150, death_function=combat.monster_death)
      ai_component = ai.BasicMonster()
      creature = classes.Object(x, y, 'T', 'troll', libtcod.darker_green, blocks=True, fighter=fighter_component, ai=ai_component)
    return creature

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

def populate_level(max_room_monsters=MAX_ROOM_MONSTERS):
  final_list = []
  for room in globals.map().rooms:
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

def level_items(max_room_items=MAX_ROOM_ITEMS):
  final_list = []
  for room in globals.map().rooms:
    num_items = libtcod.random_get_int(0, 0, max_room_items)
    final_list.extend(room_items(room, num_items))
  return final_list

def gen_item(room=None, x=None, y=None):
  if room is not None and x is None:
    x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
    y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)
  if not globals.is_blocked(x, y):
    choice = libtcod.random_get_int(0, 0, 100)
    if choice < 10:
      item_component = thing.Item(1, use_function=scroll)
      spell_component = magic.Spell(power=25, spell_range =3 , effect=magic.cast_fireball)
      item = classes.Object(x, y, chr(151), 'scroll of fireball', libtcod.red, item=item_component, spell=spell_component)
    elif choice < 10 + 10:
      item_component = thing.Item(1, use_function=scroll)
      spell_component = magic.Spell(power=40, spell_range =5 , effect=magic.cast_lightning)
      item = classes.Object(x, y, chr(151), 'scroll of lightning bolt', libtcod.light_yellow, item=item_component, spell=spell_component)
    elif choice <= 10 + 10 + 10:
      item_component = thing.Item(1, use_function=scroll)
      spell_component = magic.Spell(power=10, spell_range =5 , effect=magic.cast_confuse)
      item = classes.Object(x, y, chr(151), 'scroll of confusion', libtcod.purple, item=item_component, spell=spell_component)
    else:# choice <= 100:
      item_component = thing.Item(1, use_function=scroll)
      spell_component = magic.Spell(power=40, effect=magic.cast_heal)
      item = classes.Object(x, y, chr(144), 'healing potion', libtcod.violet, item=item_component, spell=spell_component)
    return item
#    elif choice == 5:
#      item_component = thing.Item(1, use_function=scroll)
#      spell_component = magic.Spell(power=10, spell_range =5 , effect=magic.cast_possess)
#      item = classes.Object(0, 0, chr(151), 'scroll of possession', libtcod.green, item=item_component, spell=spell_component)
#    elif choice == 'sword':
#      equipment_component = Equipment(slot='hand', power_bonus = 3)
#      item = classes.Object(x, y, chr(148), 'sword', libtcod.sky, equipment=equipment_component)
#    elif choice == 'machete':
#      equipment_component = Equipment(slot='hand', power_bonus = 2)
#      item = classes.Object(x, y, chr(148), 'machete', libtcod.gray, equipment=equipment_component)
#    elif choice == 'dagger':
#      equipment_component = Equipment(slot='hand', power_bonus = 1)
#      item = classes.Object(x, y, chr(150), 'dagger', libtcod.silver, equipment=equipment_component)
#    elif choice == 'throwing knife':
#      item_component = thing.Item(1, projectile_bonus = 2, use_function=projectile)
#      item = classes.Object(x, y, chr(150), 'throwing knife', libtcod.light_blue, item=item_component)
#    elif choice == 'bow':
#      equipment_component = Equipment(slot='hand', ammo='arrow', power_bonus = 1)
#      item = classes.Object(x, y, chr(146), 'bow', libtcod.dark_gray, equipment=equipment_component)
#    elif choice == 'arrow':
#      item_component = thing.Item(5, ammo='arrow', projectile_bonus = 1)
#      item = classes.Object(x, y, chr(147), 'arrow', libtcod.dark_gray, item=item_component)
#    if item.equipment and item.equipment.slot == 'hand' and item.equipment.ammo == None and libtcod.random_get_int(0, 1, 100) <= 50:
#      item.name = 'poisoned ' + item.name
#      item.equipment.bonus_effect = inflict_poison

    
def scroll(owner, caster):
  if owner.spell.effect(owner, caster) == 'cancelled': return 'cancelled'
  