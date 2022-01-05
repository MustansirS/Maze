import pygame, random

WIDTH = 1000
HEIGHT = 760
#WIDTH = 600
#HEIGHT = 600
BLOCK_SIDE = 40
HALF_SIDE = int(BLOCK_SIDE / 2)
NX, NY = int(WIDTH / BLOCK_SIDE), int(HEIGHT / BLOCK_SIDE)
if BLOCK_SIDE != int(WIDTH / NX) or BLOCK_SIDE != int(HEIGHT / NY):
    print("Error")
    exit()
PLAYER_SIZE = int((BLOCK_SIDE-0.3*BLOCK_SIDE)/2)
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.font.init()
FONT = pygame.font.SysFont('Comic Sans MS', 30)
HEADING = FONT.render('Solve the Maze', False, (0,0,0))
DIFFICULTY_TEXT = FONT.render('Select Difficulty', False, (0,0,0))
PLAY_TEXT = FONT.render('Play', False, (0,0,0))
QUIT_TEXT = FONT.render('Quit', False, (0,0,0))
PLAY_TEXT_SELECTED = FONT.render('Play', False, (0,255,0))
QUIT_TEXT_SELECTED = FONT.render('Quit', False, (0,255,0))
DIFFICULTY_SELECTOR = [FONT.render('%d' % (x+1), False, (0,0,0)) for x in range(10)]
DIFFICULTY_SELECTOR_SELECTED = [FONT.render('%d' % (x+1), False, (0,255,0)) for x in range(10)]
BLOCK_VISITED = (255, 230, 102)
BLOCK_CORRECT = (195, 255, 0)
BLOCK_VISITED_CORRECT = (0, 157, 255)
START_POINT_COLOR = (0, 255, 0)
END_POINT_COLOR = (255, 0, 0)


class Player():
    def __init__(self, x, y, r, color):
        self.x = x
        self.y = y
        self.r = r
        self.color = color
        self.center = (x,y)
        self.vel = 2

    def draw(self, win):
        pygame.draw.circle(win, self.color, self.center, self.r)

    def move(self, maze):
        keys = pygame.key.get_pressed()
        prevx = self.x
        prevy = self.y

        if keys[pygame.K_LEFT]:
            self.x -= self.vel

        if keys[pygame.K_RIGHT]:
            self.x += self.vel

        if keys[pygame.K_UP]:
            self.y -= self.vel

        if keys[pygame.K_DOWN]:
            self.y += self.vel

        if self.x + PLAYER_SIZE > WIDTH:
            self.x = WIDTH - PLAYER_SIZE
        if self.x - PLAYER_SIZE < 0:
            self.x = PLAYER_SIZE
        if self.y + PLAYER_SIZE > HEIGHT:
            self.y = HEIGHT - PLAYER_SIZE
        if self.y - PLAYER_SIZE < 0:
            self.y = PLAYER_SIZE

        self.x, self.y = maze.correction(self.x, self.y, prevx, prevy)

        self.center = (self.x, self.y)

    def won(self, maze):
        return maze.won(self.x, self.y)

class Computer():
    def __init__(self, x, y, r, color):
        self.x = x
        self.y = y
        self.r = r
        self.color = color
        self.center = (x,y)
        self.vel = 2

    def draw(self, win):
        pygame.draw.circle(win, self.color, self.center, self.r)

    def move(self, maze):
        prevx = self.x
        prevy = self.y
        cx = int(prevx / BLOCK_SIDE)
        cy = int(prevy / BLOCK_SIDE)
        if cx != 0 and maze.cell_at(cx-1,cy).part_of_solved and not maze.cell_at(cx-1,cy).visited and not maze.cell_at(cx,cy).walls['W']:
            self.x -= self.vel
        elif cx != NX-1 and maze.cell_at(cx+1,cy).part_of_solved and not maze.cell_at(cx+1,cy).visited and not maze.cell_at(cx,cy).walls['E']:
            self.x += self.vel
        elif cy != 0 and maze.cell_at(cx,cy-1).part_of_solved and not maze.cell_at(cx,cy-1).visited and not maze.cell_at(cx,cy).walls['N']:
            self.y -= self.vel
        elif cy != NY-1 and maze.cell_at(cx,cy+1).part_of_solved and not maze.cell_at(cx,cy+1).visited and not maze.cell_at(cx,cy).walls['S']:
            self.y += self.vel

        if self.x + PLAYER_SIZE > WIDTH:
            self.x = WIDTH - PLAYER_SIZE
        if self.x - PLAYER_SIZE < 0:
            self.x = PLAYER_SIZE
        if self.y + PLAYER_SIZE > HEIGHT:
            self.y = HEIGHT - PLAYER_SIZE
        if self.y - PLAYER_SIZE < 0:
            self.y = PLAYER_SIZE

        self.x, self.y = maze.correction(self.x, self.y, prevx, prevy)

        self.center = (self.x, self.y)

    def won(self, maze):
        return maze.won(self.x, self.y)


class Cell():
    wall_pairs = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}

    def __init__(self, x, y, wall_color):
        self.x, self.y = x, y
        self.walls = {'N': True, 'S': True, 'E': True, 'W': True}
        self.color = wall_color
        self.lu = (self.x*BLOCK_SIDE,self.y*BLOCK_SIDE)
        self.ru = ((self.x+1)*BLOCK_SIDE,self.y*BLOCK_SIDE)
        self.ld = (self.x*BLOCK_SIDE,(self.y+1)*BLOCK_SIDE)
        self.rd = ((self.x+1)*BLOCK_SIDE,(self.y+1)*BLOCK_SIDE)
        self.visited = False
        self.part_of_solved = False
        self.reveal = False

    def has_all_walls(self):
        return all(self.walls.values())

    def knock_down_wall(self, other, wall):
        self.walls[wall] = False
        other.walls[Cell.wall_pairs[wall]] = False

    def draw(self, win):
        if self.reveal:
            if self.visited and not self.part_of_solved:
                l,u = self.lu
                pygame.draw.rect(win,BLOCK_VISITED,(l,u,BLOCK_SIDE,BLOCK_SIDE),0)
            if self.part_of_solved and not self.visited:
                l,u = self.lu
                pygame.draw.rect(win,BLOCK_CORRECT,(l,u,BLOCK_SIDE,BLOCK_SIDE),0)
            if self.visited and self.part_of_solved:
                l,u = self.lu
                pygame.draw.rect(win,BLOCK_VISITED_CORRECT,(l,u,BLOCK_SIDE,BLOCK_SIDE),0)
        else:
            if self.visited:
                l,u = self.lu
                pygame.draw.rect(win,BLOCK_VISITED,(l,u,BLOCK_SIDE,BLOCK_SIDE),0)
        if self.walls['N']:
            pygame.draw.line(win,self.color,self.lu,self.ru,2)
        if self.walls['S']:
            pygame.draw.line(win,self.color,self.ld,self.rd,2)
        if self.walls['E']:
            pygame.draw.line(win,self.color,self.ru,self.rd,2)
        if self.walls['W']:
            pygame.draw.line(win,self.color,self.lu,self.ld,2)

    def correction(self, posx, posy, new_cell):
        if self.walls['N']:
            if posy - PLAYER_SIZE < self.y*BLOCK_SIDE:
                posy = self.y*BLOCK_SIDE + PLAYER_SIZE
        if self.walls['S']:
            if posy + PLAYER_SIZE > (self.y+1)*BLOCK_SIDE:
                posy = (self.y+1)*BLOCK_SIDE - PLAYER_SIZE
        if self.walls['E']:
            if posx + PLAYER_SIZE > (self.x+1)*BLOCK_SIDE:
                posx = (self.x+1)*BLOCK_SIDE - PLAYER_SIZE
        if self.walls['W']:
            if posx - PLAYER_SIZE < self.x*BLOCK_SIDE:
                posx = self.x*BLOCK_SIDE + PLAYER_SIZE
        if new_cell.x == self.x and new_cell.y == self.y:
            pass
        else:
            if self.x-1 == new_cell.x and self.y-1 == new_cell.y and new_cell.walls['E'] and new_cell.walls['S']:
                posx = self.x*BLOCK_SIDE + PLAYER_SIZE
                posy = self.y*BLOCK_SIDE + PLAYER_SIZE
            if self.x-1 == new_cell.x and self.y+1 == new_cell.y and new_cell.walls['E'] and new_cell.walls['N']:
                posx = self.x*BLOCK_SIDE + PLAYER_SIZE
                posy = (self.y+1)*BLOCK_SIDE - PLAYER_SIZE
            if self.x+1 == new_cell.x and self.y-1 == new_cell.y and new_cell.walls['W'] and new_cell.walls['S']:
                posx = (self.x+1)*BLOCK_SIDE - PLAYER_SIZE
                posy = self.y*BLOCK_SIDE + PLAYER_SIZE
            if self.x+1 == new_cell.x and self.y+1 == new_cell.y and new_cell.walls['W'] and new_cell.walls['N']:
                posx = (self.x+1)*BLOCK_SIDE - PLAYER_SIZE
                posy = (self.y+1)*BLOCK_SIDE - PLAYER_SIZE
        return posx, posy

    def mark_visited(self):
        self.visited = True

    def mark_part_of_solved(self):
        self.part_of_solved = True


class Maze():
    def __init__(self, nx, ny, wall_color, ix=0, iy=0):
        self.nx, self.ny = nx, ny
        self.ix, self.iy = ix, iy
        self.maze_map = [[Cell(x, y, wall_color) for y in range(ny)] for x in range(nx)]
        self.solving_visited = [[False for y in range(ny)] for x in range(nx)]
        corners = [(0,int((ny-1)/2)),(nx-1,int((ny-1)/2)),(int((nx-1)/2),0),(int((nx-1)/2),ny-1)]
        self.endpoint = random.choice(corners)
        a,b = self.endpoint
        if a in [0,nx-1]:
            a = nx-1 - a
            b = 0
        elif b in [0,ny-1]:
            b = ny-1 - b
            a = 0
        self.startpoint = (a,b)

    def create_copy(self, maze):
        maze.endpoint = self.endpoint
        ea, eb = self.endpoint
        if ea in [0,self.nx-1]:
            ea = self.nx-1 - ea
            eb = self.ny-1
        elif eb in [0,self.ny-1]:
            eb = self.ny-1 - eb
            ea = self.nx-1
        maze.startpoint = (ea,eb)
        if maze.nx != self.nx or maze.ny != self.ny:
            return
        for x in range(self.nx):
            for y in range(self.ny):
                maze.cell_at(x,y).walls = self.cell_at(x,y).walls

    def cell_at(self, x, y):
        return self.maze_map[x][y]

    def find_valid_neighbours(self, cell):
        delta = [('W', (-1, 0)),
                 ('E', (1, 0)),
                 ('S', (0, 1)),
                 ('N', (0, -1))]
        neighbours = []
        for direction, (dx, dy) in delta:
            x2, y2 = cell.x + dx, cell.y + dy
            if (0 <= x2 < self.nx) and (0 <= y2 < self.ny):
                neighbour = self.cell_at(x2, y2)
                if neighbour.has_all_walls():
                    neighbours.append((direction, neighbour))
        return neighbours

    def make_maze(self):
        n = self.nx * self.ny
        cell_stack = []
        current_cell = self.cell_at(self.ix, self.iy)
        nv = 1

        while nv < n:
            neighbours = self.find_valid_neighbours(current_cell)

            if not neighbours:
                current_cell = cell_stack.pop()
                continue

            direction, next_cell = random.choice(neighbours)
            current_cell.knock_down_wall(next_cell, direction)
            cell_stack.append(current_cell)
            current_cell = next_cell
            nv += 1

    def solve_maze(self, sx, sy):
        if (sx,sy) == self.endpoint:
            self.cell_at(sx,sy).mark_part_of_solved()
            return True
        if self.solving_visited[sx][sy]:
            return False
        self.solving_visited[sx][sy] = True
        if sx != 0 and not self.cell_at(sx,sy).walls['W']:
            if self.solve_maze(sx-1,sy):
                self.cell_at(sx,sy).mark_part_of_solved()
                return True
        if sx != self.nx - 1 and not self.cell_at(sx,sy).walls['E']:
            if self.solve_maze(sx+1,sy):
                self.cell_at(sx,sy).mark_part_of_solved()
                return True
        if sy != 0 and not self.cell_at(sx,sy).walls['N']:
            if self.solve_maze(sx,sy-1):
                self.cell_at(sx,sy).mark_part_of_solved()
                return True
        if sy != self.ny - 1 and not self.cell_at(sx,sy).walls['S']:
            if self.solve_maze(sx,sy+1):
                self.cell_at(sx,sy).mark_part_of_solved()
                return True
        return False

    def draw(self, win):
        for x in range(self.nx):
            for y in range(self.ny):
                self.cell_at(x,y).draw(win)
        a,b = self.startpoint
        pygame.draw.circle(win,START_POINT_COLOR,((a*BLOCK_SIDE)+HALF_SIDE,(b*BLOCK_SIDE)+HALF_SIDE),HALF_SIDE)
        a,b = self.endpoint
        pygame.draw.circle(win,END_POINT_COLOR,((a*BLOCK_SIDE)+HALF_SIDE,(b*BLOCK_SIDE)+HALF_SIDE),HALF_SIDE)

    def correction(self, posx, posy, prevx, prevy):
        x = int(prevx / BLOCK_SIDE)
        y = int(prevy / BLOCK_SIDE)
        new_x = int(posx / BLOCK_SIDE)
        new_y = int(posy / BLOCK_SIDE)
        self.cell_at(x,y).mark_visited()
        return self.cell_at(x,y).correction(posx,posy,self.cell_at(new_x,new_y))

    def won(self, posx, posy):
        x = int(posx / BLOCK_SIDE)
        y = int(posy / BLOCK_SIDE)
        return (x,y) == self.endpoint

    def reveal(self):
        for x in range(self.nx):
            for y in range(self.ny):
                self.cell_at(x,y).reveal = True

    def hide(self):
        for x in range(self.nx):
            for y in range(self.ny):
                self.cell_at(x,y).reveal = False


def redrawWindow(win,player,computer,maze):
    win.fill((255,255,255))
    maze.draw(win)
    player.draw(win)
    computer.draw(win)
    pygame.display.update()

def redrawStart(win, heading, play_text, quit_text):
    win.fill((255,255,255))
    win.blit(heading,(int(WIDTH*0.3),int(HEIGHT*0.1)))
    win.blit(play_text,(int(WIDTH*0.4),int(HEIGHT*0.4)))
    win.blit(quit_text,(int(WIDTH*0.4),int(HEIGHT*0.4)+30))
    pygame.display.update()

def redrawDifficulty(win, selector):
    win.fill((255,255,255))
    win.blit(DIFFICULTY_TEXT,(int(WIDTH*0.3),int(HEIGHT*0.1)))
    for x in range(10):
        if selector != x + 1:
            win.blit(DIFFICULTY_SELECTOR[x],(int(WIDTH*0.4),x*30+int(HEIGHT*0.25)))
        else:
            win.blit(DIFFICULTY_SELECTOR_SELECTED[x],(int(WIDTH*0.4),x*30+int(HEIGHT*0.25)))
    pygame.display.update()

ARROW_KEYS = [pygame.K_UP,pygame.K_DOWN,pygame.K_RIGHT,pygame.K_LEFT]

def main(difficulty):
    run = True
    quit = False
    m = Maze(NX,NY,(0,0,0))
    m.make_maze()
    copy = Maze(NX,NY,(0,0,0))
    m.create_copy(copy)
    a,b = m.startpoint
    p = Player((a*BLOCK_SIDE)+HALF_SIDE,(b*BLOCK_SIDE)+HALF_SIDE,PLAYER_SIZE,(0,0,0))
    na,nb = copy.startpoint
    c = Computer((na*BLOCK_SIDE)+HALF_SIDE,(nb*BLOCK_SIDE)+HALF_SIDE,PLAYER_SIZE,(0,0,0))
    m.solve_maze(a,b)
    copy.solve_maze(na,nb)
    clock = pygame.time.Clock()
    input_word = ''
    diff = 11 - difficulty

    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                quit = True
            if event.type == pygame.KEYDOWN:
                if event.key in ARROW_KEYS:
                    continue
                input_word += pygame.key.name(event.key)
                if event.key == pygame.K_ESCAPE:
                    input_word = ''
                if input_word == "reveal":
                    input_word = ''
                    m.reveal()
                if input_word == "hide":
                    input_word = ''
                    m.hide()
                if len(input_word) >= 6:
                    input_word = ''
        if run:
            p.move(m)
            diff -= 1
            if diff == 0:
                c.move(copy)
                diff = 11 - difficulty
        if p.won(m) or c.won(m):
            run = False
        redrawWindow(WINDOW, p, c, m)
    if quit:
        pygame.quit()
        return
    start_menu()

def difficulty_select():
    run = True
    clock = pygame.time.Clock()
    selector = 1
    quit = False

    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                quit = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selector -= 1
                if event.key == pygame.K_DOWN:
                    selector += 1
                if selector <= 0:
                    selector = 10
                elif selector >= 11:
                    selector = 1
                if event.key == pygame.K_SPACE:
                    run = False
        redrawDifficulty(WINDOW, selector)
    if quit:
        pygame.quit()
        return
    main(selector)

def start_menu():
    run = True
    quit = False
    clock = pygame.time.Clock()
    selector = 1

    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                quit = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    selector = selector % 2 + 1
                if event.key == pygame.K_SPACE:
                    run = False
        if selector == 1:
            redrawStart(WINDOW, HEADING, PLAY_TEXT_SELECTED, QUIT_TEXT)
        elif selector == 2:
            redrawStart(WINDOW, HEADING, PLAY_TEXT, QUIT_TEXT_SELECTED)
    if quit:
        pygame.quit()
        return
    if selector == 1:
        difficulty_select()
    elif selector == 2:
        pygame.quit()

start_menu()
