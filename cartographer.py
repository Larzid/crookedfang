import libtcodpy as libtcod
import globals

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

class Map:
  def __init__(self, width=65, height=53, map_function=None, max_rooms=None, min_room_size=None, max_room_size=None):
    self.width = width
    self.height = height
    self.topography = []
    if map_function is None:
      self.rooms = make_arena(self)
    elif max_rooms is None:
      self.rooms = map_function(self)
    else:
      self.rooms = map_function(self, max_rooms, min_room_size, max_room_size)
    self.fov = self.make_fov_map()
  def make_fov_map(self):
    fov_map = libtcod.map_new(self.width, self.height)
    for y in range(self.height):
      for x in range(self.width):
        libtcod.map_set_properties(fov_map, x, y, not self.topography[x][y].block_sight, not self.topography[x][y].blocked)
    return fov_map
  def set_tile(self, x, y, blocked, block_sight, tile_face, back_light, back_dark, fore_light, fore_dark):
    self.topography[x][y].blocked = blocked
    self.topography[x][y].block_sight = block_sight
    self.topography[x][y].tile_face = tile_face
    self.topography[x][y].back_light=back_light
    self.topography[x][y].back_dark=back_dark
    self.topography[x][y].fore_light=fore_light
    self.topography[x][y].fore_dark=fore_dark
  def dungeon_floor(self, x, y):
    self.set_tile(x, y, blocked=False, block_sight=False, tile_face=chr(172), back_light=libtcod.darker_sepia, back_dark=libtcod.darkest_sepia, fore_light=libtcod.black, fore_dark=libtcod.darkest_sepia)
  def dungeon_wall(self, x, y):
    self.set_tile(x, y, blocked=True, block_sight=True, tile_face=chr(173), back_light=libtcod.black, back_dark=libtcod.black, fore_light=libtcod.white, fore_dark=libtcod.dark_gray)

  def create_room(self, room):
    for x in range(room.x1 + 1, room.x2):
      for y in range(room.y1 + 1, room.y2):
        self.dungeon_floor(x, y)
  def create_h_tunnel(self, x1, x2, y):
    for x in range(min(x1, x2), max(x1, x2) + 1):
      self.dungeon_floor(x, y)
  def create_v_tunnel(self, y1, y2, x):
    for y in range(min(y1, y2), max(y1, y2) + 1):
      self.dungeon_floor(x, y)

def make_arena(map):
  map.topography = [[ Tile(blocked=False, block_sight=False, tile_face=chr(172), back_light=libtcod.darker_sepia, back_dark=libtcod.darkest_sepia, fore_light=libtcod.black, fore_dark=libtcod.darkest_sepia) for y in range(map.height) ] for x in range(map.width) ]
  for x in range(map.width):
    map.dungeon_wall(x, 0)
    map.dungeon_wall(x, map.height-1)
  for y in range(map.height):
    map.dungeon_wall(0, y)
    map.dungeon_wall(map.width-1, y)
  map.dungeon_wall(map.width/2 - 10, map.height/2 - 10)
  map.dungeon_wall(map.width/2 + 10, map.height/2 - 10)
  map.dungeon_wall(map.width/2 - 10, map.height/2 + 10)
  map.dungeon_wall(map.width/2 + 10, map.height/2 + 10)
  room = [Rect(0, 0, map.width - 1, map.height - 1)]
  return room
def make_dungeon(map, max_rooms, min_room_size, max_room_size):
  map.topography = [[ Tile(blocked=True, block_sight=True, tile_face=chr(173), back_light=libtcod.black, back_dark=libtcod.black, fore_light=libtcod.white, fore_dark=libtcod.dark_gray) for y in range(map.height) ] for x in range(map.width) ]
  rooms = []
  num_rooms = 0
  for r in range(max_rooms):
    w = libtcod.random_get_int(0, min_room_size, max_room_size)
    h = libtcod.random_get_int(0, min_room_size, max_room_size)
    x = libtcod.random_get_int(0, 0, map.width - w - 1)
    y = libtcod.random_get_int(0, 0, map.height - h - 1)
    new_room = Rect(x, y, w, h)
    failed = False
    for other_room in rooms:
      if new_room.intersect(other_room):
        failed = True
        break
    if not failed:
      map.create_room(new_room)
      (new_x, new_y) = new_room.center()
      if num_rooms != 0:
        (prev_x, prev_y) = rooms[num_rooms -1].center()
        if libtcod.random_get_int(0, 0, 1) == 1:
          map.create_h_tunnel(prev_x, new_x, prev_y)
          map.create_v_tunnel(prev_y, new_y, new_x)
        else:
          map.create_v_tunnel(prev_y, new_y, prev_x)
          map.create_h_tunnel(prev_x, new_x, new_y)
      rooms.append(new_room)
      num_rooms += 1
  return rooms
