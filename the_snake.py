"""
Змейка - классическая игра на Python с использованием библиотеки pg.

Игрок управляет змейкой, которая должна собирать яблоки, растущие в длину.
Цель - набрать как можно больше очков,
избегая столкновения с собственным хвостом.

Особенности реализации:
- Игровое поле 640x480 пикселей с сеткой 20x20
- Телепортация через границы экрана
- Случайное появление яблок на поле
- Управление стрелками клавиатуры
- Скорость игры: 7.5 кадров в секунду

Запуск: выполните файл для начала игры.
Управление: стрелки вверх/вниз/влево/вправо

Функции:
    choice - используется для случайного выбора направления движения змейки
    randint - используется для генерации случайных координат появления яблока
"""
from random import choice, randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Рассчитываем все возможные позиции на поле
ALL_POSITIONS = [
    (grid_x * GRID_SIZE, grid_y * GRID_SIZE)
    for grid_x in range(GRID_WIDTH)
    for grid_y in range(GRID_HEIGHT)
]

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 7.5

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """
    Базовый класс для всех игровых объектов.

    Определяет общие свойства и методы, которые будут наследоваться
    другими игровыми объектами.
    """

    def __init__(self) -> None:
        """Инициализирует игровой объект с позицией по центру экрана."""
        self.position = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))
        self.body_color = None
        self.positions = None

    def draw(self):
        """Абстрактный метод для отрисовки объекта на экране."""
        raise NotImplementedError()


class Apple(GameObject):
    """
    Класс, представляющий яблоко в игре.

    Наследуется от GameObject. Яблоко появляется в случайных позициях
    на игровом поле и служит пищей для змейки.
    """

    def __init__(self, occupied_positions=None, body_color=APPLE_COLOR):
        """
        Инициализирует яблоко со случайной позицией и цветом.

        Args:
            occupied_positions: Занятые позиции на игровом поле,
            по умолчанию None
            body_color (tuple): Цвет яблока в формате RGB,
            по умолчанию APPLE_COLOR
        """
        super().__init__()
        self.body_color = body_color
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions):
        """
        Устанавливает случайную позицию для яблока на свободной ячейке.

        Args:
            occupied_positions (list, optional): Список занятых позиций,
            которые нужно избегать. По умолчанию None
        """
        occupied_positions = occupied_positions or []

        free_positions = [pos for pos in ALL_POSITIONS
                          if pos not in occupied_positions]

        if free_positions:
            self.position = choice(free_positions)
        else:
            self.position = (randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                             randint(0, GRID_HEIGHT - 1) * GRID_SIZE)

    def draw(self):
        """
        Отрисовывает яблоко на экране.

        Создает прямоугольник в позиции яблока, заливает его цветом APPLE_COLOR
        и добавляет границу цвета BORDER_COLOR.
        """
        rect = pg.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """
    Класс, представляющий змейку в игре.

    Наследуется от GameObject. Управляет движением, отрисовкой
    и логикой змейки.
    """

    def __init__(self, body_color=SNAKE_COLOR):
        """
        Инициализирует змейку с начальной позицией и направлением.

        Устанавливает начальную длину, позицию, направление движения
        и другие необходимые атрибуты.

        Args:
            body_color (tuple): Цвет змейки в формате RGB,
            по умолчанию SNAKE_COLOR
        """
        super().__init__()
        self.body_color = body_color
        self.direction_list = [RIGHT, LEFT, UP, DOWN]
        self.reset()
        self.direction = RIGHT

    def get_head_position(self):
        """
        Возвращает позицию головы змейки.

        Returns:
            tuple: Координаты (x, y) головы змейки
        """
        return self.positions[0]

    def update_direction(self, next_direction=None):
        """
        Обновляет направление движения змейки.

        Если было установлено следующее направление (next_direction),
        применяет его и сбрасывает next_direction.

        Args:
        next_direction (tuple, optional): Следующее направление движения
        """
        if self.next_direction:
            self.direction = self.next_direction

    def move(self):
        """
        Перемещает змейку на один шаг в текущем направлении.

        Returns:
            tuple: Новая позиция головы змейки
        """
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction

        new_head = ((head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
                    (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT)

        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

        return new_head

    def check_self_collision(self):
        """
        Проверяет столкновение головы змейки с её телом.

        Returns:
            bool: True если произошло столкновение, иначе False
        """
        return self.get_head_position() in self.positions[1:]

    def grow(self):
        """Увеличивает длину змейки на 1."""
        self.length += 1

    def reset(self):
        """
        Сбрасывает состояние змейки к начальному.

        Используется при столкновении с собой. Возвращает змейку
        к начальной длине, позиции и случайному направлению.
        """
        self.length = 1
        self.positions = [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))]
        self.direction = choice(self.direction_list)
        self.next_direction = None
        self.last = None

    def draw(self):
        """
        Отрисовывает змейку на экране.

        Использует оптимизированный подход:
        - Всегда рисует голову змейки
        - Стирает только последний удаленный сегмент (если есть)
        - Не перерисовывает все тело каждый кадр
        """
        head_rect = pg.Rect(self.get_head_position(), (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, head_rect)
        pg.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)
            self.last = None


def handle_keys(game_object):
    """
    Обрабатывает нажатия клавиш для управления игрой.

    Args:
        game_object (Snake): Объект змейки, которым нужно управлять

    Обрабатывает:
        - Закрытие окна (pg.QUIT)
        - Нажатия клавиш стрелок для изменения направления движения
        - Предотвращает разворот на 180 градусов (противоположное направление)

    Исключения:
        SystemExit: При закрытии окна игры
    """
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit('Игра завершена пользователем.')
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """
    Основная функция игры, запускающая главный игровой цикл.

    Функция выполняет следующие действия:
    1. Инициализирует pygame и создает игровые объекты (змейку и яблоко)
    2. Запускает бесконечный игровой цикл, который:
       - Контролирует частоту обновления экрана с заданной скоростью SPEED
       - Обрабатывает пользовательский ввод (нажатия клавиш)
       - Обновляет направление движения змейки
       - Перемещает змейку на один шаг
       - Проверяет столкновение змейки с самой собой (сброс при столкновении)
       - Проверяет, съела ли змейка яблоко:
           * Увеличивает длину змейки при съедании яблока
           * Генерирует новую позицию для яблока, избегая позиций змейки
       - Обновляет отображение игрового поля

    Игровой цикл продолжается до закрытия окна пользователем.

    АЛГОРИТМ ИГРОВОГО ЦИКЛА:
    1. Обработка ввода пользователя
    2. Обновление направления движения
    3. Перемещение змейки
    4. Проверка столкновений и условий игры
    5. Отрисовка игровых объектов
    6. Обновление экрана
    """
    # Инициализация pygame:
    pg.init()
    # Тут нужно создать экземпляры классов.
    snake = Snake()
    apple = Apple(occupied_positions=snake.positions)
    screen.fill(BOARD_BACKGROUND_COLOR)
    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        new_head = snake.move()
        if snake.check_self_collision():
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)
        if new_head == apple.position:
            snake.grow()
            apple.randomize_position(snake.positions)
        apple.draw()
        snake.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
