import libtcodpy as libtcod # "The Doryen Library" v1.5.1 Source: https://bitbucket.org/libtcod/libtcod
import render # All related to displaying stuff on the screen.
import data # Here live the global functions and objects (player, map, object list, etc.).

def main_menu():
  while not libtcod.console_is_window_closed():
    render.title_screen()
    options =[('New Game', libtcod.green), ('Continue Game', libtcod.white), ('Controls', libtcod.sky), ('Quit', libtcod.red)]
    choice = render.menu('', options, 18)
    if choice == 0:
      data.state().new_game()
      render.init_ui()
      data.state().play_game()
    if choice == 1:
      try:
        data.state().load_game()
        render.init_ui()
        data.state().play_game()
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
data.init_state()
main_menu()
