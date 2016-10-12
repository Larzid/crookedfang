import libtcodpy as libtcod
import globals
import math

class Object: # Player, NPCs, Items... almost anything on the map is an object.
  def __init__(self, x, y, char, name, color, blocks=False, fighter=None, ai=None):
    self.x = x
    self.y = y
    self.char = char
    self.name = name
    self.color = color
    self.blocks = blocks
    self.fighter = fighter
    if self.fighter:
      self.fighter.owner = self
    self.ai = ai
    if self.ai:
      self.ai.owner = self
  def move(self, dx, dy):
    if not globals.is_blocked(self.x + dx, self.y + dy):
      self.x += dx
      self.y += dy
  def move_towards(self, target_x, target_y):
    dx = target_x - self.x
    dy = target_y - self.y
    distance = math.sqrt(dx ** 2 + dy ** 2)
    dx = int(round(dx / distance))
    dy = int(round(dx / distance))
    self.move(dx, dy)
  def distance_to(self, other):
    dx = other.x - self.x
    dy = other.y - self.y
    return math.sqrt(dx ** 2 + dy ** 2)
  def move_astar(self, target):
    fov = globals.map().make_fov_map()
    for obj in globals.objects():
      if obj.blocks and obj != self and obj != target:
        libtcod.map_set_properties(fov, obj.x, obj.y, True, False)
    my_path = libtcod.path_new_using_map(fov, 1.41)
    libtcod.path_compute(my_path, self.x, self.y, target.x, target.y)
    if not libtcod.path_is_empty(my_path) and libtcod.path_size(my_path) < 25:
      x, y = libtcod.path_walk(my_path, True)
      if x or y:
        self.x = x
        self.y = y
    else:
      self.move_towards(target.x, target.y)
    libtcod.path_delete(my_path)
  def send_to_back(self):
    globals.objects().remove(self)
    globals.objects().insert(0, self)
  def distance(self, x, y):
    return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
