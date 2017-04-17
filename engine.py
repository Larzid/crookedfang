import libtcodpy as libtcod
import descriptor
import cartographer
import shelve
import render
import glob
import os

class GameState:
  def __init__(self, player=None, level_map=None, messages=None, turn=None, d_level=None, max_d_level=None):
    self.player = player
    self.level_map = level_map
    self.turn = turn
    self.messages = messages
    self.d_level = d_level
    self.max_d_level = max_d_level
  def new_game(self):
    for f in glob.glob('lvl*'):
      os.remove(f)
    self.player = descriptor.creatures('player', 0, 0)
    self.d_level = 1
    self.max_d_level = 1
    import generator
    self.level_map = cartographer.Map(map_function=cartographer.make_dungeon)
    (self.player.x, self.player.y) = self.level_map.rooms[0].center()
    self.level_map.objects.append(self.player)
    self.level_map.objects.extend(generator.populate_level())
    self.level_map.objects.extend(generator.level_items())
    for object in self.level_map.objects:
      if object.item:
        object.send_to_back()
    self.turn= 0
    self.messages = []
    render.message('You were bored, you craved adventure and due to your total lack of common sense and reckless impulsive behavior you came here, to some strange ruins half a world away from what you call civilization!', libtcod.light_cyan)
    render.message('Did you at least told somebody what you where up to?', libtcod.crimson)
    render.message('Well, its kinda late for that.', libtcod.light_purple)
  def save_game(self):
    player_index = self.level_map.objects.index(self.player)
    self.level_map.objects.pop(player_index)
    file = shelve.open('savegame', 'n')
    file['level_map'] = self.level_map
    file['player'] = self.player
    file['messages'] = self.messages
    file['turn'] = self.turn
    file['d_level'] = self.d_level
    file['max_d_level'] = self.max_d_level
    file.close()
  def load_game(self):
    file = shelve.open('savegame', 'r')
    self.level_map = file['level_map']
    self.level_map.fov = self.level_map.make_fov_map()
    self.player = file['player']
    self.level_map.objects.insert(0, self.player)
    self.messages = file['messages']
    self.turn = file['turn']
    self.d_level = file['d_level']
    self.max_d_level = file['max_d_level']
    file.close()
  def play_game(self):
    while not libtcod.console_is_window_closed():
      self.next_turn()
      for object in self.level_map.objects:
        if object.creature and object.creature.check_status:
          object.creature.status_check()
        if object.creature and object.ai:
          object.ai.take_turn()
      if self.player.ai.action == 'exit':
        break
      if self.player.ai.action == 'next-level':
        self.next_level()
      if self.player.ai.action == 'previous-level':
        self.previous_level()
  def save_level(self, filename):
    player_index = self.level_map.objects.index(self.player)
    self.level_map.objects.pop(player_index)
    file = shelve.open(filename, 'n')
    file['lvl'] = self.level_map
    file.close()
  def load_level(self, filename):
    file = shelve.open(filename, 'r')
    self.level_map = file['lvl']
    file.close()
    self.level_map.objects.insert(0, self.player)
  def next_level(self):
    if self.d_level + 1 > self.max_d_level:
      render.message('You take a moment to rest, and recover your strength.', libtcod.light_violet)
      self.player.creature.heal(self.player.creature.max_hp / 2)
      render.message('After a rare moment of peace, you descend deeper into the heart of the dungeon...', libtcod.red)
      self.max_d_level += 1
    else:
      render.message('You descend deeper into the heart of the dungeon...', libtcod.red)
    self.save_level('lvl'+str(self.d_level))
    self.d_level += 1
    try:
      self.load_level('lvl'+str(self.d_level))
      (self.player.x, self.player.y) = self.level_map.rooms[0].center()
    except:
      import generator
      self.level_map = cartographer.Map(map_function=cartographer.make_dungeon)
      (self.player.x, self.player.y) = self.level_map.rooms[0].center()
      self.level_map.objects.append(self.player)
      self.level_map.objects.extend(generator.populate_level())
      self.level_map.objects.extend(generator.level_items())
      for object in self.level_map.objects:
        if object.item:
          object.send_to_back()
    self.player.ai.action = 'playing'
  def previous_level(self):
    render.message('You ascend into a higher level of the dungeon...', libtcod.red)
    self.save_level('lvl'+str(self.d_level))
    self.d_level -= 1
    try:
      self.load_level('lvl'+str(self.d_level))
      (self.player.x, self.player.y) = self.level_map.rooms[-1].center()
    except:
      import generator
      self.level_map = cartographer.Map(map_function=cartographer.make_dungeon)
      (self.player.x, self.player.y) = self.level_map.rooms[-1].center()
      self.level_map.objects.append(self.player)
      self.level_map.objects.extend(generator.populate_level())
      self.level_map.objects.extend(generator.level_items())
      for object in self.level_map.objects:
        if object.item:
          object.send_to_back()
    self.player.ai.action = 'playing'
  def next_turn(self):
    self.turn += 1

def init_state():
  global game_state
  game_state = GameState()

def state():
  return game_state

