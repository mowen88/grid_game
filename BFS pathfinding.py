import pygame, random
import csv
from collections import deque

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
def get_level_size(filename):
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            rows = (sum (1 for row in reader) + 1)
            cols = len(row)
    return (cols, rows)

# Read the CSV file
grid_data = []
with open('map.csv', 'r') as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        # Convert each element in the row to an integer
        int_row = [int(element) for element in row]
        grid_data.append(int_row)

# Determine the grid size based on the CSV data
level_size = get_level_size('map.csv')

# Set up the display
screen = pygame.display.set_mode((level_size[0] * TILE_SIZE, level_size[1] * TILE_SIZE))

# Create the grid
grid = grid_data

selected_unit = None

unit_group = pygame.sprite.Group()

class Unit(pygame.sprite.Sprite):
    def __init__(self, groups, pos, colour):
        super().__init__(groups)
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill((colour))
        self.rect = self.image.get_rect(topleft=pos)
        self.move_points = 6

    def update(self):
        pass


unit1 = Unit([unit_group], (random.randint(0, level_size[0] - 1), random.randint(0, level_size[1] - 1)), MAGENTA)
unit2 = Unit([unit_group], (random.randint(0, level_size[0] - 1), random.randint(0, level_size[1] - 1)), GREEN)

# Initialize the shortest path
shortest_path = []

# Initialize the potential move tiles dictionary
potential_moves = {}

# Function to find the shortest path using BFS
def find_shortest_path(start, end):
    queue = deque([(start, [])])
    visited = set([start])
    costs = {start: 0}

    while queue:
        current, path = queue.popleft()

        if current == end:
            return path

        neighbors = get_neighbors(current)
        neighbors.sort(key=lambda n: grid[n[1]][n[0]])

        for neighbor in neighbors:
            neighbor_cost = costs[current] + grid[neighbor[1]][neighbor[0]]
            if neighbor not in visited or neighbor_cost < costs[neighbor]:
                queue.append((neighbor, path + [neighbor]))
                visited.add(neighbor)
                costs[neighbor] = neighbor_cost

    return None


# Function to get valid neighboring nodes
def get_neighbors(node):
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

# Game loop
running = True
while running:
    screen.fill(WHITE)

    # Draw the grid with numbers and highlight tiles within the move point range
    for y in range(level_size[1]):
        for x in range(level_size[0]):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            value = str(grid[y][x])
            pygame.draw.rect(screen, (200, 200, 200), rect, 1)
            font = pygame.font.Font(None, 24)
            text = font.render(value, True, BLACK)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)

            # Check if the mouse is over a highlighted tile
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if rect.collidepoint(mouse_x, mouse_y):
                # Find the shortest path between the sprite and the highlighted tile
                start = (unit2.rect.topleft)
                end = (x, y)
                shortest_path = find_shortest_path(start, end)

    # Draw the sprite
    screen.blit(unit2.image, (unit2.rect.x * TILE_SIZE, unit2.rect.y * TILE_SIZE))
    screen.blit(unit1.image, (unit1.rect.x * TILE_SIZE, unit1.rect.y * TILE_SIZE))

    # Check if the potential move tiles dictionary needs to be updated
    if shortest_path:
        last_path_node = shortest_path[-1]
        if last_path_node not in potential_moves:
            potential_moves.clear()

            # Find all potential move-to tiles in blue
            for y in range(level_size[1]):
                for x in range(level_size[0]):
                    # Find the path between the sprite and the current tile
                    start = (unit2.rect.x, unit2.rect.y)
                    end = (x, y)
                    path = find_shortest_path(start, end)

                    if path:
                        accumulated_value = sum(grid[node[1]][node[0]] for node in path)
                        if accumulated_value <= unit2.move_points:
                            potential_moves[(x, y)] = path

    if selected_unit is not None:
        # Draw the potential move tiles in blue and potential attackable tiles in red
        for move_tile, path in potential_moves.items():
            attackable_tiles = get_neighbors(path[-1])
            for path_node in path:
                path_rect = pygame.Rect(path_node[0] * TILE_SIZE, path_node[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, BLUE, path_rect)
                for tile_node in attackable_tiles:
                    if tile_node not in potential_moves and tile_node != unit2.rect.topleft:
                        attackable_rect = pygame.Rect(tile_node[0] * TILE_SIZE, tile_node[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                        pygame.draw.rect(screen, CYAN, attackable_rect)

                # Draw the tile value on top of the blue tile
                tile_value = str(grid[path_node[1]][path_node[0]])
                font = pygame.font.Font(None, 24)
                text = font.render(tile_value, True, WHITE)
                text_rect = text.get_rect(center=path_rect.center)
                screen.blit(text, text_rect)

        # Draw the shortest path and their values
        accumulated_value = 0
        for path_node in shortest_path:
            path_rect = pygame.Rect(path_node[0] * TILE_SIZE, path_node[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            node_value = grid[path_node[1]][path_node[0]]
            accumulated_value += node_value

            # # Show potential attack tiles
            # target_tile = get_neighbors(shortest_path[-1])
            # if shortest_path[-1] in potential_moves:
            #     for target_node in target_tile:
            #         target_rect = pygame.Rect(target_node[0] * TILE_SIZE, target_node[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            #         if target_node not in potential_moves and target_node not in shortest_path and target_node != unit2.rect.topleft:
            #             pygame.draw.rect(screen, RED, target_rect)

            if accumulated_value <= unit2.move_points:
                pygame.draw.rect(screen, YELLOW, path_rect)

                # Draw the tile value on top of the red tile
                tile_value = str(grid[path_node[1]][path_node[0]])
                font = pygame.font.Font(None, 24)
                text = font.render(tile_value, True, WHITE)
                text_rect = text.get_rect(center=path_rect.center)
                screen.blit(text, text_rect)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button clicked
            clicked_x, clicked_y = event.pos
            clicked_tile = (clicked_x // TILE_SIZE, clicked_y // TILE_SIZE)
            
            if clicked_tile == (unit2.rect.x, unit2.rect.y):
                selected_unit = True
                
            elif selected_unit and clicked_tile in potential_moves:
                # Update the sprite position
                unit2.rect.topleft = clicked_tile
                selected_unit = None
                potential_moves.clear()
            else:
                selected_unit = None


    pygame.display.flip()

# Quit the game
pygame.quit()
