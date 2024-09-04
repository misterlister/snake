import random
import pygame as pg
import os
from constants import (
    SEG_LENGTH,
    DIS_WIDTH,
    HEADER_HEIGHT,
    PLAY_HEIGHT,
    SPRITE_SCALE,
    SPRITES_DIR
)

class Sprite():
    def __init__(self, dis):
        self.image, self.rect = None, None
        self.x, self.y = None, None
        self.place_object()
        self.dis = dis
        
    def display(self):
        self.dis.blit(self.image, self.rect)

    def collide(self, obj, radius):
        if (obj.x - self.x <= radius and obj.x - self.x >= -radius):
            if (obj.y - self.y <= radius and obj.y - self.y >= -radius):
                return True
        return False
    
    def place_object(self):
        margin = int(SEG_LENGTH // 2)
        self.x = round(random.randrange(margin, int(DIS_WIDTH - margin)))
        self.y = round(random.randrange(margin, int(PLAY_HEIGHT - margin))) + HEADER_HEIGHT*2 + margin

    def rotate(self,angle):
        self.image = pg.transform.rotate(self.image, angle)

def load_image(name, scale = SPRITE_SCALE):
    fullname = os.path.join(SPRITES_DIR, name)
    image = pg.image.load(fullname)

    size = image.get_size()
    size = (size[0] * scale, size[1] * scale)
    image = pg.transform.scale(image, size)

    image.convert()
    return image, image.get_rect()
