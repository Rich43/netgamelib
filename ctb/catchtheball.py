#! /usr/bin/env python
#Open two of me to test.
import netgamelib
import pygame
import random
import time
from pygame.locals import *
import catchtheball_sprites
# image
# ['__class__', '__copy__', '__delattr__', '__doc__', '__getattribute__', 
# '__hash__', '__init__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', 
# '__setattr__', '__str__', 'blit', 'convert', 'convert_alpha', 'copy', 'fill', 
# 'get_abs_offset', 'get_abs_parent', 'get_alpha', 'get_at', 'get_bitsize', 
# 'get_bounding_rect', 'get_buffer', 'get_bytesize', 'get_clip', 'get_colorkey',
# 'get_flags', 'get_height', 'get_locked', 'get_losses', 'get_masks', 'get_offset',
# 'get_palette', 'get_palette_at', 'get_parent', 'get_pitch', 'get_rect', 
# 'get_shifts', 'get_size', 'get_width', 'lock', 'map_rgb', 'mustlock', 
# 'set_alpha', 'set_at', 'set_clip', 'set_colorkey', 'set_palette', 
# 'set_palette_at', 'subsurface', 'unlock', 'unmap_rgb']

class Game(netgamelib.Client):
    """Class that inherits netgamelib"""
    pipes = []
    screenres = (900,600)
    pipecount = 4
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Catch the Ball")
        
        # Add sprites and configure other things....
        self.screen = pygame.display.set_mode(self.screenres, HWSURFACE|DOUBLEBUF)
        self.sprites = pygame.sprite.RenderUpdates()
        self.playerno = random.randrange(1,1000) # your unique player id
        self.other = catchtheball_sprites.Other() # other player class
        
        self.player = catchtheball_sprites.Player(self)
        self.playergroup = pygame.sprite.Group()
        self.playergroup.add(self.player)
        
        self.ball = catchtheball_sprites.Ball(self)
        self.ballgroup = pygame.sprite.Group()
        self.ballgroup.add(self.ball)
        
        # Configure Pipes
        for i in range(0,self.pipecount):
            pipe = catchtheball_sprites.Pipe(self)
            offset = pipe.image.get_width()
            pipe.setLeft((pipe.image.get_width() * 2 * i) + offset)
            self.pipes.append(pipe)
        
        # Configure ball
        random.seed(time.time())
        pipe = random.choice(self.pipes)
        self.ball.setCenter(pipe.rect.center)
        pygame.mouse.set_visible(0)

    def Connected(self):
        print "Getting ID..."
        #print "ID IS", self.GetID()
    def DataRecieved(self, data, rawdata, client):
        """Data Recieved Callback"""
        print data
        if data[0] <> self.playerno:
            self.other.setCenter((data[1],data[2]))
            
    def gameloop(self):
        """Main Loop"""
        for event in pygame.event.get():
            if((event.type == KEYDOWN and event.key == K_ESCAPE) or
             event.type == QUIT):
                self.disconnect()   # Disconnect from server
                
        self.screen.fill((255, 255, 255))
        self.sprites.draw(self.screen)
        self.sprites.update()
        pygame.display.flip()

if __name__ == "__main__":
    mygame = Game()
    mygame.connect(ip='127.0.0.1',port=9999)   # Connect to server, remove arguments to default to localhost
