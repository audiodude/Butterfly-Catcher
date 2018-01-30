import pygame
from pygame.locals import *

import random

SCREEN_RECT = Rect(0, 0, 640, 480)
BG_COLOR = (0,0,0)

# Made up units, in terms of the screen size
PTX = SCREEN_RECT.width/32

class RedBrick(pygame.sprite.Sprite):
  def __init__(self, start_rect):
    pygame.sprite.Sprite.__init__(self, self.containers)
    self.rect = start_rect
    self.image = pygame.Surface((self.rect.width, self.rect.height))
    self.image.fill((255,0,0))
    self.speed = 10
    self.direction = random.choice((-1,1))

  def update(self):
    self.rect.move_ip(0, self.speed*self.direction)
    if self.rect.bottom >= SCREEN_RECT.bottom or self.rect.top <= SCREEN_RECT.top:
      self.direction *= -1

class BlueBrick(pygame.sprite.Sprite):
  TOP, RIGHT, BOTTOM, LEFT = 0, 1, 2, 3
  
  def __init__(self, start_rect):
    pygame.sprite.Sprite.__init__(self, self.containers)
    self.rect = start_rect
    self.images = { 1 : pygame.Surface((self.rect.width, self.rect.height)).convert(),
                   -1 : pygame.Surface((self.rect.height, self.rect.width)).convert()}
    
    for image in list(self.images.values()):
      image.fill((0,0,255))

    self.orientation = 1
    self.image = self.images[self.orientation]

  def move(self, x, y):
    self.rect.move_ip(x, y)
    self.rect.clamp_ip(SCREEN_RECT)
    
  def flip(self):
    self.rect.width, self.rect.height, self.rect.center = self.rect.height, self.rect.width, self.rect.center          
    self.orientation *= -1
    self.image = self.images[self.orientation]

class Score(pygame.sprite.Sprite):
  def __init__(self, position=(0,0), scorekeeper=None, centered=True, bottomed=False, fmt_string="%d", color=Color('white')):
    pygame.sprite.Sprite.__init__(self)
    self.position = list(position)[0:2]
    self.scorekeeper = scorekeeper
    self.centered = centered
    self.bottomed = bottomed
    self.fmt_string = fmt_string
    self.color = color
    
    self.font = pygame.font.SysFont('verdana,arial', 32, bold=True)
    self.lastscore = None
    self.update()
    
    img_rect = self.image.get_rect()
    if self.centered:
      self.position[0] -= img_rect.width/2
    if self.bottomed:
      self.position[1] -= img_rect.height
    
    self.rect = img_rect.move(self.position)

  def update(self):
    score = (self.scorekeeper and self.scorekeeper()) or 0
    if score != self.lastscore:
      self.lastscore = score
      msg = self.fmt_string % score
      self.image = self.font.render(msg, 0, self.color, BG_COLOR)

class MainController():
  def __init__(self):
    self.score = 0
    self.total_time_millis = 0
    
  def current_score(self):
    return self.score
    
  def time_remaining_secs(self):
    return self.time_remaining_millis()/1000.0

  def time_remaining_millis(self):
    return 30000 - self.total_time_millis
    
  def total_time_secs(self):
    return self.total_time_millis/1000.0
    
  def main(self):
    pygame.init()
  
    # Init the screen
    screen = pygame.display.set_mode((SCREEN_RECT.width, SCREEN_RECT.height))
    pygame.display.set_caption('Butterfly Catcher')
    pygame.mouse.set_visible(0)
  
    # The background
    background = pygame.Surface((SCREEN_RECT.width, SCREEN_RECT.height))
    background.fill(BG_COLOR)
    screen.blit(background, (0,0))
    pygame.display.flip()
    
    # Sprite groups
    all = pygame.sprite.OrderedUpdates()
    red = pygame.sprite.Group()
    blue = pygame.sprite.Group()
  
    # Ladies and Gentlemen, our Sprites!
    if pygame.font:
        all.add(Score(SCREEN_RECT.midtop, scorekeeper=self.current_score))
        
        # Awesome hack here. The timer is just a Score that uses #time_remaining_secs as its scorekeeper
        all.add(Score(SCREEN_RECT.midbottom, scorekeeper=self.time_remaining_secs, bottomed=True, fmt_string="%2.2f", color=Color('yellow')))
      
    RedBrick.containers = all, red
    for i in range(4):
      RedBrick(Rect(5*PTX+(7*PTX*i), SCREEN_RECT.centery, PTX, PTX)) #recall that PTX is our made up unit
  
    BlueBrick.containers = all, blue
    BlueBrick(Rect(SCREEN_RECT.midbottom[0] - 2*PTX, SCREEN_RECT.midbottom[1] - 5*PTX, 4*PTX, PTX/2))
        
    # The clock
    clock = pygame.time.Clock()

    # Blue brick movement
    velocity = [0, 0, 0, 0]
    ACCEL = 20
  
    while True:
      # decrement the timer and limit the framerate to 60fps
      if self.time_remaining_millis() > 0:
        self.total_time_millis += clock.tick(60)
        
      for event in pygame.event.get():
          print(event)
          if event.type == QUIT:
              return self.score #Game Over
          elif event.type == KEYDOWN and event.key == K_ESCAPE:
              return self.score #Game Over
          elif event.type == KEYDOWN and (event.key == K_z or event.key == K_x or event.key == K_SPACE):
            for b in blue.sprites():
              b.flip()

      # This hack 'freezes' the game when the time runs out.
      # Since it comes after event queue processing, you can still quit (and FIXME: flip the paddles, but the screen doesn't update).
      if self.time_remaining_millis() <= 0:
        continue

      # Modify velocity based on keypresses
      keystate = pygame.key.get_pressed()
      for state, idx in zip((K_RIGHT, K_LEFT, K_UP, K_DOWN), list(range(4))):
        if keystate[state]:
          velocity[idx] += 1
          if velocity[idx] > 16:
            velocity[idx] = 16
        else:
          velocity[idx] -= 1.5
          if velocity[idx] < 0:
            velocity[idx] = 0
                
      for b in blue.sprites():
        b.move(velocity[0] - velocity[1], velocity[3] - velocity[2])
    
      # clear/erase the last drawn sprites
      all.clear(screen, background)

      all.update()
    
      # Did any of the red bricks get captured?
      for r in list(pygame.sprite.groupcollide(blue, red, 0, 1).values()):
        self.score += 1 # you get a cookie
        
        # Make a new butterfly in a random spot
        new_spot = Rect(int(random.random()*(SCREEN_RECT.width-PTX*2)+PTX),
                      int(random.random()*(SCREEN_RECT.height-PTX*2)+PTX),
                      PTX,
                      PTX).clamp(SCREEN_RECT) 
        RedBrick(new_spot)

      #draw the scene
      dirty = all.draw(screen)
      pygame.display.update(dirty)
  
if __name__ == '__main__':
  mc = MainController()
  mc.main()
  print('%d in %2.2f seconds' % (mc.score, mc.total_time_secs()))

  
