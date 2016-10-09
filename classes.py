import function

class Object: # Player, NPCs, Items... almost anything on the map is an object.
  def __init__(self, x, y, char, name, color, blocks=False):
    self.x = x
    self.y = y
    self.char = char
    self.name = name
    self.color = color
    self.blocks = blocks
  def move(self, map, dx, dy, object_list):
    if not function.is_blocked(map, self.x + dx, self.y + dy, object_list):
      self.x += dx
      self.y += dy

class Tile:
  def __init__(self, blocked, block_sight = None, tile_face=None, back_light=None, back_dark=None, fore_light=None, fore_dark=None):
    self.explored = False
    self.blocked = blocked
    if block_sight is None: block_sight = blocked
    self.block_sight = block_sight
    self.tile_face = tile_face
    self.back_light = back_light
    self.back_dark = back_dark
    self.fore_light = fore_light
    self.fore_dark = fore_dark

class Rect:
  def __init__(self, x, y, w, h):
    self.x1 = x
    self.y1 = y
    self.x2 = x + w
    self.y2 = y + h
  def center(self):
    center_x = (self.x1 + self.x2) / 2
    center_y = (self.y1 + self.y2) / 2
    return (center_x, center_y)
  def intersect(self, other):
    return (self.x1 <= other.x2 and self.x2 >= other.x1 and self.y1 <= other.y2 and self.y2 >= other.y1)
