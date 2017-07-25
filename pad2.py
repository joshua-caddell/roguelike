import curses
import time
from random import randint
import os.path
import dungeon
import hero
import enemies as e
import items as items_module

splash_screen = [" a88888b.            dP                                         ",
	    	 "d8'   `88            88                                         ",
		 "88        .d8888b. d8888P dP    dP .d8888b.                     ",
		 "88        88ooood8   88   88    88 Y8ooooo.                     ",
		 "Y8.   .88 88.  ...   88   88.  .88       88                     ",
		 " Y88888P' `88888P'   dP   `88888P' `88888P'                     ",
		 "ooooooooooooooooooooooooooooooooooooooooooooooo                 ",
		 "                                                                ",
		 "888888ba                                                        ",
		 "88    `8b                                                       ",
		 "88     88 dP    dP 88d888b. .d8888b. .d8888b. .d8888b. 88d888b. ",
		 "88     88 88    88 88'  `88 88'  `88 88ooood8 88'  `88 88'  `88 ",
		 "88    .8P 88.  .88 88    88 88.  .88 88.  ... 88.  .88 88    88 ",
		 "8888888P  `88888P' dP    dP `8888P88 `88888P' `88888P' dP    dP ",
		 "ooooooooooooooooooooooooooooo~~~~.88~ooooooooooooooooooooooooooo",
		 "                             d8888P                             "]


dead_screen = ["dP    dP                    888888ba  00                dP",
               "Y8.  .8p                    88    `8b                   88",
               " Y8aa8p .d8888b. dP    dP   88     88 dP .d8888b. .d888b88",
               "   88   88'  '88 88    88   88     88 88 88ddddd8 88'  `88",
               "   88   88.  .88 88   .88   88    .8P 88 88.  ... 88.  .88",
               "   dP   `88888P' `88888P'   8888888P  dP `88888P' `88888P8"]

win_screen = ["dP    dP                    dP   dP   dP                 ",
              "Y8.  .8p                    88   88   88                 ",
              " Y8aa8p .d8888b. dP    dP   88  .8P  .8P .d8888b. 88d88b.",
              "   88   88'  '88 88    88   88  d8'  d8' 88'  `88 88' `88",
              "   88   88.  .88 88   .88   88.d8P8.d8P  88.  .88 88   88",
              "   dP   `88888P' `88888P'   8888' Y88'   `88888P' dP   dP"]

end_screen = ["d888888P dP                   8888888b                dP",
              "   88    88                   88                      88",
              "   88    88d888b. .d8888b.   a88aaaa    88d88b. .d888b88",
              "   88    88'  `88 88ddddd8    88        88' `88 88'  `88",
              "   88    88    88 88.  ...    88        88   88 88.  .88",
              "   dP    dp    dP `88888P'    88888888P dP   dP `88888P8"]




max_x = 300
max_y = 75
#span_x = 75
#span_y = 20
pad_pos_x = 0
pad_pos_y = 0

obs = list()
move = [ord('w'), ord('a'), ord('d'), ord('s'), ord('h'), ord('j'), ord('k'), ord('l'), curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]

ground = ['.', '#', '+', '%']
items = ['~', 'a', 'c', 'h', 's', 'b', 'p', 'e', '*', 'r', '/', '&']
valid_moves = items + ground

def walk_input(q, x, y, pad, hero, enemies, map_items, msg):

    if (q == ord('w') or q == curses.KEY_UP or q == ord('k')) and y > 1:
        new_y = y - 1
        new_x = x
    elif (q == ord('s') or q == curses.KEY_DOWN or q == ord('j')) and y < max_y:
        new_y = y + 1
        new_x = x
    elif (q == ord('a') or q == curses.KEY_LEFT or q == ord('h')) and x > 1:
        new_x = x - 1
        new_y = y
    elif (q == ord('d') or q == curses.KEY_RIGHT or q == ord('l')) and x < max_x:
        new_x = x + 1
        new_y = y
    else:
        new_x = x
        new_x = x
        new_y = y

    ground_char = pad.instr(new_y, new_x, 1)

    if ground_char in ground or ground_char in items:
        #if hero picks up item, ground change to .
        if ground_char in items:
            if hero.pick_up_item((new_y, new_x), pad, map_items, msg):
                ground_char = '.'

        temp_tile = hero.tile
        temp_pos = (y, x)

        x = new_x
        y = new_y

        hero.position = (y,x)
        hero.tile = ground_char

        pad.addch(temp_pos[0], temp_pos[1], temp_tile)
        pad.addch(y, x, ord('@'))
    elif ground_char in ['A', 'S', 'G']:
        hero.attack_enemy((new_y, new_x), enemies, pad, msg, False)



    return x,y, ground_char

def redraw_pad(pad, new_pos):

    global pad_x
    global pad_y

    y, x = new_pos
    pad_x = x - span_x / 2
    pad_y = y - span_y / 2

    if pad_x < 0:
        pad_x = 0
    elif pad_x > max_x - span_x:
        pad_x = max_x - span_x

    if pad_y < 0:
        pad_y = 0
    elif pad_y > max_y - span_y:
        pad_y = max_y - span_y

    pad.noutrefresh(pad_y, pad_x, pad_pos_y, pad_pos_x, span_y, span_x)
    curses.doupdate()


def walk(pad, hero, q, enemies, map_items, msg):

    r, c = hero.position
    new_pos  = list()
    x, y, ground_char = walk_input(q, c, r, pad, hero, enemies, map_items, msg)

def init_game(hero, level, cetus_amulet_level):

    win = dungeon.curses_init()
    global span_y
    global span_x
    span_y, span_x = win.getmaxyx()
    span_y -= 1
    span_x -= 1
    pad = curses.newpad(max_y, max_x)
    pad.keypad(1) #allow curses to interpret arrow keys
    enemies = list()
    map_items = dungeon.generate_rooms(pad, enemies, level, cetus_amulet_level)
    return win, pad, enemies, map_items

def place_hero(hero, pad, save=False):
    if save == False:
        pos_char = -1
        while pos_char != ground[0]:
            pos_x = randint(1, max_x-1)
            pos_y = randint(1, max_y-1)
            pos_char = pad.instr(pos_y, pos_x, 1)

        hero.position = (pos_y, pos_x)
        hero.tile = '.'
    else:
        pos_y, pos_x = hero.position

    pad.addch(pos_y, pos_x, '@')

    pad_x = pos_x - span_x / 2
    pad_y = pos_y - span_y / 2

    if pad_x < 0:
        pad_x = 0
    elif pad_x > max_x - span_x:
        pad_x = max_x - span_x

    if pad_y < 0:
        pad_y = 0
    elif pad_y > max_y - span_y:
        pad_y = max_y - span_y

    pad.noutrefresh(pad_y, pad_x, pad_pos_y, pad_pos_x, span_y, span_x)
    curses.doupdate()


def splash_screen_func():

    choice = ""
    char = ""
    screen = curses.initscr()
    curses.noecho()
    max_y, max_x = screen.getmaxyx()
    center_y = max_y/2
    center_x = max_x/2
    y_splash = 16
    x_splash = 64
    y_start = center_y - (y_splash/2)
    x_start = center_x - (x_splash/2)
    save = False

    screen.clear()
    screen.border(0)
    for y, line in enumerate(splash_screen):
        screen.addstr(y+y_start, x_start, line)

    screen.addstr(max_y-3, center_x-14, "Press any key to continue...")
    screen.getch()
    screen.erase()

    if os.path.exists('save.hero'):
        save = True
        screen.border(0)
        screen.addstr(2, 2, "Would you like to load the previous game? (Y/N)")
        screen.move(3, 2)
        while choice != "Y" and choice != "N":
            screen.refresh()
            choice = screen.getkey()
            choice = choice.upper()
            screen.addstr(3, 2, choice)
        if choice == "Y":
            return False, None
        if choice == "N":
            os.remove('save.hero')
            os.remove('save.pad')
            os.remove('save.win')
            os.remove('save.enemies')
            os.remove('save.items')
    if save == False or choice == "N":
        screen.erase()
        screen.border(0)

        screen.addstr(2, 2, "Welcome To The Dungeon!")
        screen.addstr(4, 2, "Here Are The Fighters:")
        screen.addstr(5, 2, hero.Knight().hero_type + ": " + hero.Knight().desc())
        screen.addstr(6, 2, hero.Assassin().hero_type + ": " + hero.Assassin().desc())
        screen.addstr(7, 2, hero.Sorcerer().hero_type + ": " + hero.Sorcerer().desc())
        screen.addstr(9, 2, "Choose Your Character: (K/A/S)")
        screen.move(10, 2)
        while char != "K" and char != "A" and char != "S":
            screen.refresh()
            char = screen.getkey()
            char = char.upper()
            screen.addstr(10, 2, char)
        return True, char

def end_screen_func(window, won):
    window.refresh()
    max_y, max_x = window.getmaxyx()

    border_y = max_y-6
    border_x = max_x-6

    screen = curses.newwin(border_y, border_x, 3, 3)
    screen.border()

    max_y, max_x = screen.getmaxyx()

    center_y = max_y/2
    center_x = max_x/2
    y_all = 6
    x_won = 56
    x_dead = 58
    x_end = 56

    if won == True:
        y_start = center_y - (y_all/2)
        x_start = center_x - (x_won/2)
        for y, line in enumerate(win_screen):
            screen.addstr(y+y_start, x_start, line)
    else:
        y_start = center_y - (y_all/2)
        x_start = center_x - (x_dead/2)
        for y, line in enumerate(dead_screen):
            screen.addstr(y+y_start, x_start, line)

    screen.getch()

    screen.erase()
    screen.border()

    y_start = center_y - (y_all/2)
    x_start = center_x - (x_end/2)
    for y, line in enumerate(end_screen):
        screen.addstr(y+y_start, x_start, line)


    screen.getch()

