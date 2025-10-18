# code/simulation.py
import pygame
import random
import os # <-- ADD THIS IMPORT

# --- Constants ---
WIDTH, HEIGHT = 800, 800
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2
ROAD_WIDTH = 100
LANE_WIDTH = ROAD_WIDTH // 2

# Colors
BLACK, GREY, WHITE = (0, 0, 0), (50, 50, 50), (255, 255, 255)
RED, YELLOW, GREEN = (200, 0, 0), (200, 200, 0), (0, 200, 0)
CAR_COLORS = [(0, 150, 255), (255, 0, 150), (255, 150, 0), (150, 255, 0)]
AMBULANCE_COLOR = WHITE

# --- Vehicle Class ---
class Vehicle(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.direction = direction
        self.image = pygame.Surface((20, 20))
        self.image.fill(random.choice(CAR_COLORS))
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self.speed = random.uniform(1.5, 3)

    def update(self, phase, emergency_mode=False, ambulance=None):
        stop = False
        if emergency_mode and ambulance:
            is_ambulance_vertical = ambulance.direction in ['UP', 'DOWN']
            is_self_horizontal = self.direction in ['LEFT', 'RIGHT']
            if is_ambulance_vertical and is_self_horizontal: stop = True
            elif not is_ambulance_vertical and not is_self_horizontal: stop = True
        else:
            if self.direction in ['UP', 'DOWN'] and phase in ['HORIZONTAL_GREEN', 'H_TO_V_YELLOW']:
                if self.rect.bottom > CENTER_Y - LANE_WIDTH and self.rect.top < CENTER_Y + LANE_WIDTH: stop = True
            elif self.direction in ['LEFT', 'RIGHT'] and phase in ['VERTICAL_GREEN', 'V_TO_H_YELLOW']:
                if self.rect.right > CENTER_X - LANE_WIDTH and self.rect.left < CENTER_X + LANE_WIDTH: stop = True
        if not stop: self.move()
        self.check_bounds()

    def move(self):
        if self.direction == 'DOWN': self.rect.y += self.speed
        elif self.direction == 'UP': self.rect.y -= self.speed
        elif self.direction == 'RIGHT': self.rect.x += self.speed
        elif self.direction == 'LEFT': self.rect.x -= self.speed

    def check_bounds(self):
        off_screen = False
        if self.direction == 'DOWN' and self.rect.top > HEIGHT: off_screen = True
        elif self.direction == 'UP' and self.rect.bottom < 0: off_screen = True
        elif self.direction == 'RIGHT' and self.rect.left > WIDTH: off_screen = True
        elif self.direction == 'LEFT' and self.rect.right < 0: off_screen = True
        if off_screen: self.kill()

# --- Ambulance Class ---
class Ambulance(Vehicle):
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction)
        self.image.fill(AMBULANCE_COLOR)
        self.speed = 4

    def update(self, phase, emergency_mode=False, ambulance=None):
        self.move()
        self.check_bounds()

# --- Setup ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GreenLight Go - Listening for Signal")
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
ambulance_group = pygame.sprite.GroupSingle()

# Traffic Phases
PHASES = ['VERTICAL_GREEN', 'V_TO_H_YELLOW', 'HORIZONTAL_GREEN', 'H_TO_V_YELLOW']
PHASE_DURATIONS = {'VERTICAL_GREEN': 8000, 'V_TO_H_YELLOW': 2000, 'HORIZONTAL_GREEN': 8000, 'H_TO_V_YELLOW': 2000}
current_phase_index = 0
last_phase_change = pygame.time.get_ticks()

emergency_mode = False

# --- Functions ---
def spawn_vehicle():
    if len(all_sprites) - len(ambulance_group) < 20:
        spawn_points = {
            'DOWN': (CENTER_X + LANE_WIDTH / 2, -40),
            'UP': (CENTER_X - LANE_WIDTH / 2, HEIGHT + 40),
            'RIGHT': (-40, CENTER_Y - LANE_WIDTH / 2),
            'LEFT': (WIDTH + 40, CENTER_Y + LANE_WIDTH / 2)
        }
        direction = random.choice(list(spawn_points.keys()))
        x, y = spawn_points[direction]
        all_sprites.add(Vehicle(x, y, direction))

def spawn_ambulance():
    direction = random.choice(['DOWN', 'UP', 'RIGHT', 'LEFT'])
    spawn_points = {
        'DOWN': (CENTER_X + LANE_WIDTH / 2, -80),
        'UP': (CENTER_X - LANE_WIDTH / 2, HEIGHT + 80),
        'RIGHT': (-80, CENTER_Y - LANE_WIDTH / 2),
        'LEFT': (WIDTH + 80, CENTER_Y + LANE_WIDTH / 2)
    }
    x, y = spawn_points[direction]
    ambulance = Ambulance(x, y, direction)
    all_sprites.add(ambulance)
    ambulance_group.add(ambulance)

def draw_background():
    screen.fill(BLACK)
    pygame.draw.rect(screen, GREY, (CENTER_X - ROAD_WIDTH // 2, 0, ROAD_WIDTH, HEIGHT))
    pygame.draw.rect(screen, GREY, (0, CENTER_Y - ROAD_WIDTH // 2, WIDTH, ROAD_WIDTH))
    for y in range(0, HEIGHT, 40): pygame.draw.line(screen, WHITE, (CENTER_X, y), (CENTER_X, y + 20), 2)
    for x in range(0, WIDTH, 40): pygame.draw.line(screen, WHITE, (x, CENTER_Y), (x + 20, CENTER_Y), 2)

def draw_traffic_lights(phase):
    v_color = GREEN if phase == 'VERTICAL_GREEN' else YELLOW if phase == 'V_TO_H_YELLOW' else RED
    pygame.draw.circle(screen, v_color, (CENTER_X - ROAD_WIDTH, CENTER_Y - ROAD_WIDTH), 15)
    pygame.draw.circle(screen, v_color, (CENTER_X + ROAD_WIDTH, CENTER_Y + ROAD_WIDTH), 15)
    h_color = GREEN if phase == 'HORIZONTAL_GREEN' else YELLOW if phase == 'H_TO_V_YELLOW' else RED
    pygame.draw.circle(screen, h_color, (CENTER_X - ROAD_WIDTH, CENTER_Y + ROAD_WIDTH), 15)
    pygame.draw.circle(screen, h_color, (CENTER_X + ROAD_WIDTH, CENTER_Y - ROAD_WIDTH), 15)

# --- Main Loop ---
running = True
while running:
    # --- NEW: Check for the signal file ---
    if os.path.exists('emergency_signal.txt'):
        emergency_mode = True
        if not ambulance_group:
            spawn_ambulance()
        os.remove('emergency_signal.txt') # Delete the file to reset the signal

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # You can still use the 'E' key for manual testing
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                emergency_mode = True
                if not ambulance_group:
                    spawn_ambulance()

    current_time = pygame.time.get_ticks()

    if emergency_mode:
        ambulance = ambulance_group.sprite
        if ambulance:
            if ambulance.direction in ['UP', 'DOWN']:
                current_phase_index = 0
            else:
                current_phase_index = 2
        else:
            emergency_mode = False
            last_phase_change = current_time
    else:
        if current_time - last_phase_change > PHASE_DURATIONS[PHASES[current_phase_index]]:
            current_phase_index = (current_phase_index + 1) % len(PHASES)
            last_phase_change = current_time

    if not emergency_mode:
        spawn_vehicle()

    all_sprites.update(PHASES[current_phase_index], emergency_mode, ambulance_group.sprite)
    
    draw_background()
    draw_traffic_lights(PHASES[current_phase_index])
    all_sprites.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()