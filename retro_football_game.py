import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Retro Football")

# Colors and Country Options
GREEN = (34, 139, 34)       
WHITE = (255, 255, 255)      
BLACK = (0, 0, 0)           
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
CONFETTI_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255), (255, 255, 255)]

COUNTRIES = {
    "Argentina": {"color": (137, 207, 240)},
    "Spain": {"color": RED, "text_color": YELLOW},
    "France": {"color": (0, 0, 255)}, 
    "England": {"color": WHITE, "text_color": RED},
    "Germany": {"color": BLACK, "text_color": RED},
    "Brazil": {"color": YELLOW, "text_color": GREEN}
}
country_list = list(COUNTRIES.keys())
player1_country_index = 0
player2_country_index = 1

# Player settings
PLAYER_RADIUS = 25
PLAYER_SPEED = 5
BALL_RADIUS = 15
BALL_INITIAL_SPEED = 7

# Fonts
font = pygame.font.Font(None, 36)

# Input box settings for countries
country_box1 = pygame.Rect(400, 320, 140, 40) 
country_box2 = pygame.Rect(400, 400, 140, 40) 

# Game Variables
score_player1 = 0
score_player2 = 0
ball_velocity = [BALL_INITIAL_SPEED, BALL_INITIAL_SPEED]
game_over = False
winning_score = 8
confetti_particles = []

# Game Mode
is_two_player = True

# AI Variables
ai_bounce_counter = 0  
ai_get_out_of_the_way = False  
ai_cooldown_timer = 0  

# Field Elements Dimensions
PENALTY_BOX_WIDTH = 150
PENALTY_BOX_HEIGHT = 300
GOAL_AREA_WIDTH = 80
GOAL_AREA_HEIGHT = 150

def draw_menu():
    screen.fill(GREEN)
    
    # Title at the top
    title_text = font.render("Retro Football", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))

    # Game Mode Selection
    mode_selection_text = font.render("Select Game Mode:", True, WHITE)
    screen.blit(mode_selection_text, (SCREEN_WIDTH // 2 - mode_selection_text.get_width() // 2, 150))

    # Options for game modes
    two_player_text = font.render("Two Player Mode: Press T", True, WHITE)
    solo_text = font.render("Solo Mode (vs. AI): Press S", True, WHITE)
    screen.blit(two_player_text, (SCREEN_WIDTH // 2 - two_player_text.get_width() // 2, 200))
    screen.blit(solo_text, (SCREEN_WIDTH // 2 - solo_text.get_width() // 2, 240))

    # Instructions for country selection
    instruction_text = font.render("Click on a country to toggle selection", True, WHITE)
    screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, 290))

    # P1 Country selection
    p1_text = font.render("P1 Country:", True, WHITE)
    screen.blit(p1_text, (country_box1.x - 140, country_box1.y + 10))  
    country_name1 = country_list[player1_country_index]
    country_color1 = COUNTRIES[country_name1]["color"]
    text_color1 = COUNTRIES[country_name1].get("text_color", WHITE)
    pygame.draw.rect(screen, country_color1, country_box1)
    country1_text = font.render(country_name1, True, text_color1)
    screen.blit(country1_text, (country_box1.x + 5, country_box1.y + 5))

    # P2 Country selection
    p2_text = font.render("P2 Country:", True, WHITE)
    screen.blit(p2_text, (country_box2.x - 140, country_box2.y + 10)) 
    country_name2 = country_list[player2_country_index]
    country_color2 = COUNTRIES[country_name2]["color"]
    text_color2 = COUNTRIES[country_name2].get("text_color", WHITE)
    pygame.draw.rect(screen, country_color2, country_box2)
    country2_text = font.render(country_name2, True, text_color2)
    screen.blit(country2_text, (country_box2.x + 5, country_box2.y + 5))

    # Start Game instructions
    start_text = font.render("Press ENTER to start", True, WHITE)
    screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 500))

def calculate_bounce(ball, player):
    """Calculate the bounce direction based on the angle of impact with the player."""
    dx = (ball.x + BALL_RADIUS) - (player.x + PLAYER_RADIUS)
    dy = (ball.y + BALL_RADIUS) - (player.y + PLAYER_RADIUS)
    distance = math.sqrt(dx**2 + dy**2)

    if distance != 0:
        dx /= distance
        dy /= distance

    speed = math.sqrt(ball_velocity[0]**2 + ball_velocity[1]**2)
    ball_velocity[0] = dx * speed
    ball_velocity[1] = dy * speed

def create_confetti():
    """Generate confetti particles to celebrate the winning moment."""
    for _ in range(100): 
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT // 2) 
        color = random.choice(CONFETTI_COLORS)
        speed_y = random.uniform(1, 3) 
        confetti_particles.append({"x": x, "y": y, "color": color, "speed_y": speed_y})

def draw_confetti():
    """Draw confetti particles."""
    for particle in confetti_particles:
        pygame.draw.circle(screen, particle["color"], (int(particle["x"]), int(particle["y"])), 5)
        particle["y"] += particle["speed_y"] 
        if particle["y"] > SCREEN_HEIGHT: 
            particle["y"] = random.randint(-20, SCREEN_HEIGHT // 2)
            particle["x"] = random.randint(0, SCREEN_WIDTH)
            particle["speed_y"] = random.uniform(1, 3)

def check_win():
    global game_over
    if score_player1 >= winning_score:
        display_winner("P1")
        game_over = True
        create_confetti()
    elif score_player2 >= winning_score:
        display_winner("P2")
        game_over = True
        create_confetti()

def display_winner(winner):
    win_text = font.render(f"{winner} Wins!", True, WHITE)
    restart_text = font.render("Press ENTER to restart or SPACE to go to menu", True, WHITE)
    screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
    pygame.display.flip()

def reset_game():
    global score_player1, score_player2, ball_velocity, game_over, confetti_particles, ai_bounce_counter, ai_get_out_of_the_way, ai_cooldown_timer
    score_player1 = 0
    score_player2 = 0
    ball_velocity = [BALL_INITIAL_SPEED, BALL_INITIAL_SPEED]
    game_over = False
    confetti_particles = []
    ai_bounce_counter = 0
    ai_get_out_of_the_way = False
    ai_cooldown_timer = 0

def game_loop():
    global score_player1, score_player2, ball_velocity, game_over, ai_bounce_counter, ai_get_out_of_the_way, ai_cooldown_timer
    player1_country = country_list[player1_country_index]
    player2_country = country_list[player2_country_index]
    player1_color = COUNTRIES[player1_country]["color"]
    player2_color = COUNTRIES[player2_country]["color"]

    player1 = pygame.Rect(100, SCREEN_HEIGHT // 2 - PLAYER_RADIUS, PLAYER_RADIUS * 2, PLAYER_RADIUS * 2)
    player2 = pygame.Rect(SCREEN_WIDTH - 100 - PLAYER_RADIUS * 2, SCREEN_HEIGHT // 2 - PLAYER_RADIUS, PLAYER_RADIUS * 2, PLAYER_RADIUS * 2)
    ball = pygame.Rect(SCREEN_WIDTH // 2 - BALL_RADIUS, SCREEN_HEIGHT // 2 - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)

    goal1 = pygame.Rect(0, SCREEN_HEIGHT // 2 - 75, 10, 150)
    goal2 = pygame.Rect(SCREEN_WIDTH - 10, SCREEN_HEIGHT // 2 - 75, 10, 150)

    penalty_box1 = pygame.Rect(0, SCREEN_HEIGHT // 2 - PENALTY_BOX_HEIGHT // 2, PENALTY_BOX_WIDTH, PENALTY_BOX_HEIGHT)
    penalty_box2 = pygame.Rect(SCREEN_WIDTH - PENALTY_BOX_WIDTH, SCREEN_HEIGHT // 2 - PENALTY_BOX_HEIGHT // 2, PENALTY_BOX_WIDTH, PENALTY_BOX_HEIGHT)

    goal_area1 = pygame.Rect(0, SCREEN_HEIGHT // 2 - GOAL_AREA_HEIGHT // 2, GOAL_AREA_WIDTH, GOAL_AREA_HEIGHT)
    goal_area2 = pygame.Rect(SCREEN_WIDTH - GOAL_AREA_WIDTH, SCREEN_HEIGHT // 2 - GOAL_AREA_HEIGHT // 2, GOAL_AREA_WIDTH, GOAL_AREA_HEIGHT)

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_RETURN:
                        reset_game()
                    elif event.key == pygame.K_SPACE:
                        return

        if game_over:
            screen.fill(GREEN)
            draw_confetti()
            display_winner("P1" if score_player1 >= winning_score else "P2")
            pygame.display.flip()
            clock.tick(60)
            continue

        # Player movement controls
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and player1.top > 0:
            player1.y -= PLAYER_SPEED
        if keys[pygame.K_s] and player1.bottom < SCREEN_HEIGHT:
            player1.y += PLAYER_SPEED
        if keys[pygame.K_a] and player1.left > 0:
            player1.x -= PLAYER_SPEED
        if keys[pygame.K_d] and player1.right < SCREEN_WIDTH // 2:
            player1.x += PLAYER_SPEED

        # AI control for solo mode with improved logic
        if not is_two_player and not game_over:
            if ai_get_out_of_the_way:
                # AI is in "get out of the way" mode
                if ai_cooldown_timer > 0:
                    ai_cooldown_timer -= 1
                    # Move AI to the top or bottom away from the ball
                    if player2.y > SCREEN_HEIGHT // 2:
                        player2.y += PLAYER_SPEED
                    else:
                        player2.y -= PLAYER_SPEED
                else:
                    ai_get_out_of_the_way = False
                    ai_bounce_counter = 0
            else:
                if ball.x > SCREEN_WIDTH // 2:  # Activate AI when ball is on its side
                    if ball.y < player2.y + PLAYER_RADIUS:
                        player2.y -= PLAYER_SPEED
                    elif ball.y > player2.y + PLAYER_RADIUS:
                        player2.y += PLAYER_SPEED
                # AI retreats if too close to the wall
                if player2.top <= 10:
                    player2.y += PLAYER_SPEED
                elif player2.bottom >= SCREEN_HEIGHT - 10:
                    player2.y -= PLAYER_SPEED

        elif is_two_player:  # Manual control for two-player mode
            if keys[pygame.K_UP] and player2.top > 0:
                player2.y -= PLAYER_SPEED
            if keys[pygame.K_DOWN] and player2.bottom < SCREEN_HEIGHT:
                player2.y += PLAYER_SPEED
            if keys[pygame.K_LEFT] and player2.left > SCREEN_WIDTH // 2:
                player2.x -= PLAYER_SPEED
            if keys[pygame.K_RIGHT] and player2.right < SCREEN_WIDTH:
                player2.x += PLAYER_SPEED

        # Ball movement
        ball.x += ball_velocity[0]
        ball.y += ball_velocity[1]

        # Ball collision with top and bottom walls
        if ball.top <= 0 or ball.bottom >= SCREEN_HEIGHT:
            ball_velocity[1] = -ball_velocity[1]

        # Ball collision with players
        if ball.colliderect(player1):
            calculate_bounce(ball, player1)
        elif ball.colliderect(player2) and not game_over:
            calculate_bounce(ball, player2)
            # Increment AI bounce counter when the ball collides with the AI player
            if not is_two_player:
                ai_bounce_counter += 1
                if ai_bounce_counter >= 4:
                    ai_get_out_of_the_way = True
                    ai_cooldown_timer = 60

        # Goal detection
        if not game_over and ball.colliderect(goal1):
            score_player2 += 1
            ball.x, ball.y = SCREEN_WIDTH // 2 - BALL_RADIUS, SCREEN_HEIGHT // 2 - BALL_RADIUS
            ball_velocity = [BALL_INITIAL_SPEED, BALL_INITIAL_SPEED]
            check_win()
        elif not game_over and ball.colliderect(goal2):
            score_player1 += 1
            ball.x, ball.y = SCREEN_WIDTH // 2 - BALL_RADIUS, SCREEN_HEIGHT // 2 - BALL_RADIUS
            ball_velocity = [-BALL_INITIAL_SPEED, BALL_INITIAL_SPEED]
            check_win()

        # Ball collision with left and right walls
        if ball.left <= 0 or ball.right >= SCREEN_WIDTH:
            ball_velocity[0] = -ball_velocity[0]

        # Drawing
        screen.fill(GREEN)
        pygame.draw.line(screen, WHITE, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 5)
        pygame.draw.circle(screen, WHITE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 60, 5)

        # Draw goal and penalty areas
        pygame.draw.rect(screen, WHITE, goal1)
        pygame.draw.rect(screen, WHITE, goal2)
        pygame.draw.rect(screen, WHITE, penalty_box1, 3)
        pygame.draw.rect(screen, WHITE, penalty_box2, 3)
        pygame.draw.rect(screen, WHITE, goal_area1, 3)
        pygame.draw.rect(screen, WHITE, goal_area2, 3)

        pygame.draw.circle(screen, player1_color, (player1.x + PLAYER_RADIUS, player1.y + PLAYER_RADIUS), PLAYER_RADIUS)
        pygame.draw.circle(screen, player2_color, (player2.x + PLAYER_RADIUS, player2.y + PLAYER_RADIUS), PLAYER_RADIUS)

        pygame.draw.circle(screen, WHITE, (ball.x + BALL_RADIUS, ball.y + BALL_RADIUS), BALL_RADIUS)
        for angle in range(0, 360, 60):
            hex_x = ball.x + BALL_RADIUS + int(BALL_RADIUS * 0.6 * math.cos(math.radians(angle)))
            hex_y = ball.y + BALL_RADIUS + int(BALL_RADIUS * 0.6 * math.sin(math.radians(angle)))
            pygame.draw.circle(screen, BLACK, (hex_x, hex_y), 5)

        score_text1 = font.render(f"P1 ({player1_country}): {score_player1}", True, WHITE)
        screen.blit(score_text1, (SCREEN_WIDTH // 4 - score_text1.get_width() // 2, 20))
        score_text2 = font.render(f"P2 ({player2_country}): {score_player2}", True, WHITE)
        screen.blit(score_text2, (3 * SCREEN_WIDTH // 4 - score_text2.get_width() // 2, 20))

        pygame.display.flip()
        clock.tick(60)

def main():
    global player1_country_index, player2_country_index, is_two_player
    while True:
        menu_active = True

        while menu_active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if country_box1.collidepoint(event.pos):
                        player1_country_index = (player1_country_index + 1) % len(country_list)
                    elif country_box2.collidepoint(event.pos):
                        player2_country_index = (player2_country_index + 1) % len(country_list)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        menu_active = False
                    elif event.key == pygame.K_t:
                        is_two_player = True
                    elif event.key == pygame.K_s:
                        is_two_player = False

            draw_menu()
            pygame.display.flip()

        game_loop()

if __name__ == "__main__":
    main()
