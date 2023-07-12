import pygame
import csv
from collections import deque
import random

# Define tile size and colors
TILE_SIZE = 30
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)

# Initialize Pygame
pygame.init()


class Unit(pygame.sprite.Sprite):
    def __init__(self, pos, colour, move_points):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(colour)
        self.rect = self.image.get_rect(topleft=pos)
        self.move_points = move_points
        self.selected = False

    def update(self):
        pass


def get_level_size(filename):
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        rows = sum(1 for _ in reader)
        csvfile.seek(0)
        cols = len(next(reader))
    return cols, rows


def read_grid_data(filename):
    with open(filename, 'r') as file:
        csv_reader = csv.reader(file)
        grid_data = [[int(element) for element in row] for row in csv_reader]
    return grid_data


def find_shortest_path(start, end, grid):
    level_size = len(grid[0]), len(grid)
    queue = deque([(start, [])])
    visited = set([start])
    costs = {start: 0}

    while queue:
        current, path = queue.popleft()

        if current == end:
            return path

        neighbors = get_neighbors(current, level_size)
        neighbors.sort(key=lambda n: grid[n[1]][n[0]])

        for neighbor in neighbors:
            neighbor_cost = costs[current] + grid[neighbor[1]][neighbor[0]]
            if neighbor not in visited or neighbor_cost < costs[neighbor]:
                queue.append((neighbor, path + [neighbor]))
                visited.add(neighbor)
                costs[neighbor] = neighbor_cost

    return None


def get_neighbors(node, level_size):
    x, y = node
    neighbors = []

    if x > 0:
        neighbors.append((x - 1, y))
    if x < level_size[0] - 1:
        neighbors.append((x + 1, y))
    if y > 0:
        neighbors.append((x, y - 1))
    if y < level_size[1] - 1:
        neighbors.append((x, y + 1))

    return neighbors


def draw_grid(screen, grid):
    for y, row in enumerate(grid):
        for x, value in enumerate(row):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, BLACK, rect, 1)
            font = pygame.font.Font(None, 24)
            text = font.render(str(value), True, BLACK)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)


# Set up the display
level_size = get_level_size('map.csv')
screen = pygame.display.set_mode((level_size[0] * TILE_SIZE, level_size[1] * TILE_SIZE))

# Read the CSV file and create the grid
grid_data = read_grid_data('map.csv')

# Create the grid and units
grid = grid_data
unit1 = Unit((random.randint(0, level_size[0] - 1), random.randint(0, level_size[1] - 1)), MAGENTA, 7)
unit2 = Unit((random.randint(0, level_size[0] - 1), random.randint(0, level_size[1] - 1)), GREEN, 4)

# Create a sprite group and add the units to it
unit_group = pygame.sprite.Group()
unit_group.add(unit1, unit2)

# Set the initial current unit
current_unit = unit1

clock = pygame.time.Clock()

# Game loop
running = True
potential_moves = {}
current_path = []
while running:
    screen.fill(WHITE)

    draw_grid(screen, grid)

    # Check if a unit is selected
    if current_unit.selected:
        # Find the highlighted tile under the mouse cursor
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_tile = mouse_x // TILE_SIZE, mouse_y // TILE_SIZE

        # Draw the potential move tiles in blue
        for move_tile, path in potential_moves.items():
            for path_node in path:
                path_rect = pygame.Rect(path_node[0] * TILE_SIZE, path_node[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, BLUE, path_rect)

                # Draw the tile value on top of the blue tile
                tile_value = str(grid[path_node[1]][path_node[0]])
                font = pygame.font.Font(None, 24)
                text = font.render(tile_value, True, WHITE)
                text_rect = text.get_rect(center=path_rect.center)
                screen.blit(text, text_rect)

        # Check if the mouse is on a new potential move tile
        if mouse_tile != current_unit.rect.topleft and mouse_tile in potential_moves:
            # Find the shortest path from the unit to the highlighted tile
            start = current_unit.rect.topleft
            end = mouse_tile
            current_path = find_shortest_path(start, end, grid)

            # Draw the shortest path if it exists
            if current_path:
                for path_node in current_path:
                    path_rect = pygame.Rect(path_node[0] * TILE_SIZE, path_node[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(screen, YELLOW, path_rect)

                    # Draw the tile value on top of the yellow tile
                    tile_value = str(grid[path_node[1]][path_node[0]])
                    font = pygame.font.Font(None, 24)
                    text = font.render(tile_value, True, BLACK)
                    text_rect = text.get_rect(center=path_rect.center)
                    screen.blit(text, text_rect)

    # Draw the units
    unit_group.update()
    for unit in unit_group:
        screen.blit(unit.image, (unit.rect.x * TILE_SIZE, unit.rect.y * TILE_SIZE))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button clicked
            clicked_x, clicked_y = event.pos
            clicked_tile = clicked_x // TILE_SIZE, clicked_y // TILE_SIZE

            # Check if the clicked tile matches the current unit's position
            if current_unit.rect.topleft == clicked_tile:
                # Toggle the selected state of the current unit
                current_unit.selected = not current_unit.selected

                # Calculate potential moves if the unit is selected
                if current_unit.selected:
                    start = current_unit.rect.topleft
                    potential_moves.clear()

                    for y in range(level_size[1]):
                        for x in range(level_size[0]):
                            end = (x, y)
                            path = find_shortest_path(start, end, grid)

                            if path:
                                accumulated_value = sum(grid[node[1]][node[0]] for node in path)
                                if accumulated_value <= current_unit.move_points:
                                    potential_moves[(x, y)] = path
            else:
                # Check if the clicked tile is a potential move tile for the selected unit
                if current_unit.selected and clicked_tile in potential_moves:
                    # Update the unit's position
                    current_unit.rect.topleft = clicked_tile
                    current_unit.selected = False

                    # Switch to the other unit for the next turn
                    if current_unit == unit1:
                        current_unit = unit2
                    else:
                        current_unit = unit1

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
