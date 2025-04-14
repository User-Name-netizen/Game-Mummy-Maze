import pygame
from constants import CELL_SIZE
from images import IMAGES

class Character(pygame.sprite.Sprite):
    def __init__(self, x, y, images):
        super().__init__()
        self.images = images
        self.direction = "down"
        self.image = self.images[self.direction][0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.row = (y - 80) // CELL_SIZE
        self.col = (x - 215) // CELL_SIZE
        # Animation attributes
        self.moving = False
        self.move_speed = 4  # Pixels per frame
        self.target_pos = (x, y)
        self.current_pos = [float(x), float(y)]

        self.frame_index = 0
        self.animation_speed = 0.2  # Tốc độ chuyển khung hình (càng nhỏ càng nhanh)
        self.last_update = pygame.time.get_ticks()

    def update_image(self):
        """Cập nhật khung hình hiện tại dựa trên hướng và animation."""
        if self.moving:
            now = pygame.time.get_ticks()
            if now - self.last_update > 100:  # Cập nhật khung hình mỗi 100ms
                self.frame_index = (self.frame_index + 1) % len(self.images[self.direction])
                self.last_update = now
            self.image = self.images[self.direction][int(self.frame_index)]
        else:
            self.frame_index = 0
            self.image = self.images[self.direction][0]
    def update(self):
        if self.moving:
            target_x, target_y = self.target_pos
            dx = target_x - self.current_pos[0]
            dy = target_y - self.current_pos[1]
            distance = (dx**2 + dy**2)**0.5

            if distance <= self.move_speed:
                self.current_pos = [target_x, target_y]
                self.rect.topleft = (int(self.current_pos[0]), int(self.current_pos[1]))
                self.moving = False
                self.frame_index = 0
            else:
                move_x = (dx / distance) * self.move_speed
                move_y = (dy / distance) * self.move_speed
                self.current_pos[0] += move_x
                self.current_pos[1] += move_y
                self.rect.topleft = (int(self.current_pos[0]), int(self.current_pos[1]))
            self.update_image()

    def can_move(self, row, col, maze, walls):
        if not (0 <= row < 7 and 0 <= col < 7):
            return False
        cell = maze[row][col]
        if "walls" in cell:
            for wall in cell["walls"]:
                if (wall == "top" and self.direction == "up") or \
                   (wall == "bottom" and self.direction == "down") or \
                   (wall == "left" and self.direction == "left") or \
                   (wall == "right" and self.direction == "right"):
                    return False
        return True

class Player(Character):
    def __init__(self, x, y):
        images = {
            "up": IMAGES["player"]["up"],
            "down": IMAGES["player"]["down"],
            "left": IMAGES["player"]["left"],
            "right": IMAGES["player"]["right"]
        }
        super().__init__(x, y, images)

    def move(self, direction, maze, walls):
        if self.moving:
            return False
        new_row, new_col = self.row, self.col
        if direction == "up":
            new_row -= 1
            self.direction = "up"
        elif direction == "down":
            new_row += 1
            self.direction = "down"
        elif direction == "left":
            new_col -= 1
            self.direction = "left"
        elif direction == "right":
            new_col += 1
            self.direction = "right"
        if self.can_move(new_row, new_col, maze, walls):
            self.row, self.col = new_row, new_col
            self.target_pos = (215 + self.col * CELL_SIZE, 80 + self.row * CELL_SIZE)
            self.moving = True
            self.update_image()
            return True
        return False

class Mummy(Character):
    def __init__(self, x, y, color="white"):
        images = {
            "up": IMAGES["mummy"][f"{color}_up"],
            "down": IMAGES["mummy"][f"{color}_down"],
            "left": IMAGES["mummy"][f"{color}_left"],
            "right": IMAGES["mummy"][f"{color}_right"]
        }
        super().__init__(x, y, images)
        self.color = color

    def auto_move(self, player_row, player_col, maze, walls):
        if self.moving:
            return
        for _ in range(2):
            if self.color == "white":
                directions = ["left", "right", "up", "down"]
            else:
                directions = ["up", "down", "left", "right"]
            for direction in directions:
                new_row, new_col = self.row, self.col
                if direction == "up":
                    new_row -= 1
                elif direction == "down":
                    new_row += 1
                elif direction == "left":
                    new_col -= 1
                elif direction == "right":
                    new_col += 1
                if self.can_move(new_row, new_col, maze, walls):
                    self.row, self.col = new_row, new_col
                    self.direction = direction
                    self.target_pos = (215 + self.col * CELL_SIZE, 80 + self.row * CELL_SIZE)
                    self.moving = True
                    self.update_image()
                    break

class Scorpion(Character):
    def __init__(self, x, y, color="white"):
        images = {
            "up": IMAGES["scorpion"][f"{color}_up"],
            "down": IMAGES["scorpion"][f"{color}_down"],
            "left": IMAGES["scorpion"][f"{color}_left"],
            "right": IMAGES["scorpion"][f"{color}_right"]
        }
        super().__init__(x, y, images)
        self.color = color

    def auto_move(self, player_row, player_col, maze, walls):
        if self.moving:
            return
        if self.color == "white":
            directions = ["left", "right", "up", "down"]
        else:
            directions = ["up", "down", "left", "right"]
        for direction in directions:
            new_row, new_col = self.row, self.col
            if direction == "up":
                new_row -= 1
            elif direction == "down":
                new_row += 1
            elif direction == "left":
                new_col -= 1
            elif direction == "right":
                new_col += 1
            if self.can_move(new_row, new_col, maze, walls):
                self.row, self.col = new_row, new_col
                self.direction = direction
                self.target_pos = (215 + self.col * CELL_SIZE, 80 + self.row * CELL_SIZE)
                self.moving = True
                self.update_image()
                break

class Trap(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(IMAGES["trap_skull"], (CELL_SIZE, CELL_SIZE))
        self.rect = self.image.get_rect(topleft=(x, y))

class Key(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(IMAGES["key"], (CELL_SIZE, CELL_SIZE))
        self.rect = self.image.get_rect(topleft=(x, y))