import libtcodpy as libtcod # "The Doryen Library" v1.5.1 Source: https://bitbucket.org/libtcod/libtcod
import render # All related to displaying stuff on the screen.
import engine # Here live the global functions and objects (player, map, object list, etc.).

def main_menu():
  while not libtcod.console_is_window_closed():
    render.title_screen()
    options =[('New Game', libtcod.green), ('Continue Game', libtcod.white), ('Controls', libtcod.sky), ('Quit', libtcod.red)]
    choice = render.menu('', options, 18)
    if choice == 0:
      engine.state().new_game()
      render.init_ui()
      engine.state().play_game()
    if choice == 1:
      try:
        engine.state().load_game()
        render.init_ui()
        engine.state().play_game()
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
engine.init_state()
main_menu()
