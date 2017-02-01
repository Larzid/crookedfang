import libtcodpy as libtcod
import globals
import classes
import combat
import ai
import thing
import magic

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

def from_dungeon_level(table):
  for (value, level) in reversed(table):
    if globals.d_level() >= level:
      return value
  return 0

def gen_creature(room=None, x=None, y=None):
  monster_chances = {}
  monster_chances['snake'] = 40
  monster_chances['orc'] = 40
  monster_chances['troll'] = from_dungeon_level([[15, 3], [30, 5], [60, 7]])
  if room is not None and x is None:
    x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
    y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)
  if not globals.is_blocked(x, y):
    choice = random_choice(monster_chances)
    if choice == 'snake':
      fighter_component = combat.Fighter(faction='wild', hp=10, defense=0, power=3, sight=15, poison_resist=80, xp_bonus=20, lvl_base=20, lvl_factor=15, death_function=combat.monster_death, nat_atk_effect=globals.inflict_poison)
      ai_component = ai.BasicMonster()
      creature = classes.Object(x, y, 's', 'snake', libtcod.darker_red, blocks=True, fighter=fighter_component, ai=ai_component)
    elif choice == 'orc':
      fighter_component = combat.Fighter(faction='dungeon', hp=20, defense=0, power=4, sight=10, poison_resist=20, xp_bonus=35, lvl_base=40, lvl_factor=20, death_function=combat.monster_death)
      ai_component = ai.BasicMonster()
      creature = classes.Object(x, y, 'o', 'orc', libtcod.desaturated_green, blocks=True, fighter=fighter_component, ai=ai_component)
    elif choice == 'troll':
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

def populate_level(max_room_monsters=from_dungeon_level([[2, 1], [3, 4], [5, 6]])):
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

def level_items(max_room_items=from_dungeon_level([[2, 1], [3, 4], [5, 6]])):
  final_list = []
  for room in globals.map().rooms:
    num_items = libtcod.random_get_int(0, 0, max_room_items)
    final_list.extend(room_items(room, num_items))
  return final_list

def gen_item(room=None, x=None, y=None):
  item_chances = {}
#  item_chances['possess'] = 5
  item_chances['bow'] = 5
  item_chances['arrow'] = 10
  item_chances['throwing knife'] = from_dungeon_level([[10, 2]])
  item_chances['dagger'] = 10
  item_chances['machete'] = from_dungeon_level([[10, 2]])
  item_chances['sword'] = from_dungeon_level([[10, 3]])
  item_chances['heal'] = 35
  item_chances['lightning'] = from_dungeon_level([[25, 4]])
  item_chances['fireball'] =  from_dungeon_level([[25, 6]])
  item_chances['confuse'] =   from_dungeon_level([[10, 2]])
  if room is not None and x is None:
    x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
    y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)
  if not globals.is_blocked(x, y):
    choice = random_choice(item_chances)
    if choice == 'fireball':
      item_component = thing.Item(1, use_function=scroll)
      spell_component = magic.Spell(power=25, spell_range =3 , effect=magic.cast_fireball)
      item = classes.Object(x, y, chr(151), 'scroll of fireball', libtcod.red, item=item_component, spell=spell_component)
    elif choice == 'lightning':
      item_component = thing.Item(1, use_function=scroll)
      spell_component = magic.Spell(power=40, spell_range =5 , effect=magic.cast_lightning)
      item = classes.Object(x, y, chr(151), 'scroll of lightning bolt', libtcod.light_yellow, item=item_component, spell=spell_component)
    elif choice == 'confuse':
      item_component = thing.Item(1, use_function=scroll)
      spell_component = magic.Spell(power=10, spell_range =5 , effect=magic.cast_confuse)
      item = classes.Object(x, y, chr(151), 'scroll of confusion', libtcod.purple, item=item_component, spell=spell_component)
    elif choice == 'heal':# choice <= 100:
      item_component = thing.Item(1, use_function=scroll)
      spell_component = magic.Spell(power=40, effect=magic.cast_heal)
      item = classes.Object(x, y, chr(144), 'healing potion', libtcod.violet, item=item_component, spell=spell_component)
#    elif choice == 'possess':
#      item_component = thing.Item(1, use_function=scroll)
#      spell_component = magic.Spell(power=10, spell_range =5 , effect=magic.cast_possess)
#      item = classes.Object(0, 0, chr(151), 'scroll of possession', libtcod.green, item=item_component, spell=spell_component)
    elif choice == 'sword':
      equipment_component = thing.Equipment(slot='hand', power_bonus = 3)
      item = classes.Object(x, y, chr(148), 'sword', libtcod.sky, equipment=equipment_component)
    elif choice == 'machete':
      equipment_component = thing.Equipment(slot='hand', power_bonus = 2)
      item = classes.Object(x, y, chr(148), 'machete', libtcod.gray, equipment=equipment_component)
    elif choice == 'dagger':
      equipment_component = thing.Equipment(slot='hand', power_bonus = 1)
      item = classes.Object(x, y, chr(150), 'dagger', libtcod.silver, equipment=equipment_component)
    elif choice == 'throwing knife':
      item_component = thing.Item(1, projectile_bonus = 2, use_function=projectile)
      item = classes.Object(x, y, chr(150), 'throwing knife', libtcod.light_blue, item=item_component)
    elif choice == 'bow':
      equipment_component = thing.Equipment(slot='hand', ammo='arrow', power_bonus = 1)
      item = classes.Object(x, y, chr(146), 'bow', libtcod.dark_gray, equipment=equipment_component)
    elif choice == 'arrow':
      item_component = thing.Item(5, ammo='arrow', projectile_bonus = 1)
      item = classes.Object(x, y, chr(147), 'arrow', libtcod.dark_gray, item=item_component)
    if item.equipment and item.equipment.slot == 'hand' and item.equipment.ammo == None and libtcod.random_get_int(0, 1, 100) <= 50:
      item.name = 'poisoned ' + item.name
      item.equipment.bonus_effect = globals.inflict_poison
    return item
    
def scroll(owner, caster):
  if owner.spell.effect(owner, caster) == 'cancelled': return 'cancelled'

def projectile(proj, attacker):
  import get_input
  target = get_input.target_enemy(attacker)
  if target is None: return 'cancelled'
  if magic.projectile_attack(attacker, proj, target) == 'cancelled': return 'cancelled'
