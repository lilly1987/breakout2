import pygame
import random
import math
import sys

# --- Constants ---
DEBUG = True # Set to True to test with 16 balls
DEBUG_balls = 32

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
TOTAL_BRICKS = 200
BRICK_WIDTH = 50
BRICK_HEIGHT = 15
BRICK_COLORS = [(255, 99, 71), (255, 165, 0), (255, 215, 0), (50, 205, 50), (65, 105, 225)]

# --- Game Classes ---

class Ball:
    def __init__(self, x, y, radius, color, speed_x, speed_y):
        self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
        self.color = color
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.radius = radius
        self.speed = BALL_SPEED

    def move(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

    def normalize_speed(self):
        MIN_VERTICAL_RATIO = 0.1 # Prevent angle from being too horizontal
        min_y_speed = self.speed * MIN_VERTICAL_RATIO
        
        if abs(self.speed_y) < min_y_speed:
            if self.speed_y >= 0: # If 0, will become positive
                self.speed_y = min_y_speed
            else:
                self.speed_y = -min_y_speed

        current_speed = math.sqrt(self.speed_x**2 + self.speed_y**2)
        if current_speed > 0:
            scale = self.speed / current_speed
            self.speed_x *= scale
            self.speed_y *= scale

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
        if self.health <= 1 and self.health == self.max_health:
            return self.base_color
        if self.health > 1:
            factor = (self.health - 1) / max(self.max_health - 1, 1)
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
        
        # Create random bricks
        bricks = []
        for _ in range(TOTAL_BRICKS):
            brick_x = random.randint(0, SCREEN_WIDTH - BRICK_WIDTH)
            brick_y = random.randint(50, int(SCREEN_HEIGHT / 2))
            color = random.choice(BRICK_COLORS)
            new_brick = Brick(brick_x, brick_y, BRICK_WIDTH, BRICK_HEIGHT, color)
            # Prevent overlap
            is_overlapping = any(new_brick.rect.colliderect(b.rect) for b in bricks)
            if not is_overlapping:
                 bricks.append(new_brick)

        # Add health to bricks based on stage
        if stage > 1 and bricks:
            num_upgrades = int(len(bricks) * 0.1)
            for _ in range(stage - 1):
                 for _ in range(num_upgrades):
                    brick_to_upgrade = random.choice(bricks)
                    brick_to_upgrade.health += 1
                    brick_to_upgrade.max_health = max(brick_to_upgrade.max_health, brick_to_upgrade.health)

        # Create balls
        balls = []
        ball_on_paddle = True
        num_balls = DEBUG_balls if DEBUG else 1
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
                        main() 
                        return

                # Launch ball
                if ball_on_paddle:
                    if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                        ball_on_paddle = False
                        for ball in balls:
                            ball.speed_y = -ball.speed 

            # --- Game Logic ---
            if ball_on_paddle:
                for ball in balls:
                    ball.rect.centerx = paddle.rect.centerx
                    ball.rect.bottom = paddle.rect.top
            else:
                for ball in balls[:]:
                    ball.move()
                    
                    # Wall collision
                    if ball.rect.left <= 0 or ball.rect.right >= SCREEN_WIDTH:
                        ball.speed += 0.2
                        ball.speed_x *= -1
                        ball.normalize_speed()
                    if ball.rect.top <= 0:
                        ball.speed += 0.2
                        ball.speed_y *= -1
                        ball.normalize_speed()
                    if ball.rect.bottom >= SCREEN_HEIGHT:
                        if DEBUG:
                            ball.speed += 0.2
                            ball.speed_y *= -1
                            ball.normalize_speed()
                        else:
                            balls.remove(ball)
                    
                    # Paddle collision
                    if ball.rect.colliderect(paddle.rect) and ball.speed_y > 0:
                        ball.speed += 0.2
                        offset = (ball.rect.centerx - paddle.rect.centerx) / (PADDLE_WIDTH / 2)
                        angle_deg = offset * 80
                        final_angle_deg = max(-80, min(80, angle_deg))
                        angle_rad = math.radians(final_angle_deg - 90)
                        ball.speed_x = ball.speed * math.cos(angle_rad)
                        ball.speed_y = ball.speed * math.sin(angle_rad)
                        ball.normalize_speed()
                    
                    # Brick collision
                    for brick in bricks:
                        if brick.visible and ball.rect.colliderect(brick.rect):
                            
                            # Determine collision type based on ball's center relative to brick's slabs
                            ball_cx, ball_cy = ball.rect.center
                            brick_left, brick_right = brick.rect.left, brick.rect.right
                            brick_top, brick_bottom = brick.rect.top, brick.rect.bottom

                            in_horiz_slab = brick_left < ball_cx < brick_right
                            in_vert_slab = brick_top < ball_cy < brick_bottom

                            # Store previous direction to handle repositioning
                            moving_down = ball.speed_y > 0
                            moving_right = ball.speed_x > 0

                            if in_horiz_slab:
                                # Top or bottom collision
                                ball.speed_y *= -1
                                if moving_down:
                                    ball.rect.bottom = brick.rect.top
                                else:
                                    ball.rect.top = brick.rect.bottom
                            elif in_vert_slab:
                                # Left or right collision
                                ball.speed_x *= -1
                                if moving_right:
                                    ball.rect.right = brick.rect.left
                                else:
                                    ball.rect.left = brick.rect.right
                            else:
                                # Corner collision
                                ball.speed_y *= -1
                                ball.speed_x *= -1
                                # Simple repositioning for corners
                                if moving_down:
                                    ball.rect.bottom = brick.rect.top
                                else:
                                    ball.rect.top = brick.rect.bottom
                                if moving_right:
                                    ball.rect.right = brick.rect.left
                                else:
                                    ball.rect.left = brick.rect.right
                            
                            ball.normalize_speed()
                            brick.health -= 1
                            score += 10
                            if brick.health <= 0: brick.visible = False
                            break

            # --- State Checks ---
            if not any(b.visible for b in bricks):
                stage += 1
                screen.fill(BG_COLOR)
                win_text = font.render(f"Stage {stage-1} Clear!", True, TEXT_COLOR)
                screen.blit(win_text, (win_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))))
                pygame.display.flip()
                pygame.time.wait(2000)
                level_running = False 

            if not balls and not DEBUG:
                screen.fill(BG_COLOR)
                text = font.render("GAME OVER", True, TEXT_COLOR)
                subtext = small_font.render("Press 'R' to Restart or 'ESC' to Quit", True, TEXT_COLOR)
                screen.blit(text, (text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 20))))
                screen.blit(subtext, (subtext.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 20))))
                pygame.display.flip()
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                            main()
                            return

            # --- Drawing ---
            screen.fill(BG_COLOR)
            paddle.draw(screen)
            for ball in balls: ball.draw(screen)
            for brick in bricks: brick.draw(screen)
            
            remaining_bricks = sum(1 for b in bricks if b.visible)
            
            score_text = small_font.render(f"Score: {score}", True, TEXT_COLOR)
            stage_text = small_font.render(f"Stage: {stage}", True, TEXT_COLOR)
            bricks_text = small_font.render(f"Bricks: {remaining_bricks}", True, TEXT_COLOR)
            
            screen.blit(score_text, (10, 10))
            screen.blit(bricks_text, (10, 40))
            screen.blit(stage_text, (SCREEN_WIDTH - stage_text.get_width() - 10, 10))

            if DEBUG:
                debug_text = small_font.render("DEBUG MODE", True, (255, 0, 0))
                screen.blit(debug_text, (debug_text.get_rect(centerx=SCREEN_WIDTH/2)))

            pygame.display.flip()
            clock.tick(60)

if __name__ == '__main__':
    main()
