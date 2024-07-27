import pygame
import sys
import random
from pygame.math import Vector2
from zmienne import SNAKE
from zmienne import FRUIT
from settings import MAIN_GAME

# Initialize Pygame
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
cell_size = MAIN_GAME.cell_size
cell_number = MAIN_GAME.cell_number

screen = pygame.display.set_mode((cell_number * cell_size, cell_number * cell_size))
clock = pygame.time.Clock()
apple = pygame.image.load('Graphics/apple.png').convert_alpha()

SCREEN_UPDATE = pygame.USEREVENT
pygame.time.set_timer(SCREEN_UPDATE, 150)

initial_touch_pos = None
final_touch_pos = None

def handle_swipe(main_game):
    global initial_touch_pos, final_touch_pos
    if initial_touch_pos and final_touch_pos:
        dx = final_touch_pos[0] - initial_touch_pos[0]
        dy = final_touch_pos[1] - initial_touch_pos[1]
        if abs(dx) > abs(dy):  # Horizontal swipe
            if dx > 0 and main_game.snake.direction.x != -1:
                main_game.snake.direction = Vector2(1, 0)
            elif dx < 0 and main_game.snake.direction.x != 1:
                main_game.snake.direction = Vector2(-1, 0)
        else:  # Vertical swipe
            if dy > 0 and main_game.snake.direction.y != -1:
                main_game.snake.direction = Vector2(0, 1)
            elif dy < 0 and main_game.snake.direction.y != 1:
                main_game.snake.direction = Vector2(0, -1)
        initial_touch_pos = None
        final_touch_pos = None

class Button:
    def __init__(self, text, x, y, width, height, color, hover_color, text_color, font):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = font
        self.hovered = False

    def draw(self, surface):
        current_color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface, current_color, self.rect)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 50)
        self.buttons = [
            Button("Play", screen.get_width() / 2 - 100, screen.get_height() / 2 - 30, 200, 60, (0, 0, 255), (100, 100, 255), (255, 255, 255), self.font),
            Button("Settings", screen.get_width() / 2 - 100, screen.get_height() / 2 + 40, 200, 60, (0, 0, 255), (100, 100, 255), (255, 255, 255), self.font),
            Button("Exit", screen.get_width() / 2 - 100, screen.get_height() / 2 + 110, 200, 60, (0, 0, 255), (100, 100, 255), (255, 255, 255), self.font)
        ]

    def display_menu(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                for button in self.buttons:
                    if button.handle_event(event):
                        if button.text == "Play":
                            return 'start_game'
                        elif button.text == "Settings":
                            return 'options'
                        elif button.text == "Exit":
                            pygame.quit()
                            sys.exit()

            self.screen.fill((0, 0, 0))
            for button in self.buttons:
                button.draw(self.screen)

            pygame.display.flip()

class MAIN:
    def __init__(self):
        self.snake = SNAKE()
        self.fruit = FRUIT()

    def update(self):
        self.snake.move_snake()
        self.check_collision()
        self.check_fail()

    def draw_elements(self):
        self.draw_grass()
        self.fruit.draw_fruit()
        self.snake.draw_snake()

    def check_collision(self):
        if self.fruit.pos == self.snake.body[0]:
            self.fruit.randomize()
            self.snake.add_block()
            self.snake.play_crunch_sound()

        for block in self.snake.body[1:]:
            if block == self.fruit.pos:
                self.fruit.randomize()

    def check_fail(self):
        if not 0 <= self.snake.body[0].x < cell_number or not 0 <= self.snake.body[0].y < cell_number:
            self.snake.reset()

        for block in self.snake.body[1:]:
            if block == self.snake.body[0]:
                self.snake.reset()

    def draw_grass(self):
        grass_color = (167, 209, 61)
        for row in range(cell_number):
            if row % 2 == 0:
                for col in range(cell_number):
                    if col % 2 == 0:
                        grass_rect = pygame.Rect(col * cell_size, row * cell_size, cell_size, cell_size)
                        pygame.draw.rect(screen, grass_color, grass_rect)
            else:
                for col in range(cell_number):
                    if col % 2 != 0:
                        grass_rect = pygame.Rect(col * cell_size, row * cell_size, cell_size, cell_size)
                        pygame.draw.rect(screen, grass_color, grass_rect)

def start_game():
    main_game = MAIN()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == SCREEN_UPDATE:
                main_game.update()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    if main_game.snake.direction.y != 1:
                        main_game.snake.direction = Vector2(0, -1)
                if event.key == pygame.K_d:
                    if main_game.snake.direction.x != -1:
                        main_game.snake.direction = Vector2(1, 0)
                if event.key == pygame.K_s:
                    if main_game.snake.direction.y != -1:
                        main_game.snake.direction = Vector2(0, 1)
                if event.key == pygame.K_a:
                    if main_game.snake.direction.x != 1:
                        main_game.snake.direction = Vector2(-1, 0)
                if event.key == pygame.K_r:
                    main_game.snake.reset()
            elif event.type == pygame.FINGERDOWN:
                global initial_touch_pos
                initial_touch_pos = (event.x * cell_number * cell_size, event.y * cell_number * cell_size)
            elif event.type == pygame.FINGERUP:
                global final_touch_pos
                final_touch_pos = (event.x * cell_number * cell_size, event.y * cell_number * cell_size)
                handle_swipe(main_game)

        screen.fill((175, 215, 70))
        main_game.draw_elements()
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main_menu = MainMenu(screen)
    while True:
        action = main_menu.display_menu()
        if action == 'start_game':
            start_game()
        elif action == 'options':
            print("Options selected, not implemented yet.")
