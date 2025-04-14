import pygame
from images import IMAGES
from constants import*

class Wall(pygame.sprite.Sprite):
    def __init__(self, x , y , wall_type):
        super().__init__()
        if wall_type == "W_h":
             self.image = IMAGES["wall_horizontal"]
        elif wall_type == "W_v":
            self.image = IMAGES["wall_vertical"]
        else:   
            raise ValueError(f"Loại tường không hợp lệ: {wall_type}")
        
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))
        self.rect = self.image.get_rect(topleft=(x, y))

class Stair(pygame.sprite.Sprite):
    def __init__(self, x, y, stair_type):
        super().__init__()
        if stair_type == "S_r":
            self.image = IMAGES["stairs_right"]
        elif stair_type == "S_l":
            self.image = IMAGES["stairs_left"]
        elif stair_type == "S_t":
            self.image = IMAGES["stairs_top"]
        elif stair_type == "S_b":
            self.image = IMAGES["stairs_bottom"]

        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))
        self.rect = self.image.get_rect(topleft=(x, y))