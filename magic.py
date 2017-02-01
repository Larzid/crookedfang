import libtcodpy as libtcod
import get_input
import ai
import globals

class Spell:
  def __init__(self, power=None, spell_range=None, effect=None):
    self.power = power
    self.spell_range = spell_range
    self.effect = effect

def cast_heal(owner, caster, target=None):
  if target is None:
    target = caster
  if caster.fighter.hp == caster.fighter.max_hp:
    globals.message('You are already at full health.', libtcod.red)
    return 'cancelled'
  globals.message('Your wounds start to feel better!', libtcod.light_violet)
  target.fighter.heal(owner.spell.power)

def cast_lightning(owner, caster, target=None):
  if target is None:
    target = globals.closest_enemy(caster ,owner.spell.spell_range)
  if target is None:
    globals.message('No enemy is close enough to strike.', libtcod.red)
    return 'cancelled'
  globals.message('A lighting bolt strikes the ' + target.name + ' with a loud thunder! The damage is '
    + str(owner.spell.power) + ' hit points.', libtcod.light_blue)
  target.fighter.take_damage(caster, owner.spell.power)

def cast_confuse(owner, caster, target=None):
  if target is None:
    target = get_input.target_enemy(caster)
  if target is None: return 'cancelled'
  old_ai = target.ai
  target.ai = ai.ConfusedMonster(old_ai, owner.spell.power)
  target.ai.owner = target
  globals.message('The eyes of the ' + target.name + ' look vacant, as he starts to stumble around!', libtcod.light_green)

def cast_fireball(owner, caster, target=None):
  if target is None:
    globals.message('Select target tile with movement keys, [ENTER] to confirm and [BACKSPACE] to cancel')
    (x, y) = get_input.target_area(caster)
  else:
    (x, y) = (target.x, target.y)
  if x is None: return 'cancelled'
  globals.message('The fireball explodes, burning everything within ' + str(owner.spell.spell_range) + ' tiles!', libtcod.orange)
  victims = [victim for victim in globals.objects() if victim.distance(x, y) <= owner.spell.spell_range and victim.fighter]
  for victim in victims:
    globals.message('The ' + victim.name + ' gets burned for ' + str(owner.spell.power) + ' hit points.', libtcod.orange)
    victim.fighter.take_damage(caster, owner.spell.power)

#def cast_possess(owner, caster):
#  if len(allies) < MAX_ALLIES:
#    monster = target_monster(caster)
#    if monster is None: return 'cancelled'
#    objects.remove(monster)
#    allies.append(monster)
#    old_ai = monster.ai
#    old_color = monster.color
#    old_char = monster.char
#    old_death = monster.fighter.death_function
#    monster.char = '@'
#    monster.fighter.death_function = ally_death
#    monster.ai = PossessedMonster(old_ai, old_color, old_char, old_death, owner.spell.power)
#    monster.ai.owner = monster
#    monster.always_visible = True
#    message('The eyes of the ' + monster.name + ' look straight ahead, it is ready to obey!', libtcod.light_green)

def projectile_attack(attacker, projectile, target):
  libtcod.line_init(attacker.x, attacker.y, target.x, target.y)
  hit = True
  (x, y) = libtcod.line_step()
  while (not x is None):
    for obj in globals.objects():
      if obj.blocks and x == obj.x and y == obj.y and obj != attacker and obj != target:
        hit = False
        break
    (x, y) = libtcod.line_step()
  if hit == True:
    if projectile.item.projectile_bonus is not None:
      if attacker.fighter.equipment['good hand'] is not None and attacker.fighter.equipment['good hand'].equipment.ammo and projectile.item.ammo and attacker.fighter.equipment['good hand'].equipment.ammo == projectile.item.ammo:
        damage = attacker.fighter.power + projectile.item.projectile_bonus
      else: damage = attacker.fighter.base_power + projectile.item.projectile_bonus
    else: damage = attacker.fighter.base_power
    globals.message(attacker.name.capitalize() + ' shoot ' + target.name + ' with ' + projectile.name + ' for ' + str(damage) + 'hit points.', libtcod.silver)
    target.fighter.take_damage(attacker, damage)
  else:
    globals.message('No clear shot for ' + target.name, libtcod.red)
    return 'cancelled'

def shoot_weapon(actor, hand):
  import render
  import generator
  items = [obj for obj in actor.fighter.inventory if obj.item.ammo and obj.item.ammo == actor.fighter.equipment[hand].equipment.ammo]
  text = [(' ' + obj.char + ' ' + obj.name, obj.color) for obj in actor.fighter.inventory if obj.item.ammo and obj.item.ammo == actor.fighter.equipment['good hand'].equipment.ammo]
  if len(items) == 0: 
    globals.msgbox("You don't have any " + actor.fighter.equipment[hand].equipment.ammo, 20)
    return 'cancelled'
  else:  
    item = render.menu('Select projectile', text, 25)
    if item is not None:
      if not generator.projectile(items[item], actor) == 'cancelled':
        if items[item].item.qty > 1:
          items[item].item.qty -= 1
        else:
          actor.fighter.inventory.remove(items[item])
      else: return 'cancelled'