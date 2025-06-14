import pygame
import sys
from typing import Tuple, Optional

# Инициализация Pygame
pygame.init()
pygame.font.init()

# Константы
WINDOW_WIDTH = 350
WINDOW_HEIGHT = 340
TEXT_PADDING = 20
BACKGROUND_SRC = "background.png"
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (200, 200, 200)

# Глобальные переменные
USER_INPUT = ""
IS_USER_INPUT_DONE = False
current_input_field = None


class IntRange:
    def __init__(self, min_val: int, max_val: int):
        self.min = min_val
        self.max = max_val

    def __contains__(self, value: int) -> bool:
        return self.min <= value <= self.max


def draw_title(surface: pygame.Surface, text: str, x: int, y: int, width: int, height: int):
    font = pygame.font.SysFont('Arial', 24)
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    surface.blit(text_surface, text_rect)


def display_input_field(surface: pygame.Surface, title: str, current_value: int,
                        input_range: IntRange, x: int, y: int) -> Optional[int]:
    global USER_INPUT, IS_USER_INPUT_DONE, current_input_field

    font = pygame.font.SysFont('Arial', 15)
    small_font = pygame.font.SysFont('Arial', 9)

    # Отрисовка заголовка
    title_surface = font.render(title, True, BLACK)
    surface.blit(title_surface, (TEXT_PADDING, y))

    # Отрисовка поля ввода
    input_rect = pygame.Rect(x, y, 60, 20)
    pygame.draw.rect(surface, WHITE, input_rect)
    pygame.draw.rect(surface, BLACK, input_rect, 1)

    # Отрисовка текущего значения
    value_surface = font.render(USER_INPUT, True, BLACK)
    surface.blit(value_surface, (x + 5, y))

    # Активируем текущее поле ввода
    current_input_field = (title, input_range, x, y)

    # Если ввод завершен
    if IS_USER_INPUT_DONE:
        try:
            value = int(USER_INPUT)
            if value in input_range:
                USER_INPUT = ""
                IS_USER_INPUT_DONE = False
                current_input_field = None
                return value
            else:
                # Отрисовка сообщения об ошибке
                error_surface = small_font.render("Недопустимое значение. Повторите ввод.", True, BLACK)
                surface.blit(error_surface, (TEXT_PADDING, y + 23))
                pygame.display.flip()
                pygame.time.delay(1500)
                USER_INPUT = ""
                return None
        except ValueError:
            USER_INPUT = ""
            return None

    return None


def display_game_level_form() -> Tuple[int, int, int, int]:
    global USER_INPUT, IS_USER_INPUT_DONE, current_input_field

    # Настройки окна
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Настройки уровня игры")

    # Загрузка фона
    try:
        background = pygame.image.load(BACKGROUND_SRC)
        background = pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))
    except:
        background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        background.fill(WHITE)

    # Параметры игры
    game_level = 3  # Пользовательский уровень
    field_width = 10
    field_height = 10
    field_mines_count = 10

    # Координаты полей ввода
    input_fields = [
        ("Ширина поля (max 34):", IntRange(1, 34), 260, 120),
        ("Высота поля (5...19):", IntRange(5, 19), 260, 200),
        ("Количество мин:", IntRange(1, field_width * field_height - 1), 260, 280)
    ]

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if current_input_field:
                    title, input_range, x, y = current_input_field

                    # Обработка цифр
                    if event.unicode.isdigit() and len(USER_INPUT) < 2:
                        USER_INPUT += event.unicode

                    # Обработка Backspace
                    elif event.key == pygame.K_BACKSPACE:
                        USER_INPUT = USER_INPUT[:-1]

                    # Обработка Enter
                    elif event.key == pygame.K_RETURN:
                        IS_USER_INPUT_DONE = True

        # Отрисовка
        screen.blit(background, (0, 0))

        # Полупрозрачный белый прямоугольник
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT - 80), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 230))
        screen.blit(overlay, (0, 80))

        # Заголовок
        draw_title(screen, "Настройки уровня:", 0, 20, 270, 60)

        # Отрисовка полей ввода
        result_width = display_input_field(screen, *input_fields[0])
        if result_width is not None:
            field_width = result_width
            # Обновляем диапазон для мин
            input_fields[2] = ("Количество мин:", IntRange(1, field_width * field_height - 1), 260, 280)

        result_height = display_input_field(screen, *input_fields[1])
        if result_height is not None:
            field_height = result_height
            # Обновляем диапазон для мин
            input_fields[2] = ("Количество мин:", IntRange(1, field_width * field_height - 1), 260, 280)

        result_mines = display_input_field(screen, *input_fields[2])
        if result_mines is not None:
            field_mines_count = result_mines

            # Если все поля заполнены корректно, запускаем обратный отсчет
            if all(field[0] == "Количество мин:" or
                   (field[0] == "Ширина поля (max 34):" and field_width is not None) or
                   (field[0] == "Высота поля (5...19):" and field_height is not None)
                   for field in input_fields):

                # Обратный отсчет
                countdown_font = pygame.font.SysFont('Arial', 30)
                for i in range(3, 0, -1):
                    screen.blit(background, (0, 0))
                    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT - 80), pygame.SRCALPHA)
                    overlay.fill((255, 255, 255, 230))
                    screen.blit(overlay, (0, 80))

                    countdown_text = countdown_font.render(str(i), True, BLACK)
                    countdown_rect = countdown_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
                    screen.blit(countdown_text, countdown_rect)

                    pygame.display.flip()
                    pygame.time.delay(1000)

                running = False

        pygame.display.flip()
        clock.tick(FPS)

    return game_level, field_width, field_height, field_mines_count


if __name__ == "__main__":
    game_level, width, height, mines = display_game_level_form()
    print(f"Уровень: {game_level}, Ширина: {width}, Высота: {height}, Мины: {mines}")
    pygame.quit()