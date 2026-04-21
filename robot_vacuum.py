import pygame
import random
import heapq
import sys
from dataclasses import dataclass

GRID_SIZE = 20
CELL_SIZE = 30

WINDOW_WIDTH = GRID_SIZE * CELL_SIZE
WINDOW_HEIGHT = GRID_SIZE * CELL_SIZE + 120

FPS = 60
BLACK = (20, 25, 35)
GRID_LINE = (40, 60, 90)
EMPTY = (15, 25, 40)
WALL = (60, 75, 95)
DIRT = (46, 204, 113)
CLEANED = (30, 120, 80)
ROBOT = (52, 152, 219)
WHITE = (236, 240, 241)
PATH = (241, 196, 15)

@dataclass(order=True)
class Node:
    f: float
    x: int
    y: int

class RobotVacuum:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT)
        )
        pygame.display.set_caption(
            "Robot Vacuum Cleaner - A* Pathfinding"
        )

        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 26)

        self.running = True

        self.grid = [
            [{'wall': False, 'dirt': 0, 'cleaned': False}
             for _ in range(GRID_SIZE)]
            for _ in range(GRID_SIZE)
        ]

        self.robot_pos = [1, 1]
        self.path = []
        self.target = None

        self.dirt_total = 0
        self.dirt_cleaned = 0
        self.battery = 100

        self.is_cleaning = False

        self.generate_room()

    def generate_room(self):

        self.dirt_total = 0

        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):

                if random.random() < 0.10:
                    self.grid[x][y]['wall'] = True

                elif random.random() < 0.25:
                    self.grid[x][y]['dirt'] = 1
                    self.dirt_total += 1

        self.grid[1][1]['wall'] = False

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def get_neighbors(self, pos):

        x, y = pos
        directions = [(1,0),(-1,0),(0,1),(0,-1)]

        neighbors = []

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                if not self.grid[nx][ny]['wall']:
                    neighbors.append((nx, ny))

        return neighbors

    def find_next_dirt(self):

        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                if self.grid[x][y]['dirt'] == 1:
                    return (x, y)
        return None

    def a_star(self, start, goal):

        open_set = []
        heapq.heappush(open_set, Node(0, start[0], start[1]))

        came_from = {}
        g_score = {start: 0}

        while open_set:

            current = heapq.heappop(open_set)
            current_pos = (current.x, current.y)

            if current_pos == goal:
                return self.reconstruct_path(came_from, current_pos)

            for neighbor in self.get_neighbors(current_pos):

                tentative_g = g_score[current_pos] + 1

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current_pos
                    g_score[neighbor] = tentative_g

                    f = tentative_g + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set,
                                   Node(f, neighbor[0], neighbor[1]))

        return []
    def reconstruct_path(self, came_from, current):
        path = []

        while current in came_from:
            path.append(current)
            current = came_from[current]

        path.reverse()
        return path

    def update(self):

        if not self.path:
            self.target = self.find_next_dirt()

            if self.target:
                self.path = self.a_star(tuple(self.robot_pos),
                                        self.target)
            else:
                self.is_cleaning = False
                return

        if self.path:

            self.robot_pos = list(self.path.pop(0))
            self.battery -= 0.1

            cell = self.grid[self.robot_pos[0]][self.robot_pos[1]]

            if cell['dirt'] == 1:
                cell['dirt'] = 0
                cell['cleaned'] = True
                self.dirt_cleaned += 1

    def draw_grid(self):

        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):

                rect = pygame.Rect(
                    x * CELL_SIZE,
                    y * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )

                cell = self.grid[x][y]

                if cell['wall']:
                    color = WALL
                elif cell['dirt']:
                    color = DIRT
                elif cell['cleaned']:
                    color = CLEANED
                else:
                    color = EMPTY

                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, GRID_LINE, rect, 1)

    def draw_path(self):

        for p in self.path:
            rect = pygame.Rect(
                p[0]*CELL_SIZE,
                p[1]*CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )
            pygame.draw.rect(self.screen, PATH, rect, 2)

    def draw_robot(self):

        x, y = self.robot_pos

        center = (
            x * CELL_SIZE + CELL_SIZE//2,
            y * CELL_SIZE + CELL_SIZE//2
        )

        pygame.draw.circle(self.screen,
                           ROBOT,
                           center,
                           CELL_SIZE//2 - 4)

    def draw_ui(self):

        pygame.draw.rect(
            self.screen,
            BLACK,
            (0, GRID_SIZE*CELL_SIZE, WINDOW_WIDTH, 120)
        )

        texts = [
            f"Dirt Cleaned: {self.dirt_cleaned}/{self.dirt_total}",
            f"Battery: {int(self.battery)}%",
            "SPACE: Start | R: Reset"
        ]

        for i, t in enumerate(texts):
            txt = self.font.render(t, True, WHITE)
            self.screen.blit(
                txt,
                (20, GRID_SIZE*CELL_SIZE + 15 + i*30)
            )

    def handle_events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE:
                    self.is_cleaning = True

                if event.key == pygame.K_r:
                    self.__init__()
    def run(self):

        while self.running:

            self.handle_events()

            if self.is_cleaning and self.battery > 0:
                self.update()

            self.screen.fill(BLACK)

            self.draw_grid()
            self.draw_path()
            self.draw_robot()
            self.draw_ui()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    RobotVacuum().run()







