# GlobalConstants.py

# Режим отладки - отображаются мины
DEBUG_MODE = False  # Можно изменить на True для отладки

# Ширина клетки
WIDTH_CELL = 39

# Стандартный отступ при выводе текста
TEXT_PADDING = 40

# Путь к фоновому изображению
BACKGROUND_SRC = 'background.png'

# Размеры фонового изображения
BACKGROUND_WIDTH = 600
BACKGROUND_HEIGHT = 400

# Дополнительные константы, которые могут понадобиться
class Colors:
    """Цвета для игры"""
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (200, 200, 200)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    LIGHT_BLUE = (173, 216, 230)
    DARK_GRAY = (100, 100, 100)

class GameSymbols:
    """Символы для игры"""
    MINE = '¤'
    FLAG = '⚑'
    UNOPENED = '■'