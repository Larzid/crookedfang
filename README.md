# Generic-RL

This is a little game made in python + libtcod following the tutorial at:
http://www.roguebasin.com/index.php?title=Complete_Roguelike_Tutorial,_using_python%2Blibtcod

It's name is Generic RL because I haven't decided what will it be about, even the Title Screen, NPCs and most items are the same as those from the tutorial or with little modification (This will eventually change).

What I have concentrated on so far is on game mechanics which mostly has been adding basic stuff like stackable items and colored menus, but there's some stuff a little more instesting, here's the list of what has been done:

# V-0.0.1
# Custom side panel for stats & message panel at the bottom
# Added sight element to fighter class for FOV calculations in all fighter objects
# Improved AI clasess
# Stacking items
# Keyboard look comand
# Inventory implemented as component of fighter class (monster inventory)
# Colored menus
# Keyboard target area function
# Keyboard target monster function
# Persistent dungeon levels with Monster and Item respawning when reentering if needed
# Fighter class is aware of who is attacking to propperly assign EXP
# Equipment menu
# Equipment implemented in Fighter Class (Monsters can use equipment)
# Dual weilding (Even combinations of Ranged and Melee weapons) (Ranged weapons will only fire if weilded in the 'good hand')
# Town map generator with BSP houses (Town level is empty right now)
# Ranged weapons (1) and some (1) throwable items
# Projectile path (will not fire ranged weapon or throw item if the path is obstucted)
# handle_keys() function can take control any NPC trough the Possessed_Monster AI class
