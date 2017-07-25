from __future__ import print_function
import time
import pad2 as p
import enemies as e
import dungeon
import hero as h
import curses
import items
import cPickle as pickle
import os.path
import inventory
import overlay
from random import randint

def load():
    f = open('save.hero', 'r')
    hero = pickle.load(f)
    f.close()
    p.init_game(hero, hero.dungeonLevel, hero.cetus_amulet_level)
    f = open('save.pad', 'r')
    pad = curses.getwin(f)
    f.close()
    f = open('save.win', 'r')
    win = curses.getwin(f)
    f.close()
    f = open('save.enemies', 'r')
    enemies = pickle.load(f)
    f.close()
    f = open('save.items', 'r')
    map_items = pickle.load(f)
    f.close()
    p.place_hero(hero, pad, True)
    return hero, pad, win, enemies, map_items

def main(scr):

    newGame, char = p.splash_screen_func()

    if newGame == True:
        if char == "K":
            hero = h.Knight()
        elif char == "A":
            hero = h.Assassin()
        else:
            hero = h.Sorcerer()

        win, pad, enemies, map_items = p.init_game(hero, hero.dungeonLevel, hero.cetus_amulet_level)
        p.place_hero(hero, pad)
    else:
        hero, pad, win, enemies, map_items = load()
        os.remove('save.hero')
        os.remove('save.pad')
        os.remove('save.win')
        os.remove('save.enemies')
        os.remove('save.items')

    los_graph = e.line_of_sight_graph(pad)
    win2 = curses.newwin(4,40)
    msg = list()
    for i in range(3):
        msg.append(' ')
    dead = won = False
    q = -1
    while q != 27:
        overlay.update_status(pad, win2, hero, msg)
        #finding stairs advnaces to the next level
        if hero.tile == '%':
            if hero.dungeonLevel != 15:
                if hero.has_key:
                    dungeon.curses_deinit(win)
                    pad.erase()
                    hero.dungeonLevel += 1
                    win, pad, enemies, map_items = p.init_game(hero, hero.dungeonLevel, hero.cetus_amulet_level)
                    hero.has_key = False
                    p.place_hero(hero, pad)
                else:
                    msg.insert(0, 'You need a key')
            else:
                if hero.has_key:
                    if hero.wearing_item == 'Cetus Amulet':
                        won = True
                        break
                    else:
                       msg.insert(0, 'You need some sort of magic')
                else:
                    msg.insert(0, 'You need a key')
            overlay.update_status(pad, win2, hero, msg)

        q = pad.getch()

        if q != 27 and q in p.move:
            p.walk(pad, hero, q, enemies, map_items, msg)
            e.move_enemies(hero, pad, enemies, los_graph, msg)
            p.redraw_pad(pad, hero.position)
            hero.decrement_stamina()
        elif q == ord('e'):
            hero.eat_food()
        elif q == ord('c'):
            hero.drink_coffee()
        elif q == ord('f'):
            hero.special_attack(enemies, msg, pad)
            p.redraw_pad(pad, hero.position)
        elif q == ord('i'):
            inventory.open_menu(hero, pad, win, enemies, map_items)
            p.redraw_pad(pad, hero.position)

        if hero.curHealth <= 0:
            dead = True
            break

    if dead == True or won == True:
        time.sleep(.75)
        p.end_screen_func(win, won)
        time.sleep(.75)

    dungeon.curses_deinit(win2)


if __name__ == "__main__":
    curses.wrapper(main)
