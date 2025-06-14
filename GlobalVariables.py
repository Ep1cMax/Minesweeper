# GlobalVariables.py
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Cell:
    """Класс ячейки игрового поля"""
    mine: bool = False  # Есть ли мина
    flag: bool = False  # Есть ли флаг
    nearby_mines: int = 0  # Число мин вокруг
    opened: bool = False  # Открыта ли ячейка


class GameState:
    """Класс для хранения глобального состояния игры"""

    def __init__(self):
        # Шаг программы для отображения
        self.program_step: str = "MenuMainStep"

        # Уровень сложности (0-легкий, 1-средний, 2-сложный, 3-пользовательский)
        self.game_level: int = 0

        # Игровое поле (матрица клеток)
        self.field: List[List[Cell]] = []

        # Размеры поля
        self.field_height: int = 8
        self.field_width: int = 8

        # Количество мин
        self.field_mines_count: int = 10

        # Состояние мыши
        self.is_mouse_down: bool = False
        self.mouse_pos: Tuple[int, int] = (0, 0)
        self.mouse_button: int = 0  # 1-левая, 2-правая, 3-средняя

        # Пользовательский ввод
        self.is_user_input_done: bool = False
        self.user_input: str = ""

        # Инициализация пустого поля
        self.initialize_field()

    def initialize_field(self, width: int = None, height: int = None):
        """Инициализация игрового поля"""
        width = width or self.field_width
        height = height or self.field_height
        self.field = [[Cell() for _ in range(width)] for _ in range(height)]

    def reset_game_state(self):
        """Сброс состояния игры к начальным значениям"""
        self.__init__()


# Глобальный объект состояния игры
game_state = GameState()