#!/usr/bin/env python

# Before importing pygame, we need to set this variable to use freetype
# fonts
import os
os.environ['PYGAME_FREETYPE'] = '1'

import pygame
import random

CELL_SIZE = 64
MAX_ACTIONS = 5
IMAGE_DIR = "images/"


class Effect(object):
  def __init__(self, target, duration_turns):
    self.target = target
    self.turns_remaining = duration_turns
    self.target.set_effect(self)

  def deactivate(self):
    '''Clears the target and sets duration to 0.'''
    if self.target != None:
      self.target.remove_effect()
      self.target = None
      self.turns_remaining = 0

  def draw_with_target(self, display):
    '''Draws target at screen pos, then calls self.draw().'''
    if self.target != None:
      self.target.draw(display, target.screen_pos)
      self.draw()
    

class BubbleEffect(Effect):
  BUBBLE_DURATION_TURNS = 3
  BUBBLE_TOP_SCREEN_Y = 30
  BUBBLE_FLOAT_DY = 4
  BUBBLE_DRIFT_DIST = 2.0

  def __init__(self, target):
    Effect.init(self, target, BUBBLE_DURATION_TURNS)
    screen_pos = target.screen_pos

  def draw_with_target(self, display):
    screen_pos[0] += random.random()*BUBBLE_DRIFT_DIST - BUBBLE_DRIF_DIST/2
    screen_pos[1] += (random.random()*BUBBLE_DRIFT_DIST - BUBBLE_DRIF_DIST/2 
                      + BUBBLE_FLOAT_DIST)
    self.target.draw_at_pos(display, screen_pos)


class Power(object):
  POWER_IDLE = 'idle'
  POWER_SELECTING = 'selecting'
  POWER_ACTING = 'acting'
  POWER_KEYS = {
    pygame.K_a: 'a', pygame.K_b: 'b', pygame.K_c: 'c', pygame.K_d: 'd', 
    pygame.K_e: 'e', pygame.K_f: 'f', pygame.K_g: 'g', pygame.K_h: 'h',
    pygame.K_i: 'i', pygame.K_j: 'j', pygame.K_k: 'k', pygame.K_l: 'l', 
    pygame.K_m: 'm', pygame.K_n: 'n', pygame.K_o: 'o', pygame.K_p: 'p',
    pygame.K_q: 'q', pygame.K_r: 'r', pygame.K_s: 's', pygame.K_t: 't', 
    pygame.K_u: 'u', pygame.K_v: 'v', pygame.K_w: 'w', pygame.K_x: 'x',
    pygame.K_y: 'y', pygame.K_z: 'z', 
    pygame.K_1: '1', pygame.K_2: '2', pygame.K_3: '3', pygame.K_4: '4', 
    pygame.K_5: '5', pygame.K_6: '6', pygame.K_7: '7', pygame.K_8: '8',
    pygame.K_9: '9', pygame.K_0: '0'}

  def __init__(self, owner):
    self.state = Power.POWER_IDLE
    self.owner = owner
    self.target = None

  def is_selecting(self):
    return self.state == Power.POWER_SELECTING

  def is_acting(self):
    return self.state == Power.POWER_ACTING

  def act_on_target(self, target):
    self.target = target
    self.state = Power.POWER_ACTING
    self.draw()

  def can_attack(self, target):
    return self.owner.get_type() != target.get_type()

  def draw_actor_key(self, actor, key):
    key_font = pygame.font.Font(None, 30)
    key_display = key_font.render(key, True, (255, 255, 255))
    key_display = key_display.convert_alpha()
    actor.game.display.screen.blit(key_display, actor.screen_pos)
            

  def start_selecting(self):
    '''Transition to selecting state, assign keys to targets, 
    and draw targets.'''
    self.state = Power.POWER_SELECTING
    temp_keys = Power.POWER_KEYS.keys()
    self.actors_for_keys = {}
    
    for actor in self.owner.game.actors:
      if self.can_attack(actor):
        key = temp_keys.pop(random.randint(0, len(temp_keys)))
        self.actors_for_keys[key] = actor
        self.draw_actor_key(actor, Power.POWER_KEYS[key])
    
  def handle_event(self, event):
    if not self.is_selecting():
      print "ERROR: Power isn't selecting but is asked to handle event!"
      return False
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_DOWN:
        if event.key == pygame.K_SPACE:
          self.state = Power.POWER_IDLE
        possible_keys = keys(self.actors_for_keys.keys())
        for key in possible_keys:
          if key == event.key:
            self.act_on_target(self.actors_for_keys[key])
            return True
    return False
      
        

class BubblePower(Power):
  def __init__(self, owner):
    Power.__init__(self, owner)
    
  def get_key(self):
    return pygame.K_b

class Actor(object):
  ACTIVE = 'active'
  IDLE = 'idle'
  MOVING = 'moving'
  PIX_PER_MOVE = 8
  UNICORN = 'unicorn'
  ROBOT = 'robot'

  def __init__(self, name):
    self.name = name
    self.pos = [16, 12]
    self.screen_pos = [0, 0]
    self.move_animation_count = 0
    self.actions_left = 0
    self.actions_per_turn = 5
    self.dx = 0
    self.dy = 0
    self.sprite = []
    self.enter_idle()
    self.game = None
    self.effect = None
    self.active_power = None
    self.selecting_power = None
    self.powers = []

  def set_game(self, game):
    '''Sets the game object, and computes screen position.'''
    self.game = game
    self.screen_pos = self.game.to_screen(self.pos)

  def set_effect(self, effect):
    '''Sets effect to new effect, and deactivates any current effect.'''
    if (self.effect != None):
      self.effect.deactivate()
    self.effect = effect

  def get_info_text(self):
    return self.name + "'s Turn! Use arrows to move." 

  def draw_at_pos(self, display, screen_pos):
    display.screen.blit(self.sprite, 
                        [screen_pos[0] - self.sprite.get_width() + 
                         CELL_SIZE/2,
                         screen_pos[1] - self.sprite.get_height() + 
                         CELL_SIZE/2])

  def draw(self, display):
    if (self.effect != None):
      self.effect.draw_with_target(display)
    else :
      self.draw_at_pos(display, self.screen_pos)
    if self.state == Actor.ACTIVE:
      self.draw_active_decoration(display)

  def draw_active_decoration(self, display):
    pygame.draw.circle(display.screen, (255, 255, 0), 
                       self.screen_pos, CELL_SIZE/2, 4)

  def is_turn_over(self):
    return self.actions_left <= 0

  def handle_event(self, game, event):
    if self.state == Actor.ACTIVE:
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_DOWN:
          self.move(game, 0, 1)
          return True
        elif event.key == pygame.K_UP:
          self.move(game, 0, -1)
          return True
        elif event.key == pygame.K_LEFT:
          self.move(game, -1, 0)
          return True
        elif event.key == pygame.K_RIGHT:
          self.move(game, 1, 0)
          return True
        elif self.selecting_power != None:
          # If we have a power that's active, delegate to the power to handle
          # the keypress
          handled = self.selecting_power.handle_event(event)
          if not self.selecting_power.is_selecting:
            # power finished selection; clear our selecting power
            self.selection_power = None
          return handled
        else:
          # See if the key activates a power
          for power in self.powers:
            if event.key == power.get_key():
              power.start_selecting()
              self.selecting_power = power
              return True
    return False

  def move(self, game, di, dj):
    self.active_power = None
    if game.is_move_legal(self, [self.pos[0] + di, self.pos[1] + dj]):
      #print "move: %d %d %d" % (di, dj, self.actions_left)
      self.dx = di*Actor.PIX_PER_MOVE
      self.dy = dj*Actor.PIX_PER_MOVE
      self.pos = [self.pos[0] + di, self.pos[1] + dj]
      self.move_animation_count = CELL_SIZE/Actor.PIX_PER_MOVE
      self.enter_moving()
    else:
      print "Move isn't legal!"

  def enter_moving(self):
    print "Entering MOVING"
    self.state = Actor.MOVING

  def enter_idle(self):
    print "Entering IDLE"
    self.state = Actor.IDLE
    self.actions_left = 0

  def start_turn(self):
    # TODO skip turn if locked by effect
    self.actions_left = self.actions_per_turn
    self.enter_active()

  def enter_active(self):
    self.state = Actor.ACTIVE

  def finish_action(self):
    self.actions_left = self.actions_left-1
    if (self.is_turn_over()):
      self.enter_idle()
    else:
      self.enter_active()

  def set_position(self, p):
    self.pos[0] = p[0]
    self.pos[1] = p[1]
    self.screen_pos = self.game.to_screen(self.pos)

  def update(self):
    if (self.state == Actor.MOVING):
      self.screen_pos = [self.screen_pos[0] + self.dx, 
                         self.screen_pos[1] + self.dy]
      self.move_animation_count = self.move_animation_count-1
      if (self.move_animation_count <= 0):
        self.finish_action()

class Unicorn(Actor):
  def __init__(self, name):
    Actor.__init__(self, name)
    self.sprite = pygame.image.load(IMAGE_DIR+"unicorn_cherry.png")

  def get_type(self):
    return Actor.UNICORN

  def handle_event(self, game, event):
    return Actor.handle_event(self, game, event)

class Robot(Actor):
  def __init__(self, name):
    Actor.__init__(self, name)
    self.sprite = pygame.image.load(IMAGE_DIR+"robot_up.png")
    self.powers.append(BubblePower(self))

  def get_type(self):
    return Actor.ROBOT

  def handle_event(self, game, event):
    return Actor.handle_event(self, game, event)

class Display(object):
  INFO_TEXT_POS = (20, 20)

  def __init__(self):
    pygame.init()
    pygame.display.set_caption("Castle Raid");
    self.background = pygame.image.load(IMAGE_DIR+"castle.png")
    # TODO load top layer
    # TODO set transparency
    self.size = self.background.get_size();
    print "display size: %d %d" % self.size
    self.screen = pygame.display.set_mode(self.background.get_size())
    self.background.convert();  

  def draw(self, actors, info_text):
    self.screen.blit(self.background, (0, 0))
    for actor in actors:
      actor.draw(self)
    # TODO self.screen.blit(self.top_layer, (0, 0))
    info_font = pygame.font.Font(None, 30)
    info_display = info_font.render(info_text, True, (255, 255, 255))
    info_display = info_display.convert_alpha()
    self.screen.blit(info_display, Display.INFO_TEXT_POS)
    pygame.display.flip();

class Map(object):
  def __init__(self, max_i, max_j):
    self.max_i = max_i
    self.max_j = max_j
    print "Map: size = %d %d" % (self.max_i, self.max_j)

  def is_move_legal(self, pos):
    if (pos[0] >= 0 and pos[1] >= 0 and 
        pos[0] <= self.max_i and pos[1] <= self.max_j):
      return True
    print "Move %d %d is off map!" % (pos[0], pos[1])
    return False     

class Game(object):
  def __init__(self, display, actors, map):
    self.map = map
    self.display = display
    self.actors = actors
    self.current_actor = actors[0]
    self.turn_count = 0
    for actor in actors:
      actor.set_game(self)
      pos = (random.randint(0, self.map.max_i),
             random.randint(0, self.map.max_j))
      # Generate a random position that's not already taken
      while not self.is_move_legal(actor, pos):
        pos = (random.randint(0, self.map.max_i),
               random.randint(0, self.map.max_j))
      actor.set_position(pos)
      
    #self.font = pygame.font.SysFont('mono', 20, bold=True)

  def update(self):
    for actor in actors:
      actor.update()
    if (self.current_actor.is_turn_over()):
      self.turn_count += 1            
      actors.pop(0)
      actors.append(self.current_actor)
      self.current_actor = actors[0]
      self.current_actor.start_turn()
  
  def to_screen(self, ij):
    return (ij[0]*CELL_SIZE, ij[1]*CELL_SIZE)

  def is_move_legal(self, actor, pos):
    if (not self.map.is_move_legal(pos)):
      return False
    for actor in actors:
      if (pos[0] == actor.pos[0] and pos[1] == actor.pos[1]):
        print "Other actor at %d %d" % (pos[0], pos[1])
        return False
    return True

  def run(self):
    loop = True
    while loop:
      self.update()
      for event in pygame.event.get():
        if (event.type == pygame.QUIT or
            (event.type == pygame.KEYDOWN and
             event.key == pygame.K_ESCAPE)):
          loop = False    
        else:
          self.current_actor.handle_event(game, event)           
      self.display.draw(self.actors, self.current_actor.get_info_text())
    pygame.quit()

    
if __name__ == '__main__':
  pygame.font.init()
  actors = []
  actors.append(Unicorn("Cherry 1"))
  actors.append(Unicorn("Cherry 2"))
  actors.append(Unicorn("Cherry 3"))
  actors.append(Unicorn("Cherry 4"))
  actors.append(Unicorn("Cherry 5"))
  actors.append(Robot("Bad robot 1"))
  actors.append(Robot("Bad robot 2"))
  actors.append(Robot("Bad robot 3"))
  actors.append(Robot("Bad robot 4"))
  actors.append(Robot("Bad robot 5"))
  display = Display()
  map = Map(display.size[0]/CELL_SIZE, display.size[1]/CELL_SIZE)
  game = Game(display, actors, map)
  game.run()
