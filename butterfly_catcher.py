import pygame
from pygame.locals import *

import random

SCREEN_RECT = Rect(0, 0, 640, 480)

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
    
    for image in self.images.values():
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

def main():
  pygame.init()
  
  # Init the screen
  screen = pygame.display.set_mode((SCREEN_RECT.width, SCREEN_RECT.height))
  pygame.display.set_caption('Hello Pygame')
  pygame.mouse.set_visible(0)
  
  # The background
  background = pygame.Surface((SCREEN_RECT.width, SCREEN_RECT.height))
  background.fill((0,0,0))
  screen.blit(background, (0,0))
  pygame.display.flip()
    
  # Sprite groups
  all = pygame.sprite.RenderUpdates()
  red = pygame.sprite.Group()
  blue = pygame.sprite.Group()
  
  # Ladies and Gentlemen, our Sprites!
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
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == QUIT:
            return #Game Over
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            return
        elif event.type == KEYDOWN and (event.key == K_z or event.key == K_x or event.key == K_SPACE):
          for b in blue.sprites():
            b.flip()

    # Modify velocity based on keypresses
    keystate = pygame.key.get_pressed()
    for state, idx in zip((K_RIGHT, K_LEFT, K_UP, K_DOWN), range(4)):
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
    for r in pygame.sprite.groupcollide(blue, red, 0, 1).values():
      RedBrick(Rect(int(random.random()*SCREEN_RECT.width-PTX), SCREEN_RECT.centery, PTX, PTX).clamp(SCREEN_RECT))

    #draw the scene
    dirty = all.draw(screen)
    pygame.display.update(dirty)
  
if __name__ == '__main__':
  main()

  