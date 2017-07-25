import hero
import items
import curses
import cPickle as pickle
import dungeon
import items as i
import weapons as w

move = [ord('w'), ord('s'), curses.KEY_UP, curses.KEY_DOWN]
side_window_width = 37

def save(hero, pad, win, enemies, map_items):
    f = open('save.hero', 'w')
    pickle.dump(hero, f)
    f.close()
    f = open('save.pad', 'w')
    pad.putwin(f)
    f.close()
    f = open('save.win', 'w')
    win.putwin(f)
    f.close()
    f = open('save.enemies', 'w')
    pickle.dump(enemies, f)
    f.close()
    f = open('save.items', 'w')
    pickle.dump(map_items, f)
    f.close()
    dungeon.curses_deinit(win)
    quit()

def open_menu(hero, pad, window, enemies, map_items):
    window.refresh()

    # Window stuff
    menuY, menuX = window.getmaxyx()

    menuY -= 1
    menuX -= 1
    cursor_pos = 0

    #hero stuff

    hero_status = curses.newwin(menuY, side_window_width, 1, menuX-side_window_width)
    hero_status.clear()
    hero_status.box()
    hero_status.border()


    menu = curses.newwin(menuY, menuX, 1, 1)
    menu.keypad(1)
    menu.clear()

    menu.box()
    menu.refresh()
    create_menu(hero, menu, cursor_pos)
    update_status(hero, hero_status)
    hero_status.refresh()
    key = menu.getch()

    while key != ord("i") and key != 27:

        #menu.addstr(2,9, str(cursor_pos))
        #if len(hero.items_inv.keys()) > 0:
            #menu.addstr(2,9, hero.items_inv.keys()[cursor_pos])
        menu.refresh()
        if key in move or key == curses.KEY_UP or key == curses.KEY_DOWN:

            menu.refresh()
            if key == ord("w") or key == curses.KEY_UP:

                cursor_pos = max(0, cursor_pos -1)

            else:

                cursor_pos = min(len(hero.items_inv) -1, cursor_pos + 1)

        elif key == ord("u"):
            if hero.items_inv.keys()[cursor_pos] in i.game_items.keys():
                i.use_item(hero.items_inv.keys()[cursor_pos], hero)
                #menu.addstr(8,3, str(hero.items_inv.keys()[cursor_pos]))
            else:
                weapon = hero.items_inv.keys()[cursor_pos]
                damage = hero.items_inv[weapon][2]
                w.equipWeapon(weapon, damage, hero)
            menu.refresh()
            cursor_pos = 0
        elif key == ord("d"):
            if hero.weapon_equipped:
                w.unequipWeapon(hero)
        elif key == ord("a"):
            if hero.wearing_item:
                items.unequip_item(hero)
        elif key == ord("x"):
             save(hero, pad, window, enemies, map_items)

        menu.clear()
        create_menu(hero, menu, cursor_pos)
        #if len(hero.items_inv.keys()) > 0:
            #menu.addstr(2,9, hero.items_inv.keys()[cursor_pos])
        menu.refresh()
        hero_status.clear()
        update_status(hero, hero_status)
        hero_status.box()
        hero_status.border()
        hero_status.refresh()
        key = menu.getch()

    del menu
    del hero_status


def create_menu(hero, menu, cursor_pos):

    text_x_start = 5
    text_x_count = 30
    text_y_start = 3

    text_y = text_y_start

    inst_y, inst_x = menu.getmaxyx()

    #menu.addstr(inst_y-2, 1, "[x] saves + quits")
    menu.addstr(inst_y-2, 2, "[a] unequip item [d] unequip weapon")
    #menu.addstr(inst_y-4, text_x_start, "[d] unequips weapon")
    menu.addstr(inst_y-3, 2, "[i/Esc] return to game [x] save/quit")
    menu.addstr(inst_y-4, 2, "[u] use/equip selected item")
    menu.addch(text_y + cursor_pos, text_x_start - 2, ">")

    for item in hero.items_inv:

        if item == hero.items_inv:
            item_name = item + "(Equipped)"
        else:
            item_name = item

        if item in i.game_items.keys():
            menu.addstr(text_y, text_x_start, item_name)
            menu.addstr(text_y, text_x_count, str(hero.items_inv[item]))
        else:
            menu.addstr(text_y, text_x_start, item_name)
            #menu.addstr(text_y, text_x_count, str(hero.items_inv[item][2]) + '  attack')
        text_y += 1

    if hero.items_inv:

        try:
            selected = hero.items_inv.keys()[cursor_pos]
        except IndexError:
            selected = hero.items_inv.keys()[0]
        if selected in i.game_items.keys():
            #menu.addstr(2,9, hero.items_inv.keys()[cursor_pos])
            menu.addstr(1, 5, i.game_items[selected][0])
        else:
            #menu.addstr(2,9, hero.items_inv.keys()[cursor_pos])
            menu.addstr(1, 5, hero.items_inv[selected][1] + '. +' + str(hero.items_inv[selected][2]) + ' attack')

    menu.box()
    menu.refresh()

def update_status(hero, status):

    status.addstr(2, 3, "GAME LEVEL:  " + str(hero.dungeonLevel))
    status.addstr(3, 3, "HERO")
    status.addstr(4, 3, hero.hero_type)
    status.addstr(5, 3, "Level: " + str(hero.level))
    status.addstr(6, 3, "XP: " + str(hero.experience))

    health = hero.curHealth
    status.addstr(7, 3, "HEALTH\t" + str(round((health), 1)) + '/' + str(hero.totalHealth()))

    status.addstr(8, 3, "ATTACK\t" + str(hero.total_attack()))

    stamina = hero.curStamina + hero.addedStamina
    status.addstr(9, 3, "STAMINA\t" + str(stamina))

    status.addstr(10, 3, "AGILITY\t" + str(hero.agility))

    intelligence = hero.curInt + hero.addedInt
    status.addstr(11, 3, "INTELLIGENCE\t" + str(intelligence))
    status.addstr(12, 3, "ARMOR:\t" + str(hero.armor))
    status.addstr(13, 3, "HAS KEY:\t" + str(hero.has_key))
    status.addstr(14, 3, "ITEM WORN:\t" + str(hero.wearing_item))
    status.addstr(15, 3, "WEAPON:\t" + str(hero.weapon_equipped))



