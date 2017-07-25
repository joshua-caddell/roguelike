import pad2 as p
import dungeon
import math
import curses
from random import randint
import random
import collections

enemy_types = ['Goblin', 'Arachnid', 'Skeleton']

class Enemy(object):

    def __init__(self, name, character, position, tile, health, attack, avoid):
        """
        Name= this is the enemy type- Goblin, Arachnid, etc
        Character= the ascii character that represents this enemy
        position= enemy coordinates on the pad in form (row, col)
        tile= the tile that the character is standing on
        """
        self.name = name
        self.character = character
        self.position = position
        self.tile = tile
        self.health = health
        self.attack = attack
        self.avoidance = avoid

    def set_position(self, position):
        self.position = position

    def set_tile(self, tile):
        self.tile = tile

    def move_enemy(self, hero, pad, graph, msg):
        """
        enemies[r,c] = [character, ground tile]
        """
        hr,hc = hero.position

        er, ec = self.position

        distance = math.sqrt((math.pow(hc - ec, 2)) + math.pow(hr - er, 2))

        if distance <= 12 and distance > 1:
            if not line_of_sight(pad, hero.position, self.position, graph):
                return

            if hr > er:
                temp_er = er + 1
            elif hr < er:
                temp_er = er - 1
            else:
                temp_er = er

            if hc < ec:
                temp_ec = ec - 1
            elif hc > ec:
                temp_ec = ec + 1
            else:
                temp_ec = ec

            if math.sqrt((math.pow(hc - temp_ec, 2)) + math.pow(hr - er, 2)) <= math.sqrt((math.pow(hc - ec, 2)) + math.pow(hr - temp_er, 2)):
                if pad.instr(er, temp_ec, 1) in p.valid_moves:
                    temp_tile = self.tile
                    self.tile = pad.instr(er, temp_ec, 1) #update tile under enemy
                    pad.addstr(er, temp_ec, self.character)
                    pad.addstr(er, ec, temp_tile)
                    self.position = (er, temp_ec)
                elif pad.instr(temp_er, ec, 1) in p.valid_moves:
                    temp_tile = self.tile
                    self.tile = pad.instr(temp_er, ec, 1)
                    pad.addstr(temp_er, ec, self.character)
                    pad.addstr(er, ec, temp_tile)
                    self.position = (temp_er, ec)
            else:
                if pad.instr(temp_er, ec, 1) in p.valid_moves:
                    temp_tile = self.tile
                    self.tile = pad.instr(temp_er, ec, 1)
                    pad.addstr(temp_er, ec, self.character)
                    pad.addstr(er, ec, temp_tile)
                    self.position = (temp_er, ec)
                elif pad.instr(er, temp_ec, 1) in p.valid_moves:
                    temp_tile = self.tile
                    self.tile = pad.instr(er, temp_ec, 1)
                    pad.addstr(er, temp_ec, self.character)
                    pad.addstr(er, ec, self.tile)
                    self.position = (er, temp_ec)

            er, ec = self.position

            distance = math.sqrt((math.pow(hc - ec, 2)) + math.pow(hr - er, 2))

        if distance == 1:
            hero.defend_attack(self.attack, msg, self.name)

    def defend_attack(self, hero_attack):
        if randint(1, 100) <= self.avoidance:
             return False, 0
        starting_health = self.health
        self.health = self.health - hero_attack
        if self.health < 1:
            return True, starting_health
        else:
            return False, starting_health - self.health


#self, name, character, position, tile, level
class Skeleton(Enemy):#2
    def __init__(self, level, position):
        stat = base = 2
        for i in range(1,level):
            stat += math.floor(math.sqrt(level * base))
        chance_to_dodge = 30
        Enemy.__init__(self, "Skeleton", 'S', position,'.', stat, stat, chance_to_dodge)

class Goblin(Enemy):#3
    def __init__(self, level, position):
        stat = base = 3
        for i in range(1,level):
            stat += math.floor(math.sqrt(level * base))
        chance_to_dodge = 40
        Enemy.__init__(self,"Goblin", 'G', position, '.', stat, stat, chance_to_dodge)

class Arachnid(Enemy):#1
    def __init__(self, level, position):
        stat = base = 1
        for i in range(1,level):
            stat += math.floor(math.sqrt(level * base))
        chance_to_dodge = 20
        Enemy.__init__(self, "Arachnid", 'A', position, '.', stat, stat, chance_to_dodge)

def move_enemies(hero, pad, enemies, graph, msg):
    for enemy in enemies:
            enemy.move_enemy(hero, pad, graph, msg)

def line_of_sight(pad, start, end, graph):
    visited = collections.defaultdict(list)
    q = collections.deque()
    q.append(start)
    visited[start]

    while q:
        cur = q.popleft()
        if cur == end:
            break
        for n in graph[cur]:
            if n not in visited:
                q.append(n)
                visited[n].append(cur)
    return check_line_of_sight(pad, start, end, visited)

def check_line_of_sight(pad, start, end, path):
    rows = p.max_y
    cols = p.max_x

    if path:
        r, c = parent = path[end][0]
        while parent != start:
            r, c = parent = path[parent][0]
            if pad.instr(r, c, 1) in ['-', '|', ' ', ',']:
                return False
    else:
        return False

    return True

def line_of_sight_graph(pad):
    rows = p.max_y
    cols = p.max_x
    graph = collections.defaultdict(list)
    neighbors = [(-1, 0), (0,1), (1,0), (0, -1), (-1, -1), (1,1), (1,-1), (-1, 1)]
    for r in range(rows):
        for c in range(cols):
            for y, x in neighbors:
                if (r+y) <= rows and (c+x) <= cols and (r+y) >= 0 and (c+x) >= 0:
                    graph[(r,c)].append((r+y, c+x))

    return graph


def kill_enemies(hero_pos, pad, enemies):
    hr,hc = hero_pos

    neighbors = [(-1, 0), (0,1), (1,0), (0, -1)]

    for r, c in neighbors:
        pos = (hr + r, hc + c)
        for enemy in enemies:
            if pos == enemy.position:
                pad.addstr(pos[0], pos[1], enemy.tile)
                enemies.pop(enemies.index(enemy))

"""
add_enemies and add_items are easiest now as separate functions,
but they can be refactored into one later on.
this just seemed the most clear and readable way to do it for now.
"""
def add_enemies_room(length, width, room):
    """
    decrease length and width so that nothing is
    added right on the edge, so that you don't
    walk into something upon entering the room
    (because the doors will be added later)
    """
    l = length - 3
    w = width - 3
    enemies = list()
    prob = 100
    # 60, 30, 15 percent chance of spawning enemy
    for i in range(0,5):
        if randint(0,100) < prob:
            enemies.append(True)
        else:
            enemies.append(False)
        prob = prob/2
    for enemy in enemies:
        if enemy == True:
            # random int with more padding
            y = randint(2,w)
            x = randint(2,l)
            #choose new x and y if space is occupied
            while room[x][y] != ".":
                y = randint(2,w)
                x = randint(2,l)

            room[x][y] = "E"
    return room


def init_enemy(enemy_type, position, level):
    if enemy_type == 'Goblin':
        return Goblin(level, position)
    elif enemy_type == 'Skeleton':
        return Skeleton(level, position)
    elif enemy_type == 'Arachnid':
        return Arachnid(level, position)




