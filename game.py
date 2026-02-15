import pygame
import random
import math

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
BRICK_WIDTH = 40
BRICK_HEIGHT = 20
BRICK_GAP = 1
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
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.visible = True

    def draw(self, screen):
        if self.visible:
            pygame.draw.rect(screen, self.color, self.rect)

# --- Main Game Function ---

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Breakout Game")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 36)

    # Create game objects
    paddle = Paddle((SCREEN_WIDTH - PADDLE_WIDTH) / 2, PADDLE_Y_POS, PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_COLOR)

    bricks = []
    for row in range(BRICK_ROWS):
        for col in range(BRICK_COLS):
            brick_x = col * (BRICK_WIDTH + BRICK_GAP) + (BRICK_GAP / 2)
            brick_y = row * (BRICK_HEIGHT + BRICK_GAP) + 50
            color = BRICK_COLORS[row % len(BRICK_COLORS)]
            bricks.append(Brick(brick_x, brick_y, BRICK_WIDTH, BRICK_HEIGHT, color))

    balls = []
    ball_on_paddle = True
    num_balls = 16 if DEBUG else 1
    for _ in range(num_balls):
        ball = Ball(paddle.rect.centerx, paddle.rect.top - BALL_RADIUS, BALL_RADIUS, BALL_COLOR, 0, 0)
        balls.append(ball)

    score = 0
    running = True
    game_over = False
    win = False

    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEMOTION:
                paddle.move(event.pos[0] - PADDLE_WIDTH / 2)
            
            # Restart game
            if (game_over or win) and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                main()
                return

            # Launch ball
            if ball_on_paddle:
                if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                    ball_on_paddle = False
                    for ball in balls:
                        ball.speed_y = -BALL_SPEED # Launch straight up

        if not game_over and not win:
            if ball_on_paddle:
                # Keep all balls centered on the paddle
                for ball in balls:
                    ball.rect.centerx = paddle.rect.centerx
                    ball.rect.bottom = paddle.rect.top
            else:
                # --- Game Logic ---
                for ball in balls[:]: # Iterate over a copy
                    ball.move()

                    # Ball collision with walls
                    if ball.rect.left <= 0 or ball.rect.right >= SCREEN_WIDTH:
                        ball.speed_x *= -1
                    if ball.rect.top <= 0:
                        ball.speed_y *= -1
                    
                    # Ball collision with bottom wall
                    if ball.rect.bottom >= SCREEN_HEIGHT:
                        if DEBUG:
                            ball.speed_y *= -1 # Bounce in debug mode
                        else:
                            balls.remove(ball)
                            if not balls:
                                game_over = True

                    # Ball collision with paddle
                    if ball.rect.colliderect(paddle.rect) and ball.speed_y > 0:
                        
                        # Advanced reflection calculation
                        offset = (ball.rect.centerx - paddle.rect.centerx) / (PADDLE_WIDTH / 2)
                        angle_deg = offset * 80 # -80 to 80 degrees
                        
                        random_deviation = random.uniform(-5, 5)
                        final_angle_deg = angle_deg + random_deviation
                        
                        # Clamp to prevent extreme horizontal angles
                        final_angle_deg = max(-85, min(85, final_angle_deg))

                        angle_rad = math.radians(final_angle_deg - 90) # Adjust for pygame's coordinate system
                        
                        ball.speed_x = BALL_SPEED * math.cos(angle_rad)
                        ball.speed_y = BALL_SPEED * math.sin(angle_rad)




                    # Ball collision with bricks
                    for brick in bricks:
                        if brick.visible and ball.rect.colliderect(brick.rect):
                            brick.visible = False
                            # A small push to prevent getting stuck
                            if abs(ball.rect.bottom - brick.rect.top) < 5 and ball.speed_y > 0:
                                ball.speed_y *= -1
                            elif abs(ball.rect.top - brick.rect.bottom) < 5 and ball.speed_y < 0:
                                ball.speed_y *= -1
                            elif abs(ball.rect.right - brick.rect.left) < 5 and ball.speed_x > 0:
                                ball.speed_x *= -1
                            elif abs(ball.rect.left - brick.rect.right) < 5 and ball.speed_x < 0:
                                ball.speed_x *= -1
                            else: # Default reflection
                                ball.speed_y *= -1

                            score += 10
                            break 

                # Check for win condition
                if not any(b.visible for b in bricks):
                    win = True

        # --- Drawing ---
        screen.fill(BG_COLOR)
        paddle.draw(screen)
        for ball in balls:
            ball.draw(screen)
        for brick in bricks:
            brick.draw(screen)

        # Draw score
        score_text = small_font.render(f"Score: {score}", True, TEXT_COLOR)
        screen.blit(score_text, (10, 10))
        if DEBUG:
            debug_text = small_font.render("DEBUG MODE", True, (255, 0, 0))
            screen.blit(debug_text, (SCREEN_WIDTH - debug_text.get_width() - 10, 10))

        if game_over:
            text = font.render("GAME OVER", True, TEXT_COLOR)
            subtext = small_font.render("Press 'R' to Restart", True, TEXT_COLOR)
            screen.blit(text, (SCREEN_WIDTH/2 - text.get_width()/2, SCREEN_HEIGHT/2 - text.get_height()/2))
            screen.blit(subtext, (SCREEN_WIDTH/2 - subtext.get_width()/2, SCREEN_HEIGHT/2 + text.get_height()/2))

        if win:
            text = font.render("YOU WIN!", True, TEXT_COLOR)
            subtext = small_font.render("Press 'R' to Restart", True, TEXT_COLOR)
            screen.blit(text, (SCREEN_WIDTH/2 - text.get_width()/2, SCREEN_HEIGHT/2 - text.get_height()/2))
            screen.blit(subtext, (SCREEN_WIDTH/2 - subtext.get_width()/2, SCREEN_HEIGHT/2 + text.get_height()/2))


        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    main()
