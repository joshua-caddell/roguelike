import curses
import pad2 as p
from math import floor


def update_status(pad, win, hero, msg):
    win.erase()
    win.overlay(pad, 0, 0, 0,  0, 3, 11)
    win.addstr(0,0, "HP: " + str(round(hero.curHealth, 1)) + '/' + str(hero.totalHealth()) + ' | ' + "ARM: " + str(hero.armor) + ' | ' + "STAM: " + str(round(hero.curStamina, 1)) + '/' + str(hero.maxStamina))


    length = min(2, len(msg))
    row = 1
    for i in range(length, -1, -1):
        win.addstr(row,0, msg[i])
        row+=1

    win.refresh()

