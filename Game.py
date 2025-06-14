import pygame
import sys
import os
from dataclasses import dataclass
import GameLogic
import GameLevelForm
import GlobalConstants
import GlobalVariables
import CommonFuntions

from typing import Tuple, List, Optional, Dict

# Инициализация Pygame
pygame.init()
pygame.font.init()

# Константы игры
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 40
CELL_SIZE = 39
FPS = 60

# Пути к файлам
BACKGROUND_SRC = "background.png"
RULES_FILE = "rules.txt"
RECORDS_FILE = "records.txt"

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (200, 200, 200)
SEMI_TRANSPARENT_WHITE = (255, 255, 255, 200)
SEMI_TRANSPARENT_BLACK = (0, 0, 0, 100)

# Уровни сложности
LEVELS = {
    0: {"name": "Легкий", "width": 8, "height": 8, "mines": 10},
    1: {"name": "Нормальный", "width": 16, "height": 16, "mines": 40},
    2: {"name": "Сложный", "width": 30, "height": 19, "mines": 70}
}


@dataclass
class Cell:
    """Класс ячейки игрового поля"""
    mine: bool = False
    flag: bool = False
    nearby_mines: int = 0
    opened: bool = False


class GameState:
    """Класс для хранения состояния игры"""

    def __init__(self):
        self.program_step = "MenuMainStep"
        self.game_level = 0
        self.field_width = LEVELS[0]["width"]
        self.field_height = LEVELS[0]["height"]
        self.field_mines_count = LEVELS[0]["mines"]
        self.mouse_pos = (0, 0)
        self.mouse_button = 0
        self.is_mouse_down = False
        self.field = []
        self.initialize_field()

    def initialize_field(self, width: int = None, height: int = None):
        """Инициализация игрового поля"""
        width = width or self.field_width
        height = height or self.field_height
        self.field = [[Cell() for _ in range(width)] for _ in range(height)]

    def set_level(self, level: int):
        """Установка уровня сложности"""
        if level in LEVELS:
            self.game_level = level
            self.field_width = LEVELS[level]["width"]
            self.field_height = LEVELS[level]["height"]
            self.field_mines_count = LEVELS[level]["mines"]
            self.initialize_field()


class GameUI:
    """Класс для работы с пользовательским интерфейсом"""

    def __init__(self):
        self.fonts = {
            "title": pygame.font.SysFont('Arial', 20, bold=True),
            "button": pygame.font.SysFont('Arial', 18),
            "text": pygame.font.SysFont('Arial', 10),
            "records": pygame.font.SysFont('Arial', 18)
        }
        self.background = self.load_background()

    def load_background(self) -> pygame.Surface:
        """Загрузка фонового изображения"""
        try:
            background = pygame.image.load(BACKGROUND_SRC)
            return pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            background.fill(WHITE)
            return background

    def draw_title(self, surface: pygame.Surface, text: str, x: int, y: int, width: int, height: int):
        """Отрисовка заголовка"""
        text_surface = self.fonts["title"].render(text, True, BLACK)
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))

        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill(SEMI_TRANSPARENT_WHITE)
        surface.blit(overlay, (x, y))
        surface.blit(text_surface, text_rect)

    def draw_button(self, surface: pygame.Surface, x: int, y: int, width: int, height: int, text: str):
        """Отрисовка кнопки"""
        pygame.draw.rect(surface, LIGHT_GRAY, (x, y, width, height))
        pygame.draw.rect(surface, BLACK, (x, y, width, height), 1)

        text_surface = self.fonts["button"].render(text, True, BLACK)
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        surface.blit(text_surface, text_rect)


class MinesweeperGame:
    """Основной класс игры"""

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Игра "Сапёр"')
        self.clock = pygame.time.Clock()
        self.state = GameState()
        self.ui = GameUI()
        self.game_logic = None

    def run(self):
        """Запуск основного цикла игры"""
        if not self.check_files():
            print("Ошибка! Отсутствуют необходимые файлы")
            return

        while True:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)

    def check_files(self) -> bool:
        """Проверка наличия необходимых файлов"""
        return os.path.exists(RULES_FILE) and os.path.exists(RECORDS_FILE)

    def handle_events(self):
        """Обработка событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.state.mouse_pos = event.pos
                self.state.mouse_button = event.button
                self.state.is_mouse_down = True

    def update(self):
        """Обновление состояния игры"""
        if self.state.program_step == "MenuMainStep":
            self.update_main_menu()
        elif self.state.program_step == "MenuGameStep":
            self.update_level_menu()
        elif self.state.program_step == "RulesStep":
            self.update_rules_screen()
        elif self.state.program_step == "RecordsStep":
            self.update_records_screen()
        elif self.state.program_step == "GameStep":
            self.update_game()
        elif self.state.program_step == "GameLevelFormStep":
            self.update_custom_level_form()

    def update_main_menu(self):
        """Обновление главного меню"""
        if self.state.is_mouse_down:
            self.state.is_mouse_down = False
            x, y = self.state.mouse_pos

            if 0 <= x <= BUTTON_WIDTH and 100 <= y <= 140 and self.state.mouse_button == 1:
                self.state.program_step = "MenuGameStep"
            elif 0 <= x <= BUTTON_WIDTH and 160 <= y <= 200 and self.state.mouse_button == 1:
                self.state.program_step = "RulesStep"
            elif 0 <= x <= BUTTON_WIDTH and 220 <= y <= 260 and self.state.mouse_button == 1:
                self.state.program_step = "RecordsStep"
            elif 0 <= x <= BUTTON_WIDTH and 280 <= y <= 320 and self.state.mouse_button == 1:
                pygame.quit()
                sys.exit()

    def update_level_menu(self):
        """Обновление меню выбора уровня"""
        if self.state.is_mouse_down:
            self.state.is_mouse_down = False
            x, y = self.state.mouse_pos

            for level, data in LEVELS.items():
                btn_y = 100 + level * 60
                if 0 <= x <= BUTTON_WIDTH and btn_y <= y <= btn_y + BUTTON_HEIGHT and self.state.mouse_button == 1:
                    self.state.set_level(level)
                    self.start_game()
                    return

            if 0 <= x <= BUTTON_WIDTH and 280 <= y <= 320 and self.state.mouse_button == 1:
                self.state.program_step = "GameLevelFormStep"
            elif 0 <= x <= BUTTON_WIDTH and 340 <= y <= 380 and self.state.mouse_button == 1:
                self.state.program_step = "MenuMainStep"

    def update_custom_level_form(self):
        """Обновление формы пользовательского уровня"""
        # Получаем настройки пользовательского уровня
        level, width, height, mines = GameLevelForm.display_game_level_form()

        # Устанавливаем параметры игры
        self.state.game_level = level
        self.state.field_width = width
        self.state.field_height = height
        self.state.field_mines_count = mines
        self.state.initialize_field()

        # Запускаем игру
        self.start_game()

    def start_game(self):
        """Запуск игры с текущими параметрами"""
        # Сохраняем текущее состояние экрана
        saved_screen = self.screen.copy()

        # Инициализируем игровую логику
        self.game_logic = GameLogic.GameLogic(
            self.state.field_width,
            self.state.field_height,
            self.state.field_mines_count
        )

        # Запускаем игровой цикл
        result = self.game_logic.main()

        # Восстанавливаем экран меню
        self.screen.blit(saved_screen, (0, 0))
        pygame.display.flip()

        # Обновляем состояние программы
        if result == "MenuMainStep":
            self.state.program_step = "MenuMainStep"
        elif result == "Restart":
            self.start_game()

    def update_rules_screen(self):
        """Обновление экрана с правилами"""
        if self.state.is_mouse_down:
            self.state.is_mouse_down = False
            x, y = self.state.mouse_pos

            if 0 <= x <= BUTTON_WIDTH and 340 <= y <= 380 and self.state.mouse_button == 1:
                self.state.program_step = "MenuMainStep"

    def update_records_screen(self):
        """Обновление экрана с рекордами"""
        if self.state.is_mouse_down:
            self.state.is_mouse_down = False
            x, y = self.state.mouse_pos

            if 0 <= x <= BUTTON_WIDTH and 340 <= y <= 380 and self.state.mouse_button == 1:
                self.state.program_step = "MenuMainStep"

    def update_game(self):
        """Обновление игрового процесса"""
        # Вся игровая логика теперь в GameLogic
        pass

    def render(self):
        """Отрисовка игры"""
        if self.state.program_step == "GameStep":
            # Игровой процесс рендерится в GameLogic
            return

        self.screen.blit(self.ui.background, (0, 0))

        if self.state.program_step == "MenuMainStep":
            self.render_main_menu()
        elif self.state.program_step == "MenuGameStep":
            self.render_level_menu()
        elif self.state.program_step == "RulesStep":
            self.render_rules_screen()
        elif self.state.program_step == "RecordsStep":
            self.render_records_screen()

        pygame.display.flip()

    def render_main_menu(self):
        """Отрисовка главного меню"""
        self.ui.draw_title(self.screen, "Игра ¤ Сапёр ⚑", 0, 20, 250, 60)

        buttons = [
            (100, "Игра"), (160, "Правила"),
            (220, "Рекорды"), (280, "Выход")
        ]

        for y, text in buttons:
            self.ui.draw_button(self.screen, 0, y, BUTTON_WIDTH, BUTTON_HEIGHT, text)

        footer = self.ui.fonts["text"].render("© Николаев Максим", True, BLACK)
        self.screen.blit(footer, (0, 360))

    def render_level_menu(self):
        """Отрисовка меню выбора уровня"""
        self.ui.draw_title(self.screen, "Уровень:", 0, 20, 270, 60)

        for level, data in LEVELS.items():
            y = 100 + level * 60
            self.ui.draw_button(self.screen, 0, y, BUTTON_WIDTH, BUTTON_HEIGHT, data["name"])

        self.ui.draw_button(self.screen, 0, 280, BUTTON_WIDTH, BUTTON_HEIGHT, "Свой")
        self.ui.draw_button(self.screen, 0, 340, BUTTON_WIDTH, BUTTON_HEIGHT, "Назад")

    def render_rules_screen(self):
        """Отрисовка экрана с правилами"""
        self.ui.draw_title(self.screen, "Правила игры:", 0, 20, 250, 60)

        overlay = pygame.Surface((560, 240), pygame.SRCALPHA)
        overlay.fill(SEMI_TRANSPARENT_WHITE)
        self.screen.blit(overlay, (0, 80))

        try:
            with open(RULES_FILE, 'r', encoding='utf-8') as f:
                rules = f.read().split('\n')
        except:
            rules = ["Файл с правилами не найден"]

        y = 120
        for line in rules:
            text = self.ui.fonts["text"].render(line, True, BLACK)
            self.screen.blit(text, (40, y))
            y += 20

        self.ui.draw_button(self.screen, 0, 340, BUTTON_WIDTH, BUTTON_HEIGHT, "Назад")

    def render_records_screen(self):
        """Отрисовка экрана с рекордами"""
        self.ui.draw_title(self.screen, "Рекорды:", 0, 20, 250, 60)

        overlay = pygame.Surface((560, 240), pygame.SRCALPHA)
        overlay.fill(SEMI_TRANSPARENT_WHITE)
        self.screen.blit(overlay, (0, 80))

        try:
            with open(RECORDS_FILE, 'r', encoding='utf-8') as f:
                records = []
                for _ in range(3):
                    name = f.readline().strip()
                    score = f.readline().strip()
                    records.append((name, score))
        except:
            records = [("Нет данных", "0")] * 3

        level_names = ["Новичок", "Любитель", "Профессионал"]
        y = 120
        for i, (name, score) in enumerate(records):
            if score != "0":
                text = f"{level_names[i]}: {name} {score}сек."
            else:
                text = f"{level_names[i]}: рекорда нет"

            rendered = self.ui.fonts["records"].render(text, True, BLACK)
            self.screen.blit(rendered, (40, y))
            y += 60

        self.ui.draw_button(self.screen, 0, 340, BUTTON_WIDTH, BUTTON_HEIGHT, "Назад")


if __name__ == "__main__":
    game = MinesweeperGame()
    game.run()