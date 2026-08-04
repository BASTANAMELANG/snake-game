import os
import sys
import time
import random
import pygame

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

# Colors
BLACK = (20, 20, 20)
WHITE = (255, 255, 255)
RED = (220, 50, 50)
GREEN = (50, 205, 50)
GRAY = (100, 100, 100)
HOVER_GRAY = (150, 150, 150)

# Game variables
BLOCK_SIZE = 20
FPS = 12

# Fonts
font_large = pygame.font.SysFont("arial", 32, bold=True)
font_small = pygame.font.SysFont("arial", 20)

# Directory setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def play_video_with_audio(video_file, duration_seconds=5):
    """Bubuksan ang .mp4 file gamit ang default media player ng Windows (100% may sound)"""
    video_path = os.path.join(BASE_DIR, video_file)
    
    if os.path.exists(video_path):
        # Bubuksan ang video sa Windows Default Player
        os.startfile(video_path)
        # Maghihintay ng ilang segundo para mapanood at marinig 'yung clip
        time.sleep(duration_seconds)
    else:
        print(f"Error: Hindi mahanap ang file na '{video_path}'")


def draw_button(text, x, y, width, height, is_hovered):
    color = HOVER_GRAY if is_hovered else GRAY
    pygame.draw.rect(screen, color, (x, y, width, height), border_radius=8)
    text_surface = font_small.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surface, text_rect)


def game_over_screen():
    btn_w, btn_h = 120, 45
    try_btn_rect = pygame.Rect(WIDTH // 2 - 140, 250, btn_w, btn_h)
    exit_btn_rect = pygame.Rect(WIDTH // 2 + 20, 250, btn_w, btn_h)

    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Pag pinointer at kinlik ang TRY AGAIN
                if try_btn_rect.collidepoint(mouse_pos):
                    # I-play ang try_again.mp4 (mag-wait ng 5 seconds)
                    play_video_with_audio("try_again.mp4", duration_seconds=5)
                    return "restart"

                # Pag pinointer at kinlik ang EXIT
                if exit_btn_rect.collidepoint(mouse_pos):
                    # I-play ang exit.mp4 (mag-wait ng 5 seconds)
                    play_video_with_audio("exit.mp4", duration_seconds=5)
                    pygame.quit()
                    sys.exit()

        screen.fill(BLACK)

        msg1 = font_large.render("GAME OVER", True, RED)
        msg2 = font_small.render("Lalaro ka pa ba?", True, WHITE)

        screen.blit(msg1, msg1.get_rect(center=(WIDTH // 2, 120)))
        screen.blit(msg2, msg2.get_rect(center=(WIDTH // 2, 170)))

        draw_button("Try Again", try_btn_rect.x, try_btn_rect.y, btn_w, btn_h, try_btn_rect.collidepoint(mouse_pos))
        draw_button("Exit", exit_btn_rect.x, exit_btn_rect.y, btn_w, btn_h, exit_btn_rect.collidepoint(mouse_pos))

        pygame.display.flip()


def main():
    clock = pygame.time.Clock()

    snake = [[100, 100], [90, 100], [80, 100]]
    direction = "RIGHT"
    next_direction = direction

    food = [
        random.randrange(1, (WIDTH // BLOCK_SIZE)) * BLOCK_SIZE,
        random.randrange(1, (HEIGHT // BLOCK_SIZE)) * BLOCK_SIZE,
    ]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != "DOWN":
                    next_direction = "UP"
                elif event.key == pygame.K_DOWN and direction != "UP":
                    next_direction = "DOWN"
                elif event.key == pygame.K_LEFT and direction != "RIGHT":
                    next_direction = "LEFT"
                elif event.key == pygame.K_RIGHT and direction != "LEFT":
                    next_direction = "RIGHT"

        direction = next_direction

        head = list(snake[0])
        if direction == "UP":
            head[1] -= BLOCK_SIZE
        elif direction == "DOWN":
            head[1] += BLOCK_SIZE
        elif direction == "LEFT":
            head[0] -= BLOCK_SIZE
        elif direction == "RIGHT":
            head[0] += BLOCK_SIZE

        # Collision Check
        if (
            head[0] < 0
            or head[0] >= WIDTH
            or head[1] < 0
            or head[1] >= HEIGHT
            or head in snake
        ):
            action = game_over_screen()
            if action == "restart":
                main()

        snake.insert(0, head)

        # Eat Food
        if head[0] == food[0] and head[1] == food[1]:
            food = [
                random.randrange(1, (WIDTH // BLOCK_SIZE)) * BLOCK_SIZE,
                random.randrange(1, (HEIGHT // BLOCK_SIZE)) * BLOCK_SIZE,
            ]
        else:
            snake.pop()

        screen.fill(BLACK)

        # Draw Snake
        for segment in snake:
            pygame.draw.rect(screen, GREEN, (segment[0], segment[1], BLOCK_SIZE - 2, BLOCK_SIZE - 2))

        # Draw Food
        pygame.draw.rect(screen, RED, (food[0], food[1], BLOCK_SIZE - 2, BLOCK_SIZE - 2))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()