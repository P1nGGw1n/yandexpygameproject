Pygame
import pygame
import sys
import os

FPS = 30


def load_image(name, colorkey=None):
    fullname = os.path.join(r'C:\Users\Muza_\PycharmProjects\pythonProject', name)
    if not os.path.isfile(fullname):
        sys.exit()
    image = pygame.image.load(fullname)
    if name == "realheart.jpg":
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image


def game_over():
    global k
    k = False
    gameover = pygame.sprite.Sprite()
    gameover.image = load_image("gameover.jpg")
    gameover.rect = gameover.image.get_rect()
    all_sprites.add(gameover)
    gameover.image = pygame.transform.scale(gameover.image, (480, 400))
    gameover.x = 0
    gameover.y = 0
    all_sprites.add(gameover)


class Tower_1(pygame.sprite.Sprite):
    image = load_image("redshroom.png")

    def __init__(self, x, y, d, a_s):
        super().__init__(all_sprites)
        self.coor = (x * 40, y * 40)
        self.damage = d
        self.attack_speed = a_s
        self.image = Tower_1.image
        self.rect = self.image.get_rect()
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect.x, self.rect.y = self.coor
        global towers
        towers.append(self)

    def fire(self):
        global enemies, screen
        if len(enemies):
            enemy = enemies[-1]
            enemy.hit(self.damage)


class Tower_2(pygame.sprite.Sprite):
    image = load_image("greenshroom.png")

    def __init__(self, x, y, a_s):
        super().__init__(all_sprites)
        self.coor = (x * 40, y * 40)
        self.attack_speed = a_s
        self.image = Tower_2.image
        self.rect = self.image.get_rect()
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect.x, self.rect.y = self.coor
        global towers
        towers.append(self)

    def fire(self):
        global enemies, screen
        if len(enemies):
            enemy = enemies[-1]
            pygame.draw.line(screen, (0, 255, 0), (self.coor[0] + 20, self.coor[1] + 20),
                             (enemy.coor[0] + 10, enemy.coor[1] + 10))
            enemy.freeze = 1


class Enemy(pygame.sprite.Sprite):
    image = load_image("enemy.png")

    def __init__(self, s, h, x, y):
        self.dis = 0
        self.coor = (x * 40 + 10, y * 40 + 10)
        self.speed = s
        self.health = h
        self.freeze = 0
        super().__init__(all_sprites)
        self.image = Enemy.image
        self.rect = self.image.get_rect()
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect.x = x * 40 + 10
        self.rect.y = y * 40 + 10
        global enemies
        enemies.append(self)

    def update(self):
        global heartcnt, heart1, heart2, heart3, path
        if ((self.rect.x - 10) // 40, (self.rect.y - 10) // 40) == path[-1]:
            if heartcnt == 3:
                heart3.kill()
                heartcnt -= 1
                self.kill()
            elif heartcnt == 2:
                heart2.kill()
                heartcnt -= 1
                self.kill()
            elif heartcnt == 1:
                heart1.kill()
                heartcnt -= 1
                self.kill()
                game_over()
        self.rect.x, self.rect.y = path[int(self.dis)][0] * 40 + 10, path[int(self.dis)][1] * 40 + 10

    def __gt__(self, other):
        return self.dis > other.dis

    def __ge__(self, other):
        return self.dis >= other.dis

    def __lt__(self, other):
        return self.dis < other.dis

    def __le__(self, other):
        return self.dis <= other.dis

    def move(self):
        self.dis += self.speed * 0.8 ** self.freeze

    def hit(self, d):
        global enemies, money
        self.health -= d
        if self.health <= 0:
            money += 10
            self.kill()
            del enemies[-1]


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        global board
        board = self.board = [[0] * 8 for _ in range(12)]
        for i in range(12):
            for j in range(8):
                self.board[i][j] = Wall(i * 40, j * 40)
        self.left = 0
        self.top = 0
        self.cell_size = 30

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, screen):
        for i in range(self.width):
            for j in range(self.height):
                pygame.draw.rect(screen, "white", (self.left + i * self.cell_size, self.top + j * self.cell_size,
                                                   self.cell_size, self.cell_size), width=1)

    def get_cell(self, mouse_pos):
        a = (mouse_pos[0]) // 40
        b = (mouse_pos[1]) // 40
        if a < 12 and b < 8:
            return a, b
        return None

    def on_click(self, mouse_pos, left=False):
        global k, money, t1cnt, t2cnt
        cell_pos = self.get_cell(mouse_pos)
        if cell_pos is None:
            return
        i, j = cell_pos
        if k:
            if self.board[i][j].__class__ == PlaceForTower:
                if not left and money >= 25 * 2 ** t1cnt:
                    self.board[i][j] = Tower_1(i, j, 150, 25)
                    money -= 25 * 2 ** t1cnt
                    t1cnt += 1
                elif left and money >= 25 * 2 ** t2cnt:
                    self.board[i][j] = Tower_2(i, j, 25)
                    money -= 25 * 2 ** t2cnt
                    t2cnt += 1

        else:
            if not left:
                if self.board[i][j].__class__ == Wall:
                    self.board[i][j].kill()
                    self.board[i][j] = Road(i * 40, j * 40)
                elif self.board[i][j].__class__ == Road:
                    self.board[i][j].kill()
                    self.board[i][j] = PlaceForTower(i * 40, j * 40)
                elif self.board[i][j].__class__ == StartPoint or self.board[i][j].__class__ == PlaceForTower or \
                        self.board[i][j].__class__ == EndPoint:
                    self.board[i][j].kill()
                    self.board[i][j] = Wall(i * 40, j * 40)
            else:
                if self.board[i][j].__class__ == Wall or self.board[i][j].__class__ == PlaceForTower or Road == \
                        self.board[i][j].__class__:
                    self.board[i][j].kill()
                    self.board[i][j] = StartPoint(i * 40, j * 40)
                elif self.board[i][j].__class__ == StartPoint:
                    self.board[i][j].kill()
                    self.board[i][j] = EndPoint(i * 40, j * 40)
                elif self.board[i][j].__class__ == EndPoint:
                    self.board[i][j].kill()
                    self.board[i][j] = Wall(i * 40, j * 40)

    def find_path(self):
        global running, k
        dis = [[1000] * 8 for _ in range(12)]
        prev = [[None] * 8 for _ in range(12)]
        global xs, ys, xe, ye
        xs, ys = None, None
        xe, ye = None, None
        z = []
        for i in range(12):
            for j in range(8):
                if self.board[i][j].__class__ == StartPoint:
                    xs, ys = i, j
                if self.board[i][j].__class__ == EndPoint:
                    xe, ye = i, j
        try:
            q = [(xs, ys)]
            while q:
                x, y = q.pop(0)
                for dx, dy in (1, 0), (0, 1), (-1, 0), (0, -1):
                    x1, y1 = x + dx, y + dy
                    if 0 <= x1 < 12 and 0 <= y1 < 8 and self.board[x1][y1].__class__ in (Road, EndPoint) and dis[x1][
                        y1] == 1000:
                        dis[x1][y1] = dis[x][y] + 1
                        prev[x1][y1] = (x, y)
                        q.append((x1, y1))
            if dis[xe][ye] == 1000:
                return False
            z.append((xe, ye))
            while prev[xe][ye] != (xs, ys):
                z.insert(0, prev[xe][ye])
                xe, ye = prev[xe][ye]
            z.insert(0, prev[xe][ye])
            return z
        except:
            k = False


class Road(pygame.sprite.Sprite):
    image = load_image(r"trueroad.jpg")

    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.image = Road.image
        self.rect = self.image.get_rect()
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect.x = x
        self.rect.y = y


class Wall(pygame.sprite.Sprite):
    image = load_image(r"wall.jpg")

    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.image = Wall.image
        self.rect = self.image.get_rect()
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect.x = x
        self.rect.y = y


class PlaceForTower(pygame.sprite.Sprite):
    image = load_image(r"towerplace.png")

    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.image = PlaceForTower.image
        self.rect = self.image.get_rect()
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect.x = x
        self.rect.y = y


class StartPoint(pygame.sprite.Sprite):
    image = load_image(r"start.jpg")

    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.image = StartPoint.image
        self.rect = self.image.get_rect()
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect.x = x
        self.rect.y = y

    def update(self):
        global xs, ys, time
        if time % (100 * 0.9 ** (time // 500)) == 10:
            Enemy(0.1, int(200 * 1.1 ** (time // 500)), xs, ys)


class EndPoint(pygame.sprite.Sprite):
    image = load_image(r"finish.jpg")

    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.image = EndPoint.image
        self.rect = self.image.get_rect()
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect.x = x
        self.rect.y = y


def draw(screen):
    global t1cnt, t2cnt, money
    screen.fill((0, 0, 0))
    font = pygame.font.Font(None, 40)
    text = font.render(f"Money: {money}", True, (100, 255, 100))
    text1 = font.render(f"Price 1: {25 * 2 ** t1cnt}", True, (100, 255, 100))
    text2 = font.render(f"Price 2: {25 * 2 ** t2cnt}", True, (100, 255, 100))
    text_x = 300
    text_y = 320
    screen.blit(text, (text_x, text_y))
    screen.blit(text1, (text_x, text_y + text.get_height()))
    screen.blit(text2, (text_x, text_y + text.get_height() + text1.get_height()))


def solution():
    global path, enemies, towers, money, time, k, t1cnt, t2cnt
    board = Board(12, 8)
    board.set_view(0, 0, 40)
    global heartcnt, heart1, heart2, heart3
    heartcnt = 3
    heart1 = HeartContainer(0, 320)
    heart2 = HeartContainer(100, 320)
    heart3 = HeartContainer(200, 320)
    t1cnt, t2cnt = 0, 0
    running = True
    time = 0
    money = 100
    enemies = []
    k = False
    pygame.time.set_timer(FPS, 50)
    towers = []
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    path = board.find_path()
                    k = True
                    print(path)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[2]:
                    board.on_click(event.pos, left=True)
                if pygame.mouse.get_pressed()[0]:
                    board.on_click(event.pos)
            if event.type == FPS:
                time += 1
                for enemy in enemies:
                    enemy.move()
                enemies.sort()
                for tower in towers:
                    if time % tower.attack_speed == 0:
                        tower.fire()
                if k:
                    all_sprites.update()
        screen.fill("blue")
        board.render(screen)
        draw(screen)
        all_sprites.draw(screen)
        pygame.display.flip()


class HeartContainer(pygame.sprite.Sprite):
    image = load_image(r"realheart.jpg")

    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.image = HeartContainer.image
        self.rect = self.image.get_rect()
        self.image = pygame.transform.scale(self.image, (100, 80))
        self.rect.x = x
        self.rect.y = y


if __name__ == '__main__':
    pygame.init()
    size = 480, 400
    global screen
    screen = pygame.display.set_mode(size)
    all_sprites = pygame.sprite.Group()
    solution()
    pygame.quit()
