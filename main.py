from fileinput import close

import pygame
import os
import sys
import random
import time

# Инициализация Pygame
pygame.init()

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
GREEN = (0, 255, 0)
BROWN = (160, 130, 100)
RED = (255, 0, 0)

# Размер окна игры
width, height = 930, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Террария')

# Блоки для генерации мира
blocks = {0: [5, 1, 0]}  # начальная позиция блока
current_position = 0  # текущая позиция игрока


# Функция завершения программы
def terminate():
    pygame.quit()
    sys.exit()


# Генерация мира слева от текущей позиции
def move_left():
    global current_position
    current_position -= 1
    visible_range = [i for i in range(current_position - 16, current_position + 17)]
    generate_world(0)
    return visible_range


# Генерация мира справа от текущей позиции
def move_right():
    global current_position
    current_position += 1
    visible_range = [i for i in range(current_position - 16, current_position + 17)]
    generate_world(1)
    return visible_range


# Определение минимального и максимального значений блоков
def get_min_max():
    block_keys = list(blocks.keys())
    return [min(block_keys), max(block_keys)]


# Генерация нового блока
def generate_world(direction):
    global blocks
    elevation_changes = [-1, 1]

    if direction == 0:
        min_block_key = get_min_max()[0]
        previous_height = blocks[min_block_key][0]

        if 4 < previous_height < 11:
            height_change_options = [0, 0, 0, 1, -1]
        elif previous_height >= 10:
            height_change_options = [0, 0, 0, -1, -1]
        else:
            height_change_options = [0, 0, 0, 1, 1]

        new_height = previous_height + random.choice(height_change_options)
        new_elevation = random.choice(elevation_changes)
        blocks[min_block_key - 1] = [new_height, 1, new_elevation]

    elif direction == 1:
        max_block_key = get_min_max()[1]
        previous_height = blocks[max_block_key][0]

        if 4 < previous_height < 11:
            height_change_options = [0, 0, 0, 1, -1]
        elif previous_height >= 10:
            height_change_options = [0, 0, 0, -1, -1]
        else:
            height_change_options = [0, 0, 0, 1, 1]

        new_height = previous_height + random.choice(height_change_options)
        new_elevation = random.choice(elevation_changes)
        blocks[max_block_key + 1] = [new_height, 1, new_elevation]


# Отображение квадрата на экране
def draw_square(x, y, color):
    pygame.draw.rect(screen, color, (x, y, 29, 29))


# Начальная генерация мира
def initialize_world():
    for _ in range(17):
        generate_world(1)
    for _ in range(17):
        generate_world(0)


# Загрузка изображений
def load_image(filename, colorkey=None):
    fullname = os.path.join(filename)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((12, 12))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


# Класс монеты
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(load_image("coin.jpg", -1), (30, 30))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


def load_start_image():
    background_image = pygame.transform.scale(pygame.image.load(os.path.join('background.jpg')), [930, 600])
    screen.blit(background_image, (0, 0))
    pygame.display.flip()


def load_end_image():
    background_image = pygame.transform.scale(pygame.image.load(os.path.join('end.jpg')), [930, 600])
    screen.blit(background_image, (0, 0))
    pygame.display.flip()


# Шрифт и таймер
font = pygame.font.Font(None, 40)
time_remaining = 30
time_text = font.render(f'{time_remaining // 60:02}:{time_remaining % 60:02}', True, RED)
scroll_font = pygame.font.Font(None, 20)
score = 0
score_text = scroll_font.render(f'{score}', True, WHITE)
flag = 1
k = 1


# Основная игра
def play_game():
    global blocks, time_remaining, time_text, score, score_text, k
    k = 1
    visible_range = move_left()
    visible_range = move_right()
    screen.fill(BLACK)

    all_sprites = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    coin_group = pygame.sprite.Group()

    # Класс игрока
    class Player(pygame.sprite.Sprite):
        player_image = pygame.transform.scale(load_image("player.jpg", -1), [30, 60])

        def __init__(self, position, flipped=False):
            super().__init__(all_sprites)
            self.image = Player.player_image
            if flipped:
                self.image = pygame.transform.flip(self.image, True, False)
            self.rect = self.image.get_rect()
            self.mask = pygame.mask.from_surface(self.image)
            self.rect.x = position[0]
            self.rect.y = position[1]

        def update(self, x, y):
            self.rect = self.rect.move(x, y)

    # Спавн монет
    def spawn_coins():
        green_blocks = [i for i in visible_range[1:-1] if blocks[i][2] == 1]
        if green_blocks:
            for block_index in green_blocks:
                x = (visible_range.index(block_index) - 1) * 30
                y = height - (blocks[block_index][0] * 30) - 30
                coin = Coin(x, y)
                coin_group.add(coin)
                all_sprites.add(coin)

    # Очистка спавненных монет
    def clear_coins():
        for coin in coin_group:
            coin.kill()

    spawn_coins()
    player = Player([450, height - 210])
    player_group.add(player)
    clock = pygame.time.Clock()
    vertical_movement = 0
    frame_count = 0

    running = True
    key_event = 0
    load_start_image()
    file = open('example.txt', 'w+')
    while running:
        if time_remaining == 0:
            key_event = 2
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                k = 0
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    player.image = pygame.transform.flip(Player.player_image, True, False)
                    visible_range = move_left()
                    vertical_movement = 30 * (blocks[visible_range[17]][0] - blocks[visible_range[16]][0])
                    clear_coins()
                    spawn_coins()
                elif event.key == pygame.K_d:
                    player.image = Player.player_image
                    vertical_movement = 30 * (blocks[visible_range[16]][0] - blocks[visible_range[17]][0])
                    visible_range = move_right()
                    clear_coins()
                    spawn_coins()
                elif event.key == pygame.K_s:
                    key_event = 1
                    time_remaining = 30

        if key_event == 0:
            load_start_image()
            flag = 1
        elif key_event == 2:
            load_end_image()
            if flag:
                file.write(f'{score}\n')
                flag = 0
                time.sleep(2)
                terminate()
        else:
            flag = 1
            screen.fill('blue')
            player_group.update(0, vertical_movement)
            vertical_movement = 0

            for coin in coin_group:
                if pygame.sprite.collide_rect(player, coin):
                    coin.kill()
                    blocks[visible_range[16]][2] = 0
                    score += 1

            player_group.draw(screen)
            block_x = 0
            for block_index in visible_range[1:-1]:
                draw_square(block_x * 30, height - blocks[block_index][0] * 30, GREEN)
                if block_index == 0:
                    draw_square(block_x * 30, height - blocks[block_index][0] * 30, BLACK)
                for layer in range(int(blocks[block_index][0])):
                    if layer + 1 == int(blocks[block_index][0]) and (
                            int(blocks[block_index][0]) > int(blocks[block_index - 1][0]) or
                            int(blocks[block_index][0]) > int(blocks[block_index + 1][0])):
                        draw_square(block_x * 30, height - (layer * 30), GREEN)
                    else:
                        draw_square(block_x * 30, height - (layer * 30), BROWN)
                block_x += 1

            time_text_rect = time_text.get_rect(center=(465, 30))
            pygame.draw.rect(screen, GREY, (5, 5, 90, 30), 2)
            screen.blit(time_text, time_text_rect)
            score_text_rect = score_text.get_rect(center=(50, 20))
            score_text = scroll_font.render(f'Счёт = {score}', True, WHITE)
            time_text = font.render(f'{time_remaining // 60:02}:{time_remaining % 60:02}', True, RED)
            screen.blit(score_text, score_text_rect)
            screen.blit(time_text, time_text_rect)
            all_sprites.draw(screen)
            pygame.display.flip()

            frame_count += 1
            if frame_count == 60:
                frame_count = 0
                time_remaining -= 1

        clock.tick(60)
    close(file)


# Главная функция
def main():
    while k:
        initialize_world()
        play_game()


if __name__ == "__main__":
    main()
