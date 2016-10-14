﻿import libtcodpy as libtcod
import globals

class Spell:
  def __init__(self, power=None, spell_range=None, effect=None):
    self.power = power
    self.spell_range = spell_range
    self.effect = effect

def spell(owner, caster):
  if owner.spell.effect(owner, caster) == 'cancelled': return 'cancelled'
  
def cast_heal(owner, caster):
  if caster.fighter.hp == caster.fighter.max_hp:
    globals.message('You are already at full health.', libtcod.red)
    return 'cancelled'
  globals.message('Your wounds start to feel better!', libtcod.light_violet)
  caster.fighter.heal(owner.spell.power)

#def cast_lightning(owner, caster):
#  monster = closest_monster(caster ,owner.spell.spell_range)
#  if monster is None:
#    message('No enemy is close enough to strike.', libtcod.red)
#    return 'cancelled'
#  message('A lighting bolt strikes the ' + monster.name + ' with a loud thunder! The damage is '
#    + str(owner.spell.power) + ' hit points.', libtcod.light_blue)
#  monster.fighter.take_damage(caster, owner.spell.power)

#def cast_confuse(owner, caster):
#  monster = target_monster(caster)
#  if monster is None: return 'cancelled'
#  old_ai = monster.ai
#  monster.ai = ConfusedMonster(old_ai, owner.spell.power)
#  monster.ai.owner = monster
#  message('The eyes of the ' + monster.name + ' look vacant, as he starts to stumble around!', libtcod.light_green)

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

#def cast_fireball(owner, caster):
#  message('Select target tile with movement keys, [ENTER] to confirm and [BACKSPACE] to cancel')
#  (x, y) = target_area(caster)
#  if x is None: return 'cancelled'
#  message('The fireball explodes, burning everything within ' + str(owner.spell.spell_range) + ' tiles!', libtcod.orange)
#  victims = [victim for victim in objects if victim.distance(x, y) <= owner.spell.spell_range and victim.fighter]
#  for victim in victims:
#    message('The ' + victim.name + ' gets burned for ' + str(owner.spell.power) + ' hit points.', libtcod.orange)
#    victim.fighter.take_damage(caster, owner.spell.power)
