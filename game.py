import pygame
import random
import math
import sys

# --- Constants ---
DEBUG = True # Set to True to test with 16 balls

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BG_COLOR = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)

# Paddle
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 10
PADDLE_COLOR = (255, 255, 255)
PADDLE_Y_POS = SCREEN_HEIGHT - 40

# Ball
BALL_RADIUS = 7
BALL_COLOR = (255, 255, 255)
BALL_SPEED = 6 # Constant speed magnitude

# Bricks
BRICK_ROWS = 10
BRICK_COLS = 20
BRICK_GAP = 1
BRICK_WIDTH = (SCREEN_WIDTH - (BRICK_COLS + 1) * BRICK_GAP) / BRICK_COLS
BRICK_HEIGHT = 20
BRICK_COLORS = [(255, 99, 71), (255, 165, 0), (255, 215, 0), (50, 205, 50), (65, 105, 225)]

# --- Game Classes ---

class Ball:
    def __init__(self, x, y, radius, color, speed_x, speed_y):
        self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
        self.color = color
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.radius = radius

    def move(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.rect.center, self.radius)

class Paddle:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def move(self, x):
        self.rect.x = x
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

class Brick:
    def __init__(self, x, y, width, height, base_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.base_color = base_color
        self.visible = True
        self.health = 1
        self.max_health = 1

    def get_color(self):
        # Darken the color based on health
        if self.health <= 1 and self.health == self.max_health:
            return self.base_color
        
        # Create a stronger visual for higher health
        if self.health > 1:
            # Blend with a gray color for durability
            factor = (self.health -1) / max(self.max_health -1, 1) # 0 to 1
            r = int(self.base_color[0] * (1-factor) + 128 * factor)
            g = int(self.base_color[1] * (1-factor) + 128 * factor)
            b = int(self.base_color[2] * (1-factor) + 128 * factor)
            return (r, g, b)
        
        return self.base_color


    def draw(self, screen):
        if self.visible:
            pygame.draw.rect(screen, self.get_color(), self.rect)

# --- Main Game Function ---

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Breakout Game")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 36)

    stage = 1
    score = 0

    while True: # Main loop for stages
        # --- Stage Setup ---
        paddle = Paddle((SCREEN_WIDTH - PADDLE_WIDTH) / 2, PADDLE_Y_POS, PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_COLOR)
        
        # Create bricks
        bricks = []
        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                brick_x = col * (BRICK_WIDTH + BRICK_GAP) + (BRICK_GAP / 2)
                brick_y = row * (BRICK_HEIGHT + BRICK_GAP) + 50
                color = BRICK_COLORS[row % len(BRICK_COLORS)]
                bricks.append(Brick(brick_x, brick_y, BRICK_WIDTH, BRICK_HEIGHT, color))

        # Add health to bricks based on stage
        if stage > 1:
            num_upgrades = int(len(bricks) * 0.1)
            for _ in range(stage - 1):
                 for _ in range(num_upgrades):
                    brick_to_upgrade = random.choice(bricks)
                    brick_to_upgrade.health += 1
                    brick_to_upgrade.max_health = max(brick_to_upgrade.max_health, brick_to_upgrade.health)

        # Create balls
        balls = []
        ball_on_paddle = True
        num_balls = 16 if DEBUG else 1
        for _ in range(num_balls):
            ball = Ball(paddle.rect.centerx, paddle.rect.top - BALL_RADIUS, BALL_RADIUS, BALL_COLOR, 0, 0)
            balls.append(ball)

        # --- Level Game Loop ---
        level_running = True
        while level_running:
            # --- Event Handling ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEMOTION:
                    paddle.move(event.pos[0] - PADDLE_WIDTH / 2)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_r:
                        main() # Easiest way to restart full game
                        return

                # Launch ball
                if ball_on_paddle:
                    if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                        ball_on_paddle = False
                        for ball in balls:
                            ball.speed_y = -BALL_SPEED # Launch straight up

            # --- Game Logic ---
            if ball_on_paddle:
                for ball in balls:
                    ball.rect.centerx = paddle.rect.centerx
                    ball.rect.bottom = paddle.rect.top
            else:
                for ball in balls[:]:
                    ball.move()
                    # Wall collision
                    if ball.rect.left <= 0 or ball.rect.right >= SCREEN_WIDTH: ball.speed_x *= -1
                    if ball.rect.top <= 0: ball.speed_y *= -1
                    # Bottom wall collision
                    if ball.rect.bottom >= SCREEN_HEIGHT:
                        if DEBUG:
                            ball.speed_y *= -1
                        else:
                            balls.remove(ball)
                    # Paddle collision
                    if ball.rect.colliderect(paddle.rect) and ball.speed_y > 0:
                        offset = (ball.rect.centerx - paddle.rect.centerx) / (PADDLE_WIDTH / 2)
                        angle_deg = offset * 80 + random.uniform(-5, 5)
                        final_angle_deg = max(-85, min(85, angle_deg))
                        angle_rad = math.radians(final_angle_deg - 90)
                        ball.speed_x = BALL_SPEED * math.cos(angle_rad)
                        ball.speed_y = BALL_SPEED * math.sin(angle_rad)

                    # Brick collision
                    for brick in bricks:
                        if brick.visible and ball.rect.colliderect(brick.rect):
                            brick.health -= 1
                            score += 10
                            if brick.health <= 0:
                                brick.visible = False
                            ball.speed_y *= -1 # Simple reflection
                            break

            # --- State Checks ---
            if not any(b.visible for b in bricks): # Stage win
                stage += 1
                screen.fill(BG_COLOR)
                win_text = font.render(f"Stage {stage-1} Clear!", True, TEXT_COLOR)
                screen.blit(win_text, (SCREEN_WIDTH/2 - win_text.get_width()/2, SCREEN_HEIGHT/2 - win_text.get_height()/2))
                pygame.display.flip()
                pygame.time.wait(2000)
                level_running = False # End level loop to start next stage

            if not balls and not DEBUG: # Game Over
                screen.fill(BG_COLOR)
                text = font.render("GAME OVER", True, TEXT_COLOR)
                subtext = small_font.render("Press 'R' to Restart or 'ESC' to Quit", True, TEXT_COLOR)
                screen.blit(text, (SCREEN_WIDTH/2 - text.get_width()/2, SCREEN_HEIGHT/2 - text.get_height()/2))
                screen.blit(subtext, (SCREEN_WIDTH/2 - subtext.get_width()/2, SCREEN_HEIGHT/2 + text.get_height()/2))
                pygame.display.flip()
                
                # Wait for player input
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                            main() # Restart
                            return

            # --- Drawing ---
            screen.fill(BG_COLOR)
            paddle.draw(screen)
            for ball in balls:
                ball.draw(screen)
            for brick in bricks:
                brick.draw(screen)
            
            score_text = small_font.render(f"Score: {score}", True, TEXT_COLOR)
            stage_text = small_font.render(f"Stage: {stage}", True, TEXT_COLOR)
            screen.blit(score_text, (10, 10))
            screen.blit(stage_text, (SCREEN_WIDTH - stage_text.get_width() - 10, 10))

            if DEBUG:
                debug_text = small_font.render("DEBUG MODE", True, (255, 0, 0))
                screen.blit(debug_text, (SCREEN_WIDTH / 2 - debug_text.get_width() / 2, 10))

            pygame.display.flip()
            clock.tick(60)

if __name__ == '__main__':
    main()
