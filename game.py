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

        # Nhóm quản lý các đối tượng
        self.walls = pygame.sprite.Group()
        self.stairs = pygame.sprite.Group()
        self.characters = pygame.sprite.Group()
        self.traps = pygame.sprite.Group()
        self.keys = pygame.sprite.Group()

        # Tải cấp độ hiện tại
        self.load_level()

        self.audio_manager = audio_manager
        self.audio_manager.play_background_music()

        # Khởi tạo menu tùy chọn
        self.options_menu = OptionsMenu(self.audio_manager)

        # Danh sách các nút bấm
        self.buttons = [
            {"rect": pygame.Rect(12, 135, 125, 35), "action": lambda: undo_move(self.audio_manager), "label": "UNDO MOVE"},
            {"rect": pygame.Rect(12, 180, 125, 35), "action": lambda: reset_maze(self.audio_manager), "label": "RESET MAZE"},
            {"rect": pygame.Rect(12, 230, 125, 35), "action": lambda: show_options(self.options_menu, self.audio_manager), "label": "OPTIONS"},
            {"rect": pygame.Rect(12, 270, 125, 35), "action": lambda: show_world_map(self, self.audio_manager), "label": "WORLD MAP"},
            {"rect": pygame.Rect(12, 435, 125, 35), "action": lambda: quit_to_main(self.audio_manager), "label": "QUIT TO MAIN"}
        ]

    def load_level(self):
        """Tải dữ liệu cấp độ từ LevelManager"""
        self.walls.empty()
        self.stairs.empty()
        self.characters.empty()
        self.traps.empty()
        self.keys.empty()
        self.mummies = []
        self.scorpions = []

        maze, stairs_positions, player_start, mummies_data, scorpions_data, traps_data, keys_data = self.level_manager.get_current_level_data()
        
        if maze is None:
            print(f"Không thể tải cấp độ {self.level_manager.current_level + 1}!")
            return

        # Debug: In ra dữ liệu vừa load
        print(f"Debug level {self.level_manager.current_level + 1}:")
        print("Maze:", maze)
        print("Stairs:", stairs_positions)
        print("Player Start:", player_start)
        print("Mummies:", mummies_data)
        print("Scorpions:", scorpions_data)
        print("Traps:", traps_data)
        print("Keys:", keys_data)

        # Khởi tạo người chơi
        player_x = 215 + player_start["col"] * CELL_SIZE
        player_y = 80 + player_start["row"] * CELL_SIZE
        self.player = Player(player_x, player_y)
        self.characters.add(self.player)

        # Khởi tạo xác ướp
        for mummy_data in mummies_data:
            mummy_x = 215 + mummy_data["col"] * CELL_SIZE
            mummy_y = 80 + mummy_data["row"] * CELL_SIZE
            color = mummy_data["color"].lower()  # Normalize to lowercase
            if color not in ["white", "red"]:
                print(f"Warning: Invalid mummy color '{color}' in level {self.level_manager.current_level + 1}. Using 'white'.")
                color = "white"
            mummy = Mummy(mummy_x, mummy_y, color=color)
            self.mummies.append(mummy)
            self.characters.add(mummy)
            
        # Khởi tạo bò cạp
        for scorpion_data in scorpions_data:
            scorpion_x = 215 + scorpion_data["col"] * CELL_SIZE
            scorpion_y = 80 + scorpion_data["row"] * CELL_SIZE
            color = scorpion_data["color"].lower()  # Normalize to lowercase
            if color not in ["white", "red"]:
                print(f"Warning: Invalid scorpion color '{color}' in level {self.level_manager.current_level + 1}. Using 'white'.")
                color = "white"
            scorpion = Scorpion(scorpion_x, scorpion_y, color=color)
            self.scorpions.append(scorpion)
            self.characters.add(scorpion)
        # Khởi tạo bẫy
        for trap_data in traps_data:
            trap_x = 215 + trap_data["col"] * CELL_SIZE
            trap_y = 80 + trap_data["row"] * CELL_SIZE
            self.traps.add(Trap(trap_x, trap_y))

        # Khởi tạo chìa khóa
        for key_data in keys_data:
            key_x = 215 + key_data["col"] * CELL_SIZE
            key_y = 80 + key_data["row"] * CELL_SIZE
            self.keys.add(Key(key_x, key_y))

        # Tạo tường và cầu thang
        self.create_objects(maze, stairs_positions)

    def create_objects(self, maze, stairs_positions):
        """Tạo tường và cầu thang dựa trên dữ liệu mê cung"""
        for row in range(len(maze)):
            for col in range(len(maze[row])):
                cell = maze[row][col]
                x = 215 + col * CELL_SIZE
                y = 80 + row * CELL_SIZE

                # Tạo tường
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

        # Tạo cầu thang
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
        """Kiểm tra va chạm giữa các đối tượng"""
        # Player chạm bẫy -> Thua
        if pygame.sprite.spritecollide(self.player, self.traps, False):
            print("Người chơi rơi vào bẫy! Trò chơi kết thúc!")
            return "menu"

        # Player chạm chìa khóa -> Nhặt chìa
        keys_hit = pygame.sprite.spritecollide(self.player, self.keys, True)
        if keys_hit:
            print("Người chơi nhặt được chìa khóa! (Không có hàng rào để mở.)")

        # Player chạm cầu thang -> Chuyển cấp độ
        if pygame.sprite.spritecollide(self.player, self.stairs, False):
            print(f"Hoàn thành cấp độ {self.level_manager.current_level + 1}!")
            if self.level_manager.next_level():
                print(f"Tải cấp độ {self.level_manager.current_level + 1}")
                return "load_level"
            else:
                print("Đã hoàn thành tất cả cấp độ! Quay lại menu.")
                return "menu"

        # Xác ướp và bò cạp chạm nhau -> Bò cạp bị tiêu diệt
        for mummy in self.mummies:
            for scorpion in self.scorpions:
                if pygame.sprite.collide_rect(mummy, scorpion):
                    print("Xác ướp và bò cạp va chạm! Bò cạp bị tiêu diệt.")
                    self.scorpions.remove(scorpion)
                    self.characters.remove(scorpion)

        # Xác ướp chạm xác ướp -> Một xác ướp bị tiêu diệt
        for i, mummy1 in enumerate(self.mummies):
            for j, mummy2 in enumerate(self.mummies):
                if i != j and pygame.sprite.collide_rect(mummy1, mummy2):
                    print("Hai xác ướp va chạm! Một xác ướp bị tiêu diệt.")
                    self.mummies.remove(mummy2)
                    self.characters.remove(mummy2)
                    break

        # Người chơi chạm xác ướp hoặc bò cạp -> Thua
        for character in self.characters:
            if character != self.player and pygame.sprite.collide_rect(self.player, character):
                print("Người chơi va chạm với kẻ địch! Trò chơi kết thúc!")
                return "menu"

        return "play"

    def draw_game(self):
        """Vẽ màn hình game lên screen"""
        self.game_screen.blit(self.backdrop, (0, 0))
        self.game_screen.blit(self.floor, (215, 80))
        self.game_screen.blit(self.title_img, (10, 10))
        self.game_screen.blit(self.snake_img, (10, 60))

        # Vẽ tất cả sprite
        self.walls.draw(self.game_screen)
        self.stairs.draw(self.game_screen)
        self.characters.draw(self.game_screen)
        self.traps.draw(self.game_screen)
        self.keys.draw(self.game_screen)
        self.options_menu.draw(self.game_screen)
        self.characters.update()

    def handled_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "menu"
            elif event.key == pygame.K_UP:
                if self.player.move("up", self.level_manager.get_current_level_data()[0], self.walls):
                    for mummy in self.mummies:
                        mummy.auto_move(self.player.row, self.player.col, self.level_manager.get_current_level_data()[0], self.walls)
                    for scorpion in self.scorpions:
                        scorpion.auto_move(self.player.row, self.player.col, self.level_manager.get_current_level_data()[0], self.walls)
                    return self.check_collisions()
            elif event.key == pygame.K_DOWN:
                if self.player.move("down", self.level_manager.get_current_level_data()[0], self.walls):
                    for mummy in self.mummies:
                        mummy.auto_move(self.player.row, self.player.col, self.level_manager.get_current_level_data()[0], self.walls)
                    for scorpion in self.scorpions:
                        scorpion.auto_move(self.player.row, self.player.col, self.level_manager.get_current_level_data()[0], self.walls)
                    return self.check_collisions()
            elif event.key == pygame.K_LEFT:
                if self.player.move("left", self.level_manager.get_current_level_data()[0], self.walls):
                    for mummy in self.mummies:
                        mummy.auto_move(self.player.row, self.player.col, self.level_manager.get_current_level_data()[0], self.walls)
                    for scorpion in self.scorpions:
                        scorpion.auto_move(self.player.row, self.player.col, self.level_manager.get_current_level_data()[0], self.walls)
                    return self.check_collisions()
            elif event.key == pygame.K_RIGHT:
                if self.player.move("right", self.level_manager.get_current_level_data()[0], self.walls):
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
                        button["action"]()
                        break
        return "play"