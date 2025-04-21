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
FPS = 600

# Colors (renovated palette)
BACKGROUND_COLOR      = pygame.Color('#313638')
WALL_COLOR            = pygame.Color('#2F3537')
START_COLOR           = pygame.Color('#B0C4B1')  # green gray
END_COLOR             = pygame.Color('#FE5F55')  # mango orange
CURRENT_COLOR         = pygame.Color('#2292A4')  # highlight for current cell
SOLUTION_PATH_COLOR   = pygame.Color('#90E39A')  # light green

# Generation counter
generation_counter = 0
# Gradient speed multiplier
gradient_speed = 1

class Cell:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False

    def check_cell(self, x, y):
        idx = x + y * cols
        if 0 <= x < cols and 0 <= y < rows:
            return grid_cells[idx]
        return None

    def check_neighbors(self):
        neighbors = []
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            nb = self.check_cell(self.x + dx, self.y + dy)
            if nb and not nb.visited:
                neighbors.append(nb)
        return choice(neighbors) if neighbors else None

    def draw_walls(self):
        x, y = self.x * TILE, self.y * TILE
        w = math.ceil(TILE / 3)
        if self.walls['top']:
            pygame.draw.line(sc, WALL_COLOR, (x, y), (x + TILE, y), w)
        if self.walls['right']:
            pygame.draw.line(sc, WALL_COLOR, (x + TILE, y), (x + TILE, y + TILE), w)
        if self.walls['bottom']:
            pygame.draw.line(sc, WALL_COLOR, (x + TILE, y + TILE), (x, y + TILE), w)
        if self.walls['left']:
            pygame.draw.line(sc, WALL_COLOR, (x, y + TILE), (x, y), w)

    def draw_solution(self, full=True):
        x, y = self.x * TILE, self.y * TILE
        size = TILE if full else TILE - 4
        offset = 0 if full else 2
        pygame.draw.rect(sc, SOLUTION_PATH_COLOR, (x + offset, y + offset, size, size))

class ColoredCell(Cell):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.step = None
        self.highlighted = False

    def draw_with_color(self, max_step):
        if self.step is None or self.highlighted:
            return
        t = min(1, (self.step * gradient_speed) / max_step) if max_step > 1.3 else 0
        r = int(START_COLOR.r + (END_COLOR.r - START_COLOR.r) * t)
        g = int(START_COLOR.g + (END_COLOR.g - START_COLOR.g) * t)
        b = int(START_COLOR.b + (END_COLOR.b - START_COLOR.b) * t)
        color = pygame.Color(r, g, b)
        x, y = self.x * TILE, self.y * TILE
        pygame.draw.rect(sc, color, (x, y, TILE, TILE))
        self.draw_walls()

# Maze generation and pathfinding

def remove_walls(current, next):
    dx, dy = current.x - next.x, current.y - next.y
    if dx == 1:
        current.walls['left'] = False; next.walls['right'] = False
    elif dx == -1:
        current.walls['right'] = False; next.walls['left'] = False
    if dy == 1:
        current.walls['top'] = False; next.walls['bottom'] = False
    elif dy == -1:
        current.walls['bottom'] = False; next.walls['top'] = False

from collections import deque

def find_shortest_path():
    start, end = grid_cells[0], grid_cells[-1]
    queue = deque([start]); parents = {start: None}
    while queue:
        cur = queue.popleft()
        if cur == end: break
        for d, (dx, dy) in zip(['top','right','bottom','left'], [(0,-1),(1,0),(0,1),(-1,0)]):
            if not cur.walls[d]:
                nb = cur.check_cell(cur.x + dx, cur.y + dy)
                if nb and nb not in parents:
                    parents[nb] = cur; queue.append(nb)
    path = []
    c = end
    while c:
        path.append(c); c = parents[c]
    return list(reversed(path))

# Grid setup
grid_cells = [ColoredCell(cx, ry) for ry in range(rows) for cx in range(cols)]
current, stack = grid_cells[0], []
end_cell, solving, solution = grid_cells[-1], False, []

def draw_grid(max_step):
    sc.fill(BACKGROUND_COLOR)
    for cell in grid_cells:
        if cell.visited:
            cell.draw_with_color(max_step)
        else:
            cell.draw_walls()
    if not solving:
        pygame.draw.rect(sc, CURRENT_COLOR, (current.x * TILE + 2, current.y * TILE + 2, TILE - 4, TILE - 4))
    pygame.draw.rect(sc, START_COLOR, (0, 0, TILE, TILE))
    pygame.draw.rect(sc, END_COLOR, (end_cell.x * TILE, end_cell.y * TILE, TILE, TILE))

# Main loop
def main():
    global current, solving, solution, generation_counter
    anim = False; idx = 0
    while True:
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                pygame.quit(); return
        if not solving:
            draw_grid(generation_counter)
            current.visited = True; current.step = generation_counter
            generation_counter += 1
            nxt = current.check_neighbors()
            if nxt:
                nxt.visited = True; stack.append(current)
                remove_walls(current, nxt); current = nxt
            elif stack:
                current = stack.pop()
            else:
                solving = True; solution = find_shortest_path(); anim = True
        elif anim:
            if idx < len(solution):
                for c in solution[:idx+1]:
                    c.draw_solution()
                    c.draw_walls()
                idx += 1
            else:
                anim = False
        else:
            draw_grid(generation_counter)
            for c in solution:
                c.draw_solution()
                c.draw_walls()
        pygame.display.flip(); clock.tick(FPS)

if __name__ == '__main__':
    main()
