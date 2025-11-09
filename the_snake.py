"""
Импорт функций из модуля random для работы со случайностью в игре.

Функции:
    choice - используется для случайного выбора направления движения змейки
    randint - используется для генерации случайных координат появления яблока
"""
from random import choice, randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

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
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


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
        pass


class Apple(GameObject):
    """
    Класс, представляющий яблоко в игре.

    Наследуется от GameObject. Яблоко появляется в случайных позициях
    на игровом поле и служит пищей для змейки.
    """

    def __init__(self):
        """Инициализирует яблоко со случайной позицией и цветом."""
        super().__init__()
        self.body_color = APPLE_COLOR
        self.randomize_position()

    def randomize_position(self):
        """
        Устанавливает случайную позицию для яблока на игровом поле.

        Позиция выбирается с учетом размеров сетки, чтобы яблоко
        всегда находилось внутри игрового поля.
        """
        self.position = (randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                         randint(0, GRID_HEIGHT - 1) * GRID_SIZE)

    def draw(self):
        """
        Отрисовывает яблоко на экране.

        Создает прямоугольник в позиции яблока, заливает его цветом APPLE_COLOR
        и добавляет границу цвета BORDER_COLOR.
        """
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """
    Класс, представляющий змейку в игре.

    Наследуется от GameObject. Управляет движением, отрисовкой
    и логикой змейки.
    """

    def __init__(self):
        """
        Инициализирует змейку с начальной позицией и направлением.

        Устанавливает начальную длину, позицию, направление движения
        и другие необходимые атрибуты.
        """
        super().__init__()
        self.body_color = SNAKE_COLOR
        self.length = 1
        self.positions = [((SCREEN_HEIGHT // 2), (SCREEN_WIDTH // 2))]
        self.direction = RIGHT
        self.next_direction = None
        self.direction_list = [RIGHT, LEFT, UP, DOWN]
        self.last = None

    def get_head_position(self):
        """
        Возвращает позицию головы змейки.

        Returns:
            tuple: Координаты (x, y) головы змейки
        """
        return self.position[0]

    def update_direction(self):
        """
        Обновляет направление движения змейки.

        Если было установлено следующее направление (next_direction),
        применяет его и сбрасывает next_direction.
        """
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self, apple):
        """
        Перемещает змейку на один шаг в текущем направлении.

        Args:
            apple (Apple): Объект яблока для проверки столкновения

        Логика:
            - Вычисляет новую позицию головы
            - Обрабатывает телепортацию через границы экрана
            - Проверяет столкновение с собой (игра сбрасывается)
            - Проверяет столкновение с яблоком (змейка растет)
            - Обновляет позиции сегментов тела
        """
        new_head = (self.positions[0][0] + self.direction[0] * GRID_SIZE,
                    self.positions[0][1] + self.direction[1] * GRID_SIZE)

        new_head = ((new_head[0] % SCREEN_WIDTH),
                    (new_head[1] % SCREEN_HEIGHT))

        if new_head in self.positions[1:]:
            self.reset()

        if new_head == apple.position:
            self.length += 1
            apple.randomize_position()

        if len(self.positions) > self.length:
            self.positions.pop()
            self.last = self.positions[-1]
        else:
            self.positions.insert(0, new_head)

        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def reset(self):
        """
        Сбрасывает состояние змейки к начальному.

        Используется при столкновении с собой. Возвращает змейку
        к начальной длине, позиции и случайному направлению.
        """
        self.length = 1
        self.positions = []
        self.positions = [((SCREEN_HEIGHT // 2), (SCREEN_WIDTH // 2))]
        self.direction = choice(self.direction_list)
        screen.fill(BOARD_BACKGROUND_COLOR)

    def draw(self):
        """
        Отрисовывает змейку на экране.

        Рисует все сегменты тела змейки, включая голову.
        Каждый сегмент имеет заливку SNAKE_COLOR и границу BORDER_COLOR.
        """
        for position in self.positions[:-1]:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)


def handle_keys(game_object):
    """
    Обрабатывает нажатия клавиш для управления игрой.

    Args:
        game_object (Snake): Объект змейки, которым нужно управлять

    Обрабатывает:
        - Закрытие окна (pygame.QUIT)
        - Нажатия клавиш стрелок для изменения направления движения
        - Предотвращает разворот на 180 градусов (противоположное направление)
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """
    Основная функция игры.

    Инициализирует pygame,
    создает игровые объекты и запускает главный игровой цикл.

    В главном цикле:
        - Контролирует частоту обновления экрана
        - Обрабатывает пользовательский ввод
        - Обновляет состояние игры
        - Отрисовывает игровые объекты
        - Обновляет экран
    """
    # Инициализация PyGame:
    pygame.init()
    # Тут нужно создать экземпляры классов.
    apple = Apple()
    snake = Snake()

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move(apple)
        apple.draw()
        snake.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
