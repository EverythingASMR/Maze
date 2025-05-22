import math
import pygame
from collections import deque
from random import choice

# Constants
RES = WIDTH, HEIGHT = 360, 640
TILE = 20
cols, rows = WIDTH // TILE, HEIGHT // TILE

# Pygame setup
pygame.init()
sc = pygame.display.set_mode(RES)
pygame.display.set_caption("Shortest Path Maze Solver")
clock = pygame.time.Clock()
FPS = 6000000

# Colors
BACKGROUND_COLOR = pygame.Color('#1E1F29')
CELL_COLOR = pygame.Color('#7ECA9C')
WALL_COLOR = pygame.Color('#222C36')
START_COLOR = pygame.Color('#9FD996')
END_COLOR = pygame.Color('#5AAB61')
SOLUTION_PATH_COLOR = pygame.Color('#CCFFBD')

class Cell:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False

    def draw(self):
        """Draw the cell background (visited state)."""
        x, y = self.x * TILE, self.y * TILE
        pygame.draw.rect(sc, CELL_COLOR, (x, y, TILE, TILE))

    def draw_walls(self):
        """Draw the walls of the cell."""
        x, y = self.x * TILE, self.y * TILE
        if self.walls['top']:
            pygame.draw.line(sc, WALL_COLOR, (x, y), (x + TILE, y), math.ceil(TILE / 3))
        if self.walls['right']:
            pygame.draw.line(sc, WALL_COLOR, (x + TILE, y), (x + TILE, y + TILE), math.ceil(TILE / 3))
        if self.walls['bottom']:
            pygame.draw.line(sc, WALL_COLOR, (x + TILE, y + TILE), (x, y + TILE), math.ceil(TILE / 3))
        if self.walls['left']:
            pygame.draw.line(sc, WALL_COLOR, (x, y + TILE), (x, y), math.ceil(TILE / 3))

    def draw_solution(self, full=True):
        """Highlight the cell as part of the solution path."""
        x, y = self.x * TILE, self.y * TILE
        if full:
            pygame.draw.rect(sc, SOLUTION_PATH_COLOR, (x, y, TILE, TILE))
        else:
            pygame.draw.rect(sc, SOLUTION_PATH_COLOR, (x + 2, y + 2, TILE - 4, TILE - 4))

    def check_cell(self, x, y):
        """Check for valid neighbor cells."""
        find_index = lambda x, y: x + y * cols
        if 0 <= x < cols and 0 <= y < rows:
            return grid_cells[find_index(x, y)]
        return None

    def check_neighbors(self):
        """Find unvisited neighbors."""
        neighbors = []
        top = self.check_cell(self.x, self.y - 1)
        right = self.check_cell(self.x + 1, self.y)
        bottom = self.check_cell(self.x, self.y + 1)
        left = self.check_cell(self.x - 1, self.y)
        if top and not top.visited:
            neighbors.append(top)
        if right and not right.visited:
            neighbors.append(right)
        if bottom and not bottom.visited:
            neighbors.append(bottom)
        if left and not left.visited:
            neighbors.append(left)
        return choice(neighbors) if neighbors else None

def remove_walls(current, next):
    """Remove the wall between current and next cell."""
    dx = current.x - next.x
    dy = current.y - next.y
    if dx == 1:
        current.walls['left'] = False
        next.walls['right'] = False
    elif dx == -1:
        current.walls['right'] = False
        next.walls['left'] = False
    if dy == 1:
        current.walls['top'] = False
        next.walls['bottom'] = False
    elif dy == -1:
        current.walls['bottom'] = False
        next.walls['top'] = False

def find_shortest_path():
    """Find the shortest path using BFS."""
    start = grid_cells[0]
    end = grid_cells[-1]
    queue = deque([start])
    parents = {start: None}

    while queue:
        current = queue.popleft()
        if current == end:
            break
        for direction in ['top', 'right', 'bottom', 'left']:
            if not current.walls[direction]:
                if direction == 'top':
                    neighbor = current.check_cell(current.x, current.y - 1)
                elif direction == 'right':
                    neighbor = current.check_cell(current.x + 1, current.y)
                elif direction == 'bottom':
                    neighbor = current.check_cell(current.x, current.y + 1)
                elif direction == 'left':
                    neighbor = current.check_cell(current.x - 1, current.y)

                if neighbor and neighbor not in parents:
                    queue.append(neighbor)
                    parents[neighbor] = current
    path = []
    cell = end
    while cell:
        path.append(cell)
        cell = parents[cell]
    path.reverse()
    return path

# Initialize grid and variables
grid_cells = [Cell(col, row) for row in range(rows) for col in range(cols)]
current_cell = grid_cells[0]
stack = []
end_cell = grid_cells[-1]
solving = False
solution_path = []

def draw_grid():
    """Draw the maze grid and all cells."""
    sc.fill(BACKGROUND_COLOR)
    for cell in grid_cells:
        if cell.visited:
            cell.draw()
        cell.draw_walls()
    pygame.draw.rect(sc, START_COLOR, (0, 0, TILE, TILE))
    pygame.draw.rect(sc, END_COLOR, (end_cell.x * TILE, end_cell.y * TILE, TILE, TILE))

def main():
    global current_cell, solving, solution_path
    running = True
    animating_solution = False
    solution_index = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        if not solving:
            # Maze generation phase
            draw_grid()
            current_cell.visited = True
            next_cell = current_cell.check_neighbors()
            if next_cell:
                next_cell.visited = True
                stack.append(current_cell)
                remove_walls(current_cell, next_cell)
                current_cell = next_cell
            elif stack:
                current_cell = stack.pop()
            else:
                solving = True
                solution_path = find_shortest_path()
                animating_solution = True

        elif animating_solution:
            # Animate the shortest path
            if solution_index < len(solution_path):
                for i in range(solution_index + 1):
                    solution_path[i].draw_solution(full=True)
                    solution_path[i].draw_walls()
                solution_index += 1
            else:
                animating_solution = False

        else:
            # Final rendering of the solution path
            draw_grid()
            for cell in solution_path:
                cell.draw_solution(full=True)
                cell.draw_walls()

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
