import libtcodpy as libtcod

class Fighter:
  def __init__(self, hp, defense, power, sight, poison_resist, state=None, state_inflictor=None, xp_bonus=None, xp=None, level=None, inv_max=None, death_function=None, last_hurt=None, nat_atk_effect=None): # Any component expected to change over gameplay should be added to player_status in next_level() and previous_level()
    self.base_max_hp = hp
    self.hp = hp
    self.base_defense = defense
    self.base_power = power
    self.base_sight = sight
    self.poison_resist = poison_resist
    if state == None: state = 'normal'
    self.state = state
    self.state_inflictor = state_inflictor
    if xp_bonus == None: xp_bonus = 0
    self.xp_bonus = xp_bonus
    if xp == None: xp = 0
    self.xp = xp
    if level == None: level = 1
    self.level = level
    self.inventory = []
    if inv_max == None: inv_max = 1
    self.inv_max = inv_max
    self.equipment = {'good hand':None, 'off hand':None, 'head':None, 'torso':None, 'feet':None}
    self.death_function = death_function
    self.last_hurt = last_hurt
    self.nat_atk_effect = nat_atk_effect