import pygame
import random
import math
import ctypes
import time

pygame.init()

IMAGE_PATH = r"C:\Users\Kozak\Desktop\pisiyi.jpg"
image = pygame.image.load(IMAGE_PATH)
WIDTH, HEIGHT = image.get_size()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)

hwnd = pygame.display.get_wm_info()['window']
user32 = ctypes.windll.user32
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
LWA_COLORKEY = 0x00000001

COLORKEY_RGB = (255, 0, 255)
COLORKEY = COLORKEY_RGB[0] | (COLORKEY_RGB[1] << 8) | (COLORKEY_RGB[2] << 16)

exstyle = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
user32.SetWindowLongW(hwnd, GWL_EXSTYLE, exstyle | WS_EX_LAYERED)
user32.SetLayeredWindowAttributes(hwnd, COLORKEY, 255, LWA_COLORKEY)

class Fragment:
    def __init__(self, polygon_pts, src_image, cx, cy):
        self.cx = cx
        self.cy = cy
        angle = math.atan2(cy - HEIGHT/2, cx - WIDTH/2)
        speed = random.uniform(3, 8)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.gravity = 0.3
        self.rotation = 0
        self.rotation_speed = random.uniform(-10, 10)

        min_x = int(min(p[0] for p in polygon_pts))
        max_x = int(max(p[0] for p in polygon_pts))
        min_y = int(min(p[1] for p in polygon_pts))
        max_y = int(max(p[1] for p in polygon_pts))
        w = max_x - min_x
        h = max_y - min_y

        local_poly = [(x - min_x, y - min_y) for x, y in polygon_pts]

        tex = pygame.Surface((w, h), pygame.SRCALPHA)
        tex.blit(src_image.subsurface((min_x, min_y, w, h)), (0, 0))
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.polygon(mask, (255, 255, 255, 255), local_poly)
        tex.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        self.surface = tex

    def update(self):
        self.cx += self.vx
        self.cy += self.vy
        self.vy += self.gravity
        self.rotation += self.rotation_speed

    def draw(self, target):
        rotated = pygame.transform.rotate(self.surface, self.rotation)
        rect = rotated.get_rect(center=(self.cx, self.cy))
        target.blit(rotated, rect.topleft)

def create_fragments():
    fragments = []
    grid = 8
    cw = WIDTH // grid
    ch = HEIGHT // grid

    pts = []
    for i in range(grid + 1):
        for j in range(grid + 1):
            x = max(0, min(WIDTH,  i * cw + random.randint(-cw//4, cw//4)))
            y = max(0, min(HEIGHT, j * ch + random.randint(-ch//4, ch//4)))
            pts.append((x, y))

    for i in range(grid):
        for j in range(grid):
            idx = i * (grid + 1) + j
            poly = [pts[idx], pts[idx+1], pts[idx+grid+2], pts[idx+grid+1]]
            cx = sum(p[0] for p in poly) / 4
            cy = sum(p[1] for p in poly) / 4
            min_x = int(min(p[0] for p in poly))
            max_x = int(max(p[0] for p in poly))
            min_y = int(min(p[1] for p in poly))
            max_y = int(max(p[1] for p in poly))
            if max_x > WIDTH or max_y > HEIGHT or min_x < 0 or min_y < 0:
                continue
            if max_x - min_x <= 0 or max_y - min_y <= 0:
                continue
            fragments.append(Fragment(poly, image, cx, cy))
    return fragments

breaking = False
fragments = []
break_time = 0
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit(); raise SystemExit
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if not breaking:
                breaking = True
                fragments = create_fragments()
                break_time = time.time()

    screen.fill(COLORKEY_RGB)

    if not breaking:
        screen.blit(image, (0, 0))
    else:
        for f in fragments:
            f.update()
            f.draw(screen)
        if time.time() - break_time > 2:
            pygame.quit(); raise SystemExit

    pygame.display.flip()
    clock.tick(60)
