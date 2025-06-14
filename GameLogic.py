import pygame
import random
import time
import os
from typing import List, Dict, Tuple, Optional, Callable

# Constants
SYMBOL_MINE = '¤'
SYMBOL_FLAG = '⚑'
WIDTH_CELL = 39
TEXT_PADDING = 20
BACKGROUND_SRC = "background.png"
DEBUG_MODE = False

# Colors
clLightGray = (200, 200, 200)
clWhite = (255, 255, 255)
clBlack = (0, 0, 0)
clGreen = (0, 128, 0)
clBlue = (0, 0, 255)
clViolet = (128, 0, 128)
clDarkViolet = (148, 0, 211)
clMediumVioletRed = (199, 21, 133)
clRed = (255, 0, 0)
clDarkRed = (139, 0, 0)
clOrangeRed = (255, 69, 0)
clLightGreen = (144, 238, 144)
clIndianRed = (205, 92, 92)


class GameLogic:
    def __init__(self, field_width: int, field_height: int, field_mines_count: int):
        """Initialize game with given parameters"""
        self.FIELD_WIDTH = field_width
        self.FIELD_HEIGHT = field_height
        self.FIELD_MINES_COUNT = field_mines_count

        # Game variables
        self.PROGRAM_STEP = "GameStep"
        self.IS_MOUSE_DOWN = False
        self.MOUSE_X = 0
        self.MOUSE_Y = 0
        self.BUTTON_TYPE = 0
        self.IS_USER_INPUT_DONE = False
        self.USER_INPUT = ""

        # Field structure
        self.FIELD = [[self.Cell() for _ in range(self.FIELD_HEIGHT + 2)]
                      for _ in range(self.FIELD_WIDTH + 2)]

        # Initialize pygame
        pygame.init()
        pygame.font.init()
        self.font_small = pygame.font.SysFont('Arial', 10)
        self.font_medium = pygame.font.SysFont('Arial', 15)
        self.font_large = pygame.font.SysFont('Arial', 20)
        self.font_xlarge = pygame.font.SysFont('Arial', 25)
        self.font_xxlarge = pygame.font.SysFont('Arial', 30)

        # Game state
        self.fcount = 0
        self.xtemp = 0
        self.ytemp = 0
        self.time0 = 0
        self.time1 = 0
        self.game_time = 0
        self.windowWidth = 0
        self.windowHeight = 0
        self.windowCenterX = 0
        self.windowCenterY = 0
        self.screen = None

    class Cell:
        def __init__(self):
            self.mine = False
            self.opened = False
            self.flag = False
            self.nearbyMines = 0

    def main(self):
        """Main game loop"""
        self.display_game_step()
        pygame.quit()

    def set_window_size(self, width, height):
        self.windowWidth = width
        self.windowHeight = height
        self.screen = pygame.display.set_mode((self.windowWidth, self.windowHeight))
        pygame.display.set_caption("Minesweeper")

    def center_window(self):
        os.environ['SDL_VIDEO_CENTERED'] = '1'

    def draw_text_centered(self, text, x, y, width, height, color=clBlack, font=None):
        font = font or self.font_medium
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text_surface, text_rect)

    def draw_button(self, x1, y1, x2, y2, text, color=clLightGray):
        pygame.draw.rect(self.screen, color, (x1, y1, x2 - x1, y2 - y1))
        pygame.draw.rect(self.screen, clBlack, (x1, y1, x2 - x1, y2 - y1), 1)
        self.draw_text_centered(text, x1, y1, x2 - x1, y2 - y1)

    def display_overlay(self):
        overlay = pygame.Surface((self.windowWidth, self.windowHeight), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 200))
        self.screen.blit(overlay, (0, 0))

    def alert(self, message=""):
        vertical_padding = 0
        saved_screen = self.screen.copy()

        self.display_overlay()

        if message:
            vertical_padding = 100
            self.draw_text_centered(message, 0, 0, self.windowWidth, self.windowHeight,
                                    clBlack, self.font_large)

        self.draw_button(self.windowCenterX - 100, self.windowCenterY + vertical_padding - 20,
                         self.windowCenterX + 100, self.windowCenterY + vertical_padding + 20,
                         "Продолжить", clLightGreen)

        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    button = event.button

                    if (self.windowCenterX - 100 <= mouse_x <= self.windowCenterX + 100 and
                            self.windowCenterY + vertical_padding - 20 <= mouse_y <= self.windowCenterY + vertical_padding + 20 and
                            button == 1):
                        waiting = False
                        self.IS_MOUSE_DOWN = False

            pygame.time.delay(1)

        self.screen.blit(saved_screen, (0, 0))
        self.MOUSE_X, self.MOUSE_Y = 0, 0

    def fill_field(self):
        count = 0
        while count < self.FIELD_MINES_COUNT:
            i = random.randint(1, self.FIELD_WIDTH)
            j = random.randint(1, self.FIELD_HEIGHT)

            if not self.FIELD[i][j].mine and not self.FIELD[i][j].opened:
                self.FIELD[i][j].mine = True
                count += 1

                if DEBUG_MODE:
                    self.draw_text_centered(SYMBOL_MINE, 39 * i, 39 * j, 39, 39,
                                            clBlack, self.font_medium)

    def setup_field(self):
        for i in range(1, self.FIELD_WIDTH + 1):
            for j in range(1, self.FIELD_HEIGHT + 1):
                if not self.FIELD[i][j].mine:
                    k = 0
                    # Check all 8 surrounding cells
                    for di in [-1, 0, 1]:
                        for dj in [-1, 0, 1]:
                            if di == 0 and dj == 0:
                                continue
                            ni, nj = i + di, j + dj
                            if 1 <= ni <= self.FIELD_WIDTH and 1 <= nj <= self.FIELD_HEIGHT and self.FIELD[ni][nj].mine:
                                k += 1
                    self.FIELD[i][j].nearbyMines = k

    def open_cell(self, i, j):
        self.FIELD[i][j].opened = True
        self.fcount += 1

        pygame.draw.rect(self.screen, clWhite, (39 * i + 2, 39 * j + 2, 35, 35))

        colors = {
            1: clGreen,
            2: clBlue,
            3: clViolet,
            4: clDarkViolet,
            5: clMediumVioletRed,
            6: clRed,
            7: clDarkRed,
            8: clOrangeRed
        }

        if self.FIELD[i][j].nearbyMines > 0:
            color = colors.get(self.FIELD[i][j].nearbyMines, clBlack)
            self.draw_text_centered(str(self.FIELD[i][j].nearbyMines), 39 * i, 39 * j,
                                    39, 39, color, self.font_medium)

    def open_empty_cells(self, i, j):
        self.open_cell(i, j)

        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    continue
                ni, nj = i + di, j + dj
                if 1 <= ni <= self.FIELD_WIDTH and 1 <= nj <= self.FIELD_HEIGHT and not self.FIELD[ni][nj].opened:
                    if self.FIELD[ni][nj].nearbyMines != 0 and not self.FIELD[ni][nj].flag:
                        self.open_cell(ni, nj)
                    elif self.FIELD[ni][nj].nearbyMines == 0 and not self.FIELD[ni][nj].flag:
                        self.open_empty_cells(ni, nj)

    def open_first_cell(self, i, j):
        self.time0 = int(time.time() * 1000)
        self.game_time = 0
        self.FIELD[i][j].opened = True
        self.FIELD[i][j].mine = False

        self.fill_field()
        self.setup_field()

        if self.FIELD[i][j].nearbyMines == 0:
            self.open_empty_cells(i, j)

        pygame.draw.rect(self.screen, clWhite, (39 * i + 2, 39 * j + 2, 35, 35))

        if self.FIELD[i][j].nearbyMines > 0:
            colors = {
                1: clGreen,
                2: clBlue,
                3: clViolet,
                4: clDarkViolet,
                5: clMediumVioletRed,
                6: clRed,
                7: clDarkRed,
                8: clOrangeRed
            }
            color = colors.get(self.FIELD[i][j].nearbyMines, clBlack)
            self.draw_text_centered(str(self.FIELD[i][j].nearbyMines), 39 * i, 39 * j,
                                    39, 39, color, self.font_medium)
            self.fcount += 1

    def set_flag(self, i, j):
        self.FIELD[i][j].flag = True
        self.draw_text_centered(SYMBOL_FLAG, 39 * i, 39 * j, 39, 39,
                                clRed, self.font_medium)

    def delete_flag(self, i, j):
        self.FIELD[i][j].flag = False
        pygame.draw.rect(self.screen, clLightGray, (39 * i + 2, 39 * j + 2, 35, 35))
        pygame.draw.rect(self.screen, clWhite, (39 * i + 2, 39 * j + 2, 35, 35))

    def check_buttons_click(self):
        if self.check_menu_button_click(self.xtemp, self.ytemp, self.BUTTON_TYPE, self.FIELD_WIDTH):
            self.PROGRAM_STEP = "MenuMainStep"
        elif self.check_restart_button_click(self.xtemp, self.ytemp, self.BUTTON_TYPE, self.FIELD_WIDTH):
            self.PROGRAM_STEP = "GameStep"
        elif self.check_exit_button_click(self.xtemp, self.ytemp, self.BUTTON_TYPE, self.FIELD_HEIGHT,
                                          self.FIELD_WIDTH):
            pygame.quit()
            return

    def check_menu_button_click(self, mouse_x, mouse_y, button_type, field_width):
        return (self.windowWidth - 150 <= mouse_x <= self.windowWidth - 50 and
                WIDTH_CELL * 5 <= mouse_y <= WIDTH_CELL * 6 and
                button_type == 1)

    def check_exit_button_click(self, mouse_x, mouse_y, button_type, field_height, field_width):
        return (self.windowWidth - 150 <= mouse_x <= self.windowWidth - 50 and
                WIDTH_CELL * 7 <= mouse_y <= WIDTH_CELL * 8 and
                button_type == 1)

    def check_restart_button_click(self, mouse_x, mouse_y, button_type, field_width):
        return (self.windowWidth - 150 <= mouse_x <= self.windowWidth - 50 and
                WIDTH_CELL * 1 <= mouse_y <= WIDTH_CELL * 2 and
                button_type == 1)

    def check_pause_button_click(self, mouse_x, mouse_y, button_type, field_width):
        return (self.windowWidth - 150 <= mouse_x <= self.windowWidth - 50 and
                WIDTH_CELL * 3 <= mouse_y <= WIDTH_CELL * 4 and
                button_type == 1)

    def check_is_best(self, time_val, game_level):
        class HighScore:
            def __init__(self):
                self.name = ""
                self.score = 0

        players = [HighScore() for _ in range(3)]
        self.IS_USER_INPUT_DONE = False

        # Try to read records file
        try:
            with open("records.txt", "r") as f:
                for i in range(3):
                    players[i].name = f.readline().strip()
                    players[i].score = int(f.readline().strip())
        except FileNotFoundError:
            # Create default records if file doesn't exist
            for i in range(3):
                players[i].name = "Anonymous"
                players[i].score = 0

        if players[game_level].score == 0 or time_val < players[game_level].score:
            self.display_overlay()
            self.draw_text_centered("Новый рекорд!", 0, self.windowCenterY - 100,
                                    self.windowWidth, 40, clBlack, self.font_xxlarge)
            self.draw_text_centered("Введите ваше имя (затем Enter):", 0,
                                    self.windowCenterY - 50, self.windowWidth, 30,
                                    clBlack, self.font_large)

            self.USER_INPUT = ""
            input_active = True

            while input_active:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            input_active = False
                            self.IS_USER_INPUT_DONE = True
                        elif event.key == pygame.K_BACKSPACE:
                            self.USER_INPUT = self.USER_INPUT[:-1]
                        elif len(self.USER_INPUT) < 15:
                            self.USER_INPUT += event.unicode

                pygame.draw.rect(self.screen, clWhite,
                                 (self.windowCenterX - 100, self.windowCenterY, 200, 40))
                self.draw_text_centered(self.USER_INPUT, self.windowCenterX - 100,
                                        self.windowCenterY, 200, 40, clBlack, self.font_large)
                pygame.display.flip()

            players[game_level].name = self.USER_INPUT
            players[game_level].score = time_val

            with open("records.txt", "w") as f:
                for i in range(3):
                    f.write(f"{players[i].name}\n")
                    f.write(f"{players[i].score}\n")

        self.PROGRAM_STEP = "MenuMainStep"

    def display_win(self):
        self.time1 = int(time.time() * 1000)
        self.game_time += (self.time1 - self.time0) // 1000 + 1

        self.alert(f"Победа! Время прохождения: {self.game_time} сек.")

        if self.GAME_LEVEL != 3:
            self.check_is_best(self.game_time, self.GAME_LEVEL)
        else:
            self.PROGRAM_STEP = "MenuMainStep"

    def pause(self):
        self.time1 = int(time.time() * 1000)
        self.game_time += (self.time1 - self.time0) // 1000 + 1
        self.alert()
        self.time0 = int(time.time() * 1000)

    def display_lose(self):
        self.time1 = int(time.time() * 1000)
        self.game_time += (self.time1 - self.time0) // 1000 + 1
        self.alert(f"Вы проиграли потратив {self.game_time} секунд(ы)...")
        # Закрываем игровое окно
        pygame.display.quit()
        return "MenuMainStep"

    def display_win(self):
        self.time1 = int(time.time() * 1000)
        self.game_time += (self.time1 - self.time0) // 1000 + 1
        self.alert(f"Победа! Время прохождения: {self.game_time} сек.")

        if self.GAME_LEVEL != 3:
            self.check_is_best(self.game_time, self.GAME_LEVEL)

        # Закрываем игровое окно
        pygame.display.quit()
        return "MenuMainStep"

    def check_buttons_click(self):
        if self.check_menu_button_click(self.xtemp, self.ytemp, self.BUTTON_TYPE, self.FIELD_WIDTH):
            pygame.display.quit()
            return "MenuMainStep"
        elif self.check_restart_button_click(self.xtemp, self.ytemp, self.BUTTON_TYPE, self.FIELD_WIDTH):
            pygame.display.quit()
            return "Restart"
        elif self.check_exit_button_click(self.xtemp, self.ytemp, self.BUTTON_TYPE, self.FIELD_HEIGHT,
                                          self.FIELD_WIDTH):
            pygame.quit()
            return "Exit"

    def draw_field(self):
        for i in range(1, self.FIELD_WIDTH + 1):
            for j in range(1, self.FIELD_HEIGHT + 1):
                pygame.draw.rect(self.screen, clLightGray,
                                 (WIDTH_CELL * i, WIDTH_CELL * j, WIDTH_CELL, WIDTH_CELL))
                pygame.draw.rect(self.screen, clBlack,
                                 (WIDTH_CELL * i, WIDTH_CELL * j, WIDTH_CELL, WIDTH_CELL), 1)
                self.FIELD[i][j].opened = False
                self.FIELD[i][j].mine = False
                self.FIELD[i][j].flag = False

    def check_mine(self, i, j):
        return (1 <= i <= self.FIELD_WIDTH and 1 <= j <= self.FIELD_HEIGHT and
                self.BUTTON_TYPE == 1 and not self.FIELD[i][j].mine and
                not self.FIELD[i][j].opened and not self.FIELD[i][j].flag)

    def check_set_flag(self, i, j):
        return (1 <= i <= self.FIELD_WIDTH and 1 <= j <= self.FIELD_HEIGHT and
                self.BUTTON_TYPE == 2 and not self.FIELD[i][j].flag and
                not self.FIELD[i][j].opened)

    def check_delete_flag(self, i, j):
        return (1 <= i <= self.FIELD_WIDTH and 1 <= j <= self.FIELD_HEIGHT and
                self.BUTTON_TYPE == 2 and self.FIELD[i][j].flag and
                not self.FIELD[i][j].opened)

    def check_is_lose(self, i, j):
        return (1 <= i <= self.FIELD_WIDTH and 1 <= j <= self.FIELD_HEIGHT and
                self.BUTTON_TYPE == 1 and self.FIELD[i][j].mine and
                not self.FIELD[i][j].flag)

    def display_game_step(self):
        # Calculate window size
        self.windowWidth = self.FIELD_WIDTH * WIDTH_CELL + 240
        self.windowHeight = self.FIELD_HEIGHT * WIDTH_CELL + TEXT_PADDING * 2

        self.set_window_size(self.windowWidth, self.windowHeight)
        self.center_window()

        # Load background
        try:
            background = pygame.image.load(BACKGROUND_SRC)
            background = pygame.transform.scale(background, (self.windowWidth, self.windowHeight))
            self.screen.blit(background, (0, 0))
        except:
            self.screen.fill(clWhite)

        self.windowCenterX = self.windowWidth // 2
        self.windowCenterY = self.windowHeight // 2

        # Reset variables
        self.fcount = 0
        self.i = 0
        self.j = 0
        self.MOUSE_X = 0
        self.MOUSE_Y = 0
        self.xtemp = 0
        self.ytemp = 0

        # Draw field
        self.draw_field()

        # Draw buttons
        self.draw_button(self.windowWidth - 150, WIDTH_CELL * 1,
                         self.windowWidth - 50, WIDTH_CELL * 2, "Рестарт")
        self.draw_button(self.windowWidth - 150, WIDTH_CELL * 3,
                         self.windowWidth - 50, WIDTH_CELL * 4, "Пауза")
        self.draw_button(self.windowWidth - 150, WIDTH_CELL * 5,
                         self.windowWidth - 50, WIDTH_CELL * 6, "Меню")
        self.draw_button(self.windowWidth - 150, WIDTH_CELL * 7,
                         self.windowWidth - 50, WIDTH_CELL * 8, "Выход")

        pygame.display.flip()

        is_confirmed = False
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    return "Exit"

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.MOUSE_X, self.MOUSE_Y = event.pos
                    self.BUTTON_TYPE = event.button
                    self.IS_MOUSE_DOWN = True

                    self.i = self.MOUSE_X // WIDTH_CELL
                    self.j = self.MOUSE_Y // WIDTH_CELL

                    # First cell opening
                    if (1 <= self.i <= self.FIELD_WIDTH and 1 <= self.j <= self.FIELD_HEIGHT and
                            self.BUTTON_TYPE == 1 and self.fcount == 0):
                        self.open_first_cell(self.i, self.j)
                    elif self.check_pause_button_click(self.MOUSE_X, self.MOUSE_Y,
                                                       self.BUTTON_TYPE, self.FIELD_WIDTH):
                        self.pause()
                    elif self.check_mine(self.i, self.j):
                        if self.FIELD[self.i][self.j].nearbyMines != 0:
                            self.open_cell(self.i, self.j)
                        else:
                            self.open_empty_cells(self.i, self.j)
                    elif self.check_set_flag(self.i, self.j):
                        self.set_flag(self.i, self.j)
                    elif self.check_delete_flag(self.i, self.j):
                        self.delete_flag(self.i, self.j)
                    elif self.check_restart_button_click(self.MOUSE_X, self.MOUSE_Y,
                                                         self.BUTTON_TYPE, self.FIELD_WIDTH):
                        is_confirmed = True
                    elif self.check_menu_button_click(self.MOUSE_X, self.MOUSE_Y,
                                                      self.BUTTON_TYPE, self.FIELD_WIDTH):
                        is_confirmed = True
                    elif self.check_exit_button_click(self.MOUSE_X, self.MOUSE_Y,
                                                      self.BUTTON_TYPE, self.FIELD_HEIGHT,
                                                      self.FIELD_WIDTH):
                        is_confirmed = True

                    self.IS_MOUSE_DOWN = False
                    pygame.display.flip()

            # Check game end conditions
            if is_confirmed:
                result = self.check_buttons_click()
                if result:
                    return result
            elif self.fcount == self.FIELD_WIDTH * self.FIELD_HEIGHT - self.FIELD_MINES_COUNT:
                return self.display_win()
            elif self.check_is_lose(self.i, self.j):
                return self.display_lose()

            pygame.time.delay(1)

    def main(self):
        """Main game loop"""
        result = self.display_game_step()
        if result == "MenuMainStep":
            return result
        pygame.quit()