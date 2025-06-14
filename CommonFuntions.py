import pygame
import sys
import os
from typing import Tuple, List, Optional

# Инициализация Pygame
pygame.init()
pygame.font.init()

# Константы
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 40
BACKGROUND_SRC = "background.png"
RULES_FILE = "./rules.txt"
RECORDS_FILE = "./records.txt"
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (200, 200, 200)
SEMI_TRANSPARENT = (255, 255, 255, 200)

# Глобальные переменные
PROGRAM_STEP = "MenuMainStep"
GAME_LEVEL = 0
FIELD_WIDTH = 8
FIELD_HEIGHT = 8
FIELD_MINES_COUNT = 10
MOUSE_X = 0
MOUSE_Y = 0
BUTTON_TYPE = 0
IS_MOUSE_DOWN = False


class HighScore:
    def __init__(self):
        self.name = ""
        self.score = 0


def draw_title(surface: pygame.Surface, text: str, x: int, y: int, width: int, height: int):
    font = pygame.font.SysFont('Arial', 20, bold=True)
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))

    # Полупрозрачный фон для заголовка
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill(SEMI_TRANSPARENT)
    surface.blit(overlay, (x, y))

    surface.blit(text_surface, text_rect)


def draw_button(surface: pygame.Surface, x: int, y: int, width: int, height: int, text: str):
    pygame.draw.rect(surface, LIGHT_GRAY, (x, y, width, height))
    pygame.draw.rect(surface, BLACK, (x, y, width, height), 1)

    font = pygame.font.SysFont('Arial', 18)
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    surface.blit(text_surface, text_rect)


def display_menu_main_step() -> str:
    global MOUSE_X, MOUSE_Y, BUTTON_TYPE, IS_MOUSE_DOWN

    # Настройки окна
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Игра 'Сапёр'")

    # Загрузка фона
    try:
        background = pygame.image.load(BACKGROUND_SRC)
        background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        background.fill(WHITE)

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                MOUSE_X, MOUSE_Y = event.pos
                BUTTON_TYPE = event.button
                IS_MOUSE_DOWN = True

        # Отрисовка
        screen.blit(background, (0, 0))

        # Заголовок
        draw_title(screen, "Игра ¤ Сапёр ⚑", 0, 20, 250, 60)

        # Кнопки
        draw_button(screen, 0, 100, BUTTON_WIDTH, BUTTON_HEIGHT, "Игра")
        draw_button(screen, 0, 160, BUTTON_WIDTH, BUTTON_HEIGHT, "Правила")
        draw_button(screen, 0, 220, BUTTON_WIDTH, BUTTON_HEIGHT, "Рекорды")
        draw_button(screen, 0, 280, BUTTON_WIDTH, BUTTON_HEIGHT, "Выход")

        # Подпись внизу
        font = pygame.font.SysFont('Arial', 10)
        text_surface = font.render("© Николаев Максим, группа 243", True, BLACK)
        screen.blit(text_surface, (0, 360))

        # Проверка кликов по кнопкам
        if IS_MOUSE_DOWN:
            IS_MOUSE_DOWN = False

            # Кнопка "Игра"
            if 0 <= MOUSE_X <= BUTTON_WIDTH and 100 <= MOUSE_Y <= 140 and BUTTON_TYPE == 1:
                return "MenuGameStep"

            # Кнопка "Правила"
            elif 0 <= MOUSE_X <= BUTTON_WIDTH and 160 <= MOUSE_Y <= 200 and BUTTON_TYPE == 1:
                return "RulesStep"

            # Кнопка "Рекорды"
            elif 0 <= MOUSE_X <= BUTTON_WIDTH and 220 <= MOUSE_Y <= 260 and BUTTON_TYPE == 1:
                return "RecordsStep"

            # Кнопка "Выход"
            elif 0 <= MOUSE_X <= BUTTON_WIDTH and 280 <= MOUSE_Y <= 320 and BUTTON_TYPE == 1:
                pygame.quit()
                sys.exit()

        pygame.display.flip()
        clock.tick(FPS)

    return "MenuMainStep"


def display_menu_game_step() -> Tuple[str, int, int, int, int]:
    global MOUSE_X, MOUSE_Y, BUTTON_TYPE, IS_MOUSE_DOWN, GAME_LEVEL, FIELD_WIDTH, FIELD_HEIGHT, FIELD_MINES_COUNT

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Загрузка фона
    try:
        background = pygame.image.load(BACKGROUND_SRC)
        background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        background.fill(WHITE)

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                MOUSE_X, MOUSE_Y = event.pos
                BUTTON_TYPE = event.button
                IS_MOUSE_DOWN = True

        # Отрисовка
        screen.blit(background, (0, 0))

        # Заголовок
        draw_title(screen, "Уровень:", 0, 20, 270, 60)

        # Кнопки уровней
        draw_button(screen, 0, 100, BUTTON_WIDTH, BUTTON_HEIGHT, "Легкий")
        draw_button(screen, 0, 160, BUTTON_WIDTH, BUTTON_HEIGHT, "Нормальный")
        draw_button(screen, 0, 220, BUTTON_WIDTH, BUTTON_HEIGHT, "Сложный")
        draw_button(screen, 0, 280, BUTTON_WIDTH, BUTTON_HEIGHT, "Свой")
        draw_button(screen, 0, 340, BUTTON_WIDTH, BUTTON_HEIGHT, "Назад")

        # Проверка кликов по кнопкам
        if IS_MOUSE_DOWN:
            IS_MOUSE_DOWN = False

            # Кнопка "Легкий"
            if 0 <= MOUSE_X <= BUTTON_WIDTH and 100 <= MOUSE_Y <= 140 and BUTTON_TYPE == 1:
                GAME_LEVEL = 0
                FIELD_WIDTH = 8
                FIELD_HEIGHT = 8
                FIELD_MINES_COUNT = 10
                return "GameStep", GAME_LEVEL, FIELD_WIDTH, FIELD_HEIGHT, FIELD_MINES_COUNT

            # Кнопка "Нормальный"
            elif 0 <= MOUSE_X <= BUTTON_WIDTH and 160 <= MOUSE_Y <= 200 and BUTTON_TYPE == 1:
                GAME_LEVEL = 1
                FIELD_WIDTH = 16
                FIELD_HEIGHT = 16
                FIELD_MINES_COUNT = 40
                return "GameStep", GAME_LEVEL, FIELD_WIDTH, FIELD_HEIGHT, FIELD_MINES_COUNT

            # Кнопка "Сложный"
            elif 0 <= MOUSE_X <= BUTTON_WIDTH and 220 <= MOUSE_Y <= 260 and BUTTON_TYPE == 1:
                GAME_LEVEL = 2
                FIELD_WIDTH = 30
                FIELD_HEIGHT = 19
                FIELD_MINES_COUNT = 70
                return "GameStep", GAME_LEVEL, FIELD_WIDTH, FIELD_HEIGHT, FIELD_MINES_COUNT

            # Кнопка "Свой"
            elif 0 <= MOUSE_X <= BUTTON_WIDTH and 280 <= MOUSE_Y <= 320 and BUTTON_TYPE == 1:
                return "GameLevelFormStep", GAME_LEVEL, FIELD_WIDTH, FIELD_HEIGHT, FIELD_MINES_COUNT

            # Кнопка "Назад"
            elif 0 <= MOUSE_X <= BUTTON_WIDTH and 340 <= MOUSE_Y <= 380 and BUTTON_TYPE == 1:
                return "MenuMainStep", GAME_LEVEL, FIELD_WIDTH, FIELD_HEIGHT, FIELD_MINES_COUNT

        pygame.display.flip()
        clock.tick(FPS)

    return "MenuMainStep", GAME_LEVEL, FIELD_WIDTH, FIELD_HEIGHT, FIELD_MINES_COUNT


def display_rules_step() -> str:
    global MOUSE_X, MOUSE_Y, BUTTON_TYPE, IS_MOUSE_DOWN

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Загрузка фона
    try:
        background = pygame.image.load(BACKGROUND_SRC)
        background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        background.fill(WHITE)

    # Загрузка правил из файла
    try:
        with open(RULES_FILE, 'r', encoding='utf-8') as f:
            rules_text = f.read()
    except:
        rules_text = "Файл с правилами не найден"

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                MOUSE_X, MOUSE_Y = event.pos
                BUTTON_TYPE = event.button
                IS_MOUSE_DOWN = True

        # Отрисовка
        screen.blit(background, (0, 0))

        # Заголовок
        draw_title(screen, "Правила игры:", 0, 20, 250, 60)

        # Полупрозрачный прямоугольник для текста
        overlay = pygame.Surface((560, 240), pygame.SRCALPHA)
        overlay.fill(SEMI_TRANSPARENT)
        screen.blit(overlay, (0, 80))

        # Текст правил
        font = pygame.font.SysFont('Arial', 10)
        y_offset = 120
        for line in rules_text.split('\n'):
            text_surface = font.render(line, True, BLACK)
            screen.blit(text_surface, (40, y_offset))
            y_offset += 20

        # Кнопка "Назад"
        draw_button(screen, 0, 340, BUTTON_WIDTH, BUTTON_HEIGHT, "Назад")

        # Проверка кликов по кнопкам
        if IS_MOUSE_DOWN:
            IS_MOUSE_DOWN = False

            # Кнопка "Назад"
            if 0 <= MOUSE_X <= BUTTON_WIDTH and 340 <= MOUSE_Y <= 380 and BUTTON_TYPE == 1:
                return "MenuMainStep"

        pygame.display.flip()
        clock.tick(FPS)

    return "MenuMainStep"


def display_records_step() -> str:
    global MOUSE_X, MOUSE_Y, BUTTON_TYPE, IS_MOUSE_DOWN

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Загрузка фона
    try:
        background = pygame.image.load(BACKGROUND_SRC)
        background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        background.fill(WHITE)

    # Загрузка рекордов из файла
    players = [HighScore() for _ in range(3)]
    try:
        with open(RECORDS_FILE, 'r', encoding='utf-8') as f:
            for i in range(3):
                players[i].name = f.readline().strip()
                players[i].score = int(f.readline().strip())
    except:
        for i in range(3):
            players[i].name = "Нет данных"
            players[i].score = 0

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                MOUSE_X, MOUSE_Y = event.pos
                BUTTON_TYPE = event.button
                IS_MOUSE_DOWN = True

        # Отрисовка
        screen.blit(background, (0, 0))

        # Заголовок
        draw_title(screen, "Рекорды:", 0, 20, 250, 60)

        # Полупрозрачный прямоугольник для текста
        overlay = pygame.Surface((560, 240), pygame.SRCALPHA)
        overlay.fill(SEMI_TRANSPARENT)
        screen.blit(overlay, (0, 80))

        # Вывод рекордов
        font = pygame.font.SysFont('Arial', 18)
        for i in range(3):
            level_name = ["Новичок", "Любитель", "Профессионал"][i]

            if players[i].score != 0:
                text = f"{level_name}: {players[i].name} {players[i].score}сек."
            else:
                text = f"{level_name}: рекорда нет"

            text_surface = font.render(text, True, BLACK)
            screen.blit(text_surface, (40, 120 + i * 60))

        # Кнопка "Назад"
        draw_button(screen, 0, 340, BUTTON_WIDTH, BUTTON_HEIGHT, "Назад")

        # Проверка кликов по кнопкам
        if IS_MOUSE_DOWN:
            IS_MOUSE_DOWN = False

            # Кнопка "Назад"
            if 0 <= MOUSE_X <= BUTTON_WIDTH and 340 <= MOUSE_Y <= 380 and BUTTON_TYPE == 1:
                return "MenuMainStep"

        pygame.display.flip()
        clock.tick(FPS)

    return "MenuMainStep"


def main():
    global PROGRAM_STEP, GAME_LEVEL, FIELD_WIDTH, FIELD_HEIGHT, FIELD_MINES_COUNT

    # Проверка наличия необходимых файлов
    if not (os.path.exists(RULES_FILE) and os.path.exists(RECORDS_FILE)):
        print("Ошибка! Отсутствуют необходимые файлы")
        pygame.quit()
        sys.exit()

    pygame.display.set_caption("Игра 'Сапёр'")

    # Основной игровой цикл
    running = True
    while running:
        if PROGRAM_STEP == "MenuMainStep":
            PROGRAM_STEP = display_menu_main_step()

        elif PROGRAM_STEP == "MenuGameStep":
            result = display_menu_game_step()
            PROGRAM_STEP = result[0]
            if len(result) > 1:
                GAME_LEVEL, FIELD_WIDTH, FIELD_HEIGHT, FIELD_MINES_COUNT = result[1:]

        elif PROGRAM_STEP == "RulesStep":
            PROGRAM_STEP = display_rules_step()

        elif PROGRAM_STEP == "RecordsStep":
            PROGRAM_STEP = display_records_step()

        elif PROGRAM_STEP == "GameLevelFormStep":
            # Здесь должна быть реализация формы настройки уровня
            # Для примера просто вернемся в меню
            PROGRAM_STEP = "MenuGameStep"

        elif PROGRAM_STEP == "GameStep":
            # Здесь должна быть реализация самой игры
            # Для примера просто вернемся в меню
            PROGRAM_STEP = "MenuGameStep"

        elif PROGRAM_STEP == "Exit":
            running = False

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()