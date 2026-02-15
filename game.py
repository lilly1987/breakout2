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
TOTAL_BRICKS = 80 # Reduced for larger polygon bricks
BRICK_RADIUS = 25
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
    def __init__(self, center_x, center_y, radius, num_sides, base_color):
        self.center = (center_x, center_y)
        self.radius = radius # Radius of the circumcircle
        self.num_sides = num_sides
        self.base_color = base_color
        self.vertices = self._generate_vertices()
        # Bounding box for broad-phase collision detection
        min_x = min(v[0] for v in self.vertices)
        max_x = max(v[0] for v in self.vertices)
        min_y = min(v[1] for v in self.vertices)
        max_y = max(v[1] for v in self.vertices)
        self.rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
        
        self.visible = True
        self.health = 1
        self.max_health = 1

    def _generate_vertices(self):
        vertices = []
        # Start angle rotated by half a step to make shapes like triangles and hexagons flat on top
        start_angle = -90 - (180 / self.num_sides) if self.num_sides % 2 == 0 else -90
        for i in range(self.num_sides):
            angle = math.radians(i * (360 / self.num_sides) + start_angle)
            x = self.center[0] + self.radius * math.cos(angle)
            y = self.center[1] + self.radius * math.sin(angle)
            vertices.append((x, y))
        return vertices

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
            pygame.draw.polygon(screen, self.get_color(), self.vertices)

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
            # Try to place a brick, but give up after a few tries to avoid infinite loops
            for _ in range(20): # More retries for better packing
                center_x = random.randint(BRICK_RADIUS, SCREEN_WIDTH - BRICK_RADIUS)
                center_y = random.randint(50 + BRICK_RADIUS, int(SCREEN_HEIGHT / 1.8))
                num_sides = random.randint(3, 8)
                color = random.choice(BRICK_COLORS)
                
                new_brick = Brick(center_x, center_y, BRICK_RADIUS, num_sides, color)

                # Prevent overlap using bounding boxes for simplicity
                is_overlapping = any(new_brick.rect.colliderect(b.rect) for b in bricks)
                if not is_overlapping:
                    bricks.append(new_brick)
                    break

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
                    
                    v = (ball.speed_x, ball.speed_y)
                    reflected = False

                    # --- Wall Collision using Reflection ---
                    if ball.rect.left <= 0:
                        n = (1, 0)
                        dot = v[0]*n[0] + v[1]*n[1]
                        v = (v[0] - 2*dot*n[0], v[1] - 2*dot*n[1])
                        ball.rect.left = 0
                        reflected = True
                    elif ball.rect.right >= SCREEN_WIDTH:
                        n = (-1, 0)
                        dot = v[0]*n[0] + v[1]*n[1]
                        v = (v[0] - 2*dot*n[0], v[1] - 2*dot*n[1])
                        ball.rect.right = SCREEN_WIDTH
                        reflected = True

                    if ball.rect.top <= 0:
                        n = (0, 1)
                        dot = v[0]*n[0] + v[1]*n[1]
                        v = (v[0] - 2*dot*n[0], v[1] - 2*dot*n[1])
                        ball.rect.top = 0
                        reflected = True
                    elif ball.rect.bottom >= SCREEN_HEIGHT:
                        if DEBUG:
                            n = (0, -1)
                            dot = v[0]*n[0] + v[1]*n[1]
                            v = (v[0] - 2*dot*n[0], v[1] - 2*dot*n[1])
                            ball.rect.bottom = SCREEN_HEIGHT
                            reflected = True
                        else:
                            balls.remove(ball)
                            continue
                    
                    if reflected:
                        ball.speed_x, ball.speed_y = v
                        ball.speed += 0.2
                        ball.normalize_speed()
                        # After wall collision, skip other collision checks for this frame
                        continue

                    # --- Paddle Collision (Special Gameplay Logic) ---
                    if ball.rect.colliderect(paddle.rect) and ball.speed_y > 0:
                        ball.speed += 0.2
                        offset = (ball.rect.centerx - paddle.rect.centerx) / (PADDLE_WIDTH / 2)
                        angle_deg = offset * 80
                        final_angle_deg = max(-80, min(80, angle_deg))
                        angle_rad = math.radians(final_angle_deg - 90)
                        ball.speed_x = ball.speed * math.cos(angle_rad)
                        ball.speed_y = ball.speed * math.sin(angle_rad)
                        ball.normalize_speed()
                        # After paddle collision, skip other collision checks for this frame
                        continue

                    # --- Brick Collision using Reflection ---
                    collided_brick = None
                    for brick in bricks:
                        if brick.visible and ball.rect.colliderect(brick.rect):
                            collided_brick = brick
                            break
                    
                    if collided_brick:
                        brick = collided_brick
                        
                        # Find the closest point on the brick to the ball's center
                        closest_x = max(brick.rect.left, min(ball.rect.centerx, brick.rect.right))
                        closest_y = max(brick.rect.top, min(ball.rect.centery, brick.rect.bottom))

                        # Calculate normal vector from closest point to ball center
                        nx = ball.rect.centerx - closest_x
                        ny = ball.rect.centery - closest_y
                        
                        dist = math.sqrt(nx**2 + ny**2)

                        # Reposition the ball to be just outside the brick to prevent sticking.
                        # This is a critical step for robust collision.
                        if dist < ball.radius:
                            overlap = ball.radius - dist + 1 # +1 for a small nudge
                            # Move ball back along its path to the point of collision
                            speed_magnitude = math.sqrt(ball.speed_x**2 + ball.speed_y**2)
                            if speed_magnitude > 0:
                                ball.rect.x -= (ball.speed_x / speed_magnitude) * overlap
                                ball.rect.y -= (ball.speed_y / speed_magnitude) * overlap

                        # Re-calculate closest point and normal after repositioning for accuracy
                        closest_x = max(brick.rect.left, min(ball.rect.centerx, brick.rect.right))
                        closest_y = max(brick.rect.top, min(ball.rect.centery, brick.rect.bottom))
                        nx = ball.rect.centerx - closest_x
                        ny = ball.rect.centery - closest_y
                        dist = math.sqrt(nx**2 + ny**2)

                        # Normalize the normal vector
                        if dist != 0:
                            nx /= dist
                            ny /= dist
                        else: # Fallback if ball center is exactly on the closest point
                            nx, ny = (0, -1)

                        # Reflect velocity using the calculated normal
                        v = (ball.speed_x, ball.speed_y)
                        dot_product = v[0] * nx + v[1] * ny
                        ball.speed_x = v[0] - 2 * dot_product * nx
                        ball.speed_y = v[1] - 2 * dot_product * ny

                        ball.normalize_speed()

                        brick.health -= 1
                        score += 10
                        if brick.health <= 0: brick.visible = False

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
