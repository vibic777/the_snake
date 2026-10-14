"""Модуль для получения рандомного числа"""
from random import randint

import sys
import pygame

from constants import (
    APPLE_COLOR, BAD_APPLE_COLOR, BOARD_BACKGROUND_COLOR, BORDER_COLOR,
    CENTER_OF_COORDINATE, DELTA_SPEED, DOWN,
    GRID_HEIGHT, GRID_SIZE, GRID_WIDTH,
    LEFT, MAX_LENGTH, MAX_SPEED, MIN_SPEED, RIGHT, SCREEN_HEIGHT, SCREEN_WIDTH,
    SNAKE_COLOR, MIN_LENGTH, UP
)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

clock = pygame.time.Clock()

pygame.display.set_caption(
    'Мега питон, начальная скорость игры: '
    f'{MIN_SPEED}'
    ' длина питона: '
    f'{MIN_LENGTH}'
)


class GameObject:
    """Основной класс игрового объекта
    содержит метод draw, атрибуты, позиция и цвет.
    """

    def __init__(
            self,
            position=None,
            body_color=BOARD_BACKGROUND_COLOR
    ):
        """Инициализирует базовые атрибуты объекта,
        такие как его позиция и цвет.
        """
        self.position = CENTER_OF_COORDINATE if position is None else position
        self.body_color = body_color

    def draw(self):
        """Метод должен определять,
        как объект будет отрисовываться на экране.
        """

    @classmethod
    def draw_cell(cls, postion, color, border_color=None):
        """Отрисовать ячейку"""
        border_color = color if border_color is None else border_color
        try:
            rectangle = pygame.Rect(postion, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, color, rectangle)
            pygame.draw.rect(screen, border_color, rectangle, 1)
        except ValueError as e:
            error_message = f'Ошибка: {e}'
            return sys.exit(error_message)


class Apple(GameObject):
    """Яблоки которые будет кушать наш питон."""

    def __init__(self,
                 position=None,
                 body_color=APPLE_COLOR):
        self.position = [CENTER_OF_COORDINATE]
        super().__init__(self.position, body_color)

    def draw(self):
        """Отрисовывает яблоко на игровой поверхности."""
        self.draw_cell(self.position, self.body_color, BORDER_COLOR)

    def randomize_position(self, occupied_positions):
        """Устанавливает случайное положение яблока на игровом поле."""
        while True:
            position = [randint(1, GRID_WIDTH - 1) * GRID_SIZE,
                        randint(1, GRID_HEIGHT - 1) * GRID_SIZE]
            if position not in occupied_positions:
                break
        self.position = position


class Snake(GameObject):
    """Главный герой нашей киноленты
    о похождении питона за яблоками.
    """

    def __init__(
        self,
        length=MIN_LENGTH,
        positions=None,
        direction=RIGHT,
        next_direction=None,
        body_color=SNAKE_COLOR
    ):
        """Инициализирует начальное состояние питона."""
        self.length = length
        self.positions = ([CENTER_OF_COORDINATE] if positions is None else
                          positions)
        self.direction = direction
        self.next_direction = next_direction
        self.body_border_color = BORDER_COLOR
        self.last = []
        self.slice = 1
        super().__init__(body_color=body_color)

    def get_head_position(self):
        """Возвращает позицию головы змейки
        (первый элемент в списке positions).
        """
        return self.positions[0]

    def move(self):
        """Обновляет позицию питона (координаты каждой секции),
        добавляя условно новую голову в начало списка positions
        и удаляя последний элемент, если длина питона не увеличилась.
        """
        self.update_direction()
        new_x, new_y = (
            self.positions[0][0] + self.direction[0] * GRID_SIZE,
            self.positions[0][1] + self.direction[1] * GRID_SIZE)
        if new_x >= SCREEN_WIDTH or new_x < 0:
            new_x = new_x % SCREEN_WIDTH
        if new_y >= SCREEN_HEIGHT or new_y < 0:
            new_y = new_y % SCREEN_HEIGHT
        self.positions.insert(0,
                              [new_x,
                               new_y])
        if self.length == len(self.positions) or self.length < 1:
            self.last = self.positions[-1:]
        elif self.length < len(self.positions):
            self.slice = len(self.positions) - self.length
            self.last = self.positions[-self.slice:]
            del self.positions[-self.slice:]

    def draw(self):
        """Отрисовывает питона на экране, все алгоритмы"""
        self.draw_cell(self.positions[0],
                       self.body_color,
                       self.body_border_color)
        if self.last:
            for last_pos in self.last:
                self.draw_cell(last_pos,
                               BOARD_BACKGROUND_COLOR)

    def reset(self):
        """Сбрасывает питона в начальное состояние."""
        self.length = MIN_LENGTH
        self.direction = RIGHT
        self.next_direction = None
        self.position = [CENTER_OF_COORDINATE]

    def update_direction(self):
        """Обновляет направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None


def handle_keys(
        game_object,
):
    """Обрабатывает нажатия клавиш, чтобы изменить
    направление движения змейки (есть в прекоде).
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


def clamp(n, smallest, largest):
    """Возвращает ограниченное значение"""
    return max(smallest, min(n, largest))


def main():
    """Основная функция игры."""

    def reset_level():
        """Сброс уровня."""
        nonlocal speed_game
        snake.reset()
        speed_game = MIN_SPEED
        screen.fill(BOARD_BACKGROUND_COLOR)

    def reward():
        """Награда."""
        nonlocal speed_game
        snake.length = clamp(snake.length + 1, MIN_LENGTH, MAX_LENGTH)
        speed_game = clamp(speed_game + DELTA_SPEED, MIN_SPEED, MAX_SPEED)
        good_apple.randomize_position(
            occupied_positions=snake.positions + [bad_apple.position]
        )

    def punish():
        """Наказание."""
        nonlocal speed_game
        snake.length = clamp(snake.length - 1, MIN_LENGTH, MAX_LENGTH)
        speed_game = clamp(speed_game - DELTA_SPEED, MIN_SPEED, MAX_SPEED)
        bad_apple.randomize_position(
            occupied_positions=snake.positions + [good_apple.position]
        )

    def handle_collisions():
        """Обработка коллизий."""
        if snake.get_head_position() in snake.positions[1:]:
            reset_level()
        elif snake.get_head_position() == good_apple.position:
            reward()
        elif snake.get_head_position() == bad_apple.position:
            punish()
        else:
            return
        pygame.display.set_caption(
            'Мега питон, начальная скорость игры: '
            f'{speed_game}'
            ' длина питона: '
            f'{snake.length}'
        )

    def draw_objects():
        """Отрисовка кадра"""
        good_apple.draw()
        bad_apple.draw()
        snake.draw()

    pygame.init()
    speed_game = MIN_SPEED
    snake = Snake()
    good_apple = Apple()
    bad_apple = Apple(body_color=BAD_APPLE_COLOR)
    good_apple.randomize_position(snake.positions)
    bad_apple.randomize_position(
        occupied_positions=snake.positions + [good_apple.position])
    while True:
        clock.tick(speed_game)
        handle_keys(snake)
        snake.move()
        draw_objects()
        handle_collisions()
        pygame.display.update()


if __name__ == '__main__':
    main()
