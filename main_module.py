# This is the main game file and it will be deliberately short.
import libtcodpy as libtcod # "The Doryen Library" v1.5.1 Source: https://bitbucket.org/libtcod/libtcod
# classes.py - Here are the classes shared between modules (Tile, Object and Rect).
# component.py - The game components are defined here.
# ai. py - Artificial Inteligence classes.
# cartographer - This handles the map object (tecniaclly a class but it deserves special treatment).
# demographic.py - Functions to generate creatures and items and populate areas.
import render # All related to displaying stuff on the screen.
# get_input - Self explainatory.
import data # Here live the global functions and objects (player, map, object list, etc.).

def main_menu():
  while not libtcod.console_is_window_closed():
    render.title_screen()
    options =[('New Game', libtcod.green), ('Continue Game', libtcod.white), ('Controls', libtcod.sky), ('Quit', libtcod.red)]
    choice = render.menu('', options, 18)
    if choice == 0:
      data.new_game()
      render.init_ui()
      data.play_game()
    if choice == 1:
      try:
        data.load_game()
        render.init_ui()
        data.play_game()
      except:
        render.msgbox('\n No saved game to load.\n', 24)
        continue
      
    if choice == 2:
      render.help()
      continue
    elif choice == 3:
      break

# Start the game screen.
render.init_screen()
main_menu()
