import pygame
from images import IMAGES
from constants import *
from sprites import Wall, Stair
from button_function import undo_move, reset_maze, show_options, show_world_map, quit_to_main, OptionsMenu
from audio_manager import AudioManager
from level_manager import LevelManager
from character import Player, Mummy, Scorpion, Trap, Key

class Game:
    def __init__(self, game_screen, audio_manager, level_manager, map_instance):
        self.game_screen = game_screen
        self.level_manager = level_manager
        self.map_instance = map_instance
        self.backdrop = IMAGES["backdrop"]
        self.floor = IMAGES["floor"]
        self.title_img = IMAGES["mumlogo"]
        self.snake_img = pygame.image.load("images/snake.png")
        self.snake_img = pygame.transform.scale(self.snake_img, (130, 80))
        self.game_over_img = IMAGES["game_over"]
        self.game_over_rect = self.game_over_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))

        self.walls = pygame.sprite.Group()
        self.stairs = pygame.sprite.Group()
        self.characters = pygame.sprite.Group()
        self.traps = pygame.sprite.Group()
        self.keys = pygame.sprite.Group()

        self.game_over = False
        self.move_history = []

        self.load_level()

        self.audio_manager = audio_manager
        self.audio_manager.play_background_music()

        self.options_menu = OptionsMenu(self.audio_manager)

        self.buttons = [
            {"rect": pygame.Rect(12, 135, 125, 35), "action": lambda: undo_move(self.audio_manager), "label": "UNDO MOVE"},
            {"rect": pygame.Rect(12, 180, 125, 35), "action": lambda: reset_maze(self.audio_manager), "label": "RESET MAZE"},
            {"rect": pygame.Rect(12, 230, 125, 35), "action": lambda: show_options(self.options_menu, self.audio_manager), "label": "OPTIONS"},
            {"rect": pygame.Rect(12, 270, 125, 35), "action": lambda: show_world_map(self, self.audio_manager), "label": "WORLD MAP"},
            {"rect": pygame.Rect(12, 435, 125, 35), "action": lambda: quit_to_main(self.audio_manager), "label": "QUIT TO MAIN"}
        ]

        self.game_over_buttons = [
            {"rect": pygame.Rect(239, 300, 106, 16), "action": self.try_again, "label": "TRY AGAIN"},
            {"rect": pygame.Rect(230, 341, 106, 19), "action": self.undo_last_move, "label": "UNDO MOVE"},
            {"rect": pygame.Rect(406, 300, 119, 17), "action": self.show_world_map, "label": "WORLD MAP"}
        ]

    def load_level(self):
        self.walls.empty()
        self.stairs.empty()
        self.characters.empty()
        self.traps.empty()
        self.keys.empty()
        self.mummies = []
        self.scorpions = []
        self.move_history.clear()
        self.game_over = False

        maze, stairs_positions, player_start, mummies_data, scorpions_data, traps_data, keys_data = self.level_manager.get_current_level_data()
        
        if maze is None:
            print(f"Không thể tải cấp độ {self.level_manager.current_level + 1}!")
            return

        print(f"Debug level {self.level_manager.current_level + 1}:")
        print("Maze:", maze)
        print("Stairs:", stairs_positions)
        print("Player Start:", player_start)
        print("Mummies:", mummies_data)
        print("Scorpions:", scorpions_data)
        print("Traps:", traps_data)
        print("Keys:", keys_data)

        player_x = 215 + player_start["col"] * CELL_SIZE
        player_y = 80 + player_start["row"] * CELL_SIZE
        self.player = Player(player_x, player_y)
        self.characters.add(self.player)

        for mummy_data in mummies_data:
            mummy_x = 215 + mummy_data["col"] * CELL_SIZE
            mummy_y = 80 + mummy_data["row"] * CELL_SIZE
            color = mummy_data["color"].lower()
            if color not in ["white", "red"]:
                print(f"Warning: Invalid mummy color '{color}' in level {self.level_manager.current_level + 1}. Using 'white'.")
                color = "white"
            mummy = Mummy(mummy_x, mummy_y, color=color)
            self.mummies.append(mummy)
            self.characters.add(mummy)
            
        for scorpion_data in scorpions_data:
            scorpion_x = 215 + scorpion_data["col"] * CELL_SIZE
            scorpion_y = 80 + scorpion_data["row"] * CELL_SIZE
            color = scorpion_data["color"].lower()
            if color not in ["white", "red"]:
                print(f"Warning: Invalid scorpion color '{color}' in level {self.level_manager.current_level + 1}. Using 'white'.")
                color = "white"
            scorpion = Scorpion(scorpion_x, scorpion_y, color=color)
            self.scorpions.append(scorpion)
            self.characters.add(scorpion)
        for trap_data in traps_data:
            trap_x = 215 + trap_data["col"] * CELL_SIZE
            trap_y = 80 + trap_data["row"] * CELL_SIZE
            self.traps.add(Trap(trap_x, trap_y))

        for key_data in keys_data:
            key_x = 215 + key_data["col"] * CELL_SIZE
            key_y = 80 + key_data["row"] * CELL_SIZE
            self.keys.add(Key(key_x, key_y))

        self.create_objects(maze, stairs_positions)

    def create_objects(self, maze, stairs_positions):
        for row in range(len(maze)):
            for col in range(len(maze[row])):
                cell = maze[row][col]
                x = 215 + col * CELL_SIZE
                y = 80 + row * CELL_SIZE
                if "walls" in cell:
                    for wall_type in cell["walls"]:
                        if wall_type == "top":
                            self.walls.add(Wall(x, y, "W_h"))
                        elif wall_type == "bottom":
                            self.walls.add(Wall(x, y + CELL_SIZE, "W_h"))
                        elif wall_type == "left":
                            self.walls.add(Wall(x, y, "W_v"))
                        elif wall_type == "right":
                            self.walls.add(Wall(x + CELL_SIZE, y, "W_v"))

        for stair in stairs_positions:
            row = stair["row"]
            col = stair["col"]
            x = 215 + col * CELL_SIZE
            y = 80 + row * CELL_SIZE
            if 0 <= row <= 6 and 0 <= col <= 6:
                self.stairs.add(Stair(x, y, stair["type"]))
            else:
                print(f"Vị trí cầu thang không hợp lệ: row={row}, col={col}")

    def check_collisions(self):
        if pygame.sprite.spritecollide(self.player, self.traps, False):
            print("Người chơi rơi vào bẫy! Trò chơi kết thúc!")
            self.game_over = True
            print(f"Game Over state set to: {self.game_over}")
            return "play"

        keys_hit = pygame.sprite.spritecollide(self.player, self.keys, True)
        if keys_hit:
            print("Người chơi nhặt được chìa khóa! (Không có hàng rào để mở.)")

        if pygame.sprite.spritecollide(self.player, self.stairs, False):
            print(f"Hoàn thành cấp độ {self.level_manager.current_level + 1}!")
            if self.level_manager.next_level():
                print(f"Tải cấp độ {self.level_manager.current_level + 1}")
                return "load_level"
            else:
                print("Đã hoàn thành tất cả cấp độ! Quay lại menu.")
                return "menu"

        for mummy in self.mummies:
            for scorpion in self.scorpions:
                if pygame.sprite.collide_rect(mummy, scorpion):
                    print("Xác ướp và bò cạp va chạm! Bò cạp bị tiêu diệt.")
                    self.scorpions.remove(scorpion)
                    self.characters.remove(scorpion)

        for i, mummy1 in enumerate(self.mummies):
            for j, mummy2 in enumerate(self.mummies):
                if i != j and pygame.sprite.collide_rect(mummy1, mummy2):
                    print("Hai xác ướp va chạm! Một xác ướp bị tiêu diệt.")
                    self.mummies.remove(mummy2)
                    self.characters.remove(mummy2)
                    break

        for character in self.characters:
            if character != self.player and pygame.sprite.collide_rect(self.player, character):
                print("Người chơi va chạm với kẻ địch! Trò chơi kết thúc!")
                self.game_over = True
                print(f"Game Over state set to: {self.game_over}")
                return "play"

        return "play"

    def try_again(self):
        print("Trying again... Reloading level.")
        self.load_level()
        self.audio_manager.play_button_click()

    def undo_last_move(self):
        if self.move_history:
            last_state = self.move_history.pop()
            player_pos = last_state["player_pos"]
            mummies_data = last_state["mummies"]
            scorpions_data = last_state["scorpions"]
            traps_data = last_state["traps"]

            # Restore player position
            self.player.row, self.player.col = player_pos
            self.player.rect.topleft = (215 + self.player.col * CELL_SIZE, 80 + self.player.row * CELL_SIZE)
            self.player.current_pos = [float(self.player.rect.x), float(self.player.rect.y)]
            self.player.target_pos = (self.player.rect.x, self.player.rect.y)
            self.player.moving = False

            # Clear current enemies and traps
            self.mummies.clear()
            self.scorpions.clear()
            self.characters.empty()
            self.traps.empty()
            self.characters.add(self.player)

            # Restore mummies
            for mummy_data in mummies_data:
                mummy_x = 215 + mummy_data["col"] * CELL_SIZE
                mummy_y = 80 + mummy_data["row"] * CELL_SIZE
                mummy = Mummy(mummy_x, mummy_y, color=mummy_data["color"])
                mummy.row, mummy.col = mummy_data["row"], mummy_data["col"]
                mummy.direction = mummy_data["direction"]
                self.mummies.append(mummy)
                self.characters.add(mummy)

            # Restore scorpions
            for scorpion_data in scorpions_data:
                scorpion_x = 215 + scorpion_data["col"] * CELL_SIZE
                scorpion_y = 80 + scorpion_data["row"] * CELL_SIZE
                scorpion = Scorpion(scorpion_x, scorpion_y, color=scorpion_data["color"])
                scorpion.row, scorpion.col = scorpion_data["row"], scorpion_data["col"]
                scorpion.direction = scorpion_data["direction"]
                self.scorpions.append(scorpion)
                self.characters.add(scorpion)

            # Restore traps
            for trap_data in traps_data:
                trap_x = 215 + trap_data["col"] * CELL_SIZE
                trap_y = 80 + trap_data["row"] * CELL_SIZE
                self.traps.add(Trap(trap_x, trap_y))

            self.game_over = False
            print("Undo Move: Restored previous state.")
            # Re-check collisions to ensure no immediate game over
            self.check_collisions()
        else:
            print("No moves to undo!")
        self.audio_manager.play_button_click()
        return "play"

    def show_world_map(self):
        print("Showing world map...")
        self.map_instance.toggle("play")
        self.game_over = False
        self.audio_manager.play_button_click()
        return "map"

    def draw_game(self):
        self.game_screen.blit(self.backdrop, (0, 0))
        self.game_screen.blit(self.floor, (215, 80))
        self.game_screen.blit(self.title_img, (10, 10))
        self.game_screen.blit(self.snake_img, (10, 60))

        self.walls.draw(self.game_screen)
        self.stairs.draw(self.game_screen)
        self.characters.draw(self.game_screen)
        self.traps.draw(self.game_screen)
        self.keys.draw(self.game_screen)
        self.options_menu.draw(self.game_screen)
        self.characters.update()

        if self.game_over:
            self.game_screen.blit(self.game_over_img, self.game_over_rect)

    def handled_event(self, event):
        if self.game_over:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                print(f"Mouse clicked at: {mouse_pos}")
                for button in self.game_over_buttons:
                    print(f"Button {button['label']} rect: {button['rect']}")
                    if button["rect"].collidepoint(mouse_pos):
                        print(f"Game Over Button clicked: {button['label']}")
                        result = button["action"]()
                        if result:
                            return result
                        break
            return "play"

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "menu"
            elif event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):

                mummies_data = [{"row": m.row, "col": m.col, "color": m.color, "direction": m.direction} for m in self.mummies]
                scorpions_data = [{"row": s.row, "col": s.col, "color": s.color, "direction": s.direction} for s in self.scorpions]
                traps_data = [{"row": (t.rect.y - 80) // CELL_SIZE, "col": (t.rect.x - 215) // CELL_SIZE} for t in self.traps]
                self.move_history.append({
                    "player_pos": (self.player.row, self.player.col),
                    "mummies": mummies_data,
                    "scorpions": scorpions_data,
                    "traps": traps_data
                })

                direction = {
                    pygame.K_UP: "up",
                    pygame.K_DOWN: "down",
                    pygame.K_LEFT: "left",
                    pygame.K_RIGHT: "right"
                }[event.key]

                if self.player.move(direction, self.level_manager.get_current_level_data()[0], self.walls):
                    for mummy in self.mummies:
                        mummy.auto_move(self.player.row, self.player.col, self.level_manager.get_current_level_data()[0], self.walls)
                    for scorpion in self.scorpions:
                        scorpion.auto_move(self.player.row, self.player.col, self.level_manager.get_current_level_data()[0], self.walls)
                    return self.check_collisions()

        if self.options_menu.active:
            if self.options_menu.handle_event(event):
                return "play"
        else:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                print(f"Mouse clicked at: {mouse_pos}")

                for button in self.buttons:
                    if button["rect"].collidepoint(mouse_pos):
                        print(f"Button clicked: {button['label']}")
                        if button["label"] == "QUIT TO MAIN":
                            return "menu"
                        elif button["label"] == "WORLD MAP":
                            self.map_instance.toggle("play")
                            return "map"
                        elif button["label"] == "RESET MAZE":
                            self.load_level()
                        elif button["label"] == "UNDO MOVE":
                            self.undo_last_move()
                        button["action"]()
                        break
        return "play"