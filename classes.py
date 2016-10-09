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
