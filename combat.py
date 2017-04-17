import libtcodpy as libtcod
import get_input
import ai
import engine
import render

def cast_heal(owner, caster, target=None):
  if target is None:
    target = caster
  if caster.creature.hp == caster.creature.max_hp:
    render.message('You are already at full health.', libtcod.red)
    return 'cancelled'
  render.message('Your wounds start to feel better!', libtcod.light_violet)
  target.creature.heal(owner.spell.power)

def cast_lightning(owner, caster, target=None):
  if target is None:
    target = caster.creature.closest_enemy(owner.spell.spell_range)
  if target is None:
    render.message('No enemy is close enough to strike.', libtcod.red)
    return 'cancelled'
  render.message('A lighting bolt strikes the ' + target.name + ' with a loud thunder! The damage is '
    + str(owner.spell.power) + ' hit points.', libtcod.light_blue)
  target.creature.take_damage(caster, owner.spell.power)

def cast_confuse(owner, caster, target=None):
  if target is None:
    target = get_input.target_enemy(caster)
  if target is None: return 'cancelled'
  old_ai = target.ai
  target.ai = ai.ConfusedMonster(old_ai, owner.spell.power)
  target.ai.owner = target
  render.message('The eyes of the ' + target.name + ' look vacant, as he starts to stumble around!', libtcod.light_green)

def cast_fireball(owner, caster, target=None):
  if target is None:
    render.message('Select target tile with movement keys, [ENTER] to confirm and [BACKSPACE] to cancel')
    (x, y) = get_input.target_area(caster)
  else:
    (x, y) = (target.x, target.y)
  if x is None: return 'cancelled'
  render.message('The fireball explodes, burning everything within ' + str(owner.spell.spell_range) + ' tiles!', libtcod.orange)
  victims = [victim for victim in engine.state().level_map.objects if victim.distance(x, y) <= owner.spell.spell_range and victim.creature]
  for victim in victims:
    render.message('The ' + victim.name + ' gets burned for ' + str(owner.spell.power) + ' hit points.', libtcod.orange)
    victim.creature.take_damage(caster, owner.spell.power)

#def cast_possess(owner, caster):
#  if len(allies) < MAX_ALLIES:
#    monster = target_monster(caster)
#    if monster is None: return 'cancelled'
#    objects.remove(monster)
#    allies.append(monster)
#    old_ai = monster.ai
#    old_color = monster.color
#    old_char = monster.char
#    old_death = monster.creature.death_function
#    monster.char = '@'
#    monster.creature.death_function = ally_death
#    monster.ai = PossessedMonster(old_ai, old_color, old_char, old_death, owner.spell.power)
#    monster.ai.owner = monster
#    monster.always_visible = True
#    message('The eyes of the ' + monster.name + ' look straight ahead, it is ready to obey!', libtcod.light_green)

def projectile_attack(attacker, projectile, target):
  target = get_input.target_enemy(attacker)
  if target is None: return 'cancelled'
  libtcod.line_init(attacker.x, attacker.y, target.x, target.y)
  hit = True
  (x, y) = libtcod.line_step()
  while (not x is None):
    for obj in engine.state().level_map.objects:
      if obj.blocks and x == obj.x and y == obj.y and obj != attacker and obj != target:
        hit = False
        break
    (x, y) = libtcod.line_step()
  if hit == True:
    if projectile.item.projectile_bonus is not None:
      if attacker.creature.equipment['good hand'] is not None and attacker.creature.equipment['good hand'].equipment.ammo and projectile.item.ammo and attacker.creature.equipment['good hand'].equipment.ammo == projectile.item.ammo:
        damage = attacker.creature.power + projectile.item.projectile_bonus
      else: damage = attacker.creature.base_power + projectile.item.projectile_bonus
    else: damage = attacker.creature.base_power
    render.message(attacker.name.capitalize() + ' shoot ' + target.name + ' with ' + projectile.name + ' for ' + str(damage) + 'hit points.', libtcod.silver)
    target.creature.take_damage(attacker, damage)
  else:
    render.message('No clear shot for ' + target.name, libtcod.red)
    return 'cancelled'

def shoot_weapon(actor, hand):
  items = [obj for obj in actor.creature.inventory if obj.item.ammo and obj.item.ammo == actor.creature.equipment[hand].equipment.ammo]
  text = [(' ' + obj.char + ' ' + obj.name, obj.color) for obj in actor.creature.inventory if obj.item.ammo and obj.item.ammo == actor.creature.equipment['good hand'].equipment.ammo]
  if len(items) == 0: 
    render.msgbox("You don't have any " + actor.creature.equipment[hand].equipment.ammo, 20)
    return 'cancelled'
  else:  
    item = render.menu('Select projectile', text, 25)
    if item is not None:
      if not projectile(items[item], actor) == 'cancelled':
        if items[item].item.qty > 1:
          items[item].item.qty -= 1
        else:
          actor.creature.inventory.remove(items[item])
      else: return 'cancelled'

def projectile(proj, attacker):
  target = get_input.target_enemy(attacker)
  if target is None: return 'cancelled'
  if projectile_attack(attacker, proj, target) == 'cancelled': return 'cancelled'
