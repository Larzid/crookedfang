# This is the main game file and it will be deliberately short.
import libtcodpy as libtcod # "The Doryen Library" v1.5.1 Source: https://bitbucket.org/libtcod/libtcod
# classes.py - Here are the classes shared between modules (Tile, Object and Rect).
# component.py - The game components are defined here.
# ai. py - Artificial Inteligence classes.
import cartographer # This handles the map object (tecniaclly a class but it deserves special treatment).
# demographic.py - Functions to generate creatures and items and populate areas.
import render # All related to displaying stuff on the screen.
# get_input - Self explainatory.
import globals # Here live the global functions and objects (player, map, object list, etc.).

# Start the game screen.
render.init_screen()

# Start new game.

globals.init_player('new')
globals.init_map('new')
#globals.init_map('new', map_function=cartographer.make_dungeon)
globals.init_game_msgs('new')
globals.init_turn_counter('new')
globals.message('You were bored, you craved adventure and due to your total lack of common sense and reckless impulsive behavior you came here, to some strange ruins half a world away from what you call civilization!', libtcod.light_cyan)
globals.message('Did you at least told somebody what you where up to?', libtcod.crimson)
globals.message('Well, its kinda late for that.', libtcod.light_purple)


# Start user interface.
render.init_ui()

# Main loop.
while not libtcod.console_is_window_closed():
  globals.next_turn()
  for object in globals.objects():
    if object.fighter and object.fighter.check_status:
      object.fighter.status_check()
    if object.ai:
      object.ai.take_turn()
  if globals.player().ai.action == 'exit':
    break
