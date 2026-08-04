import asyncio
import random
import sys
import pygame

# Initialize Pygame & Audio Mixer
pygame.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
FPS = 12

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 20, 60)
GREEN = (50, 205, 50)
DARK_RED = (139, 0, 0)
GRAY = (50, 50, 50)

# Setup Display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Broken Heart Snake Game")
clock = pygame.time.Clock()

# Load Sound Effects (with safety check)
try:
    try_again_sound = pygame.mixer.Sound("try_again.ogg")
    exit_sound = pygame.mixer.Sound("exit.ogg")
except Exception:
    try_again_sound = None
    exit_sound = None


class Snake:

    def __init__(self):
        self.reset()

    def reset(self):
        self.body = [
            (WIDTH // 2, HEIGHT // 2),
            (WIDTH // 2 - GRID_SIZE, HEIGHT // 2),
            (WIDTH // 2 - (2 * GRID_SIZE), HEIGHT // 2),
        ]
        self.direction = (GRID_SIZE, 0)
        self.grow = False

    def move(self):
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)

        if self.grow:
            self.body = [new_head] + self.body
            self.grow = False
        else:
            self.body = [new_head] + self.body[:-1]

    def change_direction(self, new_dir):
        # Prevent reversing directly into itself
        if (new_dir[0] * -1, new_dir[1] * -1) != self.direction:
            self.direction = new_dir

    def check_collision(self):
        head_x, head_y = self.body[0]
        # Wall collisions
        if head_x < 0 or head_x >= WIDTH or head_y < 0 or head_y >= HEIGHT:
            return True
        # Self collision
        if self.body[0] in self.body[1:]:
            return True
        return False

    def draw(self, surface):
        for segment in self.body:
            pygame.draw.rect(
                surface,
                GREEN,
                (segment[0], segment[1], GRID_SIZE - 2, GRID_SIZE - 2),
            )


class Food:

    def __init__(self):
        self.position = (0, 0)
        self.spawn()

    def spawn(self):
        x = random.randint(0, (WIDTH - GRID_SIZE) // GRID_SIZE) * GRID_SIZE
        y = random.randint(0, (HEIGHT - GRID_SIZE) // GRID_SIZE) * GRID_SIZE
        self.position = (x, y)

    def draw(self, surface):
        pygame.draw.rect(
            surface,
            RED,
            (self.position[0], self.position[1], GRID_SIZE - 2, GRID_SIZE - 2),
        )


def draw_text(surface, text, size, color, center_pos):
    font = pygame.font.SysFont("arial", size, bold=True)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=center_pos)
    surface.blit(text_surface, text_rect)


async def show_heartbreak_screen(action_type):
    """Displays Game Over text, plays audio, and safely restarts after song duration or on keypress."""
    screen.fill(BLACK)

    if action_type == "try_again":
        if try_again_sound:
            try_again_sound.play()
        message = "Bakit ka pa babalik? Masasaktan ka lang ulit... 💔"
        sub_message = (
            "Playing track (61s)... Press SPACE or CLICK to skip & restart"
        )
        color = RED
        duration_seconds = 61  # Haba ng try_again.ogg
    else:  # exit
        if exit_sound:
            exit_sound.play()
        message = "Sige, sumuko ka na lang tulad ng ginawa niya. 👋"
        sub_message = "Playing track (47s)... Press SPACE or CLICK to skip"
        color = GRAY
        duration_seconds = 47  # Haba ng exit.ogg

    draw_text(screen, message, 28, color, (WIDTH // 2, HEIGHT // 2 - 20))
    draw_text(screen, sub_message, 18, WHITE, (WIDTH // 2, HEIGHT // 2 + 40))
    pygame.display.flip()

    # Calculate total loops (10 iterations per second)
    total_iterations = int(duration_seconds * 10)

    for _ in range(total_iterations):
        # Process window events to avoid (Not Responding) freezes & allow skipping
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if pygame.mixer.get_busy():
                    pygame.mixer.stop()
                return
            # Allow Space, Enter, or Click to skip song early!
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mixer.get_busy():
                    pygame.mixer.stop()
                return

        # Exit loop early if song finishes before timer
        if not pygame.mixer.get_busy():
            break

        pygame.display.flip()
        await asyncio.sleep(0.1)

    # Ensure audio stops before returning control
    pygame.mixer.stop()


async def game_over_menu(score):
    """Displays Game Over prompt with Try Again and Exit buttons."""
    while True:
        screen.fill(DARK_RED)

        draw_text(
            screen,
            "GAME OVER 💔",
            50,
            WHITE,
            (WIDTH // 2, HEIGHT // 2 - 100),
        )
        draw_text(
            screen,
            f"Final Score: {score}",
            30,
            WHITE,
            (WIDTH // 2, HEIGHT // 2 - 40),
        )

        try_again_rect = pygame.Rect(WIDTH // 2 - 160, HEIGHT // 2 + 30, 140, 50)
        exit_rect = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 30, 140, 50)

        pygame.draw.rect(screen, GREEN, try_again_rect, border_radius=8)
        pygame.draw.rect(screen, BLACK, exit_rect, border_radius=8)

        draw_text(screen, "Try Again", 22, WHITE, try_again_rect.center)
        draw_text(screen, "Exit", 22, WHITE, exit_rect.center)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if try_again_rect.collidepoint(mouse_pos):
                    return "try_again"
                if exit_rect.collidepoint(mouse_pos):
                    return "exit"

        await asyncio.sleep(0)


async def main():
    snake = Snake()
    food = Food()
    score = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    snake.change_direction((0, -GRID_SIZE))
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    snake.change_direction((0, GRID_SIZE))
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    snake.change_direction((-GRID_SIZE, 0))
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    snake.change_direction((GRID_SIZE, 0))

        snake.move()

        # Check Food Collision
        if snake.body[0] == food.position:
            snake.grow = True
            score += 1
            food.spawn()

        # Check Snake Collision
        if snake.check_collision():
            choice = await game_over_menu(score)
            await show_heartbreak_screen(choice)

            if choice == "try_again":
                snake.reset()
                food.spawn()
                score = 0
            else:
                running = False

        screen.fill(BLACK)
        snake.draw(screen)
        food.draw(screen)

        draw_text(screen, f"Score: {score}", 22, WHITE, (70, 20))

        pygame.display.flip()
        clock.tick(FPS)

        # Yield to browser/Pygbag main thread
        await asyncio.sleep(0)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    asyncio.run(main())