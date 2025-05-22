import math, pygame, json
from collections import deque
from random import choice

# === Constants ===
#RES = WIDTH, HEIGHT = 720, 1280
RES = WIDTH, HEIGHT = 360, 640
TILE = 32
cols, rows = WIDTH // TILE, HEIGHT // TILE
FPS = 60
CAMERA_ZOOM = 1.5
MINIMAP_SCALE = 0.2

# === Load Theme ===
with open("themes.json", "r") as f:
    themes = json.load(f)
theme_names = list(themes.keys())
theme_index = 0

def apply_theme(theme_data):
    global BACKGROUND_COLOR, WALL_COLOR, START_COLOR, END_COLOR, SOLUTION_PATH_COLOR
    BACKGROUND_COLOR = pygame.Color(theme_data["BACKGROUND_COLOR"])
    WALL_COLOR = pygame.Color(theme_data["WALL_COLOR"])
    START_COLOR = pygame.Color(theme_data["START_COLOR"])
    END_COLOR = pygame.Color(theme_data["END_COLOR"])
    SOLUTION_PATH_COLOR = pygame.Color(theme_data["SOLUTION_PATH_COLOR"])

apply_theme(themes[theme_names[theme_index]])

# === Classes ===
class Cell:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False

    def check_cell(self, x, y):
        if 0 <= x < cols and 0 <= y < rows:
            return grid_cells[x + y * cols]
        return None

    def check_neighbors(self):
        neighbors = []
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            nb = self.check_cell(self.x + dx, self.y + dy)
            if nb and not nb.visited:
                neighbors.append(nb)
        return choice(neighbors) if neighbors else None

    def draw_walls(self, surf):
        x, y = self.x * TILE, self.y * TILE
        w = math.ceil(TILE / 3)
        if self.walls['top']:
            pygame.draw.line(surf, WALL_COLOR, (x, y), (x + TILE, y), w)
        if self.walls['right']:
            pygame.draw.line(surf, WALL_COLOR, (x + TILE, y), (x + TILE, y + TILE), w)
        if self.walls['bottom']:
            pygame.draw.line(surf, WALL_COLOR, (x + TILE, y + TILE), (x, y + TILE), w)
        if self.walls['left']:
            pygame.draw.line(surf, WALL_COLOR, (x, y + TILE), (x, y), w)

    def draw_solution(self, surf, full=True, t=0):
        x, y = self.x * TILE, self.y * TILE
        size = TILE if full else TILE - 4
        offset = 0 if full else 2
        r = int(255 * (math.sin(t + 0) / 2 + 0.5))
        g = int(255 * (math.sin(t + 2) / 2 + 0.5))
        b = int(255 * (math.sin(t + 4) / 2 + 0.5))
        color = pygame.Color(r, g, b)
        pygame.draw.rect(surf, color, (x + offset, y + offset, size, size))

class ColoredCell(Cell):
    def __init__(self, x, y):
        super().__init__(x, y)

# === Maze Logic ===
def remove_walls(a, b):
    dx = a.x - b.x
    dy = a.y - b.y
    if dx == 1: a.walls['left'] = False; b.walls['right'] = False
    elif dx == -1: a.walls['right'] = False; b.walls['left'] = False
    if dy == 1: a.walls['top'] = False; b.walls['bottom'] = False
    elif dy == -1: a.walls['bottom'] = False; b.walls['top'] = False

def find_shortest_path():
    start, end = grid_cells[0], grid_cells[-1]
    queue = deque([start])
    parents = {start: None}
    while queue:
        cur = queue.popleft()
        if cur == end: break
        for dir, (dx, dy) in zip(['top','right','bottom','left'], [(0,-1),(1,0),(0,1),(-1,0)]):
            if not cur.walls[dir]:
                nb = cur.check_cell(cur.x + dx, cur.y + dy)
                if nb and nb not in parents:
                    parents[nb] = cur
                    queue.append(nb)
    path = []
    c = end
    while c:
        path.append(c)
        c = parents[c]
    return list(reversed(path))

def generate_maze():
    global grid_cells
    grid_cells = [ColoredCell(x, y) for y in range(rows) for x in range(cols)]
    current = grid_cells[0]
    stack = []
    while True:
        current.visited = True
        nxt = current.check_neighbors()
        if nxt:
            nxt.visited = True
            stack.append(current)
            remove_walls(current, nxt)
            current = nxt
        elif stack:
            current = stack.pop()
        else:
            break

# === Pygame Setup ===
pygame.init()
sc = pygame.display.set_mode(RES)
pygame.display.set_caption("Maze Cam + Minimap")
clock = pygame.time.Clock()

# === Game State ===
generate_maze()
solution = find_shortest_path()
player = grid_cells[0]
end_cell = grid_cells[-1]
show_solution = False

def move_player(dx, dy):
    global player, show_solution
    dir_map = {(0, -1): 'top', (1, 0): 'right', (0, 1): 'bottom', (-1, 0): 'left'}
    direction = dir_map[(dx, dy)]
    if not player.walls[direction]:
        nx, ny = player.x + dx, player.y + dy
        if 0 <= nx < cols and 0 <= ny < rows:
            player = grid_cells[nx + ny * cols]
            if player == end_cell:
                show_solution = True

# === Draw Functions ===
def draw_world(t):
    world_w, world_h = cols * TILE, rows * TILE
    world_surf = pygame.Surface((world_w, world_h))
    world_surf.fill(BACKGROUND_COLOR)

    if show_solution:
        for c in solution:
            c.draw_solution(world_surf, full=True, t=t)

    for cell in grid_cells:
        if cell.visited:
            cell.draw_walls(world_surf)

    pygame.draw.rect(world_surf, START_COLOR, (0, 0, TILE, TILE))
    pygame.draw.rect(world_surf, END_COLOR, (end_cell.x * TILE, end_cell.y * TILE, TILE, TILE))

    return world_surf

def draw_player_on_screen(screen_x, screen_y, t):
    size = int(TILE * CAMERA_ZOOM) - 6
    pulse = int(2 * math.sin(t * 3))
    size += pulse
    offset = (int(TILE * CAMERA_ZOOM) - size) // 2
    rect = pygame.Rect(screen_x + offset, screen_y + offset, size, size)

    r = int(255 * (math.sin(t + 0) / 2 + 0.5))
    g = int(255 * (math.sin(t + 2) / 2 + 0.5))
    b = int(255 * (math.sin(t + 4) / 2 + 0.5))
    core_color = pygame.Color(r, g, b)

    for i in range(1, 4):
        alpha = max(0, 40 - i * 10)
        glow_size = size + i * 100
        glow_offset = (int(TILE * CAMERA_ZOOM) - glow_size) // 2
        glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        glow_color = pygame.Color(r, g, b, alpha)
        pygame.draw.ellipse(glow_surface, glow_color, glow_surface.get_rect())
        sc.blit(glow_surface, (screen_x + glow_offset, screen_y + glow_offset))

    pygame.draw.rect(sc, pygame.Color(30, 30, 30), rect.inflate(2, 2), border_radius=4)
    pygame.draw.rect(sc, core_color, rect, border_radius=4)

def draw_minimap(world):
    scaled = pygame.transform.scale(world, (int(world.get_width() * MINIMAP_SCALE),
                                            int(world.get_height() * MINIMAP_SCALE)))
    sc.blit(scaled, (WIDTH - scaled.get_width() - 10, 10))

def draw(t):
    world = draw_world(t)

    cam_w, cam_h = int(WIDTH / CAMERA_ZOOM), int(HEIGHT / CAMERA_ZOOM)
    cam_x = player.x * TILE + TILE // 2 - cam_w // 2
    cam_y = player.y * TILE + TILE // 2 - cam_h // 2

    cam_x = max(0, min(cam_x, world.get_width() - cam_w))
    cam_y = max(0, min(cam_y, world.get_height() - cam_h))
    cam_rect = pygame.Rect(cam_x, cam_y, cam_w, cam_h)

    cam_view = world.subsurface(cam_rect)
    scaled = pygame.transform.smoothscale(cam_view, (WIDTH, HEIGHT))
    sc.blit(scaled, (0, 0))

    px = int((player.x * TILE - cam_x) * CAMERA_ZOOM)
    py = int((player.y * TILE - cam_y) * CAMERA_ZOOM)
    draw_player_on_screen(px, py, t)

    draw_minimap(world)

# === Main Loop ===
def main():
    global theme_index
    t = 0
    while True:
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                pygame.quit(); return
            if evt.type == pygame.KEYDOWN:
                if evt.key in [pygame.K_w, pygame.K_UP]: move_player(0, -1)
                elif evt.key in [pygame.K_s, pygame.K_DOWN]: move_player(0, 1)
                elif evt.key in [pygame.K_a, pygame.K_LEFT]: move_player(-1, 0)
                elif evt.key in [pygame.K_d, pygame.K_RIGHT]: move_player(1, 0)
                elif evt.key == pygame.K_t:
                    theme_index = (theme_index + 1) % len(theme_names)
                    apply_theme(themes[theme_names[theme_index]])

        draw(t)
        t += 0.05
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
