from __future__ import print_function
import curses
import random
import collections
from random import randint, shuffle, choice
import pad2 as p
import enemies as e
import items

def clear_doors(win, doors):
    """
    row, col- coordinates of door
    """
    space = ' '
    neighbors = [(-1, 0), (0,1), (1,0), (0, -1), (1,1), (1, -1), (-1, 1), (2,2), (-2,-2), (-2, 2), (2,-1),(-2, 0), (0,2), (2,0), (0, -2), (3,3),(-3,-3),(3,-3),(-3,3),(-3, 0), (0,3), (3,0), (0, -3)]
    for dr, dc in doors:
        for nr, nc in neighbors:
            if win.instr(dr+nr, dc+nc, 1) == ',':
                win.addstr(dr+nr, dc+nc, space)

def add_doors(room, r, c):
    """
    r,c- top left corner
    """
    num = randint(2, 4)
    sides = random.sample(['n', 's', 'e', 'w'], num)
    for side in sides:
        if side == 'n':
            if r - 5 > 0:
                col = randint(1, len(room[0])-2)
                room[0][col] = '+'
            elif len(sides) < 3:
                if 's' not in sides:
                    sides.append('s')
                else:
                    ch = random.sample(['e', 'w'], 1)
                    sides.append(ch)
        elif side == 'w':
            if c - 5 > 0:
                row = randint(1, len(room)-2)
                room[row][0] = '+'
            elif len(sides) < 3:
                if 'e' not in sides:
                    sides.append('e')
                else:
                    ch = random.sample(['s', 'n'], 1)
                    sides.append(ch)
        elif side == 'e':
            if p.max_x - (c + len(room[0])) > 5:
                row = randint(1, len(room) - 2)
                room[row][len(room[0]) - 1] = '+'
            elif len(sides) < 3:
                if 'w' not in sides:
                    sides.append('w')
                else:
                    ch = random.sample(['s', 'n'], 1)
                    sides.append(ch)
                sides.append('w')
        elif side == 's':
            if p.max_y - (r + len(room)) > 5:
                col = randint(1, len(room[0]) -2)
                room[len(room)-1][col] = '+'
            elif len(sides) < 3:
                if 'n' not in sides:
                    sides.append('n')
                else:
                    ch = random.sample(['e', 'w'], 1)
                    sides.append(ch)

def connect_rooms(win, room_doors):
    graph = make_graph(win)

    room_keys = room_doors.keys()
    visited = list()

    next_room = room_keys.pop()
    while room_keys:
        cur_room = next_room
        next_room = room_keys.pop()
        path = False
        while not path:
            door = choice(room_doors[cur_room])
            next_door = choice(room_doors[next_room])
            path = build_corridor(win, door, next_door, graph)
        visited.append(door)
        visited.append(next_door)
        print_solution(win, door, next_door, path)

    doors = list()
    for room in room_doors:
        for door in room_doors[room]:
            if door not in visited:
                doors.append(door)

    shuffle(doors)

    while len(doors) > 1:
        path = False
        count = 0
        while not path:
            door = next_door = choice(doors)
            while door == next_door:
                next_door = choice(doors)
            path = build_corridor(win, door, next_door, graph)
            count+=1
            if count == 100:
                break
        if path:
            doors.remove(door)
            doors.remove(next_door)
            print_solution(win, door, next_door, path)
        else:
            break

    for door in doors:
        path = False
        start = door
        count = 0
        while not path:
            end = ','
            while end != ' ':
                r = randint(10, p.max_y - 10)
                c = randint(10, p.max_x - 10)
                end = win.instr(r, c, 1)
            path = build_corridor(win, start, (r,c), graph)
            count+=1
            if count == 100:
                break
        if not path:
            tile = list()
            row, col = door
            tile.append(win.instr(row + 1 , col, 1))
            tile.append(win.instr(row-1, col, 1))
            if '|' not in tile:
                win.addstr(row, col, '-')
            else:
                win.addstr(row, col, '|')
        else:
            print_solution(win, start, (r,c), path)


def build_corridor(win, start, end, graph):
    visited = collections.defaultdict(list)
    q = collections.deque()
    q.append(start)
    visited[start]

    while q:
        cur = q.popleft()
        if cur == end:
            return visited
        for n in graph[cur]:
            if n not in visited:
                q.append(n)
                visited[n].append(cur)

    return False

def make_graph(win):
    """
    graph will consist of only empty cells.
    REMEMBER this when trying to connect to
    doors which ar non empty cells
    """
    rows = p.max_y
    cols = p.max_x
    graph = collections.defaultdict(list)
    neighbors = [(-1, 0), (0,1), (1,0), (0, -1)]
    for r in range(rows):
        for c in range(cols):
            ch = win.instr(r, c, 1)
            if ch == ' ' or ch == '+':
                for y, x in neighbors:
                    if (r+y) <= rows and (c+x) <= cols and (r+y) >= 0 and (c+x) >= 0:
                         nch = win.instr(r, c, 1)
                         if nch == ' ' or nch == '+':
                            graph[(r,c)].append((r+y, c+x))
                         #else:
                            #graph[(r,c)].append()
    return graph

def print_solution(win, start, end, path):
    rows = p.max_y
    cols = p.max_x

    if path:
        r, c = parent = path[end][0]
        win.addch(r, c, ord('#'))
        while parent != start:
            r, c = parent = path[parent][0]
            if win.instr(r, c, 1) != '+':
                win.addch(r, c, ord('#'))
    else:
        return False

def generate_maze(win):
    rows, cols = win.getmaxyx()#curses detects size of screen
    for y in range(rows):
        for x in range(cols):
            try:
                ch = random.sample(['','','','','','','','', '', ','],1)
                if ch[0]:
                    win.addch(y, x, ord(ch[0]))
            except (curses.error):
                pass

def random_room():
    """
    sizes can be changed, also note:
    rows and columns are not equal sizes
    (eg: a 10x10 curses window is not square)
    which is why the width is longer than the length
    """
    min_length = 9
    max_length = 16
    min_width = 14
    max_width = 26

    length = randint(min_length, max_length)
    width = randint(min_width, max_width)
    room = [["." for x in xrange(width)] for y in xrange(length)]

    for col in range(width):
        room[0][col] = room[length - 1][col] = '-'
    for row in range(length):
        room[row][0] = room[row][width - 1] = '|'

    return (length, width, room)

def add_stairs(pad, level):

    kr = randint(1, p.max_y)
    kc = randint(1, p.max_x)
    tile = pad.instr(kr, kc, 1)

    while tile != '.':
        kr = randint(1, p.max_y)
        kc = randint(1, p.max_x)
        tile = pad.instr(kr, kc, 1)


    max_row = min_row = kr
    max_col = min_col = kc

    edges = ['+', '|', '-']

    while pad.instr(max_row, kc, 1) not in edges:
        max_row += 1

    while pad.instr(min_row, kc, 1) not in edges:
        min_row -= 1

    while pad.instr(kr, max_col, 1) not in edges:
        max_col += 1

    while pad.instr(kr, min_col, 1) not in edges:
        min_col -= 1

    kr = (max_row + min_row) / 2
    kc = (max_col + min_col) / 2

    pad.addstr(kr, kc, '%')

    if level == 15:
        neighbors = [(-1, 0), (0,1), (1,0), (0, -1), (1,1), (1, -1), (-1, 1), (-1,-1)]
        for nr, nc in neighbors:
            pad.addstr(kr+nr, kc+nc, '%')

    return (kr, kc)

def curses_room(r, c, win, col_end, row_end, enemies, level):
    """
    r,c- upper left corner of room
    """
    doors = list()
    lines, cols, room = random_room()
    room = e.add_enemies_room(lines, cols, room)
    #room = add_items(lines, cols, room)
    r, c = check_room_overlap(r, c, win, room, col_end, row_end)
    add_doors(room, r, c)
    control = c
    for x in xrange(lines):
        for y in xrange(cols):
            win.addstr(r, c, room[x][y])
            if room[x][y] == '+':
                doors.append((r,c))
            elif room[x][y] == 'E':
                    enemy = random.choice(e.enemy_types) #string of enemy name
                    enemy = e.init_enemy(enemy,(r,c), level)
                    enemies.append(enemy)
                    win.addstr(r,c,enemy.character)
                    if enemy.name == 'Arachnid':
                        neighbors = [(-1, 0), (0,1), (1,0), (0, -1)]
                        count = 0
                        for nr, nc in neighbors:
                            if room[nr+x][nc+y] == '.':
                                room[nr+x][nc+y] = 'A'
                                enemies.append(e.Arachnid(level, (nr+r, nc+c)))
                                win.addstr(nr+r, nc+c, 'A')
                                count += 1
                                if count == 2:
                                    break
            c+=1
        r+=1
        c = control

    clear_doors(win, doors)
    return doors

def check_room_overlap(r, c, win, room, col_end, row_end):
    max_row, max_col = win.getmaxyx()
    room_rows = len(room)
    room_cols = len(room[0])

    if r + room_rows > row_end:
        r = ((r - r + room_rows- row_end) * -1) - 2
    if c + room_cols > col_end:
        c = ((c - c + room_cols - col_end) * -1) - 2

    return r, c

def generate_rooms(win, enemies, level, cetus_amulet_level):
    random.seed()
    max_rows = p.max_y-2
    max_cols = p.max_x-2
    height = max_rows / 3
    width = max_cols / 6
    row_start = 0
    row_end = height
    col_start = 0
    col_end = width
    room_num = 0
    room_doors = collections.defaultdict(list)
    stair_flag = False
    stair_position = None
    generate_maze(win)

    for i in range(3):
        for j in range(6):
            r = randint(row_start, row_end)
            c = randint(col_start, col_end)
            flag = random.choice([1, 1, 1, 1, 1, 0, 0, 0, 0, 0])
            if flag:
                doors = curses_room(r, c, win, col_end, row_end, enemies, level)
                room_doors[room_num] = doors
                room_num+=1
            col_start += width
            col_end += width
        row_start += height
        row_end += height
        col_start = 0
        col_end = width
    global key
    global stairs
    key = items.add_key(win)
    stairs = add_stairs(win, level)
    map_items = items.add_items(win, level, cetus_amulet_level)
    #clear_doors(win, doors)
    connect_rooms(win, room_doors)
    return map_items

def curses_init():
    win = curses.initscr()#initialize window
    curses.noecho()#prevent keystrokes echoing on screen
    curses.curs_set(0)
    win.keypad(1)#allow curses to interpret certiain special keys
    curses.cbreak()#remove need to press enter after keystrokes
    win.keypad(1)
    return win

def curses_deinit(win):
    curses.nocbreak()
    win.keypad(0)
    curses.echo()
    curses.endwin()

def main():
    random.seed()
    win = curses_init()
    cmd = ''
    while cmd != 27:
        generate_rooms(win)
        curses.doupdate()
        cmd = win.getch()
        win.erase()
    curses_deinit(win)

if __name__ == "__main__":
    main()
