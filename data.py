import libtcodpy as libtcod
import classes
import render

def init_state():
  global game_state
  game_state = classes.GameState()

def state():
  return game_state

def fov_recompute(actor):
  libtcod.map_compute_fov(game_state.level_map.fov, actor.x, actor.y, actor.creature.sight, True, 0)

def inflict_poison(attacker, target):
  if libtcod.random_get_int(0, 1, 100) > target.creature.poison_resist:
    target.creature.status = 'poison'
    target.creature.status_inflictor = attacker
    if target == game_state.player: 
      render.message(target.name.capitalize() + ' has been poisoned by ' + attacker.name + '.', libtcod.purple)
    if attacker == game_state.player:
      render.message(attacker.name.capitalize() + ' has poisoned ' + target.name + '.', libtcod.fuchsia)
