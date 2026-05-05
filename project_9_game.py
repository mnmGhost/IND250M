import pygame
import random
import math
import os
import sys

pygame.init()

WIDTH = 1000
HEIGHT = 650
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sports Skill Challenge")

clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GRAY = (160, 160, 160)
DARK_GRAY = (70, 70, 70)
GREEN = (60, 180, 80)
RED = (220, 70, 70)
BLUE = (70, 120, 230)
ORANGE = (240, 150, 50)
YELLOW = (240, 220, 70)
PURPLE = (150, 80, 220)
CYAN = (70, 220, 220)

font_big = pygame.font.SysFont("arial", 54, bold=True)
font_medium = pygame.font.SysFont("arial", 32, bold=True)
font_small = pygame.font.SysFont("arial", 22)
font_tiny = pygame.font.SysFont("arial", 18)

total_score = 0
message = "Choose an unlocked sport to play!"

ASSET_FOLDER = "assets"


sports = {
    "Soccer": {"unlock": 0, "win": 100, "lose": -30, "color": GREEN},
    "Basketball": {"unlock": 300, "win": 120, "lose": -40, "color": ORANGE},
    "Ping Pong": {"unlock": 650, "win": 150, "lose": -60, "color": CYAN},
    "Hockey": {"unlock": 1100, "win": 180, "lose": -80, "color": BLUE},
    "Baseball": {"unlock": 1700, "win": 220, "lose": -100, "color": YELLOW},
    "Track": {"unlock": 2500, "win": 250, "lose": -120, "color": PURPLE},
    "Extreme Dodgeball": {"unlock": 3500, "win": 500, "lose": -300, "color": RED}
}


def draw_text(text, font, color, x, y, center=True):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()

    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)

    screen.blit(text_surface, text_rect)


def load_sprite(filename, size, fallback_color):
    path = os.path.join(ASSET_FOLDER, filename)

    if os.path.exists(path):
        image = pygame.image.load(path).convert_alpha()
        image = pygame.transform.scale(image, size)
        return image

    image = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.ellipse(image, fallback_color, image.get_rect())
    pygame.draw.ellipse(image, BLACK, image.get_rect(), 3)
    return image


def countdown():
    for number in ["3", "2", "1", "GO!"]:
        start_time = pygame.time.get_ticks()

        while pygame.time.get_ticks() - start_time < 800:
            clock.tick(FPS)
            screen.fill((235, 240, 250))

            draw_text(number, font_big, BLACK, WIDTH // 2, HEIGHT // 2)
            draw_text("Get ready!", font_medium, DARK_GRAY, WIDTH // 2, HEIGHT // 2 + 70)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return False

            pygame.display.update()

    return True


def apply_score(points):
    global total_score

    total_score += points

    if total_score < 0:
        total_score = 0


def show_result(title, points):
    global message

    if points > 0:
        message = f"{title} won! You gained {points} points!"
    else:
        message = f"{title} lost! You lost {abs(points)} points!"

    apply_score(points)


def return_to_menu_text():
    draw_text("Press ESC to return to menu", font_small, BLACK, WIDTH // 2, HEIGHT - 30)


def soccer_game():
    if not countdown():
        return

    ball_img = load_sprite("soccer_ball.png", (40, 40), WHITE)
    goalie_img = load_sprite("goalie.png", (45, 130), RED)

    ball_rect = ball_img.get_rect(center=(100, HEIGHT // 2))
    goalie_rect = goalie_img.get_rect(center=(WIDTH - 150, HEIGHT // 2))
    goal_rect = pygame.Rect(WIDTH - 80, HEIGHT // 2 - 120, 40, 240)

    angle = 0
    power = 0
    power_direction = 1
    goalie_speed = 3
    shot = False
    ball_speed_x = 0
    ball_speed_y = 0

    while True:
        clock.tick(FPS)
        screen.fill((70, 180, 90))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

                if event.key == pygame.K_SPACE and not shot:
                    shot = True
                    ball_speed_x = 9 + power / 12
                    ball_speed_y = math.sin(math.radians(angle)) * 8

        keys = pygame.key.get_pressed()

        if not shot:
            if keys[pygame.K_UP]:
                angle -= 2
            if keys[pygame.K_DOWN]:
                angle += 2

            angle = max(-45, min(45, angle))

            power += power_direction * 2

            if power >= 100 or power <= 0:
                power_direction *= -1

        goalie_rect.y += goalie_speed

        if goalie_rect.top < 180 or goalie_rect.bottom > 470:
            goalie_speed *= -1

        if shot:
            ball_rect.x += ball_speed_x
            ball_rect.y += ball_speed_y

            if ball_rect.colliderect(goalie_rect):
                show_result("Soccer", sports["Soccer"]["lose"])
                return

            if ball_rect.colliderect(goal_rect):
                show_result("Soccer", sports["Soccer"]["win"])
                return

            if ball_rect.left > WIDTH or ball_rect.bottom < 0 or ball_rect.top > HEIGHT:
                show_result("Soccer", sports["Soccer"]["lose"])
                return

        pygame.draw.rect(screen, WHITE, goal_rect)
        pygame.draw.rect(screen, BLACK, goal_rect, 3)

        screen.blit(goalie_img, goalie_rect)
        screen.blit(ball_img, ball_rect)

        if not shot:
            aim_x = ball_rect.centerx + math.cos(math.radians(angle)) * 80
            aim_y = ball_rect.centery + math.sin(math.radians(angle)) * 80
            pygame.draw.line(screen, BLACK, ball_rect.center, (aim_x, aim_y), 4)

            pygame.draw.rect(screen, BLACK, (40, 40, 220, 25), 3)
            pygame.draw.rect(screen, ORANGE, (40, 40, int(power * 2.2), 25))

        draw_text("Soccer: Shoot past the goalie!", font_medium, BLACK, WIDTH // 2, 90)
        draw_text("UP/DOWN = Aim | SPACE = Kick", font_small, BLACK, WIDTH // 2, 130)
        return_to_menu_text()

        pygame.display.update()


def basketball_game():
    if not countdown():
        return

    ball_img = load_sprite("basketball.png", (70, 70), ORANGE)

    meter_x = WIDTH // 2 - 200
    meter_y = HEIGHT // 2
    meter_w = 400
    meter_h = 40

    marker_x = meter_x
    marker_speed = 8
    green_zone = pygame.Rect(WIDTH // 2 - 45, meter_y, 90, meter_h)

    while True:
        clock.tick(FPS)
        screen.fill((230, 190, 120))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

                if event.key == pygame.K_SPACE:
                    if green_zone.collidepoint(marker_x, meter_y + 20):
                        show_result("Basketball", sports["Basketball"]["win"])
                    else:
                        show_result("Basketball", sports["Basketball"]["lose"])
                    return

        marker_x += marker_speed

        if marker_x < meter_x or marker_x > meter_x + meter_w:
            marker_speed *= -1

        draw_text("Basketball: Stop the marker in the green zone!", font_medium, BLACK, WIDTH // 2, 120)
        draw_text("Press SPACE to shoot", font_small, BLACK, WIDTH // 2, 170)

        pygame.draw.rect(screen, RED, (meter_x, meter_y, meter_w, meter_h))
        pygame.draw.rect(screen, GREEN, green_zone)
        pygame.draw.rect(screen, BLACK, (meter_x, meter_y, meter_w, meter_h), 4)

        pygame.draw.circle(screen, ORANGE, (marker_x, meter_y + 20), 18)
        pygame.draw.circle(screen, BLACK, (marker_x, meter_y + 20), 18, 3)

        pygame.draw.rect(screen, BLACK, (WIDTH // 2 - 70, 300, 140, 20))
        screen.blit(ball_img, ball_img.get_rect(center=(WIDTH // 2, 250)))

        return_to_menu_text()
        pygame.display.update()


def ping_pong_game():
    if not countdown():
        return

    paddle_img = load_sprite("paddle.png", (30, 120), BLUE)
    ball_img = load_sprite("ping_pong_ball.png", (25, 25), WHITE)

    paddle_rect = paddle_img.get_rect(topleft=(60, HEIGHT // 2 - 60))
    ball_rect = ball_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    ball_speed_x = -7
    ball_speed_y = random.choice([-5, 5])
    hits = 0
    needed_hits = 5

    while True:
        clock.tick(FPS)
        screen.fill((40, 120, 140))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            paddle_rect.y -= 8
        if keys[pygame.K_DOWN]:
            paddle_rect.y += 8

        paddle_rect.y = max(0, min(HEIGHT - paddle_rect.height, paddle_rect.y))

        ball_rect.x += ball_speed_x
        ball_rect.y += ball_speed_y

        if ball_rect.top <= 0 or ball_rect.bottom >= HEIGHT:
            ball_speed_y *= -1

        if ball_rect.colliderect(paddle_rect):
            ball_speed_x *= -1
            hits += 1

        if ball_rect.right >= WIDTH:
            ball_speed_x *= -1

        if ball_rect.left <= 0:
            show_result("Ping Pong", sports["Ping Pong"]["lose"])
            return

        if hits >= needed_hits:
            show_result("Ping Pong", sports["Ping Pong"]["win"])
            return

        screen.blit(paddle_img, paddle_rect)
        screen.blit(ball_img, ball_rect)

        draw_text("Ping Pong: Return the ball 5 times!", font_medium, WHITE, WIDTH // 2, 60)
        draw_text(f"Hits: {hits}/{needed_hits}", font_medium, WHITE, WIDTH // 2, 110)
        draw_text("Use UP and DOWN to move", font_small, WHITE, WIDTH // 2, 150)

        return_to_menu_text()
        pygame.display.update()


def hockey_game():
    if not countdown():
        return

    player_img = load_sprite("hockey_player.png", (50, 70), RED)
    puck_img = load_sprite("puck.png", (28, 28), BLACK)

    player_rect = player_img.get_rect(center=(100, HEIGHT // 2))
    puck_rect = puck_img.get_rect(center=(160, HEIGHT // 2))

    defenders = [
        pygame.Rect(450, 120, 30, 120),
        pygame.Rect(600, 410, 30, 120)
    ]

    defender_speeds = [5, -5]
    goal = pygame.Rect(WIDTH - 80, HEIGHT // 2 - 90, 40, 180)

    shot = False
    puck_speed = 0

    while True:
        clock.tick(FPS)
        screen.fill((180, 230, 255))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

                if event.key == pygame.K_SPACE and not shot:
                    shot = True
                    puck_speed = 12

        keys = pygame.key.get_pressed()

        if not shot:
            if keys[pygame.K_UP]:
                player_rect.y -= 6
                puck_rect.y -= 6

            if keys[pygame.K_DOWN]:
                player_rect.y += 6
                puck_rect.y += 6

            player_rect.y = max(0, min(HEIGHT - player_rect.height, player_rect.y))
            puck_rect.y = max(0, min(HEIGHT - puck_rect.height, puck_rect.y))

        for i, defender in enumerate(defenders):
            defender.y += defender_speeds[i]

            if defender.top <= 0 or defender.bottom >= HEIGHT:
                defender_speeds[i] *= -1

        if shot:
            puck_rect.x += puck_speed

            for defender in defenders:
                if puck_rect.colliderect(defender):
                    show_result("Hockey", sports["Hockey"]["lose"])
                    return

            if puck_rect.colliderect(goal):
                show_result("Hockey", sports["Hockey"]["win"])
                return

            if puck_rect.left > WIDTH:
                show_result("Hockey", sports["Hockey"]["lose"])
                return

        pygame.draw.rect(screen, BLUE, goal)
        pygame.draw.rect(screen, BLACK, goal, 3)

        for defender in defenders:
            pygame.draw.rect(screen, PURPLE, defender)
            pygame.draw.rect(screen, BLACK, defender, 3)

        screen.blit(player_img, player_rect)
        screen.blit(puck_img, puck_rect)

        draw_text("Hockey: Shoot through the defenders!", font_medium, BLACK, WIDTH // 2, 60)
        draw_text("UP/DOWN = Aim | SPACE = Shoot", font_small, BLACK, WIDTH // 2, 105)

        return_to_menu_text()
        pygame.display.update()


def baseball_game():
    if not countdown():
        return

    ball_img = load_sprite("baseball.png", (35, 35), WHITE)
    bat_img = load_sprite("bat.png", (45, 160), ORANGE)

    pitch_rect = ball_img.get_rect(center=(WIDTH - 100, HEIGHT // 2))
    pitch_speed = -8

    bat_zone = pygame.Rect(170, HEIGHT // 2 - 80, 50, 160)
    bat_rect = bat_img.get_rect(center=(170, HEIGHT // 2))

    while True:
        clock.tick(FPS)
        screen.fill((110, 190, 90))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

                if event.key == pygame.K_SPACE:
                    if pitch_rect.colliderect(bat_zone):
                        show_result("Baseball", sports["Baseball"]["win"])
                    else:
                        show_result("Baseball", sports["Baseball"]["lose"])
                    return

        pitch_rect.x += pitch_speed

        if pitch_rect.right < 0:
            show_result("Baseball", sports["Baseball"]["lose"])
            return

        pygame.draw.rect(screen, ORANGE, bat_zone)
        pygame.draw.rect(screen, BLACK, bat_zone, 3)

        screen.blit(bat_img, bat_rect)
        screen.blit(ball_img, pitch_rect)

        draw_text("Baseball: Swing when the ball is in the orange zone!", font_medium, BLACK, WIDTH // 2, 90)
        draw_text("Press SPACE to swing", font_small, BLACK, WIDTH // 2, 135)

        return_to_menu_text()
        pygame.display.update()


def track_game():
    if not countdown():
        return

    runner_img = load_sprite("runner.png", (50, 70), RED)

    player_rect = runner_img.get_rect(topleft=(80, HEIGHT - 130))
    ground_y = HEIGHT - 60

    velocity_y = 0
    gravity = 0.8
    jumping = False

    obstacles = []
    spawn_timer = 0
    survived_time = 0
    target_time = 12

    while True:
        clock.tick(FPS)
        screen.fill((120, 200, 255))

        survived_time += 1 / FPS
        spawn_timer += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

                if event.key == pygame.K_SPACE and not jumping:
                    velocity_y = -15
                    jumping = True

        if spawn_timer > 90:
            spawn_timer = 0
            obstacles.append(pygame.Rect(WIDTH, ground_y - 45, 35, 45))

        player_rect.y += velocity_y
        velocity_y += gravity

        if player_rect.bottom >= ground_y:
            player_rect.bottom = ground_y
            jumping = False
            velocity_y = 0

        for obstacle in obstacles[:]:
            obstacle.x -= 8

            if obstacle.right < 0:
                obstacles.remove(obstacle)

            if player_rect.colliderect(obstacle):
                show_result("Track", sports["Track"]["lose"])
                return

        if survived_time >= target_time:
            show_result("Track", sports["Track"]["win"])
            return

        pygame.draw.rect(screen, GREEN, (0, ground_y, WIDTH, HEIGHT - ground_y))
        screen.blit(runner_img, player_rect)

        for obstacle in obstacles:
            pygame.draw.rect(screen, BLACK, obstacle)

        draw_text("Track: Jump over hurdles for 12 seconds!", font_medium, BLACK, WIDTH // 2, 70)
        draw_text("Press SPACE to jump", font_small, BLACK, WIDTH // 2, 115)
        draw_text(f"Time: {survived_time:.1f}/{target_time}", font_medium, BLACK, WIDTH // 2, 160)

        return_to_menu_text()
        pygame.display.update()


def dodgeball_game():
    if not countdown():
        return

    player_img = load_sprite("player.png", (55, 70), BLUE)
    ball_img = load_sprite("dodgeball.png", (35, 35), RED)

    player_rect = player_img.get_rect(center=(100, HEIGHT // 2))
    balls = []

    spawn_timer = 0
    survived_time = 0
    target_time = 10

    while True:
        clock.tick(FPS)
        screen.fill((250, 230, 230))

        survived_time += 1 / FPS
        spawn_timer += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            player_rect.y -= 7
        if keys[pygame.K_DOWN]:
            player_rect.y += 7
        if keys[pygame.K_LEFT]:
            player_rect.x -= 7
        if keys[pygame.K_RIGHT]:
            player_rect.x += 7

        player_rect.x = max(0, min(WIDTH - player_rect.width, player_rect.x))
        player_rect.y = max(0, min(HEIGHT - player_rect.height, player_rect.y))

        if spawn_timer > 35:
            spawn_timer = 0
            balls.append({
                "rect": ball_img.get_rect(center=(WIDTH, random.randint(40, HEIGHT - 40))),
                "speed": random.randint(8, 14)
            })

        for ball_data in balls[:]:
            ball_rect = ball_data["rect"]
            ball_rect.x -= ball_data["speed"]

            if ball_rect.right < 0:
                balls.remove(ball_data)

            if player_rect.colliderect(ball_rect):
                show_result("Extreme Dodgeball", sports["Extreme Dodgeball"]["lose"])
                return

        if survived_time >= target_time:
            show_result("Extreme Dodgeball", sports["Extreme Dodgeball"]["win"])
            return

        screen.blit(player_img, player_rect)

        for ball_data in balls:
            screen.blit(ball_img, ball_data["rect"])

        draw_text("Extreme Dodgeball: High risk, high reward!", font_medium, BLACK, WIDTH // 2, 70)
        draw_text("Avoid the dodgeballs for 10 seconds", font_small, BLACK, WIDTH // 2, 115)
        draw_text("Use ARROW KEYS to move", font_small, BLACK, WIDTH // 2, 145)
        draw_text(f"Time: {survived_time:.1f}/{target_time}", font_medium, BLACK, WIDTH // 2, 190)

        return_to_menu_text()
        pygame.display.update()


def play_sport(sport_name):
    if sport_name == "Soccer":
        soccer_game()
    elif sport_name == "Basketball":
        basketball_game()
    elif sport_name == "Ping Pong":
        ping_pong_game()
    elif sport_name == "Hockey":
        hockey_game()
    elif sport_name == "Baseball":
        baseball_game()
    elif sport_name == "Track":
        track_game()
    elif sport_name == "Extreme Dodgeball":
        dodgeball_game()


def draw_button(rect, text, color, locked=False):
    pygame.draw.rect(screen, color, rect, border_radius=15)
    pygame.draw.rect(screen, BLACK, rect, 3, border_radius=15)

    if locked:
        overlay = pygame.Surface((rect.width, rect.height))
        overlay.set_alpha(160)
        overlay.fill(DARK_GRAY)
        screen.blit(overlay, rect.topleft)
        draw_text("LOCKED", font_medium, WHITE, rect.centerx, rect.centery - 15)
        draw_text(text, font_small, WHITE, rect.centerx, rect.centery + 20)
    else:
        draw_text(text, font_medium, WHITE, rect.centerx, rect.centery)


def draw_menu():
    screen.fill((235, 240, 250))

    draw_text("Sports Skill Challenge", font_big, BLACK, WIDTH // 2, 55)
    draw_text(f"Total Score: {total_score}", font_medium, BLUE, WIDTH // 2, 115)
    draw_text(message, font_small, BLACK, WIDTH // 2, 155)
    draw_text("Earn points to unlock the next sport. Losing removes points!", font_small, DARK_GRAY, WIDTH // 2, 190)

    buttons = []

    start_x = 90
    start_y = 240
    button_w = 240
    button_h = 90
    gap_x = 55
    gap_y = 35

    sport_names = list(sports.keys())

    for index, sport_name in enumerate(sport_names):
        row = index // 3
        col = index % 3

        x = start_x + col * (button_w + gap_x)
        y = start_y + row * (button_h + gap_y)

        rect = pygame.Rect(x, y, button_w, button_h)
        unlocked = total_score >= sports[sport_name]["unlock"]

        if unlocked:
            color = sports[sport_name]["color"]
        else:
            color = GRAY

        draw_button(rect, sport_name, color, locked=not unlocked)

        if not unlocked:
            draw_text(f"Needs {sports[sport_name]['unlock']} pts", font_tiny, WHITE, rect.centerx, rect.bottom - 18)
        else:
            draw_text(f"+{sports[sport_name]['win']} / {sports[sport_name]['lose']}", font_tiny, WHITE, rect.centerx, rect.bottom - 18)

        buttons.append((rect, sport_name, unlocked))

    draw_text("Click a sport to play. Press Q to quit.", font_small, BLACK, WIDTH // 2, HEIGHT - 40)

    return buttons


def main():
    global message

    while True:
        clock.tick(FPS)

        buttons = draw_menu()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                for rect, sport_name, unlocked in buttons:
                    if rect.collidepoint(mouse_pos):
                        if unlocked:
                            play_sport(sport_name)
                        else:
                            needed = sports[sport_name]["unlock"]
                            message = f"{sport_name} is locked. You need {needed} total points."

        pygame.display.update()


main()